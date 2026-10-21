from flask import Blueprint, request, session, jsonify
from database import query
from routes.auth import login_required
from search import keywords, score

bp = Blueprint("services", __name__)

@bp.get("/api/services")
@login_required
def list_services():
    words = keywords(request.args.get("q", ""))
    category = "%" + request.args.get("category", "") + "%"
    rows = query(
        """SELECT s.*, u.full_name AS provider, u.skills AS skills, u.bio AS bio,
           (SELECT ROUND(AVG(rating), 1) FROM reviews r WHERE r.worker_id = s.user_id) AS rating
           FROM services s
           JOIN users u ON u.id = s.user_id
           WHERE s.category LIKE ?
           ORDER BY s.id DESC""", (category,))
    for r in rows:
        r["score"] = score(words, r["title"], r["description"], r["category"], r["skills"], r["bio"], r["provider"])
        del r["skills"], r["bio"]
    if words:
        rows = sorted([r for r in rows if r["score"] > 0], key=lambda r: r["score"], reverse=True)
    return jsonify(rows)

@bp.post("/api/services")
@login_required
def add_service():
    d = request.get_json()
    city = query("SELECT city FROM users WHERE id=?", (session["uid"],), one=True)["city"]
    kind = "training" if d.get("kind") == "training" else "service"
    query("INSERT INTO services (user_id, title, category, description, price, city, kind) VALUES (?,?,?,?,?,?,?)",
          (session["uid"], d["title"], d["category"], d["description"], d["price"], city, kind), commit=True)
    return jsonify(ok=True)