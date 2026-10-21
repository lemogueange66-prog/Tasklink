from flask import Blueprint, request, session, jsonify
from database import query
from routes.auth import login_required

bp = Blueprint("users", __name__)

@bp.get("/api/me")
@login_required
def get_me():
    return jsonify(query(
        "SELECT id, full_name, phone, email, city, bio, skills FROM users WHERE id=?",
        (session["uid"],), one=True))

@bp.put("/api/me")
@login_required
def update_me():
    d = request.get_json()
    query("UPDATE users SET full_name=?, city=?, bio=?, skills=? WHERE id=?",
          (d["full_name"], d["city"], d["bio"], d["skills"], session["uid"]), commit=True)
    return jsonify(ok=True)

@bp.get("/api/users/<int:user_id>")
@login_required
def get_user(user_id):
    user = query("SELECT id, full_name, phone, city, bio, skills FROM users WHERE id=?",
                 (user_id,), one=True)
    if not user:
        return jsonify(error="User not found"), 404
    user["rating"] = query(
        "SELECT ROUND(AVG(rating), 1) AS avg, COUNT(*) AS n FROM reviews WHERE worker_id=?",
        (user_id,), one=True)
    user["reviews"] = query(
        """SELECT r.rating, r.comment, u.full_name AS reviewer FROM reviews r
           JOIN users u ON u.id = r.reviewer_id
           WHERE r.worker_id=? ORDER BY r.id DESC LIMIT 10""", (user_id,))
    user["services"] = query(
        "SELECT id, title, category, description, price, kind FROM services WHERE user_id=? ORDER BY id DESC",
        (user_id,))
    return jsonify(user)

@bp.post("/api/report")
@login_required
def report():
    d = request.get_json()
    query("INSERT INTO reports (reporter_id, reported_id, reason) VALUES (?,?,?)",
          (session["uid"], d["user_id"], d["reason"]), commit=True)
    return jsonify(ok=True)