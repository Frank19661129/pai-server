"""
Task use cases.
Part of Application layer - orchestrates task management operations.
"""
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Session

from app.domain.entities.task import Task
from app.infrastructure.repositories.task_repository import TaskRepository
from app.infrastructure.repositories.person_repository import PersonRepository


class TaskUseCases:
    """
    Use cases for task management operations.
    Handles CRUD operations for tasks with delegation, status tracking, etc.
    """

    def __init__(self, db: Session):
        self.db = db
        self.task_repo = TaskRepository(db)
        self.person_repo = PersonRepository(db)

    def create_task(
        self,
        user_id: UUID,
        title: str,
        memo: Optional[str] = None,
        delegated_to_name: Optional[str] = None,
        due_date: Optional[str] = None,
        priority: str = "medium",
        tags: Optional[List[str]] = None,
    ) -> dict:
        """
        Create a new task.

        Args:
            user_id: User ID
            title: Task title
            memo: Task memo
            delegated_to_name: Person name to delegate to (will be looked up)
            due_date: Due date (flexible text)
            priority: Priority (low, medium, high)
            tags: List of tags

        Returns:
            Task dict
        """
        # Resolve delegated_to person if provided
        delegated_to_id = None
        if delegated_to_name:
            person = self.person_repo.find_person_by_name(user_id, delegated_to_name)
            if person:
                delegated_to_id = person.id

        # Use domain entity for validation
        task_entity = Task.create(
            user_id=user_id,
            title=title,
            memo=memo,
            delegated_to=delegated_to_id,
            due_date=due_date,
            priority=priority,
            tags=tags,
        )

        # Create in database
        task_model = self.task_repo.create_task(
            user_id=user_id,
            title=task_entity.title,
            memo=task_entity.memo,
            delegated_to=task_entity.delegated_to,
            due_date=task_entity.due_date,
            priority=task_entity.priority,
            status=task_entity.status,
            status_description=task_entity.status_description,
            tags=task_entity.tags,
        )

        return self._model_to_dict(task_model)

    def get_task(self, task_id: UUID, user_id: UUID) -> Optional[dict]:
        """
        Get a task by ID.

        Args:
            task_id: Task ID
            user_id: User ID (for ownership verification)

        Returns:
            Task dict or None
        """
        task_model = self.task_repo.get_task(task_id, user_id)

        if not task_model:
            return None

        return self._model_to_dict(task_model)

    def get_task_by_number(self, task_number: int, user_id: UUID) -> Optional[dict]:
        """
        Get a task by task number.

        Args:
            task_number: Task number
            user_id: User ID

        Returns:
            Task dict or None
        """
        task_model = self.task_repo.get_task_by_number(task_number, user_id)

        if not task_model:
            return None

        return self._model_to_dict(task_model)

    def list_tasks(
        self,
        user_id: UUID,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        delegated_to: Optional[UUID] = None,
        tag: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[dict]:
        """
        List tasks for a user with optional filters.

        Args:
            user_id: User ID
            status: Filter by status
            priority: Filter by priority
            delegated_to: Filter by delegated person
            tag: Filter by tag
            limit: Maximum number of results
            offset: Offset for pagination

        Returns:
            List of task dicts
        """
        tasks = self.task_repo.get_user_tasks(
            user_id=user_id,
            status=status,
            priority=priority,
            delegated_to=delegated_to,
            tag=tag,
            limit=limit,
            offset=offset,
        )

        return [self._model_to_dict(t) for t in tasks]

    def search_tasks(
        self,
        user_id: UUID,
        search_term: str,
        limit: int = 50,
    ) -> List[dict]:
        """
        Search tasks by title or memo.

        Args:
            user_id: User ID
            search_term: Search term
            limit: Maximum number of results

        Returns:
            List of task dicts
        """
        tasks = self.task_repo.search_tasks(user_id, search_term, limit)
        return [self._model_to_dict(t) for t in tasks]

    def update_task_status(
        self,
        task_id: UUID,
        user_id: UUID,
        new_status: str,
        annotation: Optional[str] = None,
    ) -> Optional[dict]:
        """
        Update task status.

        Args:
            task_id: Task ID
            user_id: User ID (for ownership verification)
            new_status: New status
            annotation: Optional annotation

        Returns:
            Updated task dict or None
        """
        # Get existing task
        task_model = self.task_repo.get_task(task_id, user_id)
        if not task_model:
            return None

        # Convert to entity and update status
        task_entity = self.task_repo.task_to_entity(task_model)
        task_entity.update_status(new_status, annotation)

        # Save to database
        updated_task = self.task_repo.update_task(
            task_id=task_id,
            status=task_entity.status,
            status_description=task_entity.status_description,
            completed_at=task_entity.completed_at if task_entity.completed_at else False,
        )

        if not updated_task:
            return None

        return self._model_to_dict(updated_task)

    def delegate_task(
        self,
        task_id: UUID,
        user_id: UUID,
        person_name: str,
    ) -> Optional[dict]:
        """
        Delegate task to a person.

        Args:
            task_id: Task ID
            user_id: User ID (for ownership verification)
            person_name: Person name to delegate to

        Returns:
            Updated task dict or None
        """
        # Get existing task
        task_model = self.task_repo.get_task(task_id, user_id)
        if not task_model:
            return None

        # Find person
        person = self.person_repo.find_person_by_name(user_id, person_name)
        if not person:
            raise ValueError(f"Person '{person_name}' not found")

        # Convert to entity and delegate
        task_entity = self.task_repo.task_to_entity(task_model)
        task_entity.delegate_to(person.id, person.name)

        # Save to database
        updated_task = self.task_repo.update_task(
            task_id=task_id,
            delegated_to=task_entity.delegated_to,
            status_description=task_entity.status_description,
        )

        if not updated_task:
            return None

        return self._model_to_dict(updated_task)

    def update_task_priority(
        self,
        task_id: UUID,
        user_id: UUID,
        new_priority: str,
    ) -> Optional[dict]:
        """
        Update task priority.

        Args:
            task_id: Task ID
            user_id: User ID (for ownership verification)
            new_priority: New priority

        Returns:
            Updated task dict or None
        """
        # Get existing task
        task_model = self.task_repo.get_task(task_id, user_id)
        if not task_model:
            return None

        # Convert to entity and update
        task_entity = self.task_repo.task_to_entity(task_model)
        task_entity.update_priority(new_priority)

        # Save to database
        updated_task = self.task_repo.update_task(
            task_id=task_id,
            priority=task_entity.priority,
            status_description=task_entity.status_description,
        )

        if not updated_task:
            return None

        return self._model_to_dict(updated_task)

    def add_task_annotation(
        self,
        task_id: UUID,
        user_id: UUID,
        annotation: str,
    ) -> Optional[dict]:
        """
        Add an annotation to a task.

        Args:
            task_id: Task ID
            user_id: User ID (for ownership verification)
            annotation: Annotation text

        Returns:
            Updated task dict or None
        """
        # Get existing task
        task_model = self.task_repo.get_task(task_id, user_id)
        if not task_model:
            return None

        # Convert to entity and add annotation
        task_entity = self.task_repo.task_to_entity(task_model)
        task_entity.add_annotation(annotation)

        # Save to database
        updated_task = self.task_repo.update_task(
            task_id=task_id,
            status_description=task_entity.status_description,
        )

        if not updated_task:
            return None

        return self._model_to_dict(updated_task)

    def update_task_fields(
        self,
        task_id: UUID,
        user_id: UUID,
        memo: Optional[str] = None,
        delegated_to_name: Optional[str] = None,
        due_date: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ) -> Optional[dict]:
        """
        Update multiple task fields at once.

        Args:
            task_id: Task ID
            user_id: User ID (for ownership verification)
            memo: New memo
            delegated_to_name: New delegated person name
            due_date: New due date
            tags: New tags list

        Returns:
            Updated task dict or None
        """
        # Get existing task
        task_model = self.task_repo.get_task(task_id, user_id)
        if not task_model:
            return None

        # Prepare update parameters
        update_params = {}

        if memo is not None:
            update_params['memo'] = memo

        if delegated_to_name is not None:
            # Find person if delegated_to_name is not empty
            if delegated_to_name:
                person = self.person_repo.find_person_by_name(user_id, delegated_to_name)
                if not person:
                    # Create person if not found
                    person = self.person_repo.create_person(user_id, delegated_to_name)
                update_params['delegated_to'] = person.id
            else:
                # Clear delegation
                update_params['delegated_to'] = None

        if due_date is not None:
            update_params['due_date'] = due_date if due_date else None

        if tags is not None:
            update_params['tags'] = tags

        # Save to database
        updated_task = self.task_repo.update_task(
            task_id=task_id,
            **update_params
        )

        if not updated_task:
            return None

        return self._model_to_dict(updated_task)

    def delete_task(self, task_id: UUID, user_id: UUID) -> bool:
        """
        Delete a task.

        Args:
            task_id: Task ID
            user_id: User ID (for ownership verification)

        Returns:
            True if deleted, False if not found
        """
        # Verify ownership
        existing = self.task_repo.get_task(task_id, user_id)
        if not existing:
            return False

        return self.task_repo.delete_task(task_id)

    def _model_to_dict(self, task_model) -> dict:
        """Convert task model to dict."""
        result = {
            "id": str(task_model.id),
            "task_number": task_model.task_number,
            "formatted_id": f"Task-{task_model.task_number:08d}" if task_model.task_number else None,
            "user_id": str(task_model.user_id),
            "title": task_model.title,
            "memo": task_model.memo,
            "delegated_to": str(task_model.delegated_to) if task_model.delegated_to else None,
            "delegated_person_name": task_model.delegated_person.name if task_model.delegated_person else None,
            "due_date": task_model.due_date,
            "priority": task_model.priority,
            "status": task_model.status,
            "status_description": task_model.status_description,
            "tags": task_model.tags or [],
            "completed_at": task_model.completed_at.isoformat() if task_model.completed_at else None,
            "created_at": task_model.created_at.isoformat(),
            "updated_at": task_model.updated_at.isoformat(),
        }
        return result
