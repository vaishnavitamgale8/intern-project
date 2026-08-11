"""AI routes: ImpactBot chat + content generator."""
from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import current_user
from app.ai.assistant import chat_answer, generate_content
from app.models import AIConversation
from app.extensions import db

ai_bp = Blueprint("ai", __name__)


@ai_bp.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    question = (data.get("message") or "").strip()
    result = chat_answer(question)
    db.session.add(AIConversation(
        user_id=current_user.id if current_user.is_authenticated else None,
        question=question, answer=result["answer"], source=result["source"],
    ))
    db.session.commit()
    return jsonify(result)


@ai_bp.route("/status")
def status():
    from app.ai.assistant import _ollama_available
    base = __import__("flask").current_app.config.get("OLLAMA_BASE_URL", "http://localhost:11434")
    online = _ollama_available(base)
    return jsonify({"online": online, "model": "llama3.2", "enabled": __import__("flask").current_app.config.get("OLLAMA_ENABLED", False)})


@ai_bp.route("/generate", methods=["POST"])
def generate():
    """Admin-only: generate awareness copy for a topic via Ollama or fallback."""
    topic = (request.form.get("topic") or "").strip()
    tone = request.form.get("tone", "professional")
    if not topic:
        flash("Please provide a topic.", "error")
        return redirect(url_for("admin.audits"))
    text = generate_content(topic, tone)
    flash(f"Generated content: {text[:220]}…", "success")
    return redirect(url_for("admin.audits"))
