
import os
import uuid
import hashlib
from pathlib import Path

from flask import (
    Flask, abort, flash, redirect, render_template,
    request, send_from_directory, url_for
)
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_login import (
    LoginManager, UserMixin, current_user, login_required,
    login_user, logout_user
)
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename


# -------------------- CONFIGURATION --------------------

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get(
    "SECRET_KEY", "change-this-before-deployment"
)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    "DATABASE_URL", "sqlite:///trustvault.db"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024

UPLOAD_FOLDER = Path(app.root_path) / "private_uploads"
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
app.config["UPLOAD_FOLDER"] = str(UPLOAD_FOLDER)

ALLOWED_EXTENSIONS = {
    "pdf", "txt", "png", "jpg", "jpeg", "docx", "xlsx"
}

db = SQLAlchemy(app)
csrf = CSRFProtect(app)
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=[],
    storage_uri=os.environ.get('RATELIMIT_STORAGE_URI', 'memory://'),
)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


# -------------------- DATABASE MODELS --------------------

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="user")
    tenant_id = db.Column(db.Integer, nullable=False, default=1)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Document(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original_filename = db.Column(db.String(255), nullable=False)
    stored_filename = db.Column(db.String(255), unique=True, nullable=False)
    sha256_hash = db.Column(db.String(64), nullable=False)
    owner_id = db.Column(
        db.Integer, db.ForeignKey("user.id"), nullable=False, index=True
    )
    tenant_id = db.Column(db.Integer, nullable=False, index=True)
    uploaded_at = db.Column(
        db.DateTime, nullable=False, default=db.func.current_timestamp()
    )
    owner = db.relationship("User", backref="documents")


class DocumentShare(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(
        db.Integer, db.ForeignKey("document.id"), nullable=False
    )
    shared_with_id = db.Column(
        db.Integer, db.ForeignKey("user.id"), nullable=False
    )
    shared_by_id = db.Column(
        db.Integer, db.ForeignKey("user.id"), nullable=False
    )
    tenant_id = db.Column(db.Integer, nullable=False)
    can_download = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(
        db.DateTime, nullable=False, default=db.func.current_timestamp()
    )
    __table_args__ = (
        db.UniqueConstraint(
            "document_id", "shared_with_id",
            name="unique_document_share"
        ),
    )


class AuditLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    actor_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)
    document_id = db.Column(
        db.Integer, db.ForeignKey("document.id"), nullable=True
    )
    target_user_id = db.Column(
        db.Integer, db.ForeignKey("user.id"), nullable=True
    )
    tenant_id = db.Column(db.Integer, nullable=False)
    action = db.Column(db.String(80), nullable=False)
    details = db.Column(db.String(500))
    created_at = db.Column(
        db.DateTime, nullable=False, default=db.func.current_timestamp()
    )


# -------------------- LOGIN SUPPORT --------------------

@login_manager.user_loader
def load_user(user_id):
    try:
        return db.session.get(User, int(user_id))
    except (TypeError, ValueError):
        return None


def record_audit(action, document_id=None,
                 target_user_id=None, details=None):
    if current_user.is_authenticated:
        db.session.add(
            AuditLog(
                actor_id=current_user.id,
                document_id=document_id,
                target_user_id=target_user_id,
                tenant_id=current_user.tenant_id,
                action=action,
                details=details,
            )
        )


def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )


def calculate_sha256(file_path):
    digest = hashlib.sha256()

    with open(file_path, "rb") as file:
        for chunk in iter(lambda: file.read(8192), b""):
            digest.update(chunk)

    return digest.hexdigest()


# -------------------- HOME --------------------

@app.route("/")
def home():
    return render_template("home.html")


# -------------------- REGISTRATION --------------------

