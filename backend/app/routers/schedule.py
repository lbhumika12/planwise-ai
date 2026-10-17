"""Schedule router - Day planning endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import ScheduleRequest, ScheduleResponse, ApplyScheduleRequest
from app.services.scheduling_service import generate_schedule, apply_schedule

router = APIRouter(prefix="/schedule", tags=["Schedule"])


@router.post("/plan", response_model=ScheduleResponse)
def plan_schedule(request: ScheduleRequest, db: Session = Depends(get_db)):
    """Generate a proposed daily schedule without modifying any data."""
    return generate_schedule(db, request)


@router.post("/apply")
def apply_schedule_endpoint(request: ApplyScheduleRequest, db: Session = Depends(get_db)):
    """Apply a proposed schedule — updates task scheduled_start times."""
    result = apply_schedule(db, request.date, request.scheduled_blocks)
    return {
        "message": f"Schedule applied: {result['total_applied']} task(s) updated",
        **result,
    }
