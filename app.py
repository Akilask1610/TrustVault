import os
import hashlib
import uuid
from pathlib import Path

from flask import (
    Flask,
    render_template_string,
    request,
    redirect,
    url_for,
    flash,
    send_from_directory,
    abort,
)
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    logout_user,
    login_required,
    current_user,
)
from flask_wtf.csrf import CSRFProtect
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename


# --------------------------------------------------
# 1. Application configuration
# --------------------------------------------------

app = Flask(__name__)

app.config["SECRET_KEY"] = os.environ.get(
    "SECRET_KEY", "dev-only-change-this-before-deployment"
)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///trustvault.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024

BASE_DIR = Path(app.root_path)
UPLOAD_FOLDER = BASE_DIR / "private_uploads"
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)

app.config["UPLOAD_FOLDER"] = str(UPLOAD_FOLDER)

ALLOWED_EXTENSIONS = {
    "pdf", "txt", "png", "jpg", "jpeg", "docx", "xlsx"
}

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

csrf = CSRFProtect(app)


# --------------------------------------------------
# 2. Database models
# --------------------------------------------------

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(
        db.String(80),
        unique=True,
        nullable=False,
    )

    password_hash = db.Column(
        db.String(255),
        nullable=False,
    )

    role = db.Column(
        db.String(20),
        nullable=False,
        default="user",
    )

    # Current demo version: all users belong to tenant 1.
    tenant_id = db.Column(
        db.Integer,
        nullable=False,
        default=1,
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Document(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    original_filename = db.Column(
        db.String(255),
        nullable=False,
    )

    stored_filename = db.Column(
        db.String(255),
        unique=True,
        nullable=False,
    )

    sha256_hash = db.Column(
        db.String(64),
        nullable=False,
    )

    owner_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False,
        index=True,
    )

    tenant_id = db.Column(
        db.Integer,
        nullable=False,
        index=True,
    )

    uploaded_at = db.Column(
        db.DateTime,
        nullable=False,
        default=db.func.current_timestamp(),
    )

    owner = db.relationship("User", backref="documents")


class DocumentShare(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    document_id = db.Column(
        db.Integer,
        db.ForeignKey("document.id"),
        nullable=False,
    )

    shared_with_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False,
    )

    shared_by_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False,
    )

    tenant_id = db.Column(db.Integer, nullable=False)

    can_download = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=db.func.current_timestamp(),
    )

    __table_args__ = (
        db.UniqueConstraint(
            "document_id",
            "shared_with_id",
            name="unique_document_share",
        ),
    )


class AuditLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    actor_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=True,
    )

    document_id = db.Column(
        db.Integer,
        db.ForeignKey("document.id"),
        nullable=True,
    )

    target_user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=True,
    )

    tenant_id = db.Column(db.Integer, nullable=False)

    action = db.Column(
        db.String(80),
        nullable=False,
    )

    details = db.Column(
        db.String(500),
        nullable=True,
    )

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=db.func.current_timestamp(),
    )


# --------------------------------------------------
# 3. Login manager and audit helper
# --------------------------------------------------

@login_manager.user_loader
def load_user(user_id):
    try:
        return db.session.get(User, int(user_id))
    except (ValueError, TypeError):
        return None


def record_audit(
    action,
    document_id=None,
    target_user_id=None,
    details=None,
):
    if not current_user.is_authenticated:
        return

    log = AuditLog(
        actor_id=current_user.id,
        document_id=document_id,
        target_user_id=target_user_id,
        tenant_id=current_user.tenant_id,
        action=action,
        details=details,
    )

    db.session.add(log)


# --------------------------------------------------
# 4. File utilities
# --------------------------------------------------

def file_sha256(file_path):
    digest = hashlib.sha256()

    with open(file_path, "rb") as file:
        for chunk in iter(lambda: file.read(8192), b""):
            digest.update(chunk)

    return digest.hexdigest()


def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower()
        in ALLOWED_EXTENSIONS
    )


