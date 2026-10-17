"""
PlanWise AI - Task Service
Core business logic for task CRUD operations and queries.
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, desc, asc
from app.models import Task
from app.schemas import TaskCreate, TaskUpdate
from app.services.date_service import get_today, is_overdue


class TaskService:

    @staticmethod
    def create_task(db: Session, data: TaskCreate) -> Task:
        """Create a new task."""
        task = Task(
            title=data.title.strip(),
            description=data.description,
            category=data.category or "General",
            priority=data.priority,
            status=data.status,
            due_date=data.due_date,
            due_time=data.due_time,
            estimated_duration=data.estimated_duration,
            scheduled_start=data.scheduled_start,
            tags=data.tags,
            is_demo=data.is_demo,
        )
        db.add(task)
        db.commit()
        db.refresh(task)
        return task

    @staticmethod
    def get_task(db: Session, task_id: int) -> Optional[Task]:
        """Get a task by ID."""
        return db.query(Task).filter(Task.id == task_id).first()

    @staticmethod
    def get_tasks(
        db: Session,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        category: Optional[str] = None,
        search: Optional[str] = None,
        due_date: Optional[str] = None,
        sort_by: str = "created_at",
        sort_dir: str = "desc",
        page: int = 1,
        per_page: int = 50,
    ) -> Dict[str, Any]:
        """Query tasks with filters, sorting, and pagination."""
        query = db.query(Task)

        if status:
            query = query.filter(Task.status == status)
        if priority:
            query = query.filter(Task.priority == priority)
        if category:
            query = query.filter(Task.category == category)
        if due_date:
            query = query.filter(Task.due_date == due_date)
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    Task.title.ilike(search_term),
                    Task.description.ilike(search_term),
                    Task.tags.ilike(search_term),
                    Task.category.ilike(search_term),
                )
            )


        total = query.count()

        # Sorting
        sort_col_map = {
            "created_at": Task.created_at,
            "updated_at": Task.updated_at,
            "due_date": Task.due_date,
            "priority": Task.priority,
            "title": Task.title,
            "status": Task.status,
        }
        sort_col = sort_col_map.get(sort_by, Task.created_at)
        if sort_dir == "asc":
            query = query.order_by(asc(sort_col))
        else:
            query = query.order_by(desc(sort_col))

        offset = (page - 1) * per_page
        tasks = query.offset(offset).limit(per_page).all()

        return {"tasks": tasks, "total": total, "page": page, "per_page": per_page}

    @staticmethod
    def update_task(db: Session, task_id: int, data: TaskUpdate) -> Optional[Task]:
        """Update a task. Returns None if not found."""
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            return None

        update_data = data.model_dump(exclude_none=True)
        for key, value in update_data.items():
            setattr(task, key, value)

        task.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(task)
        return task

    @staticmethod
    def complete_task(db: Session, task_id: int) -> Optional[Task]:
        """Mark a task as completed."""
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            return None
        task.status = "completed"
        task.completed_at = datetime.utcnow()
        task.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(task)
        return task

    @staticmethod
    def reopen_task(db: Session, task_id: int) -> Optional[Task]:
        """Reopen a completed task."""
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            return None
        task.status = "todo"
        task.completed_at = None
        task.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(task)
        return task

    @staticmethod
    def delete_task(db: Session, task_id: int) -> bool:
        """Delete a task. Returns True if deleted."""
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            return False
        db.delete(task)
        db.commit()
        return True

    @staticmethod
    def get_dashboard_data(db: Session, timezone: str = "Asia/Kolkata") -> Dict[str, Any]:
        """Compute dashboard statistics from the database."""
        today_str = get_today(timezone).strftime("%Y-%m-%d")
        all_tasks = db.query(Task).all()

        total = len(all_tasks)
        completed = [t for t in all_tasks if t.status == "completed"]
        pending = [t for t in all_tasks if t.status != "completed"]
        in_progress = [t for t in all_tasks if t.status == "in_progress"]

        due_today = [
            t for t in pending if t.due_date == today_str
        ]
        overdue = [
            t for t in pending if t.due_date and t.due_date < today_str
        ]
        upcoming = [
            t for t in pending
            if t.due_date and t.due_date > today_str
        ]
        upcoming.sort(key=lambda t: t.due_date)

        high_priority = [
            t for t in pending if t.priority in ("high", "urgent")
        ]
        high_priority.sort(
            key=lambda t: (
                0 if t.priority == "urgent" else 1,
                t.due_date or "9999-99-99"
            )
        )

        # Completed today
        completed_today = [
            t for t in completed
            if t.completed_at and t.completed_at.strftime("%Y-%m-%d") == today_str
        ]

        completion_rate = (len(completed) / total * 100) if total > 0 else 0.0

        return {
            "total_tasks": total,
            "completed_today": len(completed_today),
            "due_today": len(due_today),
            "overdue": len(overdue),
            "in_progress": len(in_progress),
            "high_priority_pending": len(high_priority),
            "completion_rate": round(completion_rate, 1),
            "tasks_due_today": [t.to_dict() for t in due_today[:5]],
            "overdue_tasks": [t.to_dict() for t in overdue[:5]],
            "upcoming_tasks": [t.to_dict() for t in upcoming[:5]],
        }

    @staticmethod
    def find_tasks_by_name(db: Session, name: str, exclude_completed: bool = False) -> List[Task]:
        """Fuzzy-find tasks by partial name match."""
        query = db.query(Task)
        if exclude_completed:
            query = query.filter(Task.status != "completed")
        search = f"%{name}%"
        return query.filter(Task.title.ilike(search)).all()

    @staticmethod
    def get_schedulable_tasks(
        db: Session,
        task_ids: Optional[List[int]] = None,
    ) -> List[Task]:
        """Get tasks eligible for scheduling (not completed, with duration)."""
        query = db.query(Task).filter(
            Task.status != "completed",
            Task.estimated_duration.isnot(None),
        )
        if task_ids:
            query = query.filter(Task.id.in_(task_ids))
        return query.all()

    @staticmethod
    def clear_demo_data(db: Session) -> int:
        """Delete all demo tasks."""
        deleted = db.query(Task).filter(Task.is_demo == True).delete()
        db.commit()
        return deleted

    @staticmethod
    def seed_demo_data(db: Session, timezone: str = "Asia/Kolkata") -> List[Task]:
        """Insert demo tasks with realistic relative dates."""
        from app.services.date_service import get_today
        from datetime import timedelta

        today = get_today(timezone)

        demo_tasks = [
            {
                "title": "Complete Machine Learning Assignment",
                "description": "Implement a neural network classifier for the MNIST dataset. Include training, evaluation, and a short report.",
                "category": "Academics",
                "priority": "urgent",
                "due_date": (today + timedelta(days=1)).strftime("%Y-%m-%d"),
                "estimated_duration": 120,
                "tags": "ML,assignment,deep-learning",
            },
            {
                "title": "Prepare for Data Structures Test",
                "description": "Revise trees, graphs, dynamic programming, and sorting algorithms. Solve at least 10 practice problems.",
                "category": "Academics",
                "priority": "high",
                "due_date": (today + timedelta(days=2)).strftime("%Y-%m-%d"),
                "estimated_duration": 90,
                "tags": "DSA,exam,revision",
            },
            {
                "title": "Finish AI/ML Project Report",
                "description": "Write the final project report covering methodology, results, and conclusions. Add references and format properly.",
                "category": "Project",
                "priority": "high",
                "due_date": (today + timedelta(days=3)).strftime("%Y-%m-%d"),
                "estimated_duration": 180,
                "tags": "AI,report,project",
            },
            {
                "title": "Review Interview Questions",
                "description": "Go through commonly asked system design and coding interview questions. Prepare two mock answers.",
                "category": "Career",
                "priority": "medium",
                "due_date": (today + timedelta(days=5)).strftime("%Y-%m-%d"),
                "estimated_duration": 60,
                "tags": "interview,career",
            },
            {
                "title": "Practice Coding Problems",
                "description": "Solve 5 LeetCode medium problems focused on arrays and strings.",
                "category": "Career",
                "priority": "medium",
                "due_date": (today + timedelta(days=4)).strftime("%Y-%m-%d"),
                "estimated_duration": 75,
                "tags": "leetcode,coding",
            },
            {
                "title": "Database Management Systems Assignment",
                "description": "Write SQL queries for normalization exercises. Demonstrate 1NF, 2NF, and 3NF.",
                "category": "Academics",
                "priority": "high",
                "due_date": today.strftime("%Y-%m-%d"),
                "estimated_duration": 60,
                "tags": "DBMS,SQL,assignment",
            },
            {
                "title": "Read Research Paper on Transformers",
                "description": "Read 'Attention Is All You Need' and write a 300-word summary.",
                "category": "Learning",
                "priority": "low",
                "due_date": (today + timedelta(days=7)).strftime("%Y-%m-%d"),
                "estimated_duration": 45,
                "tags": "research,NLP,transformers",
            },
            {
                "title": "Weekly Exercise Routine",
                "description": "30-minute workout session. Focus on cardio and stretching.",
                "category": "Personal",
                "priority": "low",
                "due_date": today.strftime("%Y-%m-%d"),
                "estimated_duration": 30,
                "tags": "health,exercise",
            },
        ]

        created = []
        for task_data in demo_tasks:
            task = Task(
                title=task_data["title"],
                description=task_data.get("description"),
                category=task_data.get("category", "General"),
                priority=task_data.get("priority", "medium"),
                status="todo",
                due_date=task_data.get("due_date"),
                estimated_duration=task_data.get("estimated_duration"),
                tags=task_data.get("tags"),
                is_demo=True,
            )
            db.add(task)
            created.append(task)

        db.commit()
        return created
