"""Tasks router - CRUD endpoints for task management."""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import TaskCreate, TaskUpdate, TaskResponse, TaskListResponse, DashboardStats
from app.services.task_service import TaskService

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.get("", response_model=TaskListResponse)
def list_tasks(
    status: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    due_date: Optional[str] = Query(None),
    sort_by: str = Query("created_at"),
    sort_dir: str = Query("desc"),
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    """Get tasks with optional filtering, sorting, and pagination."""
    result = TaskService.get_tasks(
        db,
        status=status,
        priority=priority,
        category=category,
        search=search,
        due_date=due_date,
        sort_by=sort_by,
        sort_dir=sort_dir,
        page=page,
        per_page=per_page,
    )
    return TaskListResponse(
        tasks=[_task_to_response(t) for t in result["tasks"]],
        total=result["total"],
        page=result["page"],
        per_page=result["per_page"],
    )


@router.post("", response_model=TaskResponse, status_code=201)
def create_task(data: TaskCreate, db: Session = Depends(get_db)):
    """Create a new task."""
    task = TaskService.create_task(db, data)
    return _task_to_response(task)


@router.get("/dashboard", response_model=DashboardStats)
def get_dashboard(
    timezone: str = Query("Asia/Kolkata"),
    db: Session = Depends(get_db),
):
    """Get dashboard statistics."""
    data = TaskService.get_dashboard_data(db, timezone=timezone)
    return DashboardStats(**data)


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(task_id: int, db: Session = Depends(get_db)):
    """Get a single task by ID."""
    task = TaskService.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    return _task_to_response(task)


@router.patch("/{task_id}", response_model=TaskResponse)
def update_task(task_id: int, data: TaskUpdate, db: Session = Depends(get_db)):
    """Partially update a task."""
    task = TaskService.update_task(db, task_id, data)
    if not task:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    return _task_to_response(task)


@router.patch("/{task_id}/complete", response_model=TaskResponse)
def complete_task(task_id: int, db: Session = Depends(get_db)):
    """Mark a task as completed."""
    task = TaskService.complete_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    return _task_to_response(task)


@router.patch("/{task_id}/reopen", response_model=TaskResponse)
def reopen_task(task_id: int, db: Session = Depends(get_db)):
    """Reopen a completed task."""
    task = TaskService.reopen_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    return _task_to_response(task)


@router.delete("/{task_id}", status_code=204)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    """Delete a task."""
    deleted = TaskService.delete_task(db, task_id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    return None


@router.post("/demo/seed", status_code=201)
def seed_demo_data(
    timezone: str = Query("Asia/Kolkata"),
    db: Session = Depends(get_db),
):
    """Seed the database with demo tasks."""
    tasks = TaskService.seed_demo_data(db, timezone=timezone)
    return {"message": f"Created {len(tasks)} demo tasks", "count": len(tasks)}


@router.delete("/demo/clear", status_code=200)
def clear_demo_data(db: Session = Depends(get_db)):
    """Delete all demo tasks."""
    count = TaskService.clear_demo_data(db)
    return {"message": f"Deleted {count} demo tasks", "count": count}


def _task_to_response(task) -> TaskResponse:
    d = task.to_dict()
    return TaskResponse(**d)
