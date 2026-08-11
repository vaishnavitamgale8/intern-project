"""Public website routes."""
from flask import Blueprint, render_template, request, flash, redirect, url_for
from app.models import (
    Project, Campaign, Event, Gallery, Volunteer, ImpactMetric,
    ContactMessage, Donation, User, EventRegistration,
)
from app.extensions import db
from app.utils import generate_application_id, generate_transaction_id

public_bp = Blueprint("public", __name__)


@public_bp.route("/")
def home():
    projects = Project.query.order_by(Project.created_at.desc()).limit(3).all()
    campaigns = Campaign.query.filter_by(status="ACTIVE").limit(3).all()
    events = Event.query.order_by(Event.event_date.asc()).limit(3).all()
    stats = {
        "projects": Project.query.count(),
        "volunteers": Volunteer.query.filter_by(status="APPROVED").count(),
        "beneficiaries": db.session.query(db.func.coalesce(db.func.sum(Project.beneficiaries), 0)).scalar(),
        "campaigns": Campaign.query.filter_by(status="ACTIVE").count(),
    }
    return render_template("public/home.html", projects=projects, campaigns=campaigns,
                           events=events, stats=stats)


@public_bp.route("/about")
def about():
    return render_template("public/about.html")


@public_bp.route("/projects")
def projects():
    q = request.args.get("q", "").strip()
    category = request.args.get("category", "")
    status = request.args.get("status", "")
    query = Project.query
    if q:
        query = query.filter(Project.title.ilike(f"%{q}%"))
    if category:
        query = query.filter_by(category=category)
    if status:
        query = query.filter_by(status=status)
    all_projects = query.order_by(Project.created_at.desc()).all()
    categories = db.session.query(Project.category).distinct().all()
    statuses = db.session.query(Project.status).distinct().all()
    return render_template("public/projects.html", projects=all_projects,
                           categories=[c[0] for c in categories],
                           statuses=[s[0] for s in statuses])


@public_bp.route("/projects/<int:pid>")
def project_detail(pid):
    project = db.get_or_404(Project, pid)
    return render_template("public/project_detail.html", project=project)


@public_bp.route("/campaigns")
def campaigns():
    active = Campaign.query.filter_by(status="ACTIVE").order_by(Campaign.created_at.desc()).all()
    return render_template("public/campaigns.html", campaigns=active)


@public_bp.route("/campaigns/<int:cid>")
def campaign_detail(cid):
    campaign = db.get_or_404(Campaign, cid)
    return render_template("public/campaign_detail.html", campaign=campaign)


@public_bp.route("/campaigns/<int:cid>/donate", methods=["GET", "POST"])
def donate(cid):
    campaign = db.get_or_404(Campaign, cid)
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        try:
            amount = round(float(request.form.get("amount", 0)), 2)
        except (TypeError, ValueError):
            amount = 0
        if not name or not email or amount <= 0:
            flash("Please provide a valid name, email and amount.", "error")
            return redirect(url_for("public.donate", cid=cid))
        donor = User.query.filter_by(email=email).first()
        donation = Donation(
            transaction_id=generate_transaction_id(),
            user_id=donor.id if donor else None,
            campaign_id=campaign.id,
            donor_name=name,
            donor_email=email,
            amount=amount,
            message=request.form.get("message", "").strip() or None,
            demo=True,
        )
        db.session.add(donation)
        db.session.commit()
        return render_template("public/donation_receipt.html", donation=donation)
    return render_template("public/donate.html", campaign=campaign)


@public_bp.route("/events")
def events():
    event_list = Event.query.order_by(Event.event_date.asc()).all()
    return render_template("public/events.html", events=event_list)


