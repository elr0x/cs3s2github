-- -
- Tags
#S1 #P2
---
# To-Do List (Project)
- [ ] TODO
# To-Do List (Feedback)
- [ ] TODO
---
# Business Context

**The Knowledge Hub** library is expanding its digital capabilities by transitioning from a pure on-premises setup (S2P1) into a **hybrid cloud environment**. Key business drivers include:​

- Deploying an **internal application** via PaaS, accessible only through the private network
    
- Establishing a **secure Azure Landing Zone** with Hub-Spoke topology as a governed cloud foundation
    
- Creating a **Site-to-Site VPN** between on-premises infrastructure and Azure
    
- Evolving the **monitoring tool** from S2P1 into a cloud-integrated API + managed database solution
    
- Implementing **modern endpoint management** (Intune) for staff workstations
    
- Ensuring **GDPR/AVG compliance**, OPEX/CAPEX cost awareness, and structured project management throughout​
# Requirements
| ID                          | Title                                  | Summary                                                                                                                                         |
| --------------------------- | -------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| **REQ-S2P3-001**            | Monitoring Web Interface               | The monitoring app must be accessible via a secure web interface for authorized staff, without requiring CLI or direct server access.           |
| **REQ-S2P3-002**            | Secure Access via Identity System      | Access to the web interface must be controlled through the central cloud-based identity management system (Entra ID).                           |
| **REQ-S2P3-003**            | Application Modernization – Deployment | Application components must be deployable as independent, scalable units (containers) to improve resilience and maintainability.                |
| **REQ-S2P3-004**            | Automated Delivery (CI/CD)             | An automated system must be in place to build, test, and deploy the application whenever changes are made to the codebase.                      |
| **REQ-S2P3-005**            | On-Premise Containerized Frontend      | The web frontend must be deployed as a Docker container on on-premise hardware at the main library.                                             |
| **REQ-S2P3-006**            | Extended Container Monitoring          | The monitoring system must be enhanced to provide visibility into the health and performance of the container environments.                     |
| **REQ-S2P3-007**            | Cloud Security – Zero Trust            | The cloud infrastructure must be hardened by applying Zero Trust principles (verify explicitly, least privilege, assume breach).                |
| **REQ-S2P3-008**            | IPv6 Network Support                   | The main library's network must be configured to support IPv6 addressing.                                                                       |
| **REQ-S2P3-009**            | DNS Security                           | Mechanisms must be implemented to enhance the security and integrity of DNS lookups.                                                            |
| **REQ-S2P3-010**            | Configuration Data Management          | Configurations must be managed using structured, human-readable formats (YAML/JSON) suitable for version control and automation.                |
| **REQ-S2P3-011**            | Configuration Automation (Ansible)     | Configuration management tooling (e.g., Ansible) must be explored and documented for managing the on-premise Docker host.                       |
| **REQ-S2P3-012**            | Service Resilience & Backup            | Backup and restore strategies for the containerized application environment must be defined and documented.                                     |
| **REQ-S2P3-013**            | Operational Management Processes       | Incident, problem, and change management considerations must accompany the introduction of the new deployment model and security enhancements.  |
| **REQ-SEC-01 _(Flavor A)_** | Automated IP Blocklisting              | The network must automatically and proactively block connections to/from known malicious IP addresses using up-to-date blocklists.              |
| **REQ-SEC-02 _(Flavor A)_** | Intrusion Detection (IDS)              | A system must inspect network traffic for known attack patterns and generate alerts for detected attempts.                                      |
| **REQ-SEC-03 _(Flavor A)_** | Secure Reverse Proxy Access            | The internal web app must be securely accessible from external networks without direct server exposure, with encryption and traffic inspection. |

---
# Core Assignments

## Week 1 – Analysis, Design, and Foundation

## Task 1: Project Planning & Requirement Analysis

| Subtask                             | Description                                                                                      | State |
| ----------------------------------- | ------------------------------------------------------------------------------------------------ | ----- |
| Analyze all functional requirements | Review all core REQs and Flavor A requirements                                                   | X     |
| Develop project plan                | Create plan with tasks, deliverables, estimated effort, and dependencies (Azure DevOps / Trello) | X     |
| Ongoing plan review                 | Monitor progress, identify blockers, and document key decisions                                  | X     |

## Task 2: Web Frontend Development (Flask)

