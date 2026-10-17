"""
PlanWise AI - Scheduling Service
Deterministic scheduling algorithm that fits tasks into a time window.
Priority scoring: urgency + deadline proximity + explicit priority.
"""
from datetime import datetime, date, timedelta
from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.orm import Session
from app.models import Task
from app.schemas import ScheduleRequest, ScheduleResponse, ScheduleBlock
from app.services.task_service import TaskService
from app.services.date_service import get_today


PRIORITY_WEIGHT = {"urgent": 4, "high": 3, "medium": 2, "low": 1}


def _score_task(task: Task, today_str: str) -> float:
    """
    Score a task for scheduling priority.
    Higher score = schedule first.
    Factors: priority weight, deadline proximity, overdue status.
    """
    priority_score = PRIORITY_WEIGHT.get(task.priority, 2) * 10

    deadline_score = 0
    if task.due_date:
        try:
            due = datetime.strptime(task.due_date, "%Y-%m-%d").date()
            today = datetime.strptime(today_str, "%Y-%m-%d").date()
            delta = (due - today).days
            if delta < 0:
                deadline_score = 50  # Overdue: highest priority boost
            elif delta == 0:
                deadline_score = 40  # Due today
            elif delta == 1:
                deadline_score = 30  # Due tomorrow
            elif delta <= 3:
                deadline_score = 20
            elif delta <= 7:
                deadline_score = 10
            else:
                deadline_score = max(0, 10 - delta)
        except Exception:
            pass

    in_progress_bonus = 5 if task.status == "in_progress" else 0

    return priority_score + deadline_score + in_progress_bonus


def _time_to_minutes(time_str: str) -> int:
    """Convert HH:MM to minutes from midnight."""
    h, m = map(int, time_str.split(":"))
    return h * 60 + m


def _minutes_to_time(minutes: int) -> str:
    """Convert minutes from midnight to HH:MM."""
    h = minutes // 60
    m = minutes % 60
    return f"{h:02d}:{m:02d}"


def generate_schedule(
    db: Session,
    request: ScheduleRequest,
) -> ScheduleResponse:
    """
    Main scheduling algorithm.
    1. Get eligible tasks
    2. Score and sort them
    3. Fit into time window with breaks
    4. Return scheduled blocks + unscheduled tasks
    """
    today_str = get_today(request.timezone).strftime("%Y-%m-%d")

    # Get schedulable tasks
    tasks = TaskService.get_schedulable_tasks(db, task_ids=request.task_ids)

    # Filter out tasks that are clearly not relevant (completed)
    tasks = [t for t in tasks if t.status != "completed"]

    if not tasks:
        return ScheduleResponse(
            date=request.date,
            scheduled_blocks=[],
            unscheduled_tasks=[],
            warnings=["No schedulable tasks found. Tasks need an estimated duration to be scheduled."],
            total_scheduled_minutes=0,
            available_minutes=0,
            utilization_percent=0.0,
        )

    # Sort by score descending
    tasks.sort(key=lambda t: _score_task(t, today_str), reverse=True)

    start_mins = _time_to_minutes(request.start_time)
    end_mins = _time_to_minutes(request.end_time)
    total_available = end_mins - start_mins

    if total_available <= 0:
        return ScheduleResponse(
            date=request.date,
            scheduled_blocks=[],
            unscheduled_tasks=[t.to_dict() for t in tasks],
            warnings=["End time must be after start time."],
            total_scheduled_minutes=0,
            available_minutes=0,
            utilization_percent=0.0,
        )

    # Plan breaks: one break after every ~2 hours of work
    break_duration = request.break_duration
    scheduled_blocks: List[ScheduleBlock] = []
    unscheduled: List[Task] = []
    warnings: List[str] = []

    current_time = start_mins
    work_since_break = 0
    break_threshold = 120  # minutes of work before a break
    total_scheduled = 0
    tasks_scheduled_count = 0

    for task in tasks:
        duration = task.estimated_duration
        if not duration or duration <= 0:
            unscheduled.append(task)
            warnings.append(f"'{task.title}' has no estimated duration and cannot be scheduled.")
            continue

        # Check if we need a break before scheduling this task
        if break_duration > 0 and work_since_break >= break_threshold:
            current_time += break_duration
            work_since_break = 0

        # Check if task fits
        if current_time + duration > end_mins:
            unscheduled.append(task)
            remaining = end_mins - current_time
            if remaining > 0:
                warnings.append(
                    f"'{task.title}' ({duration}min) doesn't fit in remaining {remaining}min. "
                    f"Consider reducing scope or extending your end time."
                )
            else:
                warnings.append(f"'{task.title}' ({duration}min) could not be scheduled — no time remaining.")
            continue

        # Schedule the task
        block_start = current_time
        block_end = current_time + duration
        reason = _explain_priority(task, today_str, tasks_scheduled_count)

        scheduled_blocks.append(ScheduleBlock(
            task_id=task.id,
            task_title=task.title,
            start_time=_minutes_to_time(block_start),
            end_time=_minutes_to_time(block_end),
            duration_minutes=duration,
            priority=task.priority,
            reason=reason,
        ))

        current_time = block_end
        work_since_break += duration
        total_scheduled += duration
        tasks_scheduled_count += 1

    # Check for overdue tasks that didn't get scheduled
    overdue_unscheduled = [
        t for t in unscheduled
        if t.due_date and t.due_date < today_str
    ]
    if overdue_unscheduled:
        warnings.append(
            f"Warning: {len(overdue_unscheduled)} overdue task(s) could not be scheduled today. "
            f"Consider extending your work window."
        )

    utilization = (total_scheduled / total_available * 100) if total_available > 0 else 0

    return ScheduleResponse(
        date=request.date,
        scheduled_blocks=scheduled_blocks,
        unscheduled_tasks=[t.to_dict() for t in unscheduled],
        warnings=warnings,
        total_scheduled_minutes=total_scheduled,
        available_minutes=total_available,
        utilization_percent=round(utilization, 1),
    )


