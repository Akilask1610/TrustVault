
# 🔐 TrustVault — Secure Document Sharing

## 📌 Overview

TrustVault is a Flask-based secure document management and sharing application designed to help organizations manage documents with controlled access.

The application combines user authentication, company-level access restrictions, role-based permissions, SHA-256 file integrity verification, and audit logging to improve document security and accountability.

This project demonstrates concepts used in:
- Enterprise document management
- Secure file-sharing systems
- Authentication and authorization
- Role-based access control (RBAC)
- File integrity verification
- Security auditing and activity monitoring
- PostgreSQL database integration
- Cloud application deployment

## 🚀 Live Demo & Source Code

- 🌐 **Live Demo:** https://trustvault-f7uw.onrender.com/
- 💻 **GitHub Repository:** https://github.com/Akilask1610/TrustVault

The live application allows users to explore the TrustVault web interface and its document management functionality.

> Note: The live application may take a short time to start after inactivity because of the hosting platform's free-tier behavior.

## 🎯 Features

- User registration and login
- Password hashing for secure credential storage
- Company-level document access restrictions
- Document upload and download
- Controlled sharing with registered users
- Role-based permissions for administrators and regular users
- SHA-256 file integrity verification
- Audit logging for important document activities
- Login rate limiting to reduce repeated login attempts
- Access restrictions for unauthorized users
- PostgreSQL database integration
- Flask-based web interface
- Automated tests for selected security and application behavior
- Cloud deployment using Render

## 🔄 System Workflow

### 1. User Authentication

- Users register and log in to access protected functionality.
- Passwords are stored as password hashes rather than plain text.
- Login rate limiting helps reduce repeated login attempts.

### 2. Document Upload

- An authenticated user uploads a document.
- The application stores document information and calculates its SHA-256 hash.
- The document's metadata and associated ownership information are maintained by the application.

### 3. Access Control

- The application checks authorization before allowing protected document operations.
- Access decisions can depend on document ownership, sharing permissions, company membership, and user role.
- Knowing a document URL alone should not grant unauthorized access.

### 4. Document Sharing

- An authorized document owner can share a document with an eligible registered user.
- The recipient's access depends on the application's sharing and authorization rules.
- Unauthorized users should not be able to access documents that have not been shared with them.

### 5. File Integrity Verification

- The application uses SHA-256 hashing to identify file content.
- A stored hash can be compared with a newly calculated hash to detect unexpected file changes.
- Integrity verification helps identify potential file modification.

### 6. Audit Logging

- Important activities can be recorded in the audit trail.
- Audit records support monitoring and reviewing document-related activity.
- Authorized administrators can inspect audit information according to the application's permissions.

## 🛡️ Security Features

| Security Feature | Purpose |
|---|---|
| Authentication | Restricts protected functionality to authenticated users |
| Password hashing | Avoids storing passwords as plain text |
| Company-level isolation | Helps restrict access between organizational groups |
| Ownership checks | Controls document-owner operations |
| Sharing permissions | Defines which eligible users may access shared documents |
| Role-based access control | Separates administrator and regular-user permissions |
| SHA-256 hashing | Helps detect unexpected changes to file content |
| Audit logging | Records important application activities |
| Login rate limiting | Helps reduce repeated login attempts |
| Automated tests | Checks selected application and security behavior |

**Security note:** TrustVault is an educational project and has not undergone a professional security audit. It should not be used for confidential documents or sensitive production workloads without further testing and security hardening.

## 🛠️ Technologies Used

- **Python 3** — Backend programming
- **Flask** — Web application framework
- **Flask-Login** — User session management
- **Flask-SQLAlchemy / SQLAlchemy** — Database integration
- **PostgreSQL** — Relational database for deployment
- **HTML and CSS** — Web interface
- **SHA-256** — File integrity verification
- **Git and GitHub** — Version control and source-code hosting
- **Render** — Cloud deployment
- **Pytest** — Automated testing

## 📂 Project Structure

The project includes the following key files and directories:

- `app.py` — Flask application and application routes
- `requirements.txt` — Python dependencies
- `Procfile` — Application startup configuration
- `render.yaml` — Render deployment configuration, if included
- `README.md` — Project documentation
- `PROMPTS.md` — Project prompt documentation
- `THREATS.md` — Threat analysis and security considerations
- `tests/` — Automated test files
- `templates/` — HTML templates
- `static/` — Static assets, if included
- `.venv/` — Local Python virtual environment; should not be committed

