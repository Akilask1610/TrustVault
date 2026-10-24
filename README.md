# TrustVault — Secure Document Management System

## Overview

TrustVault is a Python-based secure document management web application built using Flask. It allows users to upload, manage, and share documents while enforcing access permissions and maintaining an audit trail of important security-related activities.

The project focuses on secure file handling, authentication, authorization, file integrity verification, and protection against unauthorized access.

## Features

- **User Authentication:** Secure login using password hashing.
- **Role-Based Access Control:** Restricts administrative pages to authorized administrators.
- **Secure File Uploads:** Validates uploaded filenames and permitted file types.
- **File Integrity Verification:** Uses SHA-256 hashes to verify document integrity.
- **Document Sharing:** Supports document sharing with download permissions.
- **Tenant-Based Access Control:** Prevents users from accessing documents belonging to another tenant.
- **Audit Logging:** Records important actions, including logins, uploads, sharing, and denied download attempts.
- **Login Rate Limiting:** Limits login requests to help protect against repeated login attempts.
- **Failed-Login Auditing:** Records failed login attempts for known users without storing submitted passwords.
- **Automated Testing:** Uses pytest to validate important security controls.

## Technology Stack

- **Programming Language:** Python
- **Web Framework:** Flask
- **Database Integration:** Flask-SQLAlchemy
- **Database:** SQLite by default
- **Authentication:** Flask-Login
- **Rate Limiting:** Flask-Limiter
- **Frontend:** HTML, Jinja2 templates
- **Testing:** Pytest
- **Version Control:** Git and GitHub

## Project Structure

    TrustVault/
    ├── app.py
    ├── requirements.txt
    ├── README.md
    ├── PROMPTS.md
    ├── templates/
    └── tests/
        ├── conftest.py
        ├── test_failed_login_audit.py
        ├── test_login_rate_limit.py
        ├── test_security.py
        └── test_upload_security.py

## Installation

### 1. Clone the Repository

    git clone https://github.com/Akilask1610/TrustVault.git
    cd TrustVault

### 2. Create a Virtual Environment

For Windows PowerShell:

    python -m venv .venv
    .\.venv\Scripts\Activate.ps1

### 3. Install Dependencies

    python -m pip install -r requirements.txt

### 4. Configure the Secret Key

Set a secure secret key in PowerShell before starting the application:

    $env:SECRET_KEY = "replace-with-a-secure-random-secret"

Use a securely generated secret key for actual deployments. Never commit real credentials or secret keys to the repository.

## How to Run

### 1. Activate the Virtual Environment

    .\.venv\Scripts\Activate.ps1

### 2. Install Dependencies

    python -m pip install -r requirements.txt

### 3. Start the Application

    python app.py

### 4. Open the Application

Open the local URL displayed in the terminal in your web browser.

The application uses SQLite by default unless a different database connection is configured through the `DATABASE_URL` environment variable.

## Running the Tests

Run the automated test suite from the project directory:

    python -m pytest -v

The current test suite contains nine tests covering the following areas:

- Administrative access control
- Rejection of disallowed file types
- Rejection of empty filenames
- Document upload and audit logging
- SHA-256 file integrity verification
- Cross-tenant download protection
- Login rate limiting
- Failed-login audit logging

**Latest recorded test result:** 9 tests passed.

## Security Considerations

TrustVault includes several security measures:

- Password hashing for stored user credentials.
- Server-side authorization checks for protected resources.
- File upload validation.
- SHA-256 document integrity checks.
- Tenant-based document access restrictions.
- Audit records for selected security-related events.
- Login rate limiting.
- Failed-login logging without storing submitted passwords.

Before deploying to production, configure HTTPS, a strong secret key, appropriate database access controls, secure file storage, and production-ready rate-limit storage. Review error handling, session security, and backup procedures as well.

## Development Documentation

The `PROMPTS.md` file contains the project's development notes, implementation history, and test-validation records.

## Future Enhancements

Potential future improvements include:

- Password reset functionality.
- Multi-factor authentication.
- More advanced document search and filtering.
- Additional audit-log reporting.
- Automated deployment and continuous integration.
- Production deployment with persistent rate-limit storage.
- Expanded automated tests for sharing permissions and other edge cases.

## Conclusion

TrustVault demonstrates the implementation of a secure document management application using Python and Flask. It combines authentication, access control, file integrity verification, document permissions, audit logging, and automated security testing in a single project.

The project provides a practical foundation for demonstrating web application development and security-focused programming skills.

## Author

**Akila Shaik**

GitHub: https://github.com/Akilask1610

## Repository

https://github.com/Akilask1610/TrustVault