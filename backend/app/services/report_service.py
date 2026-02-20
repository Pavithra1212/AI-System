import uuid
import logging
from pathlib import Path
from sqlalchemy.orm import Session
from fastapi import UploadFile, HTTPException
from app.models import Report, User
from app.config import UPLOAD_DIR, MAX_UPLOAD_SIZE, ALLOWED_EXTENSIONS

logger = logging.getLogger(__name__)


def validate_upload(file: UploadFile) -> None:
    """Validate uploaded file size, extension and MIME type."""
    # Validate extension
    ext = Path(file.filename).suffix.lower() if file.filename else ""
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File type '{ext}' not allowed. Accepted: {', '.join(sorted(ALLOWED_EXTENSIONS))}",
        )

    # Validate MIME type
    if file.content_type and not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Only image files are accepted")


def save_upload(file: UploadFile) -> str:
    """Save uploaded file and return the relative path."""
    ext = Path(file.filename).suffix.lower() if file.filename else ".jpg"
    filename = f"{uuid.uuid4().hex}{ext}"
    dest = UPLOAD_DIR / filename

    # Read and validate size
    content = file.file.read()
    if len(content) > MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size: {MAX_UPLOAD_SIZE // (1024 * 1024)}MB",
        )

    with open(dest, "wb") as buffer:
        buffer.write(content)

    logger.info("Saved upload: %s (%d bytes)", filename, len(content))
    return filename


def create_report(db: Session, user: User, data: dict, image_file: UploadFile = None) -> Report:
    """Create a new report with optional image upload."""
    image_path = None
    if image_file and image_file.filename:
        validate_upload(image_file)
        image_path = save_upload(image_file)

    report = Report(
        user_id=user.id,
        type=data["type"],
        item_name=data["item_name"],
        category=data["category"],
        description=data["description"],
        block=data["block"],
        floor=data.get("floor"),
        specific_location=data.get("specific_location"),
        date_reported=data["date_reported"],
        image_path=image_path,
        status="pending",
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    return report


def get_user_reports(db: Session, user_id: int) -> list:
    """Get all reports for a specific user."""
    return db.query(Report).filter(Report.user_id == user_id).order_by(Report.created_at.desc()).all()
