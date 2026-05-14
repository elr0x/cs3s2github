# System Testing and Integration Report
**REQ-S2P3-009 | Task 13 | Author: Fernando Rodriguez**

---

## 1. Overview
This document outlines the final integration and testing of all components within The Knowledge Hub's monitoring solution, verifying that the frontend, backend, collectors, authentication, and CI/CD pipeline operate successfully end-to-end.

## 2. Components Integrated
The following major components have been successfully integrated:
- **Flask Web Application (Frontend & Backend):** Provides the user interface and serves the `/dashboard` routes.
- **Monitoring API:** Handles incoming metrics from collectors and inserts them into Azure SQL Database.
- **Monitoring Client (`monitor.py`):** Runs on endpoints and container hosts to gather system metrics (CPU, RAM, Disk) and Docker container metrics via the Docker SDK.
- **Entra ID Authentication:** Secures the web dashboard, ensuring only authorized users in the tenant can access the interface.
- **Azure SQL Database:** Persistently stores all incoming metrics and health checks.
- **CI/CD Pipeline (GitHub Actions):** Automates testing, Docker image building, pushing to ACR, and deployment to Azure App Service using a Publish Profile.

---

## 3. Test Cases & Results

### 3.1 Data Collection & API Integration
| Test Case ID | Description | Expected Result | Actual Result | Status |
|---|---|---|---|---|
| TC-01 | Run `monitor.py` locally | Script collects host and Docker metrics without errors | Metrics collected successfully | ✅ Pass |
| TC-02 | Send metrics to API | API receives POST request and returns HTTP 201 Created | HTTP 201 received | ✅ Pass |
| TC-03 | Database Insertion | API inserts metric data (including `timestamp`) into Azure SQL | Data verified in SQL tables | ✅ Pass |
| TC-04 | Handle Missing Status | API handles `null` status values gracefully during retrieval | Handled with fallback to `UNKNOWN` | ✅ Pass |

### 3.2 Web Dashboard & UI
| Test Case ID | Description | Expected Result | Actual Result | Status |
|---|---|---|---|---|
| TC-05 | Dashboard Loading | `/dashboard` loads without 500 Internal Server errors | Dashboard renders correctly | ✅ Pass |
| TC-06 | Host Details View | `/dashboard/host/<hostname>` displays specific host metrics | Metrics displayed per host | ✅ Pass |
| TC-07 | Chart Rendering | Mini-charts render correctly without infinite resize loops | Charts constrained to 120px height | ✅ Pass |
| TC-08 | Entra ID Login | Unauthenticated users are redirected to Microsoft login | Redirection and login successful | ✅ Pass |

### 3.3 CI/CD Pipeline Deployment
| Test Case ID | Description | Expected Result | Actual Result | Status |
|---|---|---|---|---|
| TC-09 | Trigger Pipeline | Push to `main` triggers GitHub Actions workflow | Workflow started automatically | ✅ Pass |
| TC-10 | Unit Tests | `pytest` runs and validates core logic | Tests pass | ✅ Pass |
| TC-11 | Docker Build & Push | Image is built and pushed to Azure Container Registry | Image verified in ACR | ✅ Pass |
| TC-12 | App Service Deploy | Web app is restarted with the latest container image | Deployment successful via Publish Profile | ✅ Pass |

---

## 4. Known Issues & Resolutions
During the final integration, several issues were encountered and resolved:
1. **Timestamp NULL values:** The database insert query was missing the `timestamp` field. **Resolved** by using `GETUTCDATE()` in the SQL `INSERT` statement.
2. **Dashboard 500 Error (NoneType upper):** Occurred when processing metrics with a `NULL` status. **Resolved** by adding a fallback `or "UNKNOWN"` before calling `.upper()`.
3. **Infinite Chart Resize:** Chart.js caused an infinite loop in the browser. **Resolved** by wrapping the `<canvas>` in a fixed-height `div` with `overflow: hidden` and `animation: false`.
4. **CI/CD Credential Privileges:** Encountered issues using an Azure Service Principal for deployment. **Resolved** by migrating the deployment step to use an Azure Web App Publish Profile instead.

## 5. Conclusion
The monitoring solution is fully integrated and functioning as intended. Data flows seamlessly from the Python collector scripts to the Azure SQL backend, and is visualized securely on the Flask dashboard. The automated CI/CD pipeline ensures reliable and consistent deployments.
