from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session, joinedload
from app.models import Report, Match, User


def get_all_reports(
    db: Session,
    section: str = None,
    time_filter: str = None,
    status: str = None,
    report_type: str = None,
) -> list:
    """Get all reports with optional filters. Eagerly loads user to avoid N+1."""
    query = (
        db.query(Report)
        .options(joinedload(Report.user))
        .join(User, Report.user_id == User.id)
    )

    if section:
        query = query.filter(User.section == section)

    if status:
        query = query.filter(Report.status == status)

    if report_type:
        query = query.filter(Report.type == report_type)

    if time_filter:
        now = datetime.now(timezone.utc)
        start = None
        end = now

        if time_filter == "today":
            start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        elif time_filter == "this_week":
            start = now - timedelta(days=now.weekday())
            start = start.replace(hour=0, minute=0, second=0, microsecond=0)
        elif time_filter == "last_week":
            start = now - timedelta(days=now.weekday() + 7)
            start = start.replace(hour=0, minute=0, second=0, microsecond=0)
            end = now - timedelta(days=now.weekday())
            end = end.replace(hour=0, minute=0, second=0, microsecond=0)
        elif time_filter == "this_month":
            start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        elif time_filter == "last_month":
            first_this_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            end = first_this_month
            start = (first_this_month - timedelta(days=1)).replace(day=1)
        elif time_filter == "this_year":
            start = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        elif time_filter == "last_year":
            start = now.replace(year=now.year - 1, month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
            end = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)

        if start:
            query = query.filter(Report.created_at >= start)
        query = query.filter(Report.created_at <= end)

    return query.order_by(Report.created_at.desc()).all()


def get_all_matches(db: Session) -> list:
    """Get all matches with related reports eagerly loaded."""
    return (
        db.query(Match)
        .options(
            joinedload(Match.lost_report).joinedload(Report.user),
            joinedload(Match.found_report).joinedload(Report.user),
        )
        .order_by(Match.combined_score.desc())
        .all()
    )


def update_report_status(db: Session, report_id: int, new_status: str) -> Report:
    """Update the status of a report."""
    valid_transitions = {
        "pending": ["match_found"],
        "match_found": ["closed"],
    }

    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        return None

    allowed = valid_transitions.get(report.status, [])
    if new_status not in allowed:
        raise ValueError(f"Cannot transition from '{report.status}' to '{new_status}'")

    report.status = new_status
    db.commit()
    db.refresh(report)
    return report
