import pytest
from sqlalchemy import create_engine

from app import app, db, User, AuditLog


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

            user = User(
                username="testuser",
                role="user",
                tenant_id=1,
            )
            user.set_password("TestPass123!")
            db.session.add(user)
            db.session.commit()

            yield app.test_client()

        finally:
            db.session.remove()
            db.drop_all()
            db.engines[None] = original_engine
            test_engine.dispose()


def test_failed_login_is_recorded(client):
    response = client.post(
        "/login",
        data={
            "username": "testuser",
            "password": "WrongPassword!",
        },
        follow_redirects=False,
    )

    assert response.status_code == 200

    with app.app_context():
        audit = AuditLog.query.filter_by(
            tenant_id=1,
            action="login_failed",
        ).first()

        assert audit is not None
        assert audit.details == "Invalid password"