# --------------------------------------------------
# 5. Common page styling
# --------------------------------------------------

PAGE_STYLE = """
<style>
    body {
        font-family: Arial, sans-serif;
        background: #101827;
        color: white;
        text-align: center;
        padding: 30px 15px;
    }

    .panel {
        max-width: 760px;
        margin: 25px auto;
        padding: 26px;
        background: #1e293b;
        border-radius: 12px;
    }

    input, button, select {
        width: 100%;
        padding: 11px;
        margin: 8px 0;
        box-sizing: border-box;
        border-radius: 6px;
    }

    input, select {
        border: 1px solid #64748b;
    }

    button {
        background: #38bdf8;
        border: none;
        font-weight: bold;
        cursor: pointer;
    }

    a {
        color: #7dd3fc;
    }

    .message {
        color: #fde68a;
    }

    .document-card {
        text-align: left;
        margin: 18px 0;
        padding: 16px;
        background: #263449;
        border-radius: 8px;
        overflow-wrap: anywhere;
    }

    code {
        overflow-wrap: anywhere;
    }

    .inline-form {
        max-width: 420px;
    }
</style>
"""


BASE_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>TrustVault</title>
    {{ style|safe }}
</head>
<body>
    <div class="panel">
        {{ content|safe }}
    </div>
