from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Index, Text
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False, default="student")  # student / admin
    department = Column(String(50), nullable=True)
    section = Column(String(20), nullable=True)

    reports = relationship("Report", back_populates="user")


class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    type = Column(String(10), nullable=False)  # lost / found
    item_name = Column(String(100), nullable=False)
    category = Column(String(50), nullable=False)
    description = Column(Text, nullable=False)
    block = Column(String(20), nullable=False)
    floor = Column(String(20), nullable=True)
    specific_location = Column(String(100), nullable=True)
    date_reported = Column(String(20), nullable=False)
    image_path = Column(String(255), nullable=True)
    status = Column(String(20), nullable=False, default="pending")  # pending / match_found / closed
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="reports")
    lost_matches = relationship("Match", foreign_keys="Match.lost_report_id", back_populates="lost_report")
    found_matches = relationship("Match", foreign_keys="Match.found_report_id", back_populates="found_report")

    __table_args__ = (
        Index("ix_reports_created_at", "created_at"),
        Index("ix_reports_status", "status"),
        Index("ix_reports_type", "type"),
    )


class Match(Base):
    __tablename__ = "matches"

    id = Column(Integer, primary_key=True, index=True)
    lost_report_id = Column(Integer, ForeignKey("reports.id"), nullable=False, index=True)
    found_report_id = Column(Integer, ForeignKey("reports.id"), nullable=False, index=True)
    image_similarity = Column(Float, default=0.0)
    text_similarity = Column(Float, default=0.0)
    combined_score = Column(Float, default=0.0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    lost_report = relationship("Report", foreign_keys=[lost_report_id], back_populates="lost_matches")
    found_report = relationship("Report", foreign_keys=[found_report_id], back_populates="found_matches")