def _explain_priority(task: Task, today_str: str, position: int) -> str:
    """Generate a human-readable explanation for why this task was prioritized."""
    reasons = []

    if task.priority == "urgent":
        reasons.append("urgent priority")
    elif task.priority == "high":
        reasons.append("high priority")

    if task.due_date:
        try:
            due = datetime.strptime(task.due_date, "%Y-%m-%d").date()
            today = datetime.strptime(today_str, "%Y-%m-%d").date()
            delta = (due - today).days
            if delta < 0:
                reasons.append(f"overdue by {abs(delta)} day{'s' if abs(delta) != 1 else ''}")
            elif delta == 0:
                reasons.append("due today")
            elif delta == 1:
                reasons.append("due tomorrow")
            elif delta <= 3:
                reasons.append(f"due in {delta} days")
        except Exception:
            pass

    if task.status == "in_progress":
        reasons.append("already in progress")

    if position == 0:
        reasons.append("top priority")
    elif position < 3:
        reasons.append(f"#{position + 1} in priority ranking")

    return ", ".join(reasons) if reasons else "scheduled by deadline and priority"


def apply_schedule(db: Session, date_str: str, blocks: List[ScheduleBlock]) -> Dict[str, Any]:
    """
    Apply a proposed schedule by updating tasks with their scheduled_start times.
    Returns a summary of applied changes.
    """
    applied = []
    failed = []

    for block in blocks:
        task = TaskService.get_task(db, block.task_id)
        if not task:
            failed.append({"task_id": block.task_id, "reason": "Task not found"})
            continue

        if task.status == "completed":
            failed.append({"task_id": block.task_id, "reason": f"'{task.title}' is already completed"})
            continue

        # Store scheduled_start as "YYYY-MM-DD HH:MM"
        task.scheduled_start = f"{date_str} {block.start_time}"
        task.status = "in_progress" if task.status == "todo" else task.status
        task.updated_at = datetime.utcnow()
        applied.append({"task_id": task.id, "title": task.title, "scheduled_start": task.scheduled_start})

    db.commit()
    return {"applied": applied, "failed": failed, "total_applied": len(applied)}
