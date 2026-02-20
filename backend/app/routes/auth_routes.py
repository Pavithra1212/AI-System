from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.schemas import LoginRequest, LoginResponse, UserOut
from app.auth import verify_password, create_access_token

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login", response_model=LoginResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    """Authenticate user and return JWT token."""
    user = db.query(User).filter(User.username == request.username).first()
    if not user or not verify_password(request.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token(data={"sub": user.username, "role": user.role})
    return LoginResponse(
        access_token=token,
        user=UserOut(
            id=user.id,
            username=user.username,
            role=user.role,
            department=user.department,
            section=user.section,
        ),
    )
