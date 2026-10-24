from getpass import getpass
from app import app, db, User

with app.app_context():
    if User.query.count() > 0:
        print("Users already exist. No changes made.")
    else:
        username = "admin"
        password = getpass("Choose admin password (hidden): ")
        confirm = getpass("Confirm admin password: ")

        if len(password) < 12:
            print("Password must contain at least 12 characters.")
        elif password != confirm:
            print("Passwords do not match. No account created.")
        else:
            admin = User(
                username=username,
                role="admin",
                tenant_id=1
            )
            admin.set_password(password)
            db.session.add(admin)
            db.session.commit()

            print("Admin account created successfully.")
            print("Username: admin")
            print("Role: admin")