@public_bp.route("/events/<int:eid>/register", methods=["POST"])
def event_register(eid):
    from flask_login import current_user, login_required
    if not current_user.is_authenticated:
        flash("Please log in to register for events.", "warning")
        return redirect(url_for("auth.login"))
    event = db.get_or_404(Event, eid)
    if event.is_full:
        flash("Sorry, this event is full.", "error")
        return redirect(url_for("public.events"))
    existing = EventRegistration.query.filter_by(user_id=current_user.id, event_id=event.id).first()
    if existing:
        flash("You are already registered for this event.", "warning")
    else:
        db.session.add(EventRegistration(user_id=current_user.id, event_id=event.id))
        db.session.commit()
        flash("Registration successful!", "success")
    return redirect(url_for("public.events"))


@public_bp.route("/gallery")
def gallery():
    items = Gallery.query.order_by(Gallery.uploaded_at.desc()).all()
    categories = db.session.query(Gallery.category).distinct().all()
    return render_template("public/gallery.html", items=items,
                           categories=[c[0] for c in categories])


@public_bp.route("/impact")
def impact():
    projects = Project.query.count()
    volunteers = Volunteer.query.filter_by(status="APPROVED").count()
    campaigns = Campaign.query.filter_by(status="ACTIVE").count()
    events = Event.query.count()
    funds = db.session.query(db.func.coalesce(db.func.sum(Donation.amount), 0)).scalar()
    beneficiaries = db.session.query(db.func.coalesce(db.func.sum(Project.beneficiaries), 0)).scalar()

    # Project categories for pie chart
    cats = db.session.query(Project.category, db.func.count(Project.id)).group_by(Project.category).all()
    # Volunteer growth by month from impact_metrics
    metrics = ImpactMetric.query.order_by(ImpactMetric.year, ImpactMetric.month).all()
    # Campaign performance
    camp_perf = [(c.title, c.amount_raised) for c in Campaign.query.all()]
    # Beneficiaries by project
    ben = [(p.title, p.beneficiaries or 0) for p in Project.query.all()]

    return render_template("public/impact.html", stats={
        "projects": projects, "volunteers": volunteers, "campaigns": campaigns,
        "events": events, "funds": round(funds, 0), "beneficiaries": beneficiaries,
    }, categories=cats, metrics=metrics, camp_perf=camp_perf, beneficiaries=ben)


@public_bp.route("/volunteer", methods=["GET", "POST"])
def volunteer_apply():
    if request.method == "POST":
        f = request.form
        required = ("full_name", "email", "phone", "city", "skills",
                    "area_of_interest", "availability", "reason")
        if any(not f.get(k, "").strip() for k in required):
            flash("Please fill in all required fields.", "error")
            return redirect(url_for("public.volunteer_apply"))
        existing = Volunteer.query.filter_by(email=f["email"].strip()).first()
        if existing:
            flash("An application for this email already exists.", "warning")
            return redirect(url_for("public.volunteer_apply"))
        user = User.query.filter_by(email=f["email"].strip()).first()
        v = Volunteer(
            application_id=generate_application_id(),
            user_id=user.id if user else None,
            full_name=f["full_name"].strip(),
            email=f["email"].strip().lower(),
            phone=f["phone"].strip(),
            city=f["city"].strip(),
            skills=f["skills"].strip(),
            area_of_interest=f["area_of_interest"].strip(),
            availability=f["availability"].strip(),
            experience=f.get("experience", "").strip() or None,
            reason=f["reason"].strip(),
            status="PENDING",
        )
        db.session.add(v)
        db.session.commit()
        return render_template("public/volunteer_success.html", application=v)
    return render_template("public/volunteer.html")


@public_bp.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        f = request.form
        if not all(f.get(k, "").strip() for k in ("name", "email", "subject", "message")):
            flash("All fields are required.", "error")
            return redirect(url_for("public.contact"))
        db.session.add(ContactMessage(
            name=f["name"].strip(), email=f["email"].strip().lower(),
            subject=f["subject"].strip(), message=f["message"].strip(),
        ))
        db.session.commit()
        flash("Your message has been sent. Thank you!", "success")
        return redirect(url_for("public.contact"))
    return render_template("public/contact.html")