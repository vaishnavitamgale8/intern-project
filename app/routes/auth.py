"""Authentication routes: register, login, logout, profile."""
from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from flask_login import login_user, logout_user, login_required, current_user
from app.models import User, Volunteer, EventRegistration, Donation
from app.extensions import db

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("public.home"))
    if request.method == "POST":
        f = request.form
        name, email, pwd = f.get("full_name", "").strip(), f.get("email", "").strip().lower(), f.get("password", "")
        if not name or not email or not pwd:
            flash("All fields are required.", "error")
            return redirect(url_for("auth.register"))
        if len(pwd) < 8:
            flash("Password must be at least 8 characters.", "error")
            return redirect(url_for("auth.register"))
        if User.query.filter_by(email=email).first():
            flash("An account with that email already exists.", "error")
            return redirect(url_for("auth.register"))
        user = User(full_name=name, email=email, role="USER",
                    phone=f.get("phone") or None, city=f.get("city") or None)
        user.set_password(pwd)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        flash(f"Welcome, {name}! Your account has been created.", "success")
        return redirect(url_for("public.home"))
    return render_template("auth/register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("public.home"))
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        user = User.query.filter_by(email=email).first()
        if not user or not user.check_password(password):
            flash("Invalid email or password.", "error")
            return redirect(url_for("auth.login"))
        if not user.is_active:
            flash("This account is disabled.", "error")
            return redirect(url_for("auth.login"))
        login_user(user)
        next_url = request.args.get("next")
        flash(f"Welcome back, {user.full_name}!", "success")
        if user.is_admin:
            return redirect(next_url or url_for("admin.dashboard"))
        return redirect(next_url or url_for("public.home"))
    return render_template("auth/login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("public.home"))


@auth_bp.route("/profile")
@login_required
def profile():
    app = Volunteer.query.filter_by(user_id=current_user.id).first()
    regs = EventRegistration.query.filter_by(user_id=current_user.id).all()
    donations = Donation.query.filter_by(user_id=current_user.id).all()
    return render_template("auth/profile.html", application=app, regs=regs, donations=donations)