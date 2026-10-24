
import io
import pytest

from app import app, db, User, Document, AuditLog


@pytest.fixture
def client():
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False

    with app.app_context():
        db.drop_all()
        db.create_all()

        user = User(username="uploadtester", role="user", tenant_id=1)
        user.set_password("TestPass123!")
        db.session.add(user)
        db.session.commit()

        yield app.test_client()

        db.session.remove()
        db.drop_all()


def login(client):
    return client.post(
        "/login",
        data={"username": "uploadtester", "password": "TestPass123!"},
        follow_redirects=True,
    )


def test_disallowed_exe_file_is_rejected(client):
    login(client)

    response = client.post(
        "/documents",
        data={"document": (io.BytesIO(b"fake executable"), "malware.exe")},
        content_type="multipart/form-data",
        follow_redirects=True,
    )

    assert b"Unsupported file type" in response.data
    assert Document.query.count() == 0


def test_empty_filename_is_rejected(client):
    login(client)

    response = client.post(
        "/documents",
        data={"document": (io.BytesIO(b""), "")},
        content_type="multipart/form-data",
        follow_redirects=True,
    )

    assert b"Please choose a document" in response.data
    assert Document.query.count() == 0


def test_valid_txt_upload_creates_document_and_audit_log(client):
    login(client)

    response = client.post(
        "/documents",
        data={"document": (io.BytesIO(b"TrustVault test document"), "sample.txt")},
        content_type="multipart/form-data",
        follow_redirects=True,
    )

    assert b"Document uploaded successfully" in response.data
    assert Document.query.count() == 1
    assert AuditLog.query.filter_by(action="document_upload").count() == 1

def test_uploaded_document_hash_matches_file_content(client):
    import hashlib
    from pathlib import Path

    login(client)
    content = b"TrustVault integrity test"

    response = client.post(
        "/documents",
        data={"document": (io.BytesIO(content), "integrity.txt")},
        content_type="multipart/form-data",
        follow_redirects=True,
    )

    assert b"Document uploaded successfully" in response.data

    document = Document.query.filter_by(
        original_filename="integrity.txt"
    ).first()

    assert document is not None
    assert document.sha256_hash == hashlib.sha256(content).hexdigest()

    stored_path = Path(app.config["UPLOAD_FOLDER"]) / document.stored_filename
    assert stored_path.read_bytes() == content


def test_user_cannot_download_document_from_another_tenant(client):
    from app import User

    login(client)

    # Create a document owned by a different tenant.
    other_user = User(
        username="other_tenant_user",
        role="user",
        tenant_id=2,
    )
    other_user.set_password("OtherPass123!")
    db.session.add(other_user)
    db.session.commit()

    document = Document(
        original_filename="private.txt",
        stored_filename="nonexistent-private-file.txt",
        sha256_hash="0" * 64,
        owner_id=other_user.id,
        tenant_id=2,
    )
    db.session.add(document)
    db.session.commit()

    response = client.get(
        f"/documents/{document.id}/download"
    )

    assert response.status_code == 404
