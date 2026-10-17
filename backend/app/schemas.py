"""
PlanWise AI - Pydantic Schemas
Request and response validation schemas.
"""
from datetime import datetime
from typing import Optional, List, Any, Dict, Union
from pydantic import BaseModel, Field, field_validator
import re


# ─── Task Schemas ────────────────────────────────────────────────────────────

VALID_PRIORITIES = {"low", "medium", "high", "urgent"}
VALID_STATUSES = {"todo", "in_progress", "completed"}


class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=500, description="Task title")
    description: Optional[str] = Field(None, max_length=5000)
    category: Optional[str] = Field("General", max_length=100)
    priority: str = Field("medium")
    status: str = Field("todo")
    due_date: Optional[str] = Field(None, description="YYYY-MM-DD format")
    due_time: Optional[str] = Field(None, description="HH:MM format")
    estimated_duration: Optional[int] = Field(None, ge=1, le=1440, description="Minutes")
    scheduled_start: Optional[str] = Field(None)
    tags: Optional[Union[str, List[str]]] = Field(None)
    is_demo: bool = Field(False)

    @field_validator("tags", mode="before")
    @classmethod
    def validate_tags(cls, v):
        if isinstance(v, list):
            return ", ".join(str(item).strip() for item in v if item)
        return v


    @field_validator("priority")
    @classmethod
    def validate_priority(cls, v):
        v = v.lower().strip()
        if v not in VALID_PRIORITIES:
            raise ValueError(f"Priority must be one of: {', '.join(VALID_PRIORITIES)}")
        return v

    @field_validator("status")
    @classmethod
    def validate_status(cls, v):
        v = v.lower().strip()
        if v not in VALID_STATUSES:
            raise ValueError(f"Status must be one of: {', '.join(VALID_STATUSES)}")
        return v

    @field_validator("due_date")
    @classmethod
    def validate_due_date(cls, v):
        if v is None:
            return v
        try:
            datetime.strptime(v, "%Y-%m-%d")
        except ValueError:
            raise ValueError("due_date must be in YYYY-MM-DD format")
        return v

    @field_validator("due_time")
    @classmethod
    def validate_due_time(cls, v):
        if v is None:
            return v
        if not re.match(r"^\d{2}:\d{2}$", v):
            raise ValueError("due_time must be in HH:MM format")
        return v


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = Field(None, max_length=5000)
    category: Optional[str] = Field(None, max_length=100)
    priority: Optional[str] = None
    status: Optional[str] = None
    due_date: Optional[str] = None
    due_time: Optional[str] = None
    estimated_duration: Optional[int] = Field(None, ge=1, le=1440)
    scheduled_start: Optional[str] = None
    tags: Optional[Union[str, List[str]]] = None

    @field_validator("tags", mode="before")
    @classmethod
    def validate_tags(cls, v):
        if isinstance(v, list):
            return ", ".join(str(item).strip() for item in v if item)
        return v


    @field_validator("priority")
    @classmethod
    def validate_priority(cls, v):
        if v is None:
            return v
        v = v.lower().strip()
        if v not in VALID_PRIORITIES:
            raise ValueError(f"Priority must be one of: {', '.join(VALID_PRIORITIES)}")
        return v

    @field_validator("status")
    @classmethod
    def validate_status(cls, v):
        if v is None:
            return v
        v = v.lower().strip()
        if v not in VALID_STATUSES:
            raise ValueError(f"Status must be one of: {', '.join(VALID_STATUSES)}")
        return v

    @field_validator("due_date")
    @classmethod
    def validate_due_date(cls, v):
        if v is None:
            return v
        try:
            datetime.strptime(v, "%Y-%m-%d")
        except ValueError:
            raise ValueError("due_date must be in YYYY-MM-DD format")
        return v


class TaskResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    category: str
    priority: str
    status: str
    due_date: Optional[str]
    due_time: Optional[str]
    estimated_duration: Optional[int]
    scheduled_start: Optional[str]
    tags: Optional[str]
    is_demo: bool
    created_at: str
    updated_at: str
    completed_at: Optional[str]

    model_config = {"from_attributes": True}


