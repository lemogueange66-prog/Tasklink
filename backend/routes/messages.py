from flask import Blueprint, request, session, jsonify
from database import query
from routes.auth import login_required

bp = Blueprint("messages", __name__)

@bp.get("/api/messages")
@login_required
def inbox():
    uid = session["uid"]
    return jsonify(query(
        """SELECT m.content, m.created, a.full_name AS sender, b.full_name AS receiver
           FROM messages m
           JOIN users a ON a.id = m.sender_id
           JOIN users b ON b.id = m.receiver_id
           WHERE m.sender_id=? OR m.receiver_id=?
           ORDER BY m.id DESC""", (uid, uid)))

@bp.post("/api/messages")
@login_required
def send():
    d = request.get_json()
    if d.get("to_id"):
        to = query("SELECT id FROM users WHERE id=?", (d["to_id"],), one=True)
    else:
        to = query("SELECT id FROM users WHERE email=?", (d.get("to_email", ""),), one=True)
    if not to:
        return jsonify(error="No user found"), 404
    query("INSERT INTO messages (sender_id, receiver_id, content) VALUES (?,?,?)",
          (session["uid"], to["id"], d["content"]), commit=True)
    return jsonify(ok=True)