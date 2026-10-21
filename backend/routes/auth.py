import time
from functools import wraps
from flask import Blueprint, request, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from database import query

bp = Blueprint("auth", __name__)
attempts = {}

def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "uid" not in session:
            return jsonify(error="Please log in"), 401
        return f(*args, **kwargs)
    return wrapper

@bp.post("/api/register")
def register():
    d = request.get_json()
    if query("SELECT id FROM users WHERE email=?", (d["email"],), one=True):
        return jsonify(error="This email is already in use"), 400
    session["uid"] = query(
        "INSERT INTO users (full_name, phone, email, city, password) VALUES (?,?,?,?,?)",
        (d["full_name"], d["phone"], d["email"], d["city"], generate_password_hash(d["password"])),
        commit=True)
    return jsonify(ok=True)

@bp.post("/api/login")
def login():
    d = request.get_json()
    key = d["email"].lower()
    recent = [t for t in attempts.get(key, []) if time.time() - t < 600]
    if len(recent) >= 5:
        return jsonify(error="Too many attempts. Try again in 10 minutes."), 429
    user = query("SELECT * FROM users WHERE email=?", (d["email"],), one=True)
    if not user or not check_password_hash(user["password"], d["password"]):
        attempts[key] = recent + [time.time()]
        return jsonify(error="Wrong email or password"), 401
    session["uid"] = user["id"]
    return jsonify(ok=True)

@bp.post("/api/logout")
def logout():
    session.clear()
    return jsonify(ok=True)