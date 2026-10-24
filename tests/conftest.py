import os
import tempfile
from pathlib import Path

# Use a separate in-memory database for tests.
os.environ["DATABASE_URL"] = "sqlite://"
os.environ["SECRET_KEY"] = "trustvault-test-secret"

# Import the app only after setting the test database.
import app as app_module

app = app_module.app
db = app_module.db

# Store uploaded test files in a temporary folder.
_test_upload_dir = tempfile.TemporaryDirectory(prefix="trustvault-test-")
_test_upload_path = Path(_test_upload_dir.name)

app.config["TESTING"] = True
app.config["WTF_CSRF_ENABLED"] = False
app.config["UPLOAD_FOLDER"] = str(_test_upload_path)

# Keep routes using the module-level folder isolated too.
app_module.UPLOAD_FOLDER = _test_upload_path