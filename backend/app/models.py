"""
PlanWise AI - Database Models
SQLAlchemy ORM models for all persisted entities.
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import (
    String, Text, Integer, DateTime, Boolean, Float,
    ForeignKey, JSON
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    category: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, default="General")
    priority: Mapped[str] = mapped_column(String(20), nullable=False, default="medium")
    # priority: low, medium, high, urgent
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="todo")
    # status: todo, in_progress, completed
    due_date: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)  # YYYY-MM-DD
    due_time: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)  # HH:MM
    estimated_duration: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # minutes
    scheduled_start: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)  # ISO datetime
    tags: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # comma-separated
    is_demo: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "category": self.category or "General",
            "priority": self.priority,
            "status": self.status,
            "due_date": self.due_date,
            "due_time": self.due_time,
            "estimated_duration": self.estimated_duration,
            "scheduled_start": self.scheduled_start,
            "tags": self.tags,
            "is_demo": self.is_demo,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }


class AppSettings(Base):
    __tablename__ = "app_settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    preferred_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, default="")
    timezone: Mapped[str] = mapped_column(String(100), nullable=False, default="Asia/Kolkata")
    default_start_time: Mapped[str] = mapped_column(String(10), nullable=False, default="09:00")
    default_end_time: Mapped[str] = mapped_column(String(10), nullable=False, default="21:00")
    default_break_duration: Mapped[int] = mapped_column(Integer, nullable=False, default=30)
    theme: Mapped[str] = mapped_column(String(20), nullable=False, default="light")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "preferred_name": self.preferred_name or "",
            "timezone": self.timezone,
            "default_start_time": self.default_start_time,
            "default_end_time": self.default_end_time,
            "default_break_duration": self.default_break_duration,
            "theme": self.theme,
        }
