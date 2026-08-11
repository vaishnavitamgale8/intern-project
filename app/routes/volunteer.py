"""Volunteer dashboard routes."""
from datetime import date
from flask import Blueprint, render_template, flash, redirect, url_for
from flask_login import login_required, current_user
from app.models import Volunteer, EventRegistration, Event, Donation
from app.extensions import db

volunteer_bp = Blueprint("volunteer", __name__)


@volunteer_bp.route("/dashboard")
@login_required
def dashboard():
    profile = Volunteer.query.filter_by(user_id=current_user.id).first()
    regs = EventRegistration.query.filter_by(user_id=current_user.id).all()
    donations = Donation.query.filter_by(user_id=current_user.id).all()
    total_donated = sum(d.amount for d in donations)
    upcomings = [r for r in regs if r.event.event_date >= date.today()]
    return render_template("volunteer/dashboard.html", profile=profile,
                           regs=regs, donations=donations,
                           total_donated=total_donated, upcomings=upcomings)


@volunteer_bp.route("/my-events")
@login_required
def my_events():
    regs = EventRegistration.query.filter_by(user_id=current_user.id).all()
    return render_template("volunteer/my_events.html", regs=regs)


@volunteer_bp.route("/my-donations")
@login_required
def my_donations():
    donations = Donation.query.filter_by(user_id=current_user.id).order_by(Donation.created_at.desc()).all()
    return render_template("volunteer/my_donations.html", donations=donations)