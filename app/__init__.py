"""ImpactBridge AI – application factory."""
import os
from flask import Flask, render_template
from flask_login import LoginManager

from app.config import get_config
from app.extensions import db, csrf

login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.login_message = "Please log in to continue."
login_manager.login_message_category = "warning"


def create_app(config_object=None):
    """Create and configure the Flask application."""
    app = Flask(__name__)
    app.config.from_object(config_object or get_config())

    # Ensure instance folder & upload folder exist
    os.makedirs(app.instance_path, exist_ok=True)
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    # Initialize extensions
    db.init_app(app)
    csrf.init_app(app)
    login_manager.init_app(app)

    # Register blueprints
    from app.routes.public import public_bp
    from app.routes.auth import auth_bp
    from app.routes.volunteer import volunteer_bp
    from app.routes.admin import admin_bp
    from app.routes.ai import ai_bp

    app.register_blueprint(public_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(volunteer_bp, url_prefix="/volunteer")
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(ai_bp, url_prefix="/ai")

    # Create tables when running from CLI / tests
    with app.app_context():
        db.create_all()

    # ── Template globals ──────────────────────────────────────────
    @app.context_processor
    def inject_globals():
        from app.models import Campaign
        active_campaigns = Campaign.query.filter_by(status="ACTIVE").count()
        return {
            "site_name": app.config["SITE_NAME"],
            "site_tagline": app.config["SITE_TAGLINE"],
            "active_campaign_count": active_campaigns,
        }

    # ── Template filters ───────────────────────────────────────────
    from datetime import datetime

    @app.template_filter("datefmt")
    def datefmt(value, fmt="%b %d, %Y"):
        if not value:
            return "—"
        if isinstance(value, str):
            value = datetime.fromisoformat(value)
        return value.strftime(fmt)

    @app.template_filter("currency")
    def currency(value):
        return "₹{:,.0f}".format(value or 0)

    @app.template_filter("status_badge")
    def status_badge(s):
        return {"PENDING": "warning", "APPROVED": "success", "REJECTED": "error",
                "ACTIVE": "success", "CLOSED": "neutral", "OPEN": "success",
                "FULL": "warning", "COMPLETED": "accent", "PLANNED": "neutral",
                "DRAFT": "neutral"}.get(s, "neutral")

    # ── Error handlers ────────────────────────────────────────────
    @app.errorhandler(403)
    def forbidden(e):
        return render_template("errors/403.html"), 403

    @app.errorhandler(404)
    def not_found(e):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def server_error(e):
        db.session.rollback()
        return render_template("errors/500.html"), 500

    @login_manager.user_loader
    def load_user(user_id):
        from app.models import User
        return db.session.get(User, int(user_id))

    return app