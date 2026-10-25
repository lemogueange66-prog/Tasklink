"""One-to-one chat: conversation list, a thread you can poll for new messages, unread counter."""
from flask import Blueprint, request, session, jsonify
from database import query
from helpers import body, fail, text, whole
from routes.auth import login_required

bp = Blueprint("chat", __name__)
PARTNER = "id, full_name, profile_photo, city"


def partner_of(uid):
    return query(f"SELECT {PARTNER} FROM users WHERE id=?", (uid,), one=True)


@bp.get("/api/chat/conversations")
@login_required
def conversations():
    me = session["uid"]
    rows = query(
        """SELECT m.id, m.content, m.created, m.sender_id,
                  CASE WHEN m.sender_id=? THEN m.receiver_id ELSE m.sender_id END AS other_id
           FROM messages m WHERE m.sender_id=? OR m.receiver_id=? ORDER BY m.id DESC""", (me, me, me))
    unread = {r["sender_id"]: r["n"] for r in query(
        "SELECT sender_id, COUNT(*) AS n FROM messages WHERE receiver_id=? AND is_read=0 GROUP BY sender_id", (me,))}
    seen, out = set(), []
    for r in rows:                                  # newest first: first row per person = last message
        if r["other_id"] in seen:
            continue
        seen.add(r["other_id"])
        p = partner_of(r["other_id"])
        if not p:
            continue
        out.append({"user": p, "last": r["content"], "created": r["created"], "mine": r["sender_id"] == me,
                    "unread": unread.get(r["other_id"], 0)})
    return jsonify(out)


@bp.get("/api/chat/unread")
@login_required
def unread_count():
    n = query("SELECT COUNT(*) AS n FROM messages WHERE receiver_id=? AND is_read=0", (session["uid"],), one=True)["n"]
    return jsonify(count=n)


@bp.get("/api/chat/<int:other>")
@login_required
def thread(other):
    """Messages with one person. ?after=ID returns only newer ones (used for live refresh)."""
    me = session["uid"]
    p = partner_of(other)
    if not p or other == me:
        return fail("User not found", 404)
    after = whole(request.args.get("after", 0), 0) or 0
    rows = query(
        """SELECT id, sender_id, content, created FROM messages
           WHERE id > ? AND ((sender_id=? AND receiver_id=?) OR (sender_id=? AND receiver_id=?))
           ORDER BY id ASC LIMIT 300""", (after, me, other, other, me))
    for r in rows:
        r["mine"] = r.pop("sender_id") == me
    query("UPDATE messages SET is_read=1 WHERE receiver_id=? AND sender_id=? AND is_read=0", (me, other), commit=True)
    return jsonify(user=p, messages=rows)


@bp.post("/api/chat/<int:other>")
@login_required
def send(other):
    me = session["uid"]
    content = text(body(), "content")
    if other == me:
        return fail("You cannot message yourself")
    if not partner_of(other):
        return fail("No user found", 404)
    if not content:
        return fail("Write a message first")
    if len(content) > 2000:
        return fail("Text is too long")
    mid = query("INSERT INTO messages (sender_id, receiver_id, content) VALUES (?,?,?)",
                (me, other, content), commit=True)
    return jsonify(ok=True, id=mid)


@bp.post("/api/chat/find")
@login_required
def find_by_email():
    """Start a chat with someone you know only by e-mail."""
    u = query("SELECT id FROM users WHERE email=?", (text(body(), "email").lower(),), one=True)
    if not u:
        return fail("No user found", 404)
    if u["id"] == session["uid"]:
        return fail("You cannot message yourself")
    return jsonify(id=u["id"])