The exact repository structure may vary as the project evolves.

## ▶️ How to Run Locally

### Prerequisites

- Python 3
- Git
- A terminal such as PowerShell or Command Prompt
- PostgreSQL, if using a local PostgreSQL database

### Step 1: Clone the Repository

    git clone https://github.com/Akilask1610/TrustVault.git
    cd TrustVault

### Step 2: Create a Virtual Environment

**Windows PowerShell:**

    python -m venv .venv
    .venv\Scripts\Activate.ps1

**Linux or macOS:**

    python3 -m venv .venv
    source .venv/bin/activate

### Step 3: Install Dependencies

    python -m pip install -r requirements.txt

### Step 4: Configure Environment Variables

Configure the environment variables required by the application before starting it.

Typical settings may include:

- `SECRET_KEY` — A strong, unique secret key
- `DATABASE_URL` — The database connection URL
- `RATELIMIT_STORAGE_URI` — The rate-limit storage backend, if configured
- `BOOTSTRAP_ADMIN_USERNAME` — Optional initial administrator username, if supported
- `BOOTSTRAP_ADMIN_PASSWORD` — Optional initial administrator password, if supported

Use the exact variable names and setup requirements defined in `app.py` and the deployment configuration.

Never commit passwords, secret keys, database credentials, or `.env` files to GitHub.

### Step 5: Start the Application

    python app.py

If the application uses a configured PostgreSQL database, make sure the database is available and the connection settings are correct before starting the application.

### Step 6: Open the Application

Visit the following address in your browser:

http://127.0.0.1:5000/

### Step 7: Run the Tests

Install the project dependencies, then run:

    python -m pytest -q

The tests check selected application and security behavior. A passing test suite does not guarantee that every possible vulnerability has been eliminated.

## 📋 Example Workflow

1. Open the TrustVault application.
2. Register an account or sign in with an authorized account.
3. Upload a sample document.
4. Review the document information and displayed integrity hash.
5. Share the document with an eligible registered user, if sharing functionality is available to that account.
6. Sign in as the intended recipient and verify the permitted access.
7. Attempt an unauthorized access only in a controlled test environment to verify access restrictions.
8. Download the document and check the application's integrity-verification behavior.
9. Review the relevant audit records through the authorized administrator interface.

Use only test accounts and non-sensitive sample documents when demonstrating the project.

## 💾 Database and File Storage

TrustVault uses SQLAlchemy to interact with its configured relational database. The deployed application is configured to use PostgreSQL through the `DATABASE_URL` environment variable.

The application also requires a suitable location or storage mechanism for uploaded files. Database records and uploaded file contents are separate concerns and should be managed accordingly.

### Deployment Considerations

- Confirm that the PostgreSQL database is persistent and available to the web service.
- Confirm that uploaded files are stored in persistent storage if they must survive redeployments or restarts.
- Do not assume that files stored on a temporary application filesystem will remain available permanently.
- Back up important data when appropriate.
- Never store real confidential documents in a demonstration environment without suitable safeguards.

## 🧪 Testing

The project includes automated tests for selected areas, including:

- Login rate limiting
- Failed-login audit behavior
- Application security checks
- Upload security checks

Run the complete test suite with:

    python -m pytest -q

Tests should be updated whenever application behavior or security requirements change.

## 🚧 Future Enhancements

- Expand automated authorization and access-control tests
- Add additional CSRF protection where required
- Improve persistent file storage integration
- Add more detailed audit-log filtering and search
- Improve user-facing validation and error messages
- Add stronger monitoring and operational logging
- Improve deployment configuration and database migration management
- Conduct a professional security review before production use
- Add backup and recovery procedures
- Improve accessibility and responsive user-interface design

## 👩‍💻 Author

Developed as a Python and Flask project to explore secure document management, controlled sharing, access control, file integrity verification, and audit logging.

**GitHub:** https://github.com/Akilask1610

## 🏁 Conclusion

TrustVault demonstrates how a Flask web application can combine authentication, access-control checks, document management, SHA-256 file integrity verification, and audit logging in a single project.

The project provides a foundation for learning secure application development and can be extended with additional testing, persistent file storage, monitoring, and security hardening.

**Live Demo:** https://trustvault-f7uw.onrender.com/

**Source Code:** https://github.com/Akilask1610/TrustVault
