"""ImpactBridge AI – entry point.

Usage:
    python run.py
"""
import os
from app import create_app
from dotenv import load_dotenv

load_dotenv()

app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    host = os.environ.get("HOST", "127.0.0.1")
    app.run(host=host, port=port, debug=app.config.get("DEBUG", True))