import logging
from sqlalchemy.orm import Session
from app.models import Report, Match
from app.utils.ai_utils import image_similarity, text_similarity, combined_score
from app.config import UPLOAD_DIR, MATCH_THRESHOLD

logger = logging.getLogger(__name__)


def run_matching(db: Session, new_report: Report) -> list:
    """
    Compare a new report against all opposite-type pending reports.
    Returns list of matches above threshold.
    """
    # Determine opposite type
    opposite_type = "found" if new_report.type == "lost" else "lost"

    candidates = (
        db.query(Report)
        .filter(Report.type == opposite_type, Report.status == "pending")
        .all()
    )

    high_matches = []

    for candidate in candidates:
        try:
            # Text similarity: combine item_name, category, description
            new_text = f"{new_report.item_name} {new_report.category} {new_report.description}"
            cand_text = f"{candidate.item_name} {candidate.category} {candidate.description}"
            txt_sim = text_similarity(new_text, cand_text)

            # Image similarity
            img_sim = 0.0
            if new_report.image_path and candidate.image_path:
                new_img = str(UPLOAD_DIR / new_report.image_path)
                cand_img = str(UPLOAD_DIR / candidate.image_path)
                img_sim = image_similarity(new_img, cand_img)

            score = combined_score(img_sim, txt_sim)

            # Store all matches (even low ones for admin visibility)
            if score > 0.05:
                # Determine which is lost and which is found
                lost_id = new_report.id if new_report.type == "lost" else candidate.id
                found_id = candidate.id if new_report.type == "lost" else new_report.id

                # Check if match already exists
                existing = (
                    db.query(Match)
                    .filter(Match.lost_report_id == lost_id, Match.found_report_id == found_id)
                    .first()
                )
                if not existing:
                    match = Match(
                        lost_report_id=lost_id,
                        found_report_id=found_id,
                        image_similarity=round(img_sim, 4),
                        text_similarity=round(txt_sim, 4),
                        combined_score=score,
                    )
                    db.add(match)

                    if score >= MATCH_THRESHOLD:
                        high_matches.append(match)
                        logger.info(
                            "High match found: report %d ↔ %d (score=%.2f)",
                            lost_id, found_id, score,
                        )

        except Exception:
            logger.exception(
                "Error matching report %d against candidate %d",
                new_report.id, candidate.id,
            )
            continue

    db.commit()
    return high_matches