@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        if not username or not password:
            flash("Username and password are required.", "error")

        elif len(username) > 80:
            flash("Username must be 80 characters or fewer.", "error")

        elif len(password) < 8:
            flash("Password must contain at least 8 characters.", "error")

        elif password != confirm_password:
            flash("Passwords do not match.", "error")

        elif User.query.filter_by(username=username).first():
            flash("Username already exists.", "error")

        else:
            user = User(
                username=username,
                role="user",
                tenant_id=1
            )
            user.set_password(password)
            db.session.add(user)

            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
                flash("Username already exists.", "error")
            else:
                flash("Account created. Please log in.", "success")
                return redirect(url_for("login"))

    return render_template("register.html")


# -------------------- LOGIN --------------------

@app.route("/login", methods=["GET", "POST"])
@limiter.limit("5 per minute")
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user)
            record_audit("login", details="User logged in")
            db.session.commit()
            return redirect(url_for("dashboard"))

        flash("Invalid username or password.", "error")

    return render_template("login.html")


# -------------------- DASHBOARD --------------------

@app.route("/dashboard")
@login_required
def dashboard():
    owned_count = Document.query.filter_by(
        owner_id=current_user.id,
        tenant_id=current_user.tenant_id
    ).count()

    shared_count = DocumentShare.query.filter_by(
        shared_with_id=current_user.id,
        tenant_id=current_user.tenant_id
    ).count()

    return render_template(
        "dashboard.html",
        owned_count=owned_count,
        shared_count=shared_count
    )


# -------------------- DOCUMENT MANAGEMENT --------------------

@app.route("/documents", methods=["GET", "POST"])
@login_required
def documents():
    if request.method == "POST":
        uploaded_file = request.files.get("document")

        if not uploaded_file or not uploaded_file.filename:
            flash("Please choose a document.", "error")
            return redirect(url_for("documents"))

        filename = secure_filename(uploaded_file.filename)

        if not filename or not allowed_file(filename):
            flash("Unsupported file type.", "error")
            return redirect(url_for("documents"))

        extension = filename.rsplit(".", 1)[1].lower()
        stored_filename = f"{uuid.uuid4().hex}.{extension}"
        destination = Path(app.config["UPLOAD_FOLDER"]) / stored_filename

        try:
            uploaded_file.save(destination)

            document = Document(
                original_filename=filename,
                stored_filename=stored_filename,
                sha256_hash=calculate_sha256(destination),
                owner_id=current_user.id,
                tenant_id=current_user.tenant_id
            )

            db.session.add(document)
            db.session.flush()

            record_audit(
                "document_upload",
                document_id=document.id,
                details=f"Uploaded {filename}"
            )

            db.session.commit()
            flash("Document uploaded successfully.", "success")

        except Exception:
            db.session.rollback()

            if destination.exists():
                destination.unlink()

            app.logger.exception("Document upload failed")
            flash("Upload failed. Please try again.", "error")

        return redirect(url_for("documents"))

    owned_documents = Document.query.filter_by(
        owner_id=current_user.id,
        tenant_id=current_user.tenant_id
    ).order_by(Document.uploaded_at.desc()).all()

    shares = DocumentShare.query.filter_by(
        shared_with_id=current_user.id,
        tenant_id=current_user.tenant_id
    ).all()

    shared_documents = []
    permissions = {}

    for share in shares:
        document = db.session.get(Document, share.document_id)

        if document and document.tenant_id == current_user.tenant_id:
            shared_documents.append(document)
            permissions[document.id] = share.can_download

    owned_ids = {document.id for document in owned_documents}

    visible_documents = owned_documents + [
        document for document in shared_documents
        if document.id not in owned_ids
    ]

    return render_template(
        "documents.html",
        documents=visible_documents,
        permissions=permissions
    )


# -------------------- SHARE DOCUMENT --------------------

