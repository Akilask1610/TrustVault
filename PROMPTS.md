# TrustVault — AI Usage Log

## Entry 1 — 2026-10-23

- **Task:** Set up the Python environment for TrustVault.
- **Prompt:** Help me set up a Flask development environment in VS Code on Windows.
- **AI output:** Commands to create a virtual environment and install Flask-related packages.
- **What I checked:** Verified installed packages using `python -m pip list`.
- **What was wrong:** No installation errors observed in the package list. Application functionality has not been tested yet.
- **What I did instead:** Confirmed the installed packages before proceeding.
- **Commit link:** To be added after committing this work.



## Entry 2 — 2026-10-23

- **Task:** Create the initial TrustVault landing page.
- **Prompt:** Help me create a Flask application with a landing page for a secure document-sharing platform.
- **AI output:** A basic Flask route that renders the TrustVault welcome page.
- **What I checked:** Ran the application locally and confirmed the page displayed the TrustVault title, description, and development status.
- **What was wrong:** No visible errors during this initial test. Authentication, authorisation, document sharing, and audit logging are not implemented yet.
- **What I did instead:** Verified the basic page before starting the next feature.
- **Commit link:** Add the actual commit URL after pushing this commit to GitHub.




## Entry 3 — 2026-10-23

- **Task:** Configure Flask-Login user loading.
- **Prompt:** Help diagnose the Missing user_loader or request_loader exception.
- **AI output:** Add a user_loader callback and make the User model inherit from UserMixin.
- **What was wrong:** Flask-Login was initialized without a callback to retrieve a user from the stored user ID.
- **What I changed:** Added a user_loader function that retrieves the user from the database and handles invalid user IDs. Added UserMixin to the User model.
- **Test:** Reopen the local landing page and verify that the exception no longer occurs.
- **Commit link:** Add the actual GitHub commit URL after pushing, if available.


## Entry 4 — 2026-10-23

- **Task:** Implement registration, login, dashboard, and logout.
- **Prompt:** Build a clean Flask authentication flow for TrustVault.
- **AI output:** Registration and login routes, password hashing,
  protected dashboard, logout, and CSRF protection.
- **What went wrong:** Earlier code edits caused a missing import
  and duplicate SQLAlchemy initialization.
- **What I changed:** Replaced app.py with one consistent application
  structure and initialized SQLAlchemy only once.
- **Testing:** Record actual registration, login, and logout results.
- **Commit link:** Add the real GitHub commit URL after pushing.