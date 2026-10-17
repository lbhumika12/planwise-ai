"""Settings router - Application settings management."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import SettingsResponse, SettingsUpdate
from app.models import AppSettings
from app.services.ai_service import get_ai_status
from datetime import datetime

router = APIRouter(prefix="/settings", tags=["Settings"])


def get_or_create_settings(db: Session) -> AppSettings:
    """Get settings or create defaults."""
    settings_obj = db.query(AppSettings).first()
    if not settings_obj:
        settings_obj = AppSettings(
            preferred_name="",
            timezone="Asia/Kolkata",
            default_start_time="09:00",
            default_end_time="21:00",
            default_break_duration=30,
            theme="light",
        )
        db.add(settings_obj)
        db.commit()
        db.refresh(settings_obj)
    return settings_obj


@router.get("", response_model=SettingsResponse)
def get_settings(db: Session = Depends(get_db)):
    """Get application settings."""
    s = get_or_create_settings(db)
    return SettingsResponse(**s.to_dict())


@router.patch("", response_model=SettingsResponse)
def update_settings(data: SettingsUpdate, db: Session = Depends(get_db)):
    """Update application settings."""
    s = get_or_create_settings(db)
    update_data = data.model_dump(exclude_none=True)
    for key, value in update_data.items():
        setattr(s, key, value)
    s.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(s)
    return SettingsResponse(**s.to_dict())


@router.get("/ai-status")
def get_ai_status_endpoint():
    """Return AI configuration status (no secrets)."""
    return get_ai_status()
