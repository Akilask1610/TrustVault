# TrustVault â€” AI Usage Log

## Entry 1 - 2026-10-23

- **Task:** Set up the TrustVault development environment.
- **Prompt:** Help me set up a Python environment for the TrustVault project using Flask.
- **AI output:** Guidance for creating a project folder, setting up a virtual environment, and installing the required Python packages.
- **What was wrong:** The initial setup required checking that the environment and dependencies were correctly configured on my Windows system.
- **What I did instead:** Created the project folder, configured the virtual environment, and installed the required dependencies.
- **Result:** The development environment was ready for application development.
- **Commit link:** https://github.com/Akilask1610/TrustVault/commit/92492d0fb6245f7b264d6413694a952bb22fbb26

## Entry 2 - 2026-10-23

- **Task:** Create the initial application landing page.
- **Prompt:** Help me create a simple landing page for TrustVault using Flask templates.
- **AI output:** Guidance for creating the Flask route and HTML template.
- **What was wrong:** The page needed to be connected to the Flask application and use the correct template structure.
- **What I did instead:** Created the landing page and tested it in the browser.
- **Result:** The TrustVault landing page opened successfully on the local development server.
- **Commit link:** https://github.com/Akilask1610/TrustVault/commit/57d86f9a43214cd92f388ca37dec1421066ef3e2

## Entry 3 - 2026-10-23

- **Task:** Configure Flask-Login user authentication.
- **Prompt:** Help me configure the Flask-Login user loader for TrustVault.
- **AI output:** Guidance for loading authenticated users from the database.
- **What was wrong:** The application needed a working user loader to manage authenticated sessions correctly.
- **What I did instead:** Updated the user loader and tested the authentication flow.
- **Result:** The Flask-Login user loader was configured.
- **Commit link:** https://github.com/Akilask1610/TrustVault/commit/2ac16b1fd2dc944cb15af55d3d4c131a547c69d8

## Entry 4 - 2026-10-23

- **Task:** Implement user registration and login.
- **Prompt:** Help me implement registration, login, logout, and a dashboard in TrustVault.
- **AI output:** Guidance for implementing authentication routes, password hashing, and HTML templates.
- **What was wrong:** The authentication pages and routes needed to work together with the database and session management.
- **What I did instead:** Implemented the registration and login flow and tested the application locally.
- **Result:** Registration, login, dashboard, and logout functionality were added.
- **Commit link:** https://github.com/Akilask1610/TrustVault/commit/856e27570dbd05fdacf60d9359659e28d5a183ee

## Entry 5 - 2026-10-23

- **Task:** Test document-sharing authorization and download permissions.
- **Prompt:** Help me verify that view-only sharing prevents unauthorized document downloads.
- **AI output:** Guidance to test the recipient account and verify that the server rejects download requests without permission.
- **What was wrong:** Hiding the download link alone would not prove that server-side authorization was enforced.
- **What I did instead:** Tested the direct download URL using the friend123 account.
- **Test result:** The server returned HTTP 403 Forbidden for the unauthorized download attempt.
- **Commit link:** https://github.com/Akilask1610/TrustVault/commit/08a5ee3288d24b4b5b655c438dfb84a0b77b367d

## Entry 6 - 2026-10-23

- **Task:** Record denied document-download attempts in the audit trail.
- **Prompt:** Help me add audit logging for download attempts rejected by the authorization check.
- **AI output:** Guidance to add a document_download_denied audit event before returning HTTP 403.
- **What was wrong:** The existing download route recorded successful downloads but did not record denied download attempts.
- **What I changed:** Added an audit event for unauthorized download attempts before returning the forbidden response.
- **Test result:** Tested the view-only document download again. The server returned HTTP 403, and the Admin Dashboard showed the document_download_denied event for Akila_Resume.pdf.
- **Commit link:** https://github.com/Akilask1610/TrustVault/commit/63e26d07c40b304dee393f3f1cb29c377a97da41

## Entry 7 - 2026-10-24

- **Task:** Add security tests for admin access, document uploads, file integrity, audit logging, and cross-tenant download protection.
- **Prompt:** Help me write pytest tests to verify that normal users cannot access admin pages, invalid uploads are rejected, valid uploads are recorded in the audit log, SHA-256 hashes match uploaded file contents, and users cannot download documents belonging to another tenant.
- **AI output:** Created tests for admin authorization, upload validation, audit logging, SHA-256 integrity, and cross-tenant download protection.
- **What was wrong:** The original test fixture changed the database URI after the Flask-SQLAlchemy extension had already initialized, so database isolation was not guaranteed.
- **What I changed:** Updated app.py to support a configurable DATABASE_URL, isolated the test database and upload storage using tests/conftest.py, and added security tests.
- **Test result:** All 7 tests passed in the original project using pytest: 2 admin-access tests and 5 upload-security tests.
- **Commit link:** https://github.com/Akilask1610/TrustVault/commit/341d13e2a701966aa5322da3d30165cb32c18ad9

## Entry 8 — Login Rate Limiting

- Added Flask-Limiter to protect the login endpoint against repeated
  failed login attempts.
- Configured a limit of 5 requests per minute for `/login`.
- Added a test verifying that the sixth login attempt receives HTTP 429.
- Isolated rate-limit state during tests so security tests do not
  interfere with each other.
- Updated `requirements.txt` with Flask-Limiter.
- Validation: `python -m pytest -v` — 8 tests passed.
