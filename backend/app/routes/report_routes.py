import asyncio
import logging
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.auth import get_current_user
from app.schemas import ReportOut
from app.services.report_service import create_report, get_user_reports
from app.services.matching_service import run_matching
from app.websocket_manager import manager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/reports", tags=["reports"])


@router.post("", response_model=ReportOut)
async def submit_report(
    type: str = Form(...),
    item_name: str = Form(...),
    category: str = Form(...),
    description: str = Form(...),
    block: str = Form(...),
    floor: str = Form(None),
    specific_location: str = Form(None),
    date_reported: str = Form(...),
    image: UploadFile = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Submit a new lost or found report."""
    # Validate report type
    if type not in ("lost", "found"):
        raise HTTPException(status_code=400, detail="Type must be 'lost' or 'found'")

    data = {
        "type": type,
        "item_name": item_name,
        "category": category,
        "description": description,
        "block": block,
        "floor": floor,
        "specific_location": specific_location,
        "date_reported": date_reported,
    }

    # create_report includes file validation (size, type, extension)
    report = await asyncio.to_thread(create_report, db, current_user, data, image)

    # Run AI matching in a thread to avoid blocking the event loop
    try:
        high_matches = await asyncio.to_thread(run_matching, db, report)
    except Exception:
        logger.exception("AI matching failed for report %d", report.id)
        high_matches = []

    # Broadcast to admin dashboard via WebSocket
    await manager.broadcast({
        "event": "new_report",
        "report": {
            "id": report.id,
            "type": report.type,
            "item_name": report.item_name,
            "category": report.category,
            "description": report.description,
            "block": report.block,
            "floor": report.floor,
            "status": report.status,
            "created_at": str(report.created_at),
            "username": current_user.username,
            "section": current_user.section,
            "image_path": report.image_path,
        },
        "high_matches": len(high_matches),
    })

    # Attach user info
    report_out = ReportOut(
        id=report.id,
        user_id=report.user_id,
        type=report.type,
        item_name=report.item_name,
        category=report.category,
        description=report.description,
        block=report.block,
        floor=report.floor,
        specific_location=report.specific_location,
        date_reported=report.date_reported,
        image_path=report.image_path,
        status=report.status,
        created_at=report.created_at,
        username=current_user.username,
        section=current_user.section,
    )
    return report_out


@router.get("/my", response_model=list[ReportOut])
def my_reports(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all reports submitted by the current user."""
    reports = get_user_reports(db, current_user.id)
    result = []
    for r in reports:
        result.append(ReportOut(
            id=r.id,
            user_id=r.user_id,
            type=r.type,
            item_name=r.item_name,
            category=r.category,
            description=r.description,
            block=r.block,
            floor=r.floor,
            specific_location=r.specific_location,
            date_reported=r.date_reported,
            image_path=r.image_path,
            status=r.status,
            created_at=r.created_at,
            username=current_user.username,
            section=current_user.section,
        ))
    return result
