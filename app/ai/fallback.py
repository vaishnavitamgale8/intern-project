"""Rule-based fallback answer engine used when Ollama is unavailable."""
import re

KEYWORD_ANSWERS = {
    "volunteer": "You can apply to volunteer on the Volunteer page. After submitting, our team reviews applications and you'll be notified by email.",
    "donat": "You can donate to an active campaign from the Campaigns page. Donations on this academic demo are simulated – no real payment is processed.",
    "event": "Check the Events page for upcoming volunteering & awareness events. Log in and press 'Register' to reserve a seat.",
    "project": "Browse our Projects page to see social-impact initiatives with details on objectives, activities and beneficiaries.",
    "impact": "The Impact dashboard shows beneficiaries reached, volunteers engaged, funds raised and project categories.",
    "contact": "Use the Contact page to send us a message – our team typically replies within 1-2 working days.",
    "login": "Create an account from the Register page. After logging in you get a personal dashboard, event registrations and donation history.",
    "ai": "ImpactBridge AI is a local AI assistant. When Ollama is running it generates rich answers; otherwise it uses a built-in knowledge base.",
    "help": "I can answer questions about volunteering, projects, campaigns, donations, events and our impact. Try asking 'How do I volunteer?'",
    "hi": "Hello! 👋 I'm ImpactBot, your ImpactBridge AI assistant. Ask me about volunteering, our projects, or how to donate.",
    "hello": "Hello! 👋 I'm ImpactBot, your ImpactBridge AI assistant. Ask me about volunteering, our projects, or how to donate.",
}

GREETING = re.compile(r"\b(hi|hello|hey|namaste)\b", re.I)


def get_fallback_answer(question: str) -> str:
    q = question.lower()
    if GREETING.search(q):
        return KEYWORD_ANSWERS["hi"]
    for key, answer in KEYWORD_ANSWERS.items():
        if key in q:
            return answer
    return (
        "I can help you with: volunteering, projects, campaigns, donations, events, "
        "and our impact. Please ask a question about one of these topics – for example "
        "'How do I register for an event?'"
    )