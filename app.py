
from flask import Flask, render_template_string

app = Flask(__name__)

HOME_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TrustVault</title>
    <style>
        body {
            margin: 0;
            font-family: Arial, sans-serif;
            background: #0f172a;
            color: #f8fafc;
            display: grid;
            place-items: center;
            min-height: 100vh;
        }
        .card {
            text-align: center;
            padding: 40px;
            max-width: 520px;
            background: #1e293b;
            border: 1px solid #334155;
            border-radius: 18px;
        }
        h1 { color: #38bdf8; }
        p { color: #cbd5e1; line-height: 1.7; }
        .status {
            display: inline-block;
            padding: 8px 14px;
            background: #064e3b;
            color: #a7f3d0;
            border-radius: 20px;
        }
    </style>
</head>
<body>
    <main class="card">
        <h1>TrustVault</h1>
        <p>Secure Document Sharing Platform</p>
        <p>Manage documents with controlled access and a reliable audit trail.</p>
        <span class="status">Development server running</span>
    </main>
</body>
</html>
"""


@app.route("/")
def home():
    return render_template_string(HOME_PAGE)


if __name__ == "__main__":
    app.run(debug=True)
