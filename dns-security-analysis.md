# DNS Security Analysis – The Knowledge Hub
**REQ-S2P3-009 | Task 7 | Author: Fernando Rodriguez**

---

## 1. Current DNS Security Posture

The Knowledge Hub currently operates a hybrid cloud environment combining an on-premises network (connected via Site-to-Site VPN) with Azure infrastructure. In its current state:

- **Internal DNS resolution** is handled by the on-premises pfSense router, which forwards queries to the ISP's default DNS resolvers.
- **Azure workloads** (App Service, Azure SQL) use Azure's internal DNS by default (`168.63.129.16`), which is encrypted within Azure's backbone but opaque to the organisation.
- **No explicit DNS security mechanisms** (DoH, DoT, or DNSSEC) have been configured on either the on-premises side or for client workstations.

**Identified risks:**
| Risk | Description |
|------|-------------|
| DNS Spoofing / Cache Poisoning | An attacker on the same network path could intercept unencrypted UDP DNS traffic and inject malicious responses. |
| DNS Eavesdropping | Plain DNS queries expose which websites/services staff visit, leaking internal infrastructure information. |
| Man-in-the-Middle (MITM) | Without validation, clients cannot verify that a DNS response is authentic. |

---

## 2. DNS Security Mechanisms Compared

### 2.1 DNS over HTTPS (DoH) – RFC 8484
DoH encrypts DNS queries by wrapping them inside standard HTTPS traffic (port 443). Because it is indistinguishable from regular web traffic, it is effectively immune to network-level blocking.

| Aspect | Detail |
|--------|--------|
| **Protocol** | DNS inside HTTPS (port 443) |
| **Encryption** | Yes (TLS 1.2+) |
| **Authentication** | Yes (TLS certificates) |
| **Implementation** | Browser-level or OS-level (Windows 11, Android) |
| **Pros** | Hardest to block, works through restrictive firewalls, widely supported by browsers and modern OSes |
| **Cons** | Bypasses central IT network monitoring; harder for enterprise administrators to inspect or filter DNS centrally |

### 2.2 DNS over TLS (DoT) – RFC 7858
DoT encrypts DNS queries using TLS on a **dedicated port (853)**. Because it uses a separate port, network administrators can more easily monitor, allow, or block it compared to DoH.

| Aspect | Detail |
|--------|--------|
| **Protocol** | DNS inside TLS (port 853) |
| **Encryption** | Yes (TLS 1.2+) |
| **Authentication** | Yes (TLS certificates) |
| **Implementation** | OS-level or DNS resolver level (pfSense can act as forwarder) |
| **Pros** | Protects traffic in transit; allows enterprise network-level control and monitoring; supported by pfSense's Unbound resolver |
| **Cons** | Port 853 can be blocked by restrictive ISPs; slightly higher latency than plain DNS |

### 2.3 DNSSEC – RFC 4033/4034/4035
DNSSEC does **not encrypt** DNS queries. Instead, it adds **cryptographic signatures** to DNS records, allowing clients to verify that a response truly originates from the authoritative server and has not been tampered with.

| Aspect | Detail |
|--------|--------|
| **Protocol** | DNS with RSA/ECDSA signatures (standard ports 53/853) |
| **Encryption** | ❌ No (queries remain visible) |
| **Authentication** | ✅ Yes (chain of trust from root zone) |
| **Implementation** | Configured on the DNS zone/registrar and validated by the resolver |
| **Pros** | Prevents DNS spoofing and cache poisoning at the root level; protects public-facing zones |
| **Cons** | Does not protect privacy; complex to manage (key rotation); relies on registrar/hosting support |

---

## 3. Recommendation for The Knowledge Hub

The optimal strategy is a **layered approach**, combining DoT and DNSSEC:

### Primary Recommendation: DNS over TLS (DoT) on pfSense
Configure pfSense's **Unbound DNS resolver** to forward all DNS queries over TLS to a trusted upstream provider (e.g., Cloudflare `1.1.1.1` or Quad9 `9.9.9.9`).

**Why DoT over DoH for The Knowledge Hub:**
- The Knowledge Hub is a library with a managed network. DoT on the gateway **protects all devices on the network** without requiring per-device configuration.
- IT administrators retain the ability to **monitor DNS traffic** on port 853 using pfSense's logging capabilities, which is essential for compliance and the IDS integration (Suricata).
- pfSense has native support for DoT via Unbound, making implementation straightforward.

### Secondary Recommendation: DNSSEC Validation
Enable **DNSSEC validation** in Unbound on pfSense. This ensures that DNS responses received from upstream resolvers have a valid cryptographic chain of trust, preventing cache poisoning attacks even before they reach the network.

**Complementary (not replacing DoT):** DoH can be enabled on staff workstations managed via Intune for an additional layer of protection when working remotely outside the library network.

---

## 4. Implementation Plan (pfSense – Unbound)

The following configuration would be applied to the pfSense VM in the on-premises environment:

```
# pfSense > Services > DNS Resolver > Custom Options
server:
  tls-upstream: yes
  tls-cert-bundle: "/etc/ssl/cert.pem"

forward-zone:
  name: "."
  forward-tls-upstream: yes
  forward-addr: 1.1.1.1@853#cloudflare-dns.com
  forward-addr: 1.0.0.1@853#cloudflare-dns.com
  forward-addr: 9.9.9.9@853#dns.quad9.net
```

And DNSSEC validation enabled via:
- pfSense > Services > DNS Resolver > DNSSEC ✅ Enabled

---

## 5. Summary

| Mechanism | Encrypts Queries | Validates Responses | Recommended |
|-----------|:-:|:-:|:-:|
| DoH | ✅ | ❌ | ✅ (client devices / remote work) |
| DoT | ✅ | ❌ | ✅ **Primary – pfSense gateway** |
| DNSSEC | ❌ | ✅ | ✅ **Secondary – combined with DoT** |

**Final recommendation:** Implement **DoT on pfSense** as the primary control (encrypts all DNS on the network), combined with **DNSSEC validation** (ensures authenticity of responses). This satisfies **REQ-S2P3-009** while maintaining enterprise-grade visibility and control appropriate for a managed library environment.
