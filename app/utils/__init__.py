"""Helper utilities: uploads, ID generation, formatting."""
import os
import secrets
import uuid
import re
from datetime import datetime
from flask import current_app
from werkzeug.utils import secure_filename

ALLOWED_EXT = {"png", "jpg", "jpeg", "gif", "webp", "svg"}


def generate_application_id() -> str:
    return "VOL-" + datetime.utcnow().strftime("%Y%m%d") + "-" + secrets.token_hex(3).upper()


def generate_transaction_id() -> str:
    return "TXN-" + secrets.token_hex(6).upper()


def save_upload(file, subfolder: str) -> str:
    """Save an uploaded image and return the static-relative URL path."""
    if not file or not file.filename:
        raise ValueError("No file provided")
    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    if ext not in ALLOWED_EXT:
        raise ValueError("Unsupported file type")
    folder = os.path.join(current_app.config["UPLOAD_FOLDER"], subfolder)
    os.makedirs(folder, exist_ok=True)
    name = uuid.uuid4().hex + "." + ext
    file.save(os.path.join(folder, name))
    return f"/static/uploads/{subfolder}/{name}"


def format_date(value, fmt="%b %d, %Y"):
    if not value:
        return "—"
    if isinstance(value, str):
        value = datetime.fromisoformat(value)
    return value.strftime(fmt)


def slugify(text: str) -> str:
    s = text.lower().strip().replace(" ", "-")
    return re.sub(r"[^a-z0-9-]", "", s)


def safe_int(value, default=0):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def safe_float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def clean_phone(value: str) -> str:
    digits = re.sub(r"\D", "", value or "")
    return digits[:15]