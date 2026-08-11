"""Admin dashboard routes."""
from functools import wraps
from datetime import datetime, date
from flask import Blueprint, render_template, request, flash, redirect, url_for, abort
from flask_login import login_required, current_user
from app.models import (User, Project, Campaign, Event, Volunteer, Donation,
                        Gallery, ContactMessage, ImpactMetric, AuditResult)
from app.extensions import db

admin_bp = Blueprint("admin", __name__)


def admin_required(fn):
    @wraps(fn)
    @login_required
    def wrapper(*args, **kwargs):
        if not current_user.is_admin:
            abort(403)
        return fn(*args, **kwargs)
    return wrapper


def status_badge(s):
    return {"PENDING": "warning", "APPROVED": "success", "REJECTED": "error",
            "ACTIVE": "success", "CLOSED": "neutral", "OPEN": "success",
            "FULL": "warning", "COMPLETED": "accent", "PLANNED": "neutral",
            "DRAFT": "neutral"}.get(s, "neutral")


admin_bp.add_app_template_filter(status_badge, "status_badge")


@admin_bp.route("/dashboard")
@admin_required
def dashboard():
    stats = {
        "users": User.query.count(),
        "projects": Project.query.count(),
        "campaigns": Campaign.query.count(),
        "events": Event.query.count(),
        "volunteers": Volunteer.query.count(),
        "pending_volunteers": Volunteer.query.filter_by(status="PENDING").count(),
        "donations": Donation.query.count(),
        "funds": round(db.session.query(db.func.coalesce(db.func.sum(Donation.amount), 0)).scalar(), 2),
        "messages": ContactMessage.query.filter_by(is_read=False).count(),
        "audits": AuditResult.query.count(),
    }
    recent_apps = Volunteer.query.order_by(Volunteer.applied_at.desc()).limit(5).all()
    recent_msgs = ContactMessage.query.order_by(ContactMessage.created_at.desc()).limit(5).all()
    return render_template("admin/dashboard.html", stats=stats,
                           recent_apps=recent_apps, recent_msgs=recent_msgs)


# ── Volunteers ─────────────────────────────────────────────────────
@admin_bp.route("/volunteers")
@admin_required
def volunteers():
    status = request.args.get("status", "")
    query = Volunteer.query
    if status:
        query = query.filter_by(status=status)
    vlist = query.order_by(Volunteer.applied_at.desc()).all()
    return render_template("admin/volunteers.html", volunteers=vlist)


@admin_bp.route("/volunteers/<int:vid>/<action>", methods=["POST"])
@admin_required
def volunteer_review(vid, action):
    v = db.get_or_404(Volunteer, vid)
    if action not in ("approve", "reject"):
        abort(404)
    v.status = "APPROVED" if action == "approve" else "REJECTED"
    v.reviewed_at = db.func.now()
    db.session.commit()
    flash(f"Application {v.application_id} marked {v.status.lower()}.", "success")
    return redirect(url_for("admin.volunteers"))


# ── Projects CRUD ──────────────────────────────────────────────────
@admin_bp.route("/projects")
@admin_required
def projects():
    plist = Project.query.order_by(Project.created_at.desc()).all()
    return render_template("admin/projects.html", projects=plist)


@admin_bp.route("/projects/new", methods=["GET", "POST"])
@admin_required
def project_new():
    if request.method == "POST":
        from app.utils import save_upload
        f = request.form
        image = ""
        if "image" in request.files:
            try:
                image = save_upload(request.files["image"], "projects")
            except ValueError:
                image = ""
        p = Project(
            title=f["title"].strip(), description=f["description"].strip(),
            category=f["category"].strip(), location=f["location"].strip(),
            start_date=f["start_date"], end_date=f.get("end_date") or None,
            status=f.get("status", "ACTIVE"),
            beneficiaries=int(f.get("beneficiaries", 0) or 0),
            objectives=f.get("objectives") or None, activities=f.get("activities") or None,
            image=image or None,
        )
        db.session.add(p)
        db.session.commit()
        flash("Project created.", "success")
        return redirect(url_for("admin.projects"))
    return render_template("admin/project_form.html", project=None)


@admin_bp.route("/projects/<int:pid>/edit", methods=["GET", "POST"])
@admin_required
def project_edit(pid):
    p = db.get_or_404(Project, pid)
    if request.method == "POST":
        f = request.form
        from app.utils import save_upload
        image = p.image
        if "image" in request.files and request.files["image"].filename:
            try:
                image = save_upload(request.files["image"], "projects")
            except ValueError:
                pass
        p.title = f["title"].strip()
        p.description = f["description"].strip()
        p.category = f["category"].strip()
        p.location = f["location"].strip()
        p.start_date = f["start_date"]
        p.end_date = f.get("end_date") or None
        p.status = f.get("status", "ACTIVE")
        p.beneficiaries = int(f.get("beneficiaries", 0) or 0)
        p.objectives = f.get("objectives") or None
        p.activities = f.get("activities") or None
        p.image = image or None
        db.session.commit()
        flash("Project updated.", "success")
        return redirect(url_for("admin.projects"))
    return render_template("admin/project_form.html", project=p)


