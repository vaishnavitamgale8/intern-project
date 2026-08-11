"""ImpactBot assistant: Ollama live answers with local fallback engine."""
import re
import requests
from flask import current_app
from app.ai.fallback import get_fallback_answer

MODEL = "llama3.2"

GREETING = re.compile(r"\b(hi|hello|hey|namaste)\b", re.I)


def _system_prompt():
    return (
        "You are ImpactBot, the AI assistant for ImpactBridge AI, a platform that "
        "connects volunteers, donors and social-impact projects. Answer concisely in "
        "2-4 sentences using warm, helpful language. Mention how to use the website "
        "where relevant. If asked something unrelated, politely steer back to the platform."
    )


def _ollama_available(base_url: str) -> bool:
    try:
        r = requests.get(f"{base_url}/api/tags", timeout=2)
        return r.status_code == 200
    except Exception:
        return False


def chat_answer(question: str) -> dict:
    """Return {'answer': str, 'source': 'ollama'|'fallback'}."""
    q = question.strip()
    if not q:
        return {"answer": "Please ask me a question!", "source": "fallback"}

    base_url = current_app.config.get("OLLAMA_BASE_URL", "http://localhost:11434")

    if current_app.config.get("OLLAMA_ENABLED", False) and _ollama_available(base_url):
        try:
            r = requests.post(
                f"{base_url}/api/generate",
                json={
                    "model": MODEL,
                    "prompt": f"{_system_prompt()}\n\nUser: {q}\nAssistant:",
                    "stream": False,
                    "options": {"temperature": 0.6, "max_tokens": 280},
                },
                timeout=30,
            )
            if r.status_code == 200:
                answer = r.json().get("response", "").strip()
                if answer:
                    return {"answer": answer, "source": "ollama"}
        except Exception:
            pass

    return {"answer": get_fallback_answer(q), "source": "fallback"}


def generate_content(topic: str, tone: str = "professional") -> str:
    """Generate short marketing/awareness copy using Ollama if available, else template."""
    base_url = current_app.config.get("OLLAMA_BASE_URL", "http://localhost:11434")
    if current_app.config.get("OLLAMA_ENABLED", False) and _ollama_available(base_url):
        try:
            r = requests.post(
                f"{base_url}/api/generate",
                json={
                    "model": MODEL,
                    "prompt": (
                        f"Write a short {tone} awareness paragraph (50-80 words) about: {topic}. "
                        "End with one call-to-action sentence."
                    ),
                    "stream": False,
                    "options": {"temperature": 0.7, "max_tokens": 200},
                },
                timeout=30,
            )
            if r.status_code == 200 and r.json().get("response", "").strip():
                return r.json()["response"].strip()
        except Exception:
            pass

    return (
        f"{topic} – small actions create lasting change. At ImpactBridge AI we turn "
        f"awareness into action by connecting passionate volunteers with communities "
        f"that need them most. Join one of our projects or campaigns today and help us "
        f"build a brighter, fairer future for everyone."
    )