</body>
</html>
"""


FLASH_TEMPLATE = """
{% with messages = get_flashed_messages() %}
    {% for message in messages %}
        <p class="message">{{ message }}</p>
    {% endfor %}
{% endwith %}
"""


def page(content, **context):
    template = BASE_TEMPLATE.replace(
        "{{ content|safe }}",
        content,
    )

    return render_template_string(
        template,
        style=PAGE_STYLE,
        **context,
    )


# --------------------------------------------------
# 6. Home page
# --------------------------------------------------

@app.route("/")
def home():
    content = """
    <h1>TrustVault</h1>

    <h3>Secure Document Sharing Platform</h3>

    <p>
        Manage documents with controlled access
        and an audit trail.
    </p>

    {% if current_user.is_authenticated %}
        <p>Welcome, {{ current_user.username }}!</p>

        <p>
            <a href="{{ url_for('dashboard') }}">
                Open Dashboard
            </a>
        </p>

        <form method="POST" action="{{ url_for('logout') }}">
            <input type="hidden"
                   name="csrf_token"
                   value="{{ csrf_token() }}">

            <button type="submit">Logout</button>
        </form>
    {% else %}
        <p>
            <a href="{{ url_for('register') }}">
                Create Account
            </a>
        </p>

        <p>
            <a href="{{ url_for('login') }}">
                Login
            </a>
        </p>
    {% endif %}
    """

    return page(content)


# --------------------------------------------------
# 7. User registration
# --------------------------------------------------

@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        username = request.form.get(
            "username", ""
        ).strip()

        password = request.form.get("password", "")

        confirm_password = request.form.get(
            "confirm_password", ""
        )

        if not username or not password:
            flash("Username and password are required.")

        elif len(username) > 80:
            flash("Username must be 80 characters or fewer.")

        elif len(password) < 8:
            flash("Password must contain at least 8 characters.")

        elif password != confirm_password:
            flash("Passwords do not match.")

        elif User.query.filter_by(
            username=username
        ).first():
            flash("Username already exists.")

        else:
            user = User(
                username=username,
                role="user",
                tenant_id=1,
            )

            user.set_password(password)

            db.session.add(user)
            db.session.commit()

            flash("Registration successful. Please log in.")

            return redirect(url_for("login"))

    content = """
    <h1>Create Account</h1>

    """ + FLASH_TEMPLATE + """

    <form method="POST">
        <input type="hidden"
               name="csrf_token"
               value="{{ csrf_token() }}">

        <input type="text"
               name="username"
               placeholder="Username"
               maxlength="80"
               required>

        <input type="password"
               name="password"
               placeholder="Password (minimum 8 characters)"
               minlength="8"
               required>

        <input type="password"
               name="confirm_password"
               placeholder="Confirm password"
               required>

        <button type="submit">Register</button>
    </form>

    <p>
        Already registered?
        <a href="{{ url_for('login') }}">Login</a>
    </p>

    <p>
        <a href="{{ url_for('home') }}">Home</a>
    </p>
    """

    return page(content)


# --------------------------------------------------
# 8. User login
# --------------------------------------------------

@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        username = request.form.get(
            "username", ""
        ).strip()

        password = request.form.get("password", "")

        user = User.query.filter_by(
            username=username
        ).first()

        if user and user.check_password(password):
            login_user(user)

            record_audit(
                "login",
                details="User logged in",
            )

            db.session.commit()

            return redirect(url_for("dashboard"))

        flash("Invalid username or password.")

    content = """
    <h1>Login</h1>

    """ + FLASH_TEMPLATE + """

    <form method="POST">
        <input type="hidden"
               name="csrf_token"
               value="{{ csrf_token() }}">

        <input type="text"
               name="username"
               placeholder="Username"
               required>

        <input type="password"
               name="password"
               placeholder="Password"
               required>

        <button type="submit">Login</button>
    </form>

    <p>
        New user?
        <a href="{{ url_for('register') }}">
            Create account
        </a>
    </p>

    <p>
        <a href="{{ url_for('home') }}">Home</a>
    </p>
    """

    return page(content)


# --------------------------------------------------
# 9. User dashboard
# --------------------------------------------------

@app.route("/dashboard")
@login_required
def dashboard():
    content = """
    <h1>TrustVault Dashboard</h1>

    <p>Welcome, {{ current_user.username }}!</p>

    <p>Your role: {{ current_user.role }}</p>

    <p>
        <a href="{{ url_for('documents') }}">
            Open My Documents
        </a>
    </p>

    {% if current_user.role == "admin" %}
        <p>
            <a href="{{ url_for('admin_dashboard') }}">
                Open Admin Dashboard
            </a>
        </p>
    {% endif %}

    <form method="POST" action="{{ url_for('logout') }}">
        <input type="hidden"
               name="csrf_token"
               value="{{ csrf_token() }}">

        <button type="submit">Logout</button>
    </form>

    <p>
        <a href="{{ url_for('home') }}">Home</a>
    </p>
    """

    return page(content)


# --------------------------------------------------
# 10. Document upload and document list
# --------------------------------------------------

@app.route("/documents", methods=["GET", "POST"])
@login_required
def documents():
    if request.method == "POST":
        uploaded_file = request.files.get("document")

        if not uploaded_file or not uploaded_file.filename:
            flash("Please select a file.")
            return redirect(url_for("documents"))

        safe_original_name = secure_filename(
            uploaded_file.filename
        )

        if not safe_original_name:
            flash("Invalid filename.")
            return redirect(url_for("documents"))

        if not allowed_file(safe_original_name):
            flash("This file type is not allowed.")
            return redirect(url_for("documents"))

        extension = safe_original_name.rsplit(
            ".", 1
        )[1].lower()

        stored_name = f"{uuid.uuid4().hex}.{extension}"

        destination = (
            Path(app.config["UPLOAD_FOLDER"]) / stored_name
        )

        try:
            uploaded_file.save(destination)

            digest = file_sha256(destination)

            document = Document(
                original_filename=safe_original_name,
                stored_filename=stored_name,
                sha256_hash=digest,
                owner_id=current_user.id,
                tenant_id=current_user.tenant_id,
            )

            db.session.add(document)
            db.session.flush()

            record_audit(
                "document_upload",
                document_id=document.id,
                details=f"Uploaded {safe_original_name}",
            )

            db.session.commit()

            flash("Document uploaded successfully.")

        except Exception:
            db.session.rollback()

            if destination.exists():
                destination.unlink()

            app.logger.exception(
                "Document upload failed"
            )

            flash("Upload failed. Please try again.")

        return redirect(url_for("documents"))

    owned_documents = Document.query.filter_by(
        owner_id=current_user.id,
        tenant_id=current_user.tenant_id,
    ).all()

    my_shares = DocumentShare.query.filter_by(
        shared_with_id=current_user.id,
        tenant_id=current_user.tenant_id,
    ).all()

    shared_documents = []

    for share in my_shares:
        document = db.session.get(
            Document,
            share.document_id,
        )

        if (
            document is not None
            and document.tenant_id == current_user.tenant_id
        ):
            shared_documents.append(document)

    owned_ids = {
        doc.id for doc in owned_documents
    }

    user_documents = owned_documents + [
        doc
        for doc in shared_documents
        if doc.id not in owned_ids
    ]

    download_permissions = {
        share.document_id: share.can_download
        for share in my_shares
    }

    content = """
    <h1>My Documents</h1>

    """ + FLASH_TEMPLATE + """

    <form method="POST" enctype="multipart/form-data">
        <input type="hidden"
               name="csrf_token"
               value="{{ csrf_token() }}">

        <input type="file"
               name="document"
               accept=".pdf,.txt,.png,.jpg,.jpeg,.docx,.xlsx"
               required>

        <button type="submit">Upload Document</button>
    </form>

    <hr>

    {% if documents %}
        {% for doc in documents %}
            <div class="document-card">

                <strong>{{ doc.original_filename }}</strong>

                <p>Owner: {{ doc.owner.username }}</p>

                <p>Uploaded: {{ doc.uploaded_at }}</p>

                <p>SHA-256:</p>

                <code>{{ doc.sha256_hash }}</code>

                {% if doc.owner_id == current_user.id %}
                    <form class="inline-form"
                          method="POST"
                          action="{{ url_for(
                              'share_document',
                              document_id=doc.id
                          ) }}">

                        <input type="hidden"
                               name="csrf_token"
                               value="{{ csrf_token() }}">

                        <input type="text"
                               name="username"
                               placeholder="Recipient username"
                               required>

                        <select name="permission">
                            <option value="view">
                                View only
                            </option>

                            <option value="download">
                                Allow download
                            </option>
                        </select>

                        <button type="submit">
                            Share Document
                        </button>
                    </form>
                {% endif %}

                {% if doc.owner_id == current_user.id
                      or download_permissions.get(doc.id, false) %}
                    <p>
                        <a href="{{ url_for(
                            'download_document',
                            document_id=doc.id
                        ) }}">
                            Download document
                        </a>
                    </p>
                {% else %}
                    <p>
                        View-only access.
                        Download is not permitted.
                    </p>
                {% endif %}

            </div>
        {% endfor %}
    {% else %}
        <p>No documents uploaded or shared with you yet.</p>
    {% endif %}

    <p>
        <a href="{{ url_for('dashboard') }}">
            Back to Dashboard
        </a>
    </p>
    """

    return page(
        content,
        documents=user_documents,
        download_permissions=download_permissions,
    )


# --------------------------------------------------
# 11. Share document with another user
# --------------------------------------------------

@app.route(
    "/documents/<int:document_id>/share",
    methods=["POST"],
)
@login_required
def share_document(document_id):
    document = db.session.get(
        Document,
        document_id,
    )

    if document is None:
        abort(404)

    if (
        document.owner_id != current_user.id
        or document.tenant_id != current_user.tenant_id
    ):
        abort(403)

    username = request.form.get(
        "username", ""
    ).strip()

    permission = request.form.get(
        "permission", "view"
    )

    if permission not in ("view", "download"):
        abort(400)

    target_user = User.query.filter_by(
        username=username,
        tenant_id=current_user.tenant_id,
    ).first()

    if target_user is None:
        flash("User not found in your company.")
        return redirect(url_for("documents"))

    if target_user.id == current_user.id:
        flash("You already own this document.")
        return redirect(url_for("documents"))

    existing_share = DocumentShare.query.filter_by(
        document_id=document.id,
        shared_with_id=target_user.id,
    ).first()

    if existing_share:
        existing_share.can_download = (
            permission == "download"
        )

        existing_share.tenant_id = current_user.tenant_id
        existing_share.shared_by_id = current_user.id

    else:
        share = DocumentShare(
            document_id=document.id,
            shared_with_id=target_user.id,
            shared_by_id=current_user.id,
            tenant_id=current_user.tenant_id,
            can_download=(permission == "download"),
        )

        db.session.add(share)

    record_audit(
        "document_shared",
        document_id=document.id,
        target_user_id=target_user.id,
        details=(
            f"Permission set to {permission} "
            f"for {target_user.username}"
        ),
    )

    db.session.commit()

    flash(
        f"Document shared with {target_user.username}."
    )

    return redirect(url_for("documents"))


# --------------------------------------------------
# 12. Download document with access control
# --------------------------------------------------

@app.route(
    "/documents/<int:document_id>/download"
)
@login_required
def download_document(document_id):
    document = db.session.get(
        Document,
        document_id,
    )

    if document is None:
        abort(404)

    is_owner = (
        document.owner_id == current_user.id
        and document.tenant_id == current_user.tenant_id
    )

    share = DocumentShare.query.filter_by(
        document_id=document.id,
        shared_with_id=current_user.id,
        tenant_id=current_user.tenant_id,
        can_download=True,
    ).first()

    if not is_owner and share is None:
        abort(403)

    record_audit(
        "document_download",
        document_id=document.id,
        details="Document downloaded",
    )

    db.session.commit()

    return send_from_directory(
        app.config["UPLOAD_FOLDER"],
        document.stored_filename,
        as_attachment=True,
        download_name=document.original_filename,
    )


# --------------------------------------------------
# 13. Admin dashboard and audit logs
# --------------------------------------------------

@app.route("/admin")
@login_required
def admin_dashboard():
    if current_user.role != "admin":
        abort(403)

    total_users = User.query.filter_by(
        tenant_id=current_user.tenant_id
    ).count()

    total_documents = Document.query.filter_by(
        tenant_id=current_user.tenant_id
    ).count()

    total_shares = DocumentShare.query.filter_by(
        tenant_id=current_user.tenant_id
    ).count()

    audit_logs = (
        AuditLog.query.filter_by(
            tenant_id=current_user.tenant_id
        )
        .order_by(AuditLog.created_at.desc())
        .limit(100)
        .all()
    )

    content = """
    <h1>Admin Dashboard</h1>

    <p>Users in tenant: {{ total_users }}</p>

    <p>Documents in tenant: {{ total_documents }}</p>

    <p>Document shares: {{ total_shares }}</p>

    <h2>Recent Audit Events (up to 100)</h2>

    {% if audit_logs %}
        {% for log in audit_logs %}
            <div class="document-card">

                <strong>{{ log.action }}</strong>

                <p>Time: {{ log.created_at }}</p>

                <p>Actor user ID: {{ log.actor_id }}</p>

                <p>Document ID: {{ log.document_id }}</p>

                <p>Target user ID: {{ log.target_user_id }}</p>

                <p>Details: {{ log.details or "" }}</p>

            </div>
        {% endfor %}
    {% else %}
        <p>No audit events recorded yet.</p>
    {% endif %}

    <p>
        <a href="{{ url_for('dashboard') }}">
            Back to Dashboard
        </a>
    </p>
    """

    return page(
        content,
        total_users=total_users,
        total_documents=total_documents,
        total_shares=total_shares,
        audit_logs=audit_logs,
    )


# --------------------------------------------------
# 14. Logout
# --------------------------------------------------

@app.route("/logout", methods=["POST"])
@login_required
def logout():
    record_audit(
        "logout",
        details="User logged out",
    )

    db.session.commit()

    logout_user()

    flash("You have logged out successfully.")

    return redirect(url_for("login"))


# --------------------------------------------------
# 15. Create database tables and start application
# --------------------------------------------------

with app.app_context():
    db.create_all()


if __name__ == "__main__":
    app.run(debug=True)