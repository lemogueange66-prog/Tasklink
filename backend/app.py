import os, secrets
from flask import Flask
from models import init_db
from routes import auth, users, services, missions, messages, portfolio

FRONTEND = os.path.join(os.path.dirname(__file__), "..", "frontend")
app = Flask(__name__, static_folder=FRONTEND, static_url_path="")
app.secret_key = os.environ.get("SECRET_KEY") or secrets.token_hex(32)
app.config.update(MAX_CONTENT_LENGTH=50 * 1024 * 1024, SESSION_COOKIE_SAMESITE="Lax")

for module in (auth, users, services, missions, messages, portfolio):
    app.register_blueprint(module.bp)

@app.route("/")
def index():
    return app.send_static_file("index.html")

if __name__ == "__main__":
    init_db()
    app.run(debug=os.environ.get("FLASK_DEBUG") == "1")