@app.route("/documents/<int:document_id>/share", methods=["POST"])
@login_required
def share_document(document_id):
    document = db.session.get(Document, document_id)

    if document is None:
        abort(404)

    if (
        document.owner_id != current_user.id
        or document.tenant_id != current_user.tenant_id
    ):
        abort(403)

    username = request.form.get("username", "").strip()
    permission = request.form.get("permission", "view")

    if permission not in {"view", "download"}:
        abort(400)

    recipient = User.query.filter_by(
        username=username,
        tenant_id=current_user.tenant_id
    ).first()

    if recipient is None:
        flash("Recipient username not found.", "error")
        return redirect(url_for("documents"))

    if recipient.id == current_user.id:
        flash("You cannot share a document with yourself.", "error")
        return redirect(url_for("documents"))

    share = DocumentShare.query.filter_by(
        document_id=document.id,
        shared_with_id=recipient.id
    ).first()

    if share:
        share.can_download = permission == "download"
        share.shared_by_id = current_user.id
        share.tenant_id = current_user.tenant_id
    else:
        db.session.add(
            DocumentShare(
                document_id=document.id,
                shared_with_id=recipient.id,
                shared_by_id=current_user.id,
                tenant_id=current_user.tenant_id,
                can_download=(permission == "download")
            )
        )

    record_audit(
        "document_shared",
        document_id=document.id,
        target_user_id=recipient.id,
        details=f"Shared with {recipient.username}; permission={permission}"
    )

    db.session.commit()
    flash(f"Document shared with {recipient.username}.", "success")
    return redirect(url_for("documents"))


# -------------------- DOWNLOAD DOCUMENT --------------------

@app.route("/documents/<int:document_id>/download")
@login_required
def download_document(document_id):
    document = db.session.get(Document, document_id)

    if document is None or document.tenant_id != current_user.tenant_id:
        abort(404)

    is_owner = document.owner_id == current_user.id

    share = None

    if not is_owner:
        share = DocumentShare.query.filter_by(
            document_id=document.id,
            shared_with_id=current_user.id,
            tenant_id=current_user.tenant_id,
            can_download=True
        ).first()

    if not is_owner and share is None:
        record_audit(
            "document_download_denied",
            document_id=document.id,
            details=f"Unauthorized download attempt for {document.original_filename}"
        )
        db.session.commit()
        abort(403)

    file_path = Path(app.config["UPLOAD_FOLDER"]) / document.stored_filename

    if not file_path.is_file():
        abort(404)

    record_audit(
        "document_download",
        document_id=document.id,
        details=f"Downloaded {document.original_filename}"
    )
    db.session.commit()

    return send_from_directory(
        app.config["UPLOAD_FOLDER"],
        document.stored_filename,
        as_attachment=True,
        download_name=document.original_filename
    )


# -------------------- ADMIN DASHBOARD --------------------

@app.route("/admin")
@login_required
def admin_dashboard():
    if current_user.role != "admin":
        abort(403)

    users = User.query.filter_by(
        tenant_id=current_user.tenant_id
    ).order_by(User.username).all()

    logs = AuditLog.query.filter_by(
        tenant_id=current_user.tenant_id
    ).order_by(AuditLog.created_at.desc()).limit(100).all()

    document_count = Document.query.filter_by(
        tenant_id=current_user.tenant_id
    ).count()

    share_count = DocumentShare.query.filter_by(
        tenant_id=current_user.tenant_id
    ).count()

    return render_template(
        "admin.html",
        users=users,
        logs=logs,
        user_count=len(users),
        document_count=document_count,
        share_count=share_count
    )


# -------------------- LOGOUT --------------------

@app.route("/logout", methods=["POST"])
@login_required
def logout():
    record_audit("logout", details="User logged out")
    db.session.commit()

    logout_user()
    flash("You have logged out.", "success")

    return redirect(url_for("login"))


# -------------------- ERROR PAGES --------------------

@app.errorhandler(403)
def forbidden(_error):
    return render_template(
        "error.html",
        code=403,
        message="You do not have permission to access this page."
    ), 403


@app.errorhandler(404)
def not_found(_error):
    return render_template(
        "error.html",
        code=404,
        message="The requested page or document was not found."
    ), 404


@app.errorhandler(413)
def too_large(_error):
    return render_template(
        "error.html",
        code=413,
        message="File too large. Maximum size is 10 MB."
    ), 413


# -------------------- INITIALIZE DATABASE --------------------

with app.app_context():
    db.create_all()


if __name__ == "__main__":
    app.run(debug=True)
