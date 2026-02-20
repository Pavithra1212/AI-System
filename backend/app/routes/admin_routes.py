from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.auth import require_admin
from app.schemas import ReportOut, MatchOut, StatusUpdate
from app.services.admin_service import get_all_reports, get_all_matches, update_report_status

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.get("/reports", response_model=list[ReportOut])
def admin_reports(
    section: str = Query(None),
    time_filter: str = Query(None),
    status: str = Query(None),
    report_type: str = Query(None),
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """Get all reports with optional filters (admin only)."""
    reports = get_all_reports(db, section, time_filter, status, report_type)
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
            username=r.user.username if r.user else None,
            section=r.user.section if r.user else None,
        ))
    return result


@router.get("/matches", response_model=list[MatchOut])
def admin_matches(
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """Get all AI matches with scores (admin only)."""
    matches = get_all_matches(db)
    result = []
    for m in matches:
        lost_r = m.lost_report
        found_r = m.found_report
        result.append(MatchOut(
            id=m.id,
            lost_report_id=m.lost_report_id,
            found_report_id=m.found_report_id,
            image_similarity=m.image_similarity,
            text_similarity=m.text_similarity,
            combined_score=m.combined_score,
            created_at=m.created_at,
            lost_report=ReportOut(
                id=lost_r.id,
                user_id=lost_r.user_id,
                type=lost_r.type,
                item_name=lost_r.item_name,
                category=lost_r.category,
                description=lost_r.description,
                block=lost_r.block,
                floor=lost_r.floor,
                specific_location=lost_r.specific_location,
                date_reported=lost_r.date_reported,
                image_path=lost_r.image_path,
                status=lost_r.status,
                created_at=lost_r.created_at,
                username=lost_r.user.username if lost_r.user else None,
                section=lost_r.user.section if lost_r.user else None,
            ) if lost_r else None,
            found_report=ReportOut(
                id=found_r.id,
                user_id=found_r.user_id,
                type=found_r.type,
                item_name=found_r.item_name,
                category=found_r.category,
                description=found_r.description,
                block=found_r.block,
                floor=found_r.floor,
                specific_location=found_r.specific_location,
                date_reported=found_r.date_reported,
                image_path=found_r.image_path,
                status=found_r.status,
                created_at=found_r.created_at,
                username=found_r.user.username if found_r.user else None,
                section=found_r.user.section if found_r.user else None,
            ) if found_r else None,
        ))
    return result


@router.patch("/reports/{report_id}/status")
def change_status(
    report_id: int,
    body: StatusUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """Update report status (admin only). Valid: pending→match_found→closed."""
    try:
        report = update_report_status(db, report_id, body.status)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return {"message": "Status updated", "new_status": report.status}