| Subtask                               | Description                                                             | State |
| ------------------------------------- | ----------------------------------------------------------------------- | ----- |
| Analyze web interface functionalities | Determine what information and features the web interface should expose | X     |
| Design wireframes and Flask routes    | Create mockups, design routes, templates, and static asset structure    | X     |
| Begin Flask development               | Develop initial Flask app connected to existing backend/data source     | X     |

## Task 3: Research & Architecture Design

| Subtask                                      | Description                                                                                     | State |
| -------------------------------------------- | ----------------------------------------------------------------------------------------------- | ----- |
| Design multi-container architecture          | Define components (frontend, backend API, data collectors), responsibilities, and communication | X     |
| Research Docker, Compose, and GitHub Actions | Select technologies and methods for containerization, orchestration, and CI/CD                  | X     |
| Research Zero Trust Architecture (ZTA)       | Study ZTA principles and their application to the existing Azure infrastructure                 | X     |

## Week 2 – Containerization and Initial CI/CD Setup

## Task 4: Secure Authentication (Entra ID)

|Subtask|Description|State|
|---|---|---|
|Analyze and design Entra ID + OAuth2/OIDC flow|Design the authentication flow for the Flask application|🔲 To Do|
|Implement Entra ID authentication in Flask|Integrate Entra ID; register the application in Azure Entra ID|🔲 To Do|

## Task 5: Application Containerization (Docker & Compose)

|Subtask|Description|State|
|---|---|---|
|Analyze and design container breakdown|Divide the app into logical components; define responsibilities and networking|✅ Done|
|Write Dockerfiles for each component|Create Dockerfiles for frontend, API, and data collector containers|✅ Done|
|Create docker-compose.yml (local)|Define services, networks, volumes, and environment variables|✅ Done|
|Implement persistent storage with volumes|Configure volumes for monitoring data and application configuration|✅ Done|

## Task 6: CI/CD Pipeline – GitHub Actions (Setup)

|Subtask|Description|State|
|---|---|---|
|Design CI/CD pipeline|Define triggers, build steps, push to registry, and deployment strategy|✅ Done|
|Implement initial GitHub Actions workflow|Set up build and image push pipeline|✅ Done|

## Task 7: DNS Security Analysis

|Subtask|Description|State|
|---|---|---|
|Analyze current DNS security posture|Research DoH, DoT, and DNSSEC; select suitable mechanism(s) for The Knowledge Hub|🔲 To Do|

## Week 3 – Deployment, Security & Advanced Monitoring

## Task 8: CI/CD Pipeline – Deployment Extension

|Subtask|Description|State|
|---|---|---|
|Extend pipeline with automated deployment|Add deployment steps to Azure Container Apps in the GitHub Actions workflow|🔲 To Do|

## Task 9: Container Platform Monitoring

|Subtask|Description|State|
|---|---|---|
|Research container monitoring methods|Investigate Docker API, docker stats, cAdvisor, and similar tools|🔲 To Do|
|Develop Python scripts for metric collection|Create/extend scripts to capture metrics from the Docker environment|🔲 To Do|
|Integrate container metrics into Flask dashboard|Display collected container data on the web frontend|🔲 To Do|

## Task 10: Cloud Security Hardening (ZTA)

|Subtask|Description|State|
|---|---|---|
|Review current Azure infrastructure|Analyze VNets, NSGs, IAM/RBAC, VM access, and data storage|🔲 To Do|
|Design ZTA improvements|Propose refined NSG rules, strict RBAC, MFA, Private Link, and Conditional Access|🔲 To Do|
|Implement ZTA enhancements|Apply selected changes to Azure and document rationale|🔲 To Do|

## Task 11: Network Enhancements (IPv6 & DNS Security)

|Subtask|Description|State|
|---|---|---|
|Configure IPv6 on VM / network interface|Assign IPv6 address and test basic connectivity in the lab|🔲 To Do|
|Implement DNS security mechanisms|Configure DoH/DoT/DNSSEC on a client or local resolver; document security benefits|🔲 To Do|

## Task 12: Service Management & Resilience

|Subtask|Description|State|
|---|---|---|
|Document incident, problem, and change management|Apply ITIL concepts to the containerized environment and CI/CD pipeline|🔲 To Do|
|Define backup and restore strategy|Document what to back up (volumes, configs, images) and how to restore service|🔲 To Do|

## Week 4 – Finalization, Testing, Documentation & Reflection

## Task 13: Final Integration & Testing

|Subtask|Description|State|
|---|---|---|
|Final integration of all components|Ensure frontend, backend, collectors, authentication, and CI/CD work end-to-end|🔲 To Do|
|Thorough system testing|Test web frontend, containers, CI/CD pipeline, Entra ID auth, and security enhancements|🔲 To Do|

## Task 14: Documentation Set

|Subtask|Description|State|
|---|---|---|
|System architecture document|Overall diagram, container design, and data flow documentation|🔲 To Do|
|Deployment and configuration guide|Dockerfiles, docker-compose.yml, GitHub Actions workflow, on-premise setup instructions|🔲 To Do|
|Security report|ZTA measures applied, Entra ID integration details, DNS security implementation|🔲 To Do|
|Service management & resilience document|Incident/Problem/Change Management considerations + backup/restore strategy|🔲 To Do|
|User guide|How to access and use the monitoring web dashboard|🔲 To Do|

## Task 15: Presentation & Reflection

|Subtask|Description|State|
|---|---|---|
|Prepare presentation and live demo|Build a short presentation with a working demo of the full solution|🔲 To Do|
|Individual and team reflection|Document challenges, lessons learned, planning adherence, and individual contributions|🔲 To Do|

---

# Flavor

## Flavor A – Tech Driven: The Future Secure Network

## Week 1

**Task A.1 – Advanced IPv6 on pfSense (Analysis & Design)**  
Research SLAAC vs. DHCPv6 for corporate networks. Analyze IPv6 firewall rule principles (including mandatory ICMPv6 allowances). Create a detailed IPv6 addressing plan for The Knowledge Hub's internal networks and design the required pfSense firewall rules.

**Task A.2 – Automation & Security Hardening (Analysis)**  
Investigate the pfSense REST API (`jaredhendrickson13/pfsense-api`): installation, authentication, and basic configuration tasks via external scripts. Research which pfSense packages satisfy REQ-SEC-01, REQ-SEC-02, and REQ-SEC-03 (candidates: pfBlockerNG, Suricata, HAProxy) and justify the selection.

## Week 2

**Task A.2 – Automation & Security Hardening (Design)**  
Design a Python script that uses the REST API to automate a meaningful task (e.g., create an IP alias and a corresponding block rule). Create a configuration design for the chosen security packages: blocklist selection for pfBlockerNG, ruleset activation for Suricata, and reverse proxy setup for HAProxy.

## Week 3

**Task A.1 – IPv6 on pfSense (Realization)**  
Implement the designed IPv6 configuration on a pfSense VM: configure the LAN interface, set up DHCPv6 or Router Advertisements (SLAAC), and apply the designed firewall rules. Test connectivity from a client VM on the LAN.

**Task A.2 – Automation & Security (Realization)**  
Install the REST API package on pfSense and execute the designed Python script. Demonstrate that pfSense configuration is automatically updated. Install and configure pfBlockerNG, Suricata, and HAProxy according to the Week 2 design.

## Week 4

**Task A – Evidence & Documentation**  
Test and provide evidence for all three security requirements (blocked malicious IP logs, IDS alerts, secure access via reverse proxy). Complete all Flavor A deliverables: IPv6 implementation plan, automation and security report, Python script code, screenshots/video evidence, and an updated network architecture diagram.

---

# Planning

## Week 1

|Task / Subtask|Description|State|
|---|---|---|
|**Task 1** – Analyze all functional requirements|Review all core REQs and Flavor A requirements|🔲 To Do|
|**Task 1** – Develop project plan|Create plan with tasks, deliverables, estimated effort, and dependencies|🔲 To Do|
|**Task 1** – Ongoing plan review|Monitor progress, identify blockers, and document key decisions|🔲 To Do|
|**Task 2** – Analyze web interface functionalities|Determine what information and features the web interface should expose|🔲 To Do|
|**Task 2** – Design wireframes and Flask routes|Create mockups, design routes, templates, and static asset structure|🔲 To Do|
|**Task 2** – Begin Flask development|Develop initial Flask app connected to existing backend/data source|🔲 To Do|
|**Task 3** – Design multi-container architecture|Define components (frontend, backend API, data collectors), responsibilities, and communication|🔲 To Do|
|**Task 3** – Research Docker, Compose, and GitHub Actions|Select technologies and methods for containerization, orchestration, and CI/CD|🔲 To Do|
|**Task 3** – Research Zero Trust Architecture (ZTA)|Study ZTA principles and their application to the existing Azure infrastructure|🔲 To Do|