class TaskListResponse(BaseModel):
    tasks: List[TaskResponse]
    total: int
    page: int
    per_page: int


# ─── Assistant Schemas ────────────────────────────────────────────────────────

class ChatMessage(BaseModel):
    role: str = Field(..., pattern="^(user|assistant)$")
    content: str


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=5000)
    history: Optional[List[ChatMessage]] = Field(default_factory=list)
    timezone: Optional[str] = Field("Asia/Kolkata")


class ActionCard(BaseModel):
    action_type: str  # create_task, update_task, delete_task, etc.
    task_id: Optional[int] = None
    task_data: Optional[Dict[str, Any]] = None
    requires_confirmation: bool = False
    confirmation_message: Optional[str] = None


class ChatResponse(BaseModel):
    message: str
    intent: Optional[str] = None
    tasks: Optional[List[Dict[str, Any]]] = None
    schedule_blocks: Optional[List[Dict[str, Any]]] = None
    action_card: Optional[ActionCard] = None
    ai_powered: bool = False
    suggested_prompts: Optional[List[str]] = None


# ─── Schedule Schemas ─────────────────────────────────────────────────────────

class ScheduleRequest(BaseModel):
    date: str = Field(..., description="YYYY-MM-DD")
    start_time: str = Field("09:00", description="HH:MM")
    end_time: str = Field("21:00", description="HH:MM")
    break_duration: int = Field(30, ge=0, le=120, description="Break in minutes")
    task_ids: Optional[List[int]] = Field(None, description="Specific task IDs to schedule")
    prioritize_urgent: bool = Field(True)
    timezone: str = Field("Asia/Kolkata")

    @field_validator("date")
    @classmethod
    def validate_date(cls, v):
        try:
            datetime.strptime(v, "%Y-%m-%d")
        except ValueError:
            raise ValueError("date must be in YYYY-MM-DD format")
        return v


class ScheduleBlock(BaseModel):
    task_id: int
    task_title: str
    start_time: str
    end_time: str
    duration_minutes: int
    priority: str
    reason: str


class ScheduleResponse(BaseModel):
    date: str
    scheduled_blocks: List[ScheduleBlock]
    unscheduled_tasks: List[Dict[str, Any]]
    warnings: List[str]
    total_scheduled_minutes: int
    available_minutes: int
    utilization_percent: float


class ApplyScheduleRequest(BaseModel):
    date: str
    scheduled_blocks: List[ScheduleBlock]


# ─── Settings Schemas ─────────────────────────────────────────────────────────

class SettingsResponse(BaseModel):
    id: int
    preferred_name: str
    timezone: str
    default_start_time: str
    default_end_time: str
    default_break_duration: int
    theme: str

    model_config = {"from_attributes": True}


class SettingsUpdate(BaseModel):
    preferred_name: Optional[str] = Field(None, max_length=100)
    timezone: Optional[str] = Field(None, max_length=100)
    default_start_time: Optional[str] = None
    default_end_time: Optional[str] = None
    default_break_duration: Optional[int] = Field(None, ge=0, le=120)
    theme: Optional[str] = Field(None, pattern="^(light|dark)$")

    @field_validator("default_start_time", "default_end_time")
    @classmethod
    def validate_time(cls, v):
        if v is None:
            return v
        if not re.match(r"^\d{2}:\d{2}$", v):
            raise ValueError("Time must be in HH:MM format")
        return v


# ─── Dashboard Schemas ────────────────────────────────────────────────────────

class DashboardStats(BaseModel):
    total_tasks: int
    completed_today: int
    due_today: int
    overdue: int
    in_progress: int
    high_priority_pending: int
    completion_rate: float
    tasks_due_today: List[Dict[str, Any]]
    overdue_tasks: List[Dict[str, Any]]
    upcoming_tasks: List[Dict[str, Any]]
