"""Seed script – creates the admin account and demo content.

Usage:
    python seed.py
"""
import os
import random
import sys
from datetime import date, timedelta

from app import create_app
from app.extensions import db
from app.models import (
    User, Project, Volunteer, Campaign, Donation, Event, Gallery,
    ImpactMetric, ContactMessage,
)

app = create_app()

# ── Demo data ────────────────────────────────────────────────────────

PROJECTS = [
    {
        "title": "Digital Literacy for Rural Schools",
        "description": "Equipping three rural schools with computer labs and digital literacy training for 300+ students, bridging the digital divide in underserved communities.",
        "category": "Education",
        "location": "Maharashtra, India",
        "start_date": date(2025, 1, 15),
        "end_date": date(2025, 9, 30),
        "status": "ACTIVE",
        "beneficiaries": 312,
        "objectives": "Provide 30 computers; train 15 teachers; reach 300 students with foundational digital skills.",
        "activities": "Set up computer labs; conduct weekly workshops; organise coding camps; distribute learning kits.",
        "image": None,
    },
    {
        "title": "Clean Water Initiative",
        "description": "Installing community water purification systems in five villages, providing safe drinking water to over 2,000 residents and reducing waterborne disease.",
        "category": "Water & Sanitation",
        "location": "Rajasthan, India",
        "start_date": date(2024, 6, 1),
        "end_date": date(2025, 3, 31),
        "status": "COMPLETED",
        "beneficiaries": 2100,
        "objectives": "Install 5 purification units; train local caretakers; achieve 90% reduction in waterborne illness reports.",
        "activities": "Site surveys; installation; community training; health-impact monitoring.",
        "image": None,
    },
    {
        "title": "Green Urban Forests",
        "description": "Creating urban micro-forests across the city to improve air quality, support biodiversity, and build climate resilience through community planting drives.",
        "category": "Environment",
        "location": "Bengaluru, India",
        "start_date": date(2025, 4, 1),
        "end_date": None,
        "status": "PLANNED",
        "beneficiaries": 0,
        "objectives": "Plant 10,000 native trees; engage 500 volunteers; establish 4 micro-forest sites.",
        "activities": "Site preparation; sapling drives; maintenance schedules; eco-education workshops.",
        "image": None,
    },
    {
        "title": "Vocational Skills for Youth",
        "description": "Six-month vocational training in tailoring, electronics, and hospitality for unemployed youth, improving employability and income for 180 participants.",
        "category": "Livelihood",
        "location": "Uttar Pradesh, India",
        "start_date": date(2025, 2, 1),
        "end_date": date(2025, 8, 31),
        "status": "ACTIVE",
        "beneficiaries": 180,
        "objectives": "Certify 180 youth; achieve 70% job placement; establish partnerships with 12 local employers.",
        "activities": "Skill modules; industry mentorships; placement drives; follow-up support.",
        "image": None,
    },
]

CAMPAIGNS = [
    {
        "title": "Books for Every Child",
        "description": "Help us distribute 5,000 storybooks to children in under-resourced schools and set up 20 mini-libraries in community centres.",
        "category": "Education",
        "target_amount": 250000,
        "start_date": date(2025, 1, 1),
        "end_date": date(2025, 6, 30),
        "status": "ACTIVE",
        "image": None,
    },
    {
        "title": "Solar Power for Community Clinics",
        "description": "Funding solar installations for three community health clinics so vital services never lose power.",
        "category": "Health",
        "target_amount": 400000,
        "start_date": date(2024, 10, 1),
        "end_date": date(2025, 4, 30),
        "status": "ACTIVE",
        "image": None,
    },
    {
        "title": "Warm Winters Drive",
        "description": "Collecting blankets, warm clothes and heaters for families in mountain regions during harsh winters.",
        "category": "Relief",
        "target_amount": 150000,
        "start_date": date(2024, 11, 1),
        "end_date": date(2025, 2, 28),
        "status": "CLOSED",
        "image": None,
    },
    {
        "title": "Women's Entrepreneurship Fund",
        "description": "Seed grants and mentorship for women-led micro-enterprises in semi-urban areas to build financial independence.",
        "category": "Livelihood",
        "target_amount": 500000,
        "start_date": date(2025, 3, 1),
        "end_date": date(2025, 9, 30),
        "status": "ACTIVE",
        "image": None,
    },
]

EVENTS = [
    {
        "title": "River Clean-up Drive",
        "description": "Join volunteers to clean a 2 km stretch of the riverbank. Gloves, bags and refreshments provided.",
        "location": "Riverside Park",
        "event_date": date(2025, 5, 18),
        "start_time": "07:00 AM",
        "capacity": 100,
        "status": "OPEN",
        "image": None,
    },
    {
        "title": "Community Health Camp",
        "description": "Free health check-ups, blood pressure screening, and nutrition counselling for residents.",
        "location": "Community Hall",
        "event_date": date(2025, 6, 10),
        "start_time": "09:00 AM",
        "capacity": 150,
        "status": "OPEN",
        "image": None,
    },
    {
        "title": "Tree Plantation Weekend",
        "description": "Family-friendly planting event to grow the urban forest. Saplings and tools provided.",
        "location": "City Green Belt",
        "event_date": date(2025, 4, 12),
        "start_time": "08:00 AM",
        "capacity": 80,
        "status": "FULL",
        "image": None,
    },
    {
        "title": "Youth Coding Workshop",
        "description": "Hands-on introduction to programming for teens using free, open-source tools.",
        "location": "Innovation Centre",
        "event_date": date(2025, 5, 25),
        "start_time": "10:00 AM",
        "capacity": 40,
        "status": "OPEN",
        "image": None,
    },
]