@admin_bp.route("/projects/<int:pid>/delete", methods=["POST"])
@admin_required
def project_delete(pid):
    p = db.get_or_404(Project, pid)
    db.session.delete(p)
    db.session.commit()
    flash("Project deleted.", "success")
    return redirect(url_for("admin.projects"))


# ── Campaigns CRUD ─────────────────────────────────────────────────
@admin_bp.route("/campaigns")
@admin_required
def campaigns():
    clist = Campaign.query.order_by(Campaign.created_at.desc()).all()
    return render_template("admin/campaigns.html", campaigns=clist)


@admin_bp.route("/campaigns/new", methods=["GET", "POST"])
@admin_required
def campaign_new():
    if request.method == "POST":
        from app.utils import save_upload
        f = request.form
        image = ""
        if "image" in request.files:
            try:
                image = save_upload(request.files["image"], "campaigns")
            except ValueError:
                image = ""
        c = Campaign(
            title=f["title"].strip(), description=f["description"].strip(),
            category=f["category"].strip(), target_amount=float(f.get("target_amount", 0)),
            start_date=f["start_date"], end_date=f["end_date"],
            status=f.get("status", "ACTIVE"), image=image or None,
        )
        db.session.add(c)
        db.session.commit()
        flash("Campaign created.", "success")
        return redirect(url_for("admin.campaigns"))
    return render_template("admin/campaign_form.html", campaign=None)


@admin_bp.route("/campaigns/<int:cid>/edit", methods=["GET", "POST"])
@admin_required
def campaign_edit(cid):
    c = db.get_or_404(Campaign, cid)
    if request.method == "POST":
        f = request.form
        from app.utils import save_upload
        image = c.image
        if "image" in request.files and request.files["image"].filename:
            try:
                image = save_upload(request.files["image"], "campaigns")
            except ValueError:
                pass
        c.title = f["title"].strip()
        c.description = f["description"].strip()
        c.category = f["category"].strip()
        c.target_amount = float(f.get("target_amount", 0))
        c.start_date = f["start_date"]
        c.end_date = f["end_date"]
        c.status = f.get("status", "ACTIVE")
        c.image = image or None
        db.session.commit()
        flash("Campaign updated.", "success")
        return redirect(url_for("admin.campaigns"))
    return render_template("admin/campaign_form.html", campaign=c)


@admin_bp.route("/campaigns/<int:cid>/delete", methods=["POST"])
@admin_required
def campaign_delete(cid):
    c = db.get_or_404(Campaign, cid)
    db.session.delete(c)
    db.session.commit()
    flash("Campaign deleted.", "success")
    return redirect(url_for("admin.campaigns"))


# ── Events CRUD ────────────────────────────────────────────────────
@admin_bp.route("/events")
@admin_required
def events():
    elist = Event.query.order_by(Event.event_date.asc()).all()
    return render_template("admin/events.html", events=elist)


@admin_bp.route("/events/new", methods=["GET", "POST"])
@admin_required
def event_new():
    if request.method == "POST":
        from app.utils import save_upload
        f = request.form
        image = ""
        if "image" in request.files:
            try:
                image = save_upload(request.files["image"], "events")
            except ValueError:
                image = ""
        e = Event(
            title=f["title"].strip(), description=f["description"].strip(),
            location=f["location"].strip(), event_date=f["event_date"],
            start_time=f.get("start_time") or None,
            capacity=int(f.get("capacity", 0) or 0),
            status=f.get("status", "OPEN"), image=image or None,
        )
        db.session.add(e)
        db.session.commit()
        flash("Event created.", "success")
        return redirect(url_for("admin.events"))
    return render_template("admin/event_form.html", event=None)


@admin_bp.route("/events/<int:eid>/edit", methods=["GET", "POST"])
@admin_required
def event_edit(eid):
    e = db.get_or_404(Event, eid)
    if request.method == "POST":
        f = request.form
        from app.utils import save_upload
        image = e.image
        if "image" in request.files and request.files["image"].filename:
            try:
                image = save_upload(request.files["image"], "events")
            except ValueError:
                pass
        e.title = f["title"].strip()
        e.description = f["description"].strip()
        e.location = f["location"].strip()
        e.event_date = f["event_date"]
        e.start_time = f.get("start_time") or None
        e.capacity = int(f.get("capacity", 0) or 0)
        e.status = f.get("status", "OPEN")
        e.image = image or None
        db.session.commit()
        flash("Event updated.", "success")
        return redirect(url_for("admin.events"))
    return render_template("admin/event_form.html", event=e)


