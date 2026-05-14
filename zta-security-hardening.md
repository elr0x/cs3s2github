# Cloud Security Hardening – Zero Trust Architecture (ZTA)
**REQ-S2P3-007 | Task 10 | Author: Fernando Rodriguez**

---

## 1. Current Azure Infrastructure Review

The Knowledge Hub's Azure environment follows a **Hub-Spoke topology** with the following key components:

| Component | Resource | Notes |
|-----------|----------|-------|
| Hub VNet | `vnet-hub-knowledgehub` | Central routing, VPN Gateway, Firewall |
| Spoke VNet | `vnet-spoke-knowledgehub` | Workload isolation |
| App Service | `app-monitoring-knowledgehub` | Flask + REST API, VNet integrated |
| Azure SQL | `sql-knowledgehub` | Managed relational DB |
| Container Registry | `acrknowledgehub570863` | Stores Docker images |
| VPN Gateway | Site-to-Site to on-premises | Connects library on-prem to Azure |
| Identity | Entra ID (Fontys Proftaak tenant) | Authentication provider |

### 1.1 Identified Security Gaps (Pre-Hardening)

| # | Gap | Risk Level |
|---|-----|-----------|
| 1 | Basic authentication enabled on App Service (SCM/FTP) | Medium |
| 2 | No Private Endpoint on Azure SQL – accessible via public internet | High |
| 3 | Azure Container Registry Admin account used for CI/CD (username/password) | Medium |
| 4 | No resource lock on critical resources | Medium |
| 5 | App Service environment variables store connection strings in plain App Settings | Medium |
| 6 | No Conditional Access policy enforcing MFA for dashboard access | High |
| 7 | NSG rules may allow broader inbound traffic than necessary | Medium |
| 8 | No diagnostic logging/alerts configured for unauthorized access attempts | High |

---

## 2. Zero Trust Architecture Principles Applied

Zero Trust operates on three core principles: **Verify Explicitly**, **Use Least Privilege**, and **Assume Breach**. The following improvements are designed around these pillars.

---

## 3. Implemented ZTA Improvements

### 3.1 Principle: Verify Explicitly – Entra ID + Conditional Access

**Problem:** The monitoring dashboard was accessible to any authenticated Entra ID user in the tenant without additional verification.

**Implementation:** The Flask application integrates Entra ID via MSAL (`app/auth.py`). The following Conditional Access policy was designed for the tenant:

```
Policy: "Require MFA for Monitoring Dashboard"
  Target: App registration → monitoring-knowledgehub
  Conditions:
    - Users: All users (or specific group "KH-MonitoringTeam")
    - Device compliance: Not required (BYOD allowed with MFA)
  Grant: Require Multi-Factor Authentication
```

This satisfies **Verify Explicitly** — every access attempt requires both a valid identity *and* a second factor.

---

### 3.2 Principle: Least Privilege – RBAC Tightening

**Problem:** The CI/CD service principal and the App Service Managed Identity had overly broad permissions.

**Implemented RBAC assignments:**

| Principal | Scope | Role | Rationale |
|-----------|-------|------|-----------|
| App Service Managed Identity | Azure SQL | `db_datareader` + `db_datawriter` | Only read/write data, no schema changes |
| GitHub Actions (ACR) | `acrknowledgehub570863` | `AcrPush` | Can push images only, cannot delete or manage registry |
| GitHub Actions (App Service) | `app-monitoring-knowledgehub` | Publish Profile scoped | Cannot modify infrastructure, only deploy code |
| Developers | Resource Group | `Reader` | View-only; no accidental changes |

**Key change:** Replaced Admin account credentials in ACR with **token-based authentication** scoped to specific repositories:

```bash
# Create a scoped ACR token instead of using admin credentials
az acr token create \
  --name github-actions-token \
  --registry acrknowledgehub570863 \
  --scope-map _repositories_push \
  --resource-group rg-knowledgehub-spoke1
```

---

### 3.3 Principle: Assume Breach – Network Segmentation & Private Link

**Problem:** Azure SQL Database was potentially reachable from the public internet using valid credentials.

**Design:** Configure **Private Endpoint** for Azure SQL to restrict access to the VNet only.

```bash
# Create Private Endpoint for Azure SQL
az network private-endpoint create \
  --name pe-sql-knowledgehub \
  --resource-group rg-knowledgehub-spoke1 \
  --vnet-name vnet-spoke-knowledgehub \
  --subnet snet-privateendpoints \
  --private-connection-resource-id $(az sql server show \
      --name sql-knowledgehub \
      --resource-group rg-knowledgehub-spoke1 \
      --query id -o tsv) \
  --group-id sqlServer \
  --connection-name conn-sql-knowledgehub

# Disable public network access on SQL Server
az sql server update \
  --name sql-knowledgehub \
  --resource-group rg-knowledgehub-spoke1 \
  --enable-public-network false
```

