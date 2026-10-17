"""
PlanWise AI - Assistant Router
Handles conversational AI requests with LLM + deterministic fallback.
"""
import logging
import re
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db

from app.schemas import ChatRequest, ChatResponse, ActionCard
from app.services.intent_parser import (
    detect_intent, extract_task_name, extract_priority,
    extract_duration, extract_date, extract_time_window,
    extract_free_time, extract_task_title_from_create,
)
from app.services.task_service import TaskService
from app.services.ai_service import call_ai, get_ai_status
from app.services.date_service import get_today, format_relative_date
from app.services.scheduling_service import generate_schedule, _score_task
from app.schemas import ScheduleRequest

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/assistant", tags=["Assistant"])


@router.get("/status")
def assistant_status():
    """Return AI configuration status."""
    return get_ai_status()


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, db: Session = Depends(get_db)):
    """
    Process a conversational message.
    Tries LLM first, falls back to rule-based intent handling.
    """
    message = request.message.strip()
    timezone = request.timezone or "Asia/Kolkata"
    today_str = get_today(timezone).strftime("%Y-%m-%d")

    # Try AI first
    ai_result = None
    if get_ai_status()["available"]:
        # Build task context for the AI
        dashboard = TaskService.get_dashboard_data(db, timezone)
        context = _build_context(db, timezone, dashboard)
        try:
            ai_result = await call_ai(message, history=request.history, context=context)
        except Exception as e:
            logger.error(f"AI call error: {e}")

    # If AI succeeded and returned a valid result, use it
    if ai_result and isinstance(ai_result, dict) and "message" in ai_result:
        return await _process_ai_result(ai_result, message, db, timezone, today_str)

    # Fallback: deterministic rule-based handling
    return await _handle_deterministic(message, db, timezone, today_str)


async def _process_ai_result(
    ai_result: Dict[str, Any],
    original_message: str,
    db: Session,
    timezone: str,
    today_str: str,
) -> ChatResponse:
    """Process AI-generated result, executing validated actions."""
    msg = ai_result.get("message", "")
    intent = ai_result.get("intent", "general")
    action_data = ai_result.get("action")
    suggested = ai_result.get("suggested_prompts", [])
    tasks_list = None
    schedule_blocks = None
    action_card = None

    if action_data and isinstance(action_data, dict):
        action_type = action_data.get("action_type")

        if action_type == "create_task":
            task_data = action_data.get("task_data", {})
            if task_data.get("title"):
                from app.schemas import TaskCreate
                try:
                    tc = TaskCreate(**{k: v for k, v in task_data.items() if v is not None})
                    task = TaskService.create_task(db, tc)
                    msg += f"\n\n✓ Task created: **{task.title}**"
                except Exception as e:
                    msg += f"\n\nCouldn't create task: {str(e)}"

        elif action_type == "complete_task":
            task_query = action_data.get("task_query", "")
            tasks = TaskService.find_tasks_by_name(db, task_query, exclude_completed=True)
            if len(tasks) == 1:
                TaskService.complete_task(db, tasks[0].id)
                msg += f"\n\n✓ Marked **{tasks[0].title}** as completed."
            elif len(tasks) > 1:
                msg = f"I found multiple tasks matching '{task_query}'. Which one did you mean?\n\n"
                for t in tasks[:5]:
                    msg += f"• **{t.title}**\n"
                tasks_list = [t.to_dict() for t in tasks[:5]]

        elif action_type == "delete_task":
            task_query = action_data.get("task_query", "")
            tasks = TaskService.find_tasks_by_name(db, task_query)
            if len(tasks) == 1:
                action_card = ActionCard(
                    action_type="delete_task",
                    task_id=tasks[0].id,
                    requires_confirmation=True,
                    confirmation_message=f"Are you sure you want to delete '{tasks[0].title}'?",
                )
            elif len(tasks) > 1:
                msg = f"I found multiple tasks matching '{task_query}'. Which one?\n\n"
                tasks_list = [t.to_dict() for t in tasks[:5]]

    return ChatResponse(
        message=msg,
        intent=intent,
        tasks=tasks_list,
        schedule_blocks=schedule_blocks,
        action_card=action_card,
        ai_powered=True,
        suggested_prompts=suggested if suggested else _default_prompts(),
    )


