# TrustVault Threat Model

## 1. Project Overview

TrustVault is a Flask-based document management and sharing application. It supports user authentication, role-based access, document uploads, sharing, and audit logging.

## 2. Assets to Protect

- User credentials and password hashes
- Uploaded documents and their contents
- User accounts and role assignments
- Tenant and document ownership information
- Document-sharing permissions
- Audit logs and security events
- Session cookies and application secrets

## 3. Threats, Impact, and Mitigations

### Threat 1: Unauthorized Account Access

**Threat:** An attacker guesses or obtains a user's password.

**Impact:** The attacker may access documents and account functionality available to that user.

**Mitigations:** Password hashing, authenticated sessions, generic login error messages, and login rate limiting.

**Verification:** Automated login and rate-limit tests.

### Threat 2: Privilege Escalation

**Threat:** A normal user attempts to access administrator functionality.

**Impact:** Unauthorized access to user-management information or audit records.

**Mitigations:** The admin route checks the authenticated user's role and rejects non-admin users.

**Verification:** Automated admin-access tests.

### Threat 3: Unauthorized Document Access

**Threat:** A user changes a document ID or directly requests a download URL without permission.

**Impact:** Confidential documents could be exposed.

**Mitigations:** Server-side authorization checks must verify document ownership, tenant boundaries, and sharing permissions before serving files.

**Verification:** Upload-security and cross-tenant download tests.

### Threat 4: Malicious File Upload

**Threat:** An attacker uploads a disallowed or unexpectedly large file.

**Impact:** Storage abuse or potential exploitation of downstream software that processes the file.

**Mitigations:** File-extension validation, secure filename handling, and a 10 MB request-size limit.

**Limitations:** Extension checks alone do not prove that a file's contents are safe. Production deployments should consider content-type validation, malware scanning, and storage isolation.

### Threat 5: Document Tampering

**Threat:** A stored document is modified without authorization.

**Impact:** Users may receive altered or unreliable content.

**Mitigations:** SHA-256 hashes can help detect changes when the stored content is compared with a trusted original hash.

**Limitations:** A hash does not prevent tampering by itself. The reference hash must be protected from unauthorized modification.

### Threat 6: Abuse of Login Requests

**Threat:** An attacker repeatedly submits login requests.

**Impact:** Increased server load and attempts to guess credentials.

**Mitigations:** Flask-Limiter restricts login requests to five per minute per client IP using the configured limiter storage.

**Limitations:** In-memory rate-limit storage is not shared across multiple workers or service instances.

### Threat 7: Missing Security Audit Records

**Threat:** Suspicious login or document-access activity is not recorded.

**Impact:** Investigating security incidents becomes more difficult.

**Mitigations:** Audit events record selected login and document-access actions, including tested denied-download events.

**Limitations:** Audit logs require appropriate access controls, retention policies, and protection against unauthorized modification.

### Threat 8: Secret Exposure

**Threat:** Application secrets are committed to source control or use predictable default values.

**Impact:** Attackers may compromise sessions or other security controls.

**Mitigations:** Configure a strong SECRET_KEY through deployment environment variables and never commit its value.

**Deployment requirement:** The application must not run publicly with the development fallback secret.

### Threat 9: Data Loss During Deployment

**Threat:** The application stores its database and uploaded documents on an ephemeral filesystem.

**Impact:** Data may disappear after restarts or redeployments.

**Mitigations:** Use a suitable persistent database and durable file storage for production.

**Demo limitation:** A free hosting environment with ephemeral storage should be treated as a temporary demonstration, not reliable permanent document storage.

## 4. Residual Risks

- Extension-based upload validation is not equivalent to malware detection.
- Hash verification is only meaningful when the reference hash is trusted.
- In-memory rate limiting is not distributed rate limiting.
- Audit logging does not guarantee tamper-proof records.
- Persistent storage and secret configuration must be verified in the deployed environment.

## 5. Security Testing Plan

- Verify that valid users can log in and invalid credentials are rejected.
- Verify that repeated login requests are rate-limited.
- Verify that non-admin users cannot access admin-only routes.
- Verify that unauthorized and cross-tenant document downloads are rejected.
- Verify that invalid uploads are rejected.
- Verify that uploaded document hashes match the original contents.
- Verify that relevant security events appear in the audit log.
- Repeat the checks against the deployed application before submission.