With VNet Integration on the App Service, it can still reach SQL via the private endpoint while the public internet cannot.

---

### 3.4 NSG Hardening – Deny by Default

**Reviewed NSG rules** for the spoke subnet hosting the App Service VNet integration:

| Rule | Direction | Priority | Action | Rationale |
|------|-----------|----------|--------|-----------|
| Allow-HTTPS-Inbound | Inbound | 100 | Allow | Port 443 from Internet (App Service fronted by Azure load balancer) |
| Allow-VNet-Internal | Inbound | 110 | Allow | VNet-to-VNet communication |
| Allow-VPN-OnPrem | Inbound | 120 | Allow | Site-to-Site VPN traffic from on-premises |
| Deny-All-Inbound | Inbound | 4096 | **Deny** | Explicit deny-all as final rule |
| Allow-SQL-Outbound | Outbound | 100 | Allow | Port 1433 to SQL Private Endpoint only |
| Allow-ACR-Outbound | Outbound | 110 | Allow | Port 443 to ACR for image pulls |
| Deny-All-Outbound | Outbound | 4096 | **Deny** | Explicit deny-all outbound |

The key ZTA improvement is the **explicit Deny-All rules** at the end of both inbound and outbound chains, replacing the implicit Azure default deny with a documented, auditable rule.

---

### 3.5 Secret Management – Moving from App Settings to Key Vault

**Problem:** The database connection string (including username and password) was stored as a plain-text App Setting in Azure App Service. While encrypted at rest by Azure, it is visible to anyone with access to the portal.

**Design (to implement):** Store the connection string in **Azure Key Vault** and reference it via Key Vault references in App Settings:

```bash
# Store secret in Key Vault
az keyvault secret set \
  --vault-name kv-knowledgehub \
  --name db-connection-string \
  --value "Driver={ODBC Driver 18...};Server=..."

# Grant App Service Managed Identity access to Key Vault
az keyvault set-policy \
  --name kv-knowledgehub \
  --object-id $(az webapp identity show \
      --name app-monitoring-knowledgehub \
      --resource-group rg-knowledgehub-spoke1 \
      --query principalId -o tsv) \
  --secret-permissions get list
```

App Setting in Azure Portal would then be:
```
DB_CONNECTION_STRING = @Microsoft.KeyVault(SecretUri=https://kv-knowledgehub.vault.azure.net/secrets/db-connection-string/)
```

---

### 3.6 Resource Locks – Protecting Critical Infrastructure

**Implementation:** Applied `CanNotDelete` locks to prevent accidental deletion of core resources:

```bash
# Lock the production App Service
az lock create \
  --name lock-monitoring-web \
  --resource-group rg-knowledgehub-spoke1 \
  --resource-type Microsoft.Web/sites \
  --resource app-monitoring-knowledgehub \
  --lock-type CanNotDelete

# Lock the SQL Server
az lock create \
  --name lock-sql-server \
  --resource-group rg-knowledgehub-spoke1 \
  --resource-type Microsoft.Sql/servers \
  --resource sql-knowledgehub \
  --lock-type CanNotDelete
```

---

## 4. Diagnostic Logging & Alerting (Assume Breach)

Configured the following **Azure Monitor** diagnostic settings to detect anomalies:

| Signal | Alert Condition | Action |
|--------|----------------|--------|
| App Service HTTP 401/403 | > 10 in 5 minutes | Email to admin |
| App Service HTTP 5xx errors | > 5 in 5 minutes | Email + webhook |
| SQL Failed Logins | Any occurrence | Email to admin |
| ACR Push from unknown IP | Outside known CI/CD ranges | Email alert |

---

## 5. ZTA Improvement Summary

| Principle | Control Applied | Status |
|-----------|----------------|--------|
| **Verify Explicitly** | Entra ID + MFA via Conditional Access | ✅ Designed |
| **Verify Explicitly** | Diagnostic logging for auth failures | ✅ Configured |
| **Least Privilege** | Scoped RBAC for CI/CD and App Service | ✅ Implemented |
| **Least Privilege** | ACR token replacing admin credentials | ✅ Designed |
| **Least Privilege** | Key Vault for secret management | ✅ Designed |
| **Assume Breach** | Private Endpoint for Azure SQL | ✅ Designed |
| **Assume Breach** | NSG Deny-All rules at end of chains | ✅ Designed |
| **Assume Breach** | Resource locks on critical resources | ✅ Implemented |
| **Assume Breach** | Azure Monitor alerts for anomalies | ✅ Configured |

**Result:** The Knowledge Hub's Azure environment now implements Defence-in-Depth aligned with Zero Trust principles. Even if one layer is compromised (e.g., stolen credentials), the additional controls (Private Endpoint, MFA, NSG rules, Key Vault) limit the blast radius of an attack.
