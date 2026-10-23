
import os

from flask import (
    Flask,
    render_template_string,
    request,
    redirect,
    url_for,
    flash,
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
from werkzeug.security import (
    generate_password_hash,
    check_password_hash,
)


# --------------------------------------------------
# 1. Application configuration
# --------------------------------------------------

app = Flask(__name__)

app.config["SECRET_KEY"] = os.environ.get(
    "SECRET_KEY",
    "dev-only-change-this-before-deployment",
)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///trustvault.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize each extension only once.
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

csrf = CSRFProtect(app)


# --------------------------------------------------
# 2. Database model
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

    tenant_id = db.Column(
        db.Integer,
        nullable=False,
        default=1,
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


@login_manager.user_loader
def load_user(user_id):
    try:
        return db.session.get(User, int(user_id))
    except (ValueError, TypeError):
        return None


# --------------------------------------------------
# 3. Common page styling
# --------------------------------------------------

PAGE_STYLE = """
<style>
    body {
        font-family: Arial, sans-serif;
        background: #101827;
        color: white;
        text-align: center;
        padding: 35px 15px;
    }

    .panel {
        max-width: 480px;
        margin: 30px auto;
        padding: 28px;
        background: #1e293b;
        border-radius: 12px;
    }

    input, button {
        width: 100%;
        padding: 12px;
        margin: 9px 0;
        box-sizing: border-box;
        border-radius: 6px;
    }

    input {
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
</style>
"""


# --------------------------------------------------
# 4. Home page
# --------------------------------------------------

@app.route("/")
def home():
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>TrustVault</title>
        {{ style|safe }}
    </head>
    <body>
        <div class="panel">
            <h1>TrustVault</h1>

            <h3>Secure Document Sharing Platform</h3>

            <p>
                Manage documents with controlled access
                and a reliable audit trail.
            </p>

            {% if current_user.is_authenticated %}
                <p>Welcome, {{ current_user.username }}!</p>
                <p>
                    <a href="{{ url_for('dashboard') }}">
                        Open Dashboard
                    </a>
                </p>

                <form method="POST"
                      action="{{ url_for('logout') }}">
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
        </div>
    </body>
    </html>
    """, style=PAGE_STYLE)


# --------------------------------------------------
# 5. User registration
# --------------------------------------------------

@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
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

        elif User.query.filter_by(username=username).first():
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

    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>TrustVault - Register</title>
        {{ style|safe }}
    </head>
    <body>
        <div class="panel">
            <h1>Create Account</h1>

            {% with messages = get_flashed_messages() %}
                {% for message in messages %}
                    <p class="message">{{ message }}</p>
                {% endfor %}
            {% endwith %}

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

            <p><a href="{{ url_for('home') }}">Home</a></p>
        </div>
    </body>
    </html>
    """, style=PAGE_STYLE)


# --------------------------------------------------
# 6. User login
# --------------------------------------------------

@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for("dashboard"))

        flash("Invalid username or password.")

    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>TrustVault - Login</title>
        {{ style|safe }}
    </head>
    <body>
        <div class="panel">
            <h1>Login</h1>

            {% with messages = get_flashed_messages() %}
                {% for message in messages %}
                    <p class="message">{{ message }}</p>
                {% endfor %}
            {% endwith %}

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

            <p><a href="{{ url_for('home') }}">Home</a></p>
        </div>
    </body>
    </html>
    """, style=PAGE_STYLE)


# --------------------------------------------------
# 7. Protected user dashboard
# --------------------------------------------------

@app.route("/dashboard")
@login_required
def dashboard():
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>TrustVault - Dashboard</title>
        {{ style|safe }}
    </head>
    <body>
        <div class="panel">
            <h1>TrustVault Dashboard</h1>

            <p>Welcome, {{ current_user.username }}!</p>
            <p>Your role: {{ current_user.role }}</p>

            <p>You are successfully logged in.</p>

            <p>Document management features are coming next.</p>

            <form method="POST"
                  action="{{ url_for('logout') }}">
                <input type="hidden"
                       name="csrf_token"
                       value="{{ csrf_token() }}">

                <button type="submit">Logout</button>
            </form>

            <p><a href="{{ url_for('home') }}">Home</a></p>
        </div>
    </body>
    </html>
    """, style=PAGE_STYLE)


# --------------------------------------------------
# 8. User logout
# --------------------------------------------------

@app.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    flash("You have logged out successfully.")
    return redirect(url_for("login"))


# --------------------------------------------------
# 9. Create database tables
# --------------------------------------------------

with app.app_context():
    db.create_all()


# --------------------------------------------------
# 10. Start development server
# --------------------------------------------------

if __name__ == "__main__":
    app.run(debug=True)