@admin_bp.route("/events/<int:eid>/delete", methods=["POST"])
@admin_required
def event_delete(eid):
    e = db.get_or_404(Event, eid)
    db.session.delete(e)
    db.session.commit()
    flash("Event deleted.", "success")
    return redirect(url_for("admin.events"))


# ── Donations / messages / gallery / impact ────────────────────────
@admin_bp.route("/donations")
@admin_required
def donations():
    dlist = Donation.query.order_by(Donation.created_at.desc()).all()
    return render_template("admin/donations.html", donations=dlist)


@admin_bp.route("/messages")
@admin_required
def messages():
    mlist = ContactMessage.query.order_by(ContactMessage.created_at.desc()).all()
    return render_template("admin/messages.html", messages=mlist)


@admin_bp.route("/messages/<int:mid>/toggle", methods=["POST"])
@admin_required
def message_toggle(mid):
    m = db.get_or_404(ContactMessage, mid)
    m.is_read = not m.is_read
    db.session.commit()
    return redirect(url_for("admin.messages"))


@admin_bp.route("/messages/<int:mid>/delete", methods=["POST"])
@admin_required
def message_delete(mid):
    m = db.get_or_404(ContactMessage, mid)
    db.session.delete(m)
    db.session.commit()
    flash("Message deleted.", "success")
    return redirect(url_for("admin.messages"))


@admin_bp.route("/users")
@admin_required
def users():
    ulist = User.query.order_by(User.created_at.desc()).all()
    return render_template("admin/users.html", users=ulist)


@admin_bp.route("/users/<int:uid>/toggle", methods=["POST"])
@admin_required
def user_toggle(uid):
    u = db.get_or_404(User, uid)
    if u.id == current_user.id:
        flash("You cannot disable your own account.", "warning")
        return redirect(url_for("admin.users"))
    u.is_active = not u.is_active
    db.session.commit()
    flash(f"User {'enabled' if u.is_active else 'disabled'}.", "success")
    return redirect(url_for("admin.users"))


@admin_bp.route("/gallery", methods=["GET", "POST"])
@admin_required
def gallery():
    if request.method == "POST":
        from app.utils import save_upload
        f = request.form
        try:
            image = save_upload(request.files["image"], "gallery")
        except ValueError:
            flash("Invalid file type.", "error")
            return redirect(url_for("admin.gallery"))
        project_id = f.get("project_id") or None
        db.session.add(Gallery(image=image, caption=f.get("caption") or None,
                               category=f["category"].strip(),
                               project_id=int(project_id) if project_id else None))
        db.session.commit()
        flash("Gallery image added.", "success")
        return redirect(url_for("admin.gallery"))
    items = Gallery.query.order_by(Gallery.uploaded_at.desc()).all()
    projects = Project.query.all()
    return render_template("admin/gallery.html", items=items, projects=projects)


@admin_bp.route("/gallery/<int:gid>/delete", methods=["POST"])
@admin_required
def gallery_delete(gid):
    g = db.get_or_404(Gallery, gid)
    db.session.delete(g)
    db.session.commit()
    flash("Gallery image deleted.", "success")
    return redirect(url_for("admin.gallery"))


@admin_bp.route("/impact", methods=["GET", "POST"])
@admin_required
def impact():
    if request.method == "POST":
        f = request.form
        db.session.add(ImpactMetric(
            year=int(f["year"]), month=int(f.get("month") or 0) or None,
            beneficiaries=int(f.get("beneficiaries", 0) or 0),
            volunteers=int(f.get("volunteers", 0) or 0),
            projects=int(f.get("projects", 0) or 0),
            funds_raised=float(f.get("funds_raised", 0) or 0),
        ))
        db.session.commit()
        flash("Impact metric added.", "success")
        return redirect(url_for("admin.impact"))
    metrics = ImpactMetric.query.order_by(ImpactMetric.year.desc(), ImpactMetric.month).all()
    return render_template("admin/impact.html", metrics=metrics,
                           current_year=datetime.utcnow().year)


@admin_bp.route("/impact/<int:mid>/delete", methods=["POST"])
@admin_required
def impact_delete(mid):
    m = db.get_or_404(ImpactMetric, mid)
    db.session.delete(m)
    db.session.commit()
    flash("Metric deleted.", "success")
    return redirect(url_for("admin.impact"))


# ── Audits ─────────────────────────────────────────────────────────
@admin_bp.route("/audits", methods=["GET", "POST"])
@admin_required
def audits():
    if request.method == "POST":
        try:
            from app.services.audit import run_audit
            result = run_audit()
            flash(f"Audit complete — {result.grade} ({result.overall_score}/100). "
                  f"Found {len(result.issues)} issue(s).", "success")
        except Exception:
            flash("Audit could not reach the site. Make sure the server is running.", "error")
        return redirect(url_for("admin.audits"))
    results = AuditResult.query.order_by(AuditResult.created_at.desc()).all()
    return render_template("admin/audits.html", results=results)