GALLERY = [
    {"image": "https://images.unsplash.com/photo-1522202176988-66273c2fd55f?w=800", "caption": "Students at the new computer lab", "category": "Education"},
    {"image": "https://images.unsplash.com/photo-1523362628745-0c100150b504?w=800", "caption": "Water purification unit installation", "category": "Water & Sanitation"},
    {"image": "https://images.unsplash.com/photo-1559027615-cd4628902d4a?w=800", "caption": "Volunteers at the river clean-up", "category": "Environment"},
    {"image": "https://images.unsplash.com/photo-1523240795612-9a054b0db644?w=800", "caption": "Vocational training in session", "category": "Livelihood"},
    {"image": "https://images.unsplash.com/photo-1576091160399-112ba8d25d1d?w=800", "caption": "Health camp volunteers", "category": "Health"},
    {"image": "https://images.unsplash.com/photo-1481627834876-b7833e8f5570?w=800", "caption": "Community library opening", "category": "Education"},
]

METRICS = [
    # (year, month, beneficiaries, volunteers, projects, funds)
    (2023, 3, 1200, 80, 4, 150000),
    (2023, 6, 1800, 110, 5, 220000),
    (2023, 9, 2400, 140, 6, 310000),
    (2023, 12, 3000, 170, 7, 380000),
    (2024, 3, 3600, 200, 8, 460000),
    (2024, 6, 4300, 240, 9, 550000),
    (2024, 9, 5100, 280, 10, 640000),
    (2024, 12, 6100, 320, 11, 780000),
    (2025, 3, 7200, 380, 12, 940000),
    (2025, 6, 8600, 450, 13, 1150000),
    (2025, 9, 10100, 520, 14, 1380000),
    (2025, 12, 11800, 600, 15, 1650000),
]

VOLUNTEER = {
    "application_id": "VOL-2025-0001",
    "full_name": "Aarav Sharma",
    "email": "aarav@example.com",
    "phone": "+91 98765 43210",
    "city": "Mumbai",
    "skills": "Teaching, Event management, First aid",
    "area_of_interest": "Education",
    "availability": "Weekends",
    "experience": "2 years of teaching at a local NGO.",
    "reason": "I want to give back to my community through education.",
    "status": "APPROVED",
}


def seed():
    with app.app_context():
        db.create_all()

        # Admin account (idempotent)
        admin = User.query.filter_by(email="admin@impactbridge.ai").first()
        if not admin:
            admin = User(full_name="ImpactBridge Admin", email="admin@impactbridge.ai", role="ADMIN")
            admin.set_password("Admin@123")
            db.session.add(admin)
            print("Created admin: admin@impactbridge.ai / Admin@123")

        # Demo user
        demo = User.query.filter_by(email="demo@impactbridge.ai").first()
        if not demo:
            demo = User(full_name="Demo Volunteer", email="demo@impactbridge.ai", role="USER",
                        phone="+91 90000 00000", city="Pune")
            demo.set_password("Demo@123")
            db.session.add(demo)
            print("Created demo user: demo@impactbridge.ai / Demo@123")

        # Projects
        if Project.query.count() == 0:
            for p in PROJECTS:
                db.session.add(Project(**p))
            print(f"Seeded {len(PROJECTS)} projects")

        # Campaigns
        if Campaign.query.count() == 0:
            for c in CAMPAIGNS:
                db.session.add(Campaign(**c))
            print(f"Seeded {len(CAMPAIGNS)} campaigns")

        # Events
        if Event.query.count() == 0:
            for e in EVENTS:
                db.session.add(Event(**e))
            print(f"Seeded {len(EVENTS)} events")

        # Gallery
        if Gallery.query.count() == 0:
            for g in GALLERY:
                db.session.add(Gallery(**g))
            print(f"Seeded {len(GALLERY)} gallery items")

        # Impact metrics
        if ImpactMetric.query.count() == 0:
            for year, month, benef, vol, proj, funds in METRICS:
                db.session.add(ImpactMetric(year=year, month=month, beneficiaries=benef,
                                            volunteers=vol, projects=proj, funds_raised=funds))
            print(f"Seeded {len(METRICS)} impact metrics")

        # Volunteer application
        if Volunteer.query.count() == 0:
            vol = Volunteer(**VOLUNTEER, user_id=demo.id if demo else None)
            db.session.add(vol)
            print("Seeded 1 volunteer application")

        # Demo donations against active campaigns
        if Donation.query.count() == 0:
            campaigns = Campaign.query.filter_by(status="ACTIVE").all()
            donors = [
                ("Riya Patel", "riya@example.com", 2500),
                ("Karan Mehta", "karan@example.com", 5000),
                ("Sneha Iyer", "sneha@example.com", 1500),
                ("Vikram Singh", "vikram@example.com", 10000),
                ("Ananya Gupta", "ananya@example.com", 3000),
                ("Rohit Nair", "rohit@example.com", 700),
            ]
            for i, (name, email, amount) in enumerate(donors):
                if campaigns:
                    camp = campaigns[i % len(campaigns)]
                    db.session.add(Donation(
                        transaction_id=f"TXN-DEMO-{i+1:04d}",
                        user_id=demo.id if i % 3 == 0 else None,
                        campaign_id=camp.id,
                        donor_name=name,
                        donor_email=email,
                        amount=amount,
                        message="Great initiative, keep it up!" if i % 2 == 0 else None,
                        demo=True,
                    ))
            print("Seeded demo donations")

        db.session.commit()
        print("\n✔ Seed complete!")
        print("  Admin login : admin@impactbridge.ai / Admin@123")
        print("  Demo login  : demo@impactbridge.ai / Demo@123")


if __name__ == "__main__":
    seed()