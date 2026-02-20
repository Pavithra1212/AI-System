from sqlalchemy.orm import Session
from app.models import User
from app.auth import hash_password


def get_section(roll_number: str) -> str:
    """Determine section based on roll number suffix."""
    try:
        num = int(roll_number[-3:])
    except (ValueError, IndexError):
        return "IT-A"

    if num <= 149:
        return "IT-A"
    elif num <= 299:
        return "IT-B"
    else:
        return "IT-C"


PREDEFINED_USERS = [
    {"username": "727625BIT116", "password": "MCET12345", "role": "student", "department": "IT", "section": "IT-B"},
    {"username": "727625BIT120", "password": "MCET12345", "role": "student", "department": "IT", "section": "IT-B"},
    {"username": "727625BIT280", "password": "MCET12345", "role": "student", "department": "IT", "section": "IT-B"},
    {"username": "727625BIT390", "password": "MCET12345", "role": "student", "department": "IT", "section": "IT-B"},
    {"username": "ADMINMCET", "password": "ADMIN12345", "role": "admin", "department": None, "section": None},
]


def seed_users(db: Session):
    """Seed predefined users if they don't already exist."""
    for user_data in PREDEFINED_USERS:
        existing = db.query(User).filter(User.username == user_data["username"]).first()
        if existing:
            # Update section if it has changed
            new_section = user_data.get("section")
            if new_section and existing.section != new_section:
                existing.section = new_section
            continue

        # Use explicit section from user_data, fallback to auto-detect
        section = user_data.get("section")
        if not section and user_data["role"] == "student":
            section = get_section(user_data["username"])

        user = User(
            username=user_data["username"],
            password_hash=hash_password(user_data["password"]),
            role=user_data["role"],
            department=user_data["department"],
            section=section,
        )
        db.add(user)

    db.commit()
    print("✅ Users seeded successfully.")
