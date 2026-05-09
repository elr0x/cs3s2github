# Microsoft Intune Design Strategy
**Case Study: Knowledge Hub | Task: Intune Management**

This document details the enrollment strategy and mobile device management (MDM/MAM) capabilities using Microsoft Intune to ensure corporate and security policies are applied across the *Knowledge Hub* device fleet.

---

## 1. Enrollment Strategy

The goal is to facilitate the onboarding process for both corporate-owned and employee/student-owned (BYOD) devices while maintaining strict data security.

### A. Corporate-Owned Devices
*   **Method:** Windows Autopilot (User-driven mode).
*   **Purpose:** When an employee or student receives a new laptop, they simply power it on, connect to Wi-Fi, and sign in with their Microsoft Entra ID credentials from *Knowledge Hub*.
*   **Benefit:** Intune automatically provisions the device in the background (installs VPN, certificates, Office applications, and applies policies) without the IT team having to configure each device manually (Zero-Touch IT).

### B. Personal Devices (BYOD - Bring Your Own Device)
*   **Method:** User-driven enrollment with *Mobile Application Management (MAM)* via App Protection Policies (APP) and Windows Information Protection (WIP).
*   **Purpose:** For staff or students using their own mobile devices or laptops.
*   **Benefit:** Instead of taking full control of the user's personal device via Mobile Device Management (MDM), Microsoft Intune will only manage and protect the *corporate applications* (e.g., Outlook, Teams, OneDrive), keeping personal data and company data strictly separated.

---

## 2. Configuration Profiles

Configuration profiles allow us to automatically deploy settings and features to enrolled devices without user intervention.

### Profile 1: `Win11-Endpoint-Security-Baseline`
*   **Platform:** Windows 10 and later
*   **Profile Type:** Template (Security Baseline)
*   **Objective:** Apply Microsoft's recommended security standards across the fleet.
*   **Key Settings:**
    *   **BitLocker:** Require full disk encryption for OS and data drives. Recovery keys are automatically escrowed to Entra ID.
    *   **Microsoft Defender Antivirus:** Enable real-time protection, block Potentially Unwanted Apps (PUA), and enable cloud-delivered protection.
    *   **Windows Defender Firewall:** Block unsolicited incoming traffic from public networks.
    *   **SmartScreen:** Turned on and forced to block malicious downloads.

### Profile 2: `Win11-Network-and-Browser-Restrictions`
*   **Platform:** Windows 10 and later
*   **Profile Type:** Settings Catalog
*   **Objective:** Facilitate connection to internal resources and standardize the web browsing experience.
*   **Key Settings:**
    *   **Wi-Fi:** Pre-configure the corporate Wi-Fi profile (`KnowledgeHub-Secure`) using WPA2-Enterprise/Certificate authentication, so devices connect automatically while on campus.
    *   **Microsoft Edge:**
        *   Set the startup page to the *Knowledge Hub* intranet.
        *   Block the use of InPrivate/Incognito mode (if required for compliance).
        *   Add the *Knowledge Hub* domain to the allowed trusted sites list.

---

## 3. Compliance Policy

Before a device can access company data (email, SharePoint, internal APIs), it must prove that it is "secure" and "compliant" by using Conditional Access policies.

### Policy: `Policy-Win-Corporate-Compliance`
*   **Platform:** Windows 10 and later
*   **Assignment:** All corporate users.
*   **Compliance Rules:**
    1.  **Device Health:** Require *Secure Boot* to be enabled (protects against rootkits).
    2.  **Device Properties:** Minimum allowed OS version: `10.0.19045` (Windows 10 22H2). Outdated and unpatched devices will be blocked.
    3.  **System Security:**
        *   Password required to unlock the device (minimum 8 alphanumeric characters).
        *   Data storage encryption (`BitLocker`) must be reported as 'Active'.
        *   Windows Firewall must be turned on.
        *   Antivirus must be turned on and up to date.
    4.  **Device Risk (Defender for Endpoint):** The maximum acceptable device threat level is *Low* or *Clear*.

*   **Action for non-compliance:**
    *   *Immediately:* Mark the device as "Non-compliant" (which will instantly cut off access to Office 365 due to Conditional Access).
    *   *After 3 days:* Send a warning email to the user with instructions on how to remediate the issue (e.g., "Please enable your Antivirus").
