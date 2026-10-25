import time, sqlite3
from functools import wraps
from flask import Blueprint, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from database import query
from helpers import body, fail, text, valid_phone, CITIES, EMAIL_RE

bp = Blueprint("auth", __name__)
attempts = {}          # email -> times of recent wrong passwords (kept in memory)
WINDOW, MAX_TRIES = 600, 5


def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "uid" not in session:
            return jsonify(error="Please log in"), 401
        return f(*args, **kwargs)
    return wrapper


@bp.post("/api/register")
def register():
    d = body()
    name, phone = text(d, "full_name"), text(d, "phone")
    email, city = text(d, "email").lower(), text(d, "city")
    password = d.get("password")
    if not (name and phone and email and city) or not isinstance(password, str) or not password:
        return fail("Please complete all required fields")
    if len(password) < 6:
        return fail("Password must contain at least 6 characters")
    if len(password) > 128 or len(name) > 80:
        return fail("Text is too long")
    if not EMAIL_RE.match(email) or len(email) > 120:
        return fail("Enter a valid email address")
    if not valid_phone(phone):
        return fail("Enter a valid phone number")
    if city not in CITIES:
        return fail("Choose a city from the list")
    if query("SELECT id FROM users WHERE email=?", (email,), one=True):
        return fail("This email is already in use")
    try:
        uid = query("INSERT INTO users (full_name, phone, email, city, password) VALUES (?,?,?,?,?)",
                    (name, phone, email, city, generate_password_hash(password)), commit=True)
    except sqlite3.IntegrityError:          # two sign-ups with the same email at the same time
        return fail("This email is already in use")
    session.clear()
    session.permanent = True
    session["uid"] = uid
    return jsonify(ok=True)


@bp.post("/api/login")
def login():
    d = body()
    key, password = text(d, "email").lower(), d.get("password")
    if not key or not isinstance(password, str) or not password:
        return fail("Wrong email or password", 401)
    now = time.time()
    recent = [t for t in attempts.get(key, []) if now - t < WINDOW]
    if len(recent) >= MAX_TRIES:
        attempts[key] = recent
        return fail("Too many attempts. Try again in 10 minutes.", 429)
    user = query("SELECT id, password FROM users WHERE email=?", (key,), one=True)
    if not user or not check_password_hash(user["password"], password):
        attempts[key] = recent + [now]
        return fail("Wrong email or password", 401)
    attempts.pop(key, None)
    session.clear()
    session.permanent = True
    session["uid"] = user["id"]
    return jsonify(ok=True)


@bp.post("/api/logout")
def logout():
    session.clear()
    return jsonify(ok=True)
