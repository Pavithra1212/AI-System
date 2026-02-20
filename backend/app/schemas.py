from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime


# ── Auth ──────────────────────────────────────────
class LoginRequest(BaseModel):
    username: str = Field(..., min_length=1, max_length=50)
    password: str = Field(..., min_length=1, max_length=128)


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: "UserOut"


class UserOut(BaseModel):
    id: int
    username: str
    role: str
    department: Optional[str] = None
    section: Optional[str] = None

    class Config:
        from_attributes = True


# ── Report ────────────────────────────────────────
class ReportCreate(BaseModel):
    type: Literal["lost", "found"]
    item_name: str = Field(..., min_length=1, max_length=100)
    category: str = Field(..., min_length=1, max_length=50)
    description: str = Field(..., min_length=1, max_length=2000)
    block: str = Field(..., min_length=1, max_length=50)
    floor: Optional[str] = Field(None, max_length=50)
    specific_location: Optional[str] = Field(None, max_length=100)
    date_reported: str = Field(..., max_length=20)


class ReportOut(BaseModel):
    id: int
    user_id: int
    type: str
    item_name: str
    category: str
    description: str
    block: str
    floor: Optional[str] = None
    specific_location: Optional[str] = None
    date_reported: str
    image_path: Optional[str] = None
    status: str
    created_at: Optional[datetime] = None
    username: Optional[str] = None
    section: Optional[str] = None

    class Config:
        from_attributes = True


# ── Match ─────────────────────────────────────────
class MatchOut(BaseModel):
    id: int
    lost_report_id: int
    found_report_id: int
    image_similarity: float
    text_similarity: float
    combined_score: float
    created_at: Optional[datetime] = None
    lost_report: Optional[ReportOut] = None
    found_report: Optional[ReportOut] = None

    class Config:
        from_attributes = True


# ── Admin ─────────────────────────────────────────
class StatusUpdate(BaseModel):
    status: Literal["pending", "match_found", "closed"]


# Rebuild forward refs
LoginResponse.model_rebuild()
