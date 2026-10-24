import pytest
from sqlalchemy import create_engine

from app import app, db, User


@pytest.fixture
def client():
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False

    with app.app_context():
        original_engine = db.engines[None]
        test_engine = create_engine("sqlite://")
        db.engines[None] = test_engine

        try:
            db.create_all()

            admin = User(username="testadmin", role="admin", tenant_id=1)
            admin.set_password("TestPass123!")

            normal_user = User(username="testuser", role="user", tenant_id=1)
            normal_user.set_password("TestPass123!")

            db.session.add_all([admin, normal_user])
            db.session.commit()

            yield app.test_client()

        finally:
            db.session.remove()
            db.drop_all()
            db.engines[None] = original_engine
            test_engine.dispose()


def login(client, username, password="TestPass123!"):
    return client.post(
        "/login",
        data={"username": username, "password": password},
        follow_redirects=True,
    )


def test_normal_user_cannot_access_admin(client):
    login(client, "testuser")
    response = client.get("/admin")
    assert response.status_code == 403


def test_admin_can_access_admin(client):
    login(client, "testadmin")
    response = client.get("/admin")
    assert response.status_code == 200
