from flask import Blueprint, request, session, jsonify
from database import query
from routes.auth import login_required
from search import keywords, score

bp = Blueprint("missions", __name__)

def own_mission(mid):
    return query("SELECT * FROM missions WHERE id=? AND user_id=?", (mid, session["uid"]), one=True)

@bp.get("/api/missions")
@login_required
def list_missions():
    words = keywords(request.args.get("q", ""))
    rows = query(
        """SELECT m.*, u.full_name AS author,
           EXISTS(SELECT 1 FROM applications a WHERE a.mission_id=m.id AND a.user_id=?) AS applied
           FROM missions m JOIN users u ON u.id = m.user_id
           WHERE m.status='open' AND m.user_id != ?
           ORDER BY m.id DESC""", (session["uid"], session["uid"]))
    if words:
        rows = [r for r in rows if score(words, r["title"], r["description"]) > 0]
    return jsonify(rows)

@bp.get("/api/my-missions")
@login_required
def my_missions():
    missions = query("SELECT * FROM missions WHERE user_id=? ORDER BY id DESC", (session["uid"],))
    for m in missions:
        m["applicants"] = query(
            "SELECT u.id, u.full_name FROM applications a JOIN users u ON u.id=a.user_id WHERE a.mission_id=?",
            (m["id"],))
        m["reviewed"] = bool(query("SELECT id FROM reviews WHERE mission_id=?", (m["id"],), one=True))
        worker = query("SELECT full_name FROM users WHERE id=?", (m["worker_id"],), one=True)
        m["worker"] = worker["full_name"] if worker else None
    return jsonify(missions)

@bp.post("/api/missions")
@login_required
def add_mission():
    d = request.get_json()
    city = query("SELECT city FROM users WHERE id=?", (session["uid"],), one=True)["city"]
    query("INSERT INTO missions (user_id, title, description, budget, city) VALUES (?,?,?,?,?)",
          (session["uid"], d["title"], d["description"], d["budget"], city), commit=True)
    return jsonify(ok=True)

@bp.post("/api/missions/<int:mid>/apply")
@login_required
def apply(mid):
    m = query("SELECT user_id, status FROM missions WHERE id=?", (mid,), one=True)
    if not m or m["status"] != "open" or m["user_id"] == session["uid"]:
        return jsonify(error="You cannot apply to this mission"), 400
    query("INSERT OR IGNORE INTO applications (mission_id, user_id) VALUES (?,?)",
          (mid, session["uid"]), commit=True)
    return jsonify(ok=True)

@bp.post("/api/missions/<int:mid>/accept")
@login_required
def accept(mid):
    worker = request.get_json().get("user_id")
    if not own_mission(mid) or not query(
            "SELECT id FROM applications WHERE mission_id=? AND user_id=?", (mid, worker), one=True):
        return jsonify(error="Not allowed"), 400
    query("UPDATE missions SET status='in_progress', worker_id=? WHERE id=?", (worker, mid), commit=True)
    return jsonify(ok=True)

@bp.post("/api/missions/<int:mid>/complete")
@login_required
def complete(mid):
    m = own_mission(mid)
    if not m or m["status"] != "in_progress":
        return jsonify(error="Not allowed"), 400
    query("UPDATE missions SET status='done' WHERE id=?", (mid,), commit=True)
    return jsonify(ok=True)

@bp.post("/api/missions/<int:mid>/review")
@login_required
def review(mid):
    d = request.get_json()
    m = own_mission(mid)
    try:
        rating = int(d.get("rating", 0))
    except (TypeError, ValueError):
        rating = 0
    if (not m or m["status"] != "done" or not 1 <= rating <= 5
            or query("SELECT id FROM reviews WHERE mission_id=?", (mid,), one=True)):
        return jsonify(error="Not allowed"), 400
    query("INSERT INTO reviews (mission_id, reviewer_id, worker_id, rating, comment) VALUES (?,?,?,?,?)",
          (mid, session["uid"], m["worker_id"], rating, d.get("comment", "")), commit=True)
    return jsonify(ok=True)