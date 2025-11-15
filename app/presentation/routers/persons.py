"""
Persons router - CRUD endpoints for person management.
Part of Presentation layer.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr
from uuid import UUID

from app.core.dependencies import get_db, get_current_user
from app.application.use_cases.person_use_cases import PersonUseCases


router = APIRouter(prefix="/persons", tags=["persons"])


# ==================== Request/Response Models ====================


class PersonCreateRequest(BaseModel):
    """Request to create a person."""
    name: str = Field(..., min_length=1, max_length=200)
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = Field(None, max_length=50)


class PersonUpdateRequest(BaseModel):
    """Request to update a person."""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = Field(None, max_length=50)


class PersonResponse(BaseModel):
    """Person response model."""
    id: str
    user_id: str
    name: str
    email: Optional[str]
    phone_number: Optional[str]
    created_at: str
    updated_at: str


# ==================== Endpoints ====================


@router.post("", response_model=PersonResponse, status_code=status.HTTP_201_CREATED)
def create_person(
    request: PersonCreateRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Create a new person.
    """
    try:
        use_cases = PersonUseCases(db)
        person = use_cases.create_person(
            user_id=UUID(current_user["id"]),
            name=request.name,
            email=request.email,
            phone_number=request.phone_number,
        )
        return person
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create person: {str(e)}",
        )


@router.get("", response_model=List[PersonResponse])
def list_persons(
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    List all persons for the current user.
    """
    try:
        use_cases = PersonUseCases(db)
        persons = use_cases.list_persons(
            user_id=UUID(current_user["id"]),
            limit=limit,
            offset=offset,
        )
        return persons
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list persons: {str(e)}",
        )


@router.get("/{person_id}", response_model=PersonResponse)
def get_person(
    person_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Get a person by ID.
    """
    try:
        use_cases = PersonUseCases(db)
        person = use_cases.get_person(person_id, UUID(current_user["id"]))

        if not person:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Person not found",
            )

        return person
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get person: {str(e)}",
        )


@router.put("/{person_id}", response_model=PersonResponse)
def update_person(
    person_id: UUID,
    request: PersonUpdateRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Update a person.
    """
    try:
        use_cases = PersonUseCases(db)
        person = use_cases.update_person(
            person_id=person_id,
            user_id=UUID(current_user["id"]),
            name=request.name,
            email=request.email,
            phone_number=request.phone_number,
        )

        if not person:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Person not found",
            )

        return person
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update person: {str(e)}",
        )


@router.delete("/{person_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_person(
    person_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Delete a person.
    """
    try:
        use_cases = PersonUseCases(db)
        deleted = use_cases.delete_person(person_id, UUID(current_user["id"]))

        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Person not found",
            )

        return None
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete person: {str(e)}",
        )
