"""
Tasks router - CRUD endpoints for task management.
Part of Presentation layer.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional, List
from pydantic import BaseModel, Field
from uuid import UUID

from app.core.dependencies import get_db, get_current_user
from app.application.use_cases.task_use_cases import TaskUseCases


router = APIRouter(prefix="/tasks", tags=["tasks"])


# ==================== Request/Response Models ====================


class TaskCreateRequest(BaseModel):
    """Request to create a task."""
    title: str = Field(..., min_length=1, max_length=500)
    memo: Optional[str] = None
    delegated_to_name: Optional[str] = None
    due_date: Optional[str] = None
    priority: str = Field("medium", pattern="^(low|medium|high)$")
    tags: Optional[List[str]] = None


class TaskUpdateStatusRequest(BaseModel):
    """Request to update task status."""
    status: str = Field(..., pattern="^(new|in_progress|overdue|done|cancelled)$")
    annotation: Optional[str] = None


class TaskDelegateRequest(BaseModel):
    """Request to delegate a task."""
    person_name: str = Field(..., min_length=1)


class TaskUpdatePriorityRequest(BaseModel):
    """Request to update task priority."""
    priority: str = Field(..., pattern="^(low|medium|high)$")


class TaskAddAnnotationRequest(BaseModel):
    """Request to add an annotation."""
    annotation: str = Field(..., min_length=1)


class TaskResponse(BaseModel):
    """Task response model."""
    id: str
    task_number: int
    formatted_id: Optional[str]
    user_id: str
    title: str
    memo: Optional[str]
    delegated_to: Optional[str]
    delegated_person_name: Optional[str]
    due_date: Optional[str]
    priority: str
    status: str
    status_description: Optional[str]
    tags: List[str]
    completed_at: Optional[str]
    created_at: str
    updated_at: str


# ==================== Endpoints ====================


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(
    request: TaskCreateRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Create a new task.
    """
    try:
        use_cases = TaskUseCases(db)
        task = use_cases.create_task(
            user_id=UUID(current_user["id"]),
            title=request.title,
            memo=request.memo,
            delegated_to_name=request.delegated_to_name,
            due_date=request.due_date,
            priority=request.priority,
            tags=request.tags,
        )
        return task
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create task: {str(e)}",
        )


@router.get("", response_model=List[TaskResponse])
def list_tasks(
    status_filter: Optional[str] = None,
    priority: Optional[str] = None,
    delegated_to: Optional[UUID] = None,
    tag: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    List tasks for the current user with optional filters.
    """
    try:
        use_cases = TaskUseCases(db)
        tasks = use_cases.list_tasks(
            user_id=UUID(current_user["id"]),
            status=status_filter,
            priority=priority,
            delegated_to=delegated_to,
            tag=tag,
            limit=limit,
            offset=offset,
        )
        return tasks
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list tasks: {str(e)}",
        )


@router.get("/search", response_model=List[TaskResponse])
def search_tasks(
    q: str,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Search tasks by title or memo.
    """
    try:
        use_cases = TaskUseCases(db)
        tasks = use_cases.search_tasks(
            user_id=UUID(current_user["id"]),
            search_term=q,
            limit=limit,
        )
        return tasks
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to search tasks: {str(e)}",
        )


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(
    task_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Get a task by ID.
    """
    try:
        use_cases = TaskUseCases(db)
        task = use_cases.get_task(task_id, UUID(current_user["id"]))

        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found",
            )

        return task
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get task: {str(e)}",
        )


@router.get("/number/{task_number}", response_model=TaskResponse)
def get_task_by_number(
    task_number: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Get a task by task number.
    """
    try:
        use_cases = TaskUseCases(db)
        task = use_cases.get_task_by_number(task_number, UUID(current_user["id"]))

        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found",
            )

        return task
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get task: {str(e)}",
        )


@router.patch("/{task_id}/status", response_model=TaskResponse)
def update_task_status(
    task_id: UUID,
    request: TaskUpdateStatusRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Update task status.
    """
    try:
        use_cases = TaskUseCases(db)
        task = use_cases.update_task_status(
            task_id=task_id,
            user_id=UUID(current_user["id"]),
            new_status=request.status,
            annotation=request.annotation,
        )

        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found",
            )

        return task
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update task status: {str(e)}",
        )


@router.patch("/{task_id}/delegate", response_model=TaskResponse)
def delegate_task(
    task_id: UUID,
    request: TaskDelegateRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Delegate task to a person.
    """
    try:
        use_cases = TaskUseCases(db)
        task = use_cases.delegate_task(
            task_id=task_id,
            user_id=UUID(current_user["id"]),
            person_name=request.person_name,
        )

        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found",
            )

        return task
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delegate task: {str(e)}",
        )


@router.patch("/{task_id}/priority", response_model=TaskResponse)
def update_task_priority(
    task_id: UUID,
    request: TaskUpdatePriorityRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Update task priority.
    """
    try:
        use_cases = TaskUseCases(db)
        task = use_cases.update_task_priority(
            task_id=task_id,
            user_id=UUID(current_user["id"]),
            new_priority=request.priority,
        )

        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found",
            )

        return task
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update task priority: {str(e)}",
        )


@router.post("/{task_id}/annotations", response_model=TaskResponse)
def add_task_annotation(
    task_id: UUID,
    request: TaskAddAnnotationRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Add an annotation to a task.
    """
    try:
        use_cases = TaskUseCases(db)
        task = use_cases.add_task_annotation(
            task_id=task_id,
            user_id=UUID(current_user["id"]),
            annotation=request.annotation,
        )

        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found",
            )

        return task
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add annotation: {str(e)}",
        )


class TaskUpdateRequest(BaseModel):
    """Request to update task fields."""
    memo: Optional[str] = None
    delegated_to_name: Optional[str] = None
    due_date: Optional[str] = None
    tags: Optional[List[str]] = None


@router.patch("/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: UUID,
    request: TaskUpdateRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Update task fields (memo, delegated_to, due_date, tags).
    """
    try:
        use_cases = TaskUseCases(db)

        # Update task fields
        task = use_cases.update_task_fields(
            task_id=task_id,
            user_id=UUID(current_user["id"]),
            memo=request.memo,
            delegated_to_name=request.delegated_to_name,
            due_date=request.due_date,
            tags=request.tags,
        )

        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found",
            )

        return task

    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update task: {str(e)}",
        )


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Delete a task.
    """
    try:
        use_cases = TaskUseCases(db)
        deleted = use_cases.delete_task(task_id, UUID(current_user["id"]))

        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found",
            )

        return None
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete task: {str(e)}",
        )
