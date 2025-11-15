"""
Task repository - data access layer.
Part of Infrastructure layer.
"""
from typing import Optional, List
from uuid import UUID
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc, or_

from app.infrastructure.database.models import TaskModel
from app.domain.entities.task import Task


class TaskRepository:
    """Repository for task persistence operations."""

    def __init__(self, db: Session):
        self.db = db

    def create_task(
        self,
        user_id: UUID,
        title: str,
        memo: Optional[str] = None,
        delegated_to: Optional[UUID] = None,
        due_date: Optional[str] = None,
        priority: str = "medium",
        status: str = "new",
        status_description: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ) -> TaskModel:
        """
        Create a new task.

        Args:
            user_id: User ID
            title: Task title
            memo: Task memo
            delegated_to: Person ID to delegate to
            due_date: Due date (flexible text)
            priority: Priority (low, medium, high)
            status: Status
            status_description: Status description with annotations
            tags: List of tags

        Returns:
            Created TaskModel
        """
        task = TaskModel(
            user_id=user_id,
            title=title,
            memo=memo,
            delegated_to=delegated_to,
            due_date=due_date,
            priority=priority,
            status=status,
            status_description=status_description,
            tags=tags or [],
        )

        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)

        return task

    def get_task(
        self,
        task_id: UUID,
        user_id: Optional[UUID] = None,
    ) -> Optional[TaskModel]:
        """
        Get a task by ID.

        Args:
            task_id: Task ID
            user_id: Optional user ID to verify ownership

        Returns:
            TaskModel or None
        """
        query = self.db.query(TaskModel).options(
            joinedload(TaskModel.delegated_person)
        ).filter(TaskModel.id == task_id)

        if user_id:
            query = query.filter(TaskModel.user_id == user_id)

        return query.first()

    def get_task_by_number(
        self,
        task_number: int,
        user_id: UUID,
    ) -> Optional[TaskModel]:
        """
        Get a task by task number.

        Args:
            task_number: Task number
            user_id: User ID

        Returns:
            TaskModel or None
        """
        return (
            self.db.query(TaskModel)
            .options(joinedload(TaskModel.delegated_person))
            .filter(TaskModel.task_number == task_number)
            .filter(TaskModel.user_id == user_id)
            .first()
        )

    def get_user_tasks(
        self,
        user_id: UUID,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        delegated_to: Optional[UUID] = None,
        tag: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[TaskModel]:
        """
        Get tasks for a user with optional filters.

        Args:
            user_id: User ID
            status: Filter by status
            priority: Filter by priority
            delegated_to: Filter by delegated person
            tag: Filter by tag
            limit: Maximum number of results
            offset: Offset for pagination

        Returns:
            List of TaskModel
        """
        query = self.db.query(TaskModel).options(
            joinedload(TaskModel.delegated_person)
        ).filter(TaskModel.user_id == user_id)

        if status:
            query = query.filter(TaskModel.status == status)

        if priority:
            query = query.filter(TaskModel.priority == priority)

        if delegated_to:
            query = query.filter(TaskModel.delegated_to == delegated_to)

        if tag:
            # Check if tag exists in tags array
            query = query.filter(TaskModel.tags.contains([tag]))

        query = query.order_by(desc(TaskModel.updated_at))
        query = query.limit(limit).offset(offset)

        return query.all()

    def search_tasks(
        self,
        user_id: UUID,
        search_term: str,
        limit: int = 50,
    ) -> List[TaskModel]:
        """
        Search tasks by title or memo.

        Args:
            user_id: User ID
            search_term: Search term
            limit: Maximum number of results

        Returns:
            List of TaskModel
        """
        search_pattern = f"%{search_term}%"

        tasks = (
            self.db.query(TaskModel)
            .options(joinedload(TaskModel.delegated_person))
            .filter(TaskModel.user_id == user_id)
            .filter(
                or_(
                    TaskModel.title.ilike(search_pattern),
                    TaskModel.memo.ilike(search_pattern),
                )
            )
            .order_by(desc(TaskModel.updated_at))
            .limit(limit)
            .all()
        )

        return tasks

    def update_task(
        self,
        task_id: UUID,
        title: Optional[str] = None,
        memo: Optional[str] = None,
        delegated_to: Optional[UUID] = None,
        due_date: Optional[str] = None,
        priority: Optional[str] = None,
        status: Optional[str] = None,
        status_description: Optional[str] = None,
        tags: Optional[List[str]] = None,
        completed_at: Optional[object] = None,  # Can be datetime or False to clear
    ) -> Optional[TaskModel]:
        """
        Update a task.

        Args:
            task_id: Task ID
            title: New title
            memo: New memo
            delegated_to: New delegated person ID
            due_date: New due date
            priority: New priority
            status: New status
            status_description: New status description
            tags: New tags list
            completed_at: New completed_at timestamp (or False to clear)

        Returns:
            Updated TaskModel or None
        """
        task = self.db.query(TaskModel).filter(TaskModel.id == task_id).first()

        if not task:
            return None

        if title is not None:
            task.title = title

        if memo is not None:
            task.memo = memo

        if delegated_to is not None:
            task.delegated_to = delegated_to

        if due_date is not None:
            task.due_date = due_date

        if priority is not None:
            task.priority = priority

        if status is not None:
            task.status = status

        if status_description is not None:
            task.status_description = status_description

        if tags is not None:
            task.tags = tags

        if completed_at is not None:
            if completed_at is False:
                task.completed_at = None
            else:
                task.completed_at = completed_at

        self.db.commit()
        self.db.refresh(task)

        return task

    def delete_task(self, task_id: UUID) -> bool:
        """
        Delete a task.

        Args:
            task_id: Task ID

        Returns:
            True if deleted, False if not found
        """
        task = self.db.query(TaskModel).filter(TaskModel.id == task_id).first()

        if not task:
            return False

        self.db.delete(task)
        self.db.commit()

        return True

    def task_to_entity(self, model: TaskModel) -> Task:
        """
        Convert TaskModel to domain entity.

        Args:
            model: TaskModel from database

        Returns:
            Task domain entity
        """
        return Task(
            id=model.id,
            task_number=model.task_number,
            user_id=model.user_id,
            title=model.title,
            memo=model.memo,
            delegated_to=model.delegated_to,
            due_date=model.due_date,
            priority=model.priority,
            status=model.status,
            status_description=model.status_description,
            tags=model.tags or [],
            completed_at=model.completed_at,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