async def _handle_deterministic(
    message: str,
    db: Session,
    timezone: str,
    today_str: str,
) -> ChatResponse:
    """Rule-based intent handling — no LLM required."""
    intent = detect_intent(message)
    tasks_list = None
    schedule_blocks = None
    action_card = None
    suggested = _default_prompts()

    # ── Help / Greeting ──
    if intent == "help":
        msg = (
            "Hi! I'm **PlanWise AI**, your productivity assistant. 👋\n\n"
            "Here's what I can do:\n"
            "• **Add tasks** — 'Add a machine learning assignment due tomorrow'\n"
            "• **Show tasks** — 'What tasks do I have today?'\n"
            "• **Complete tasks** — 'Mark my database assignment as done'\n"
            "• **Prioritize** — 'What should I work on first?'\n"
            "• **Plan your day** — 'Plan my day from 9 AM to 5 PM'\n"
            "• **Find free time tasks** — 'I have 90 minutes free, what can I do?'\n"
            "• **Show overdue** — 'Show my overdue tasks'\n\n"
            "_Note: Running in rule-based mode. Add an AI API key for smarter responses._"
        )
        suggested = [
            "Add a task due tomorrow",
            "What should I focus on first?",
            "Plan my day from 9 AM to 6 PM",
        ]

    # ── Create Task ──
    elif intent == "create_task":
        title = extract_task_title_from_create(message)
        priority = extract_priority(message) or "medium"
        due_date, _ = extract_date(message, timezone)
        duration = extract_duration(message)

        if not title or len(title) < 2:
            msg = "What would you like to name the task? Please provide more details."
        else:
            from app.schemas import TaskCreate
            tc = TaskCreate(
                title=title,
                priority=priority,
                due_date=due_date,
                estimated_duration=duration,
            )
            task = TaskService.create_task(db, tc)
            due_label = format_relative_date(due_date) if due_date else "no due date"
            dur_label = f"{duration} min" if duration else "no estimate"
            msg = (
                f"✓ Task created: **{task.title}**\n\n"
                f"• Priority: {priority.capitalize()}\n"
                f"• Due: {due_label}\n"
                f"• Duration: {dur_label}"
            )
            suggested = [
                "Add another task",
                f"Show my {priority} priority tasks",
                "Plan my day",
            ]

    # ── List Tasks ──
    elif intent == "list_tasks":
        # Determine filter
        msg_lower = message.lower()
        status_filter = None
        due_filter = None

        if "today" in msg_lower or "due today" in msg_lower:
            due_filter = today_str
        elif "overdue" in msg_lower:
            pass  # handled by overdue_tasks intent
        elif "completed" in msg_lower or "done" in msg_lower:
            status_filter = "completed"
        elif "in progress" in msg_lower:
            status_filter = "in_progress"

        result = TaskService.get_tasks(
            db,
            status=status_filter,
            due_date=due_filter,
            sort_by="due_date",
            sort_dir="asc",
            per_page=20,
        )
        task_list = result["tasks"]

        if not task_list:
            msg = "No tasks found matching your criteria."
            suggested = ["Add a new task", "Show all tasks", "Plan my day"]
        else:
            label = f"{result['total']} task{'s' if result['total'] != 1 else ''}"
            if due_filter:
                label += " due today"
            elif status_filter:
                label += f" {status_filter.replace('_', ' ')}"
            msg = f"Here are your **{label}**:"
            tasks_list = [t.to_dict() for t in task_list[:10]]
            suggested = [
                "Mark a task as complete",
                "Filter by priority",
                "Plan my day",
            ]

    # ── Complete Task ──
    elif intent == "complete_task":
        task_name = extract_task_name(message)
        if not task_name:
            # Try extracting after "mark" or "complete"
            m = re.search(r"(?:mark|complete|finish|done)\s+(?:my\s+)?(.+?)(?:\s+as\s+|\s+done|\s+complete|$)", message, re.I)
            if m:
                task_name = m.group(1).strip()

        if not task_name:
            msg = "Which task would you like to mark as complete? Please include the task name."
        else:
            tasks = TaskService.find_tasks_by_name(db, task_name, exclude_completed=True)
            if not tasks:
                msg = f"I couldn't find an incomplete task matching '{task_name}'. Check spelling or try a shorter keyword."
                suggested = ["Show my tasks", "What tasks do I have today?"]
            elif len(tasks) == 1:
                TaskService.complete_task(db, tasks[0].id)
                msg = f"✓ Marked **{tasks[0].title}** as completed! Great work!"
                suggested = ["Show my remaining tasks", "Plan my day", "What should I work on next?"]
            else:
                msg = f"I found {len(tasks)} tasks matching '{task_name}'. Which one did you mean?\n"
                tasks_list = [t.to_dict() for t in tasks[:5]]

    # ── Delete Task ──
    elif intent == "delete_task":
        task_name = extract_task_name(message)
        if not task_name:
            m = re.search(r"(?:delete|remove|cancel|drop)\s+(?:my\s+)?(?:task\s+)?(.+?)$", message, re.I)
            if m:
                task_name = m.group(1).strip()

        if not task_name:
            msg = "Which task would you like to delete? Please provide the task name."
        else:
            tasks = TaskService.find_tasks_by_name(db, task_name)
            if not tasks:
                msg = f"I couldn't find a task matching '{task_name}' to delete."
            elif len(tasks) == 1:
                t = tasks[0]
                msg = f"Are you sure you want to delete **{t.title}**? Deleting a task is permanent and cannot be undone."
                action_card = ActionCard(
                    action_type="delete_task",
                    task_id=t.id,
                    requires_confirmation=True,
                    confirmation_message=f"Delete task: {t.title}",
                )
                suggested = ["Show all tasks", "Plan my day"]
            else:
                msg = f"I found {len(tasks)} tasks matching '{task_name}'. Which one would you like to delete?\n"
                tasks_list = [t.to_dict() for t in tasks[:5]]

    # ── Prioritize ──
    elif intent == "prioritize":

        result = TaskService.get_tasks(db, sort_by="priority", per_page=10)
        pending = [t for t in result["tasks"] if t.status != "completed"]

        if not pending:
            msg = "You have no pending tasks! Enjoy your free time 🎉"
        else:
            # Score and sort
            pending.sort(key=lambda t: _score_task(t, today_str), reverse=True)
            top = pending[:3]
            msg = "Based on **priority and deadlines**, here's what to focus on:\n\n"
            for i, t in enumerate(top, 1):
                due = format_relative_date(t.due_date) if t.due_date else "no due date"
                dur = f"{t.estimated_duration}min" if t.estimated_duration else "—"
                msg += f"**{i}. {t.title}**\n   {t.priority.capitalize()} · {due} · {dur}\n\n"
            tasks_list = [t.to_dict() for t in top]
            suggested = ["Plan my day around these tasks", "Mark top task as in-progress", "Show all tasks"]

    # ── Generate Schedule ──
    elif intent == "generate_schedule":
        start_time, end_time = extract_time_window(message)
        start_time = start_time or "09:00"
        end_time = end_time or "21:00"

        sched_req = ScheduleRequest(
            date=today_str,
            start_time=start_time,
            end_time=end_time,
            break_duration=30,
            timezone=timezone,
        )
        result = generate_schedule(db, sched_req)

        if result.scheduled_blocks:
            msg = (
                f"📅 Here's your plan for today ({start_time}–{end_time}):\n\n"
                f"**{len(result.scheduled_blocks)} tasks** scheduled in "
                f"**{result.total_scheduled_minutes} minutes** "
                f"({result.utilization_percent:.0f}% of your time)"
            )
            if result.unscheduled_tasks:
                msg += f"\n\n⚠️ {len(result.unscheduled_tasks)} task(s) could not fit."
            if result.warnings:
                msg += "\n\n" + "\n".join(f"• {w}" for w in result.warnings[:2])
            schedule_blocks = [b.model_dump() for b in result.scheduled_blocks]
        else:
            msg = "I couldn't schedule any tasks. Make sure your tasks have estimated durations."
            if result.warnings:
                msg += "\n\n" + "\n".join(f"• {w}" for w in result.warnings)
        suggested = ["Apply this schedule", "Show my overdue tasks", "Add more tasks"]

    # ── Available Time ──
    elif intent == "available_time":
        free_mins = extract_free_time(message)
        if not free_mins:
            msg = "How much free time do you have? (e.g., '2 hours' or '90 minutes')"
        else:
            result = TaskService.get_tasks(db, sort_by="priority", per_page=50)
            pending = [t for t in result["tasks"] if t.status != "completed" and t.estimated_duration]
            pending.sort(key=lambda t: _score_task(t, today_str), reverse=True)

            fitting = []
            time_left = free_mins
            for t in pending:
                if t.estimated_duration <= time_left:
                    fitting.append(t)
                    time_left -= t.estimated_duration
                    if time_left <= 0:
                        break

            if fitting:
                hrs = free_mins // 60
                mins = free_mins % 60
                time_str = f"{hrs}h {mins}m" if hrs else f"{mins}min"
                msg = f"With **{time_str}** free, you could complete:\n\n"
                for t in fitting:
                    msg += f"• **{t.title}** ({t.estimated_duration}min)\n"
                msg += f"\nTotal: {free_mins - time_left}min of {free_mins}min used."
                tasks_list = [t.to_dict() for t in fitting]
            else:
                msg = (
                    f"No tasks fit in {free_mins} minutes, or your tasks don't have duration estimates. "
                    "Try adding estimated durations when creating tasks."
                )
        suggested = ["Show all tasks", "Plan my full day", "Add a quick task"]

    # ── Overdue Tasks ──
    elif intent == "overdue_tasks":
        result = TaskService.get_tasks(db, sort_by="due_date", sort_dir="asc", per_page=20)
        overdue = [
            t for t in result["tasks"]
            if t.status != "completed" and t.due_date and t.due_date < today_str
        ]
        if not overdue:
            msg = "Great news — you have no overdue tasks! 🎉"
        else:
            msg = f"You have **{len(overdue)} overdue task{'s' if len(overdue) != 1 else ''}**:\n"
            tasks_list = [t.to_dict() for t in overdue[:10]]
            suggested = ["Mark one as complete", "Move overdue to tomorrow", "Prioritize overdue tasks"]

    # ── General ──
    else:
        dashboard = TaskService.get_dashboard_data(db, timezone)
        total = dashboard["total_tasks"]
        overdue_count = dashboard["overdue"]
        due_today_count = dashboard["due_today"]

        if total == 0:
            msg = (
                "You have no tasks yet! Start by adding some:\n\n"
                "• 'Add a math assignment due tomorrow'\n"
                "• 'Create a study session for Friday'\n"
                "• 'Remind me to review interview questions'\n\n"
                "You can also load demo data from Settings."
            )
        else:
            msg = (
                f"You have **{total} task{'s' if total != 1 else ''}** total. "
            )
            if due_today_count:
                msg += f"**{due_today_count}** due today. "
            if overdue_count:
                msg += f"**{overdue_count}** overdue. "
            msg += "\n\nWhat would you like to do?"
        suggested = [
            "Show my tasks for today",
            "What should I work on first?",
            "Plan my day from 9 AM to 6 PM",
        ]

    return ChatResponse(

        message=msg,
        intent=intent,
        tasks=tasks_list,
        schedule_blocks=schedule_blocks,
        action_card=action_card,
        ai_powered=False,
        suggested_prompts=suggested,
    )


def _build_context(db: Session, timezone: str, dashboard: dict) -> str:
    """Build a task context string for the AI."""
    lines = [
        f"Today: {get_today(timezone).strftime('%A, %B %d, %Y')}",
        f"Total tasks: {dashboard['total_tasks']}",
        f"Due today: {dashboard['due_today']}",
        f"Overdue: {dashboard['overdue']}",
        f"In progress: {dashboard['in_progress']}",
        "",
        "Tasks due today:",
    ]
    for t in dashboard.get("tasks_due_today", [])[:3]:
        lines.append(f"  - [{t['priority'].upper()}] {t['title']} (est: {t.get('estimated_duration', '?')}min)")
    lines.append("Overdue tasks:")
    for t in dashboard.get("overdue_tasks", [])[:3]:
        lines.append(f"  - [{t['priority'].upper()}] {t['title']} (due: {t.get('due_date', '?')})")
    return "\n".join(lines)


def _default_prompts() -> List[str]:
    return [
        "Help me plan my day.",
        "What should I focus on first?",
        "Show my overdue tasks.",
    ]