## Week 2

|Task / Subtask|Description|State|
|---|---|---|
|**Task 4** – Analyze and design Entra ID + OAuth2/OIDC flow|Design the authentication flow for the Flask application|🔲 To Do|
|**Task 4** – Implement Entra ID authentication in Flask|Integrate Entra ID; register the application in Azure Entra ID|🔲 To Do|
|**Task 5** – Analyze and design container breakdown|Divide the app into logical components; define responsibilities and networking|✅ Done|
|**Task 5** – Write Dockerfiles for each component|Create Dockerfiles for frontend, API, and data collector containers|✅ Done|
|**Task 5** – Create docker-compose.yml (local)|Define services, networks, volumes, and environment variables|✅ Done|
|**Task 5** – Implement persistent storage with volumes|Configure volumes for monitoring data and application configuration|✅ Done|
|**Task 6** – Design CI/CD pipeline|Define triggers, build steps, push to registry, and deployment strategy|✅ Done|
|**Task 6** – Implement initial GitHub Actions workflow|Set up build and image push pipeline|✅ Done|
|**Task 7** – Analyze current DNS security posture|Research DoH, DoT, and DNSSEC; select suitable mechanism(s) for The Knowledge Hub|🔲 To Do|

## Week 3

|Task / Subtask|Description|State|
|---|---|---|
|**Task 8** – Extend pipeline with automated deployment|Add deployment steps to Azure Container Apps in the GitHub Actions workflow|🔲 To Do|
|**Task 9** – Research container monitoring methods|Investigate Docker API, docker stats, cAdvisor, and similar tools|🔲 To Do|
|**Task 9** – Develop Python scripts for metric collection|Create/extend scripts to capture metrics from the Docker environment|🔲 To Do|
|**Task 9** – Integrate container metrics into Flask dashboard|Display collected container data on the web frontend|🔲 To Do|
|**Task 10** – Review current Azure infrastructure|Analyze VNets, NSGs, IAM/RBAC, VM access, and data storage|🔲 To Do|
|**Task 10** – Design ZTA improvements|Propose refined NSG rules, strict RBAC, MFA, Private Link, and Conditional Access|🔲 To Do|
|**Task 10** – Implement ZTA enhancements|Apply selected changes to Azure and document rationale|🔲 To Do|
|**Task 11** – Configure IPv6 on VM / network interface|Assign IPv6 address and test basic connectivity in the lab|🔲 To Do|
|**Task 11** – Implement DNS security mechanisms|Configure DoH/DoT/DNSSEC on a client or local resolver; document security benefits|🔲 To Do|
|**Task 12** – Document incident, problem, and change management|Apply ITIL concepts to the containerized environment and CI/CD pipeline|🔲 To Do|
|**Task 12** – Define backup and restore strategy|Document what to back up (volumes, configs, images) and how to restore service|🔲 To Do|

## Week 4

|Task / Subtask|Description|State|
|---|---|---|
|**Task 13** – Final integration of all components|Ensure frontend, backend, collectors, authentication, and CI/CD work end-to-end|🔲 To Do|
|**Task 13** – Thorough system testing|Test web frontend, containers, CI/CD pipeline, Entra ID auth, and security enhancements|🔲 To Do|
|**Task 14** – System architecture document|Overall diagram, container design, and data flow documentation|🔲 To Do|
|**Task 14** – Deployment and configuration guide|Dockerfiles, docker-compose.yml, GitHub Actions workflow, on-premise setup instructions|🔲 To Do|
|**Task 14** – Security report|ZTA measures applied, Entra ID integration details, DNS security implementation|🔲 To Do|
|**Task 14** – Service management & resilience document|Incident/Problem/Change Management considerations + backup/restore strategy|🔲 To Do|
|**Task 14** – User guide|How to access and use the monitoring web dashboard|🔲 To Do|
|**Task 15** – Prepare presentation and live demo|Build a short presentation with a working demo of the full solution|🔲 To Do|
|**Task 15** – Individual and team reflection|Document challenges, lessons learned, planning adherence, and individual contributions|🔲 To Do|