"""
Person use cases.
Part of Application layer - orchestrates person CRUD operations.
"""
from typing import Optional, List
from uuid import UUID
from sqlalchemy.orm import Session

from app.domain.entities.person import Person
from app.infrastructure.repositories.person_repository import PersonRepository


class PersonUseCases:
    """
    Use cases for person management operations.
    Handles CRUD operations for persons who can be assigned tasks.
    """

    def __init__(self, db: Session):
        self.db = db
        self.person_repo = PersonRepository(db)

    def create_person(
        self,
        user_id: UUID,
        name: str,
        email: Optional[str] = None,
        phone_number: Optional[str] = None,
    ) -> dict:
        """
        Create a new person.

        Args:
            user_id: User ID
            name: Person name
            email: Email address
            phone_number: Phone number

        Returns:
            Person dict
        """
        # Use domain entity for validation
        person_entity = Person.create(
            user_id=user_id,
            name=name,
            email=email,
            phone_number=phone_number,
        )

        # Create in database
        person_model = self.person_repo.create_person(
            user_id=user_id,
            name=person_entity.name,
            email=person_entity.email,
            phone_number=person_entity.phone_number,
        )

        return {
            "id": str(person_model.id),
            "user_id": str(person_model.user_id),
            "name": person_model.name,
            "email": person_model.email,
            "phone_number": person_model.phone_number,
            "created_at": person_model.created_at.isoformat(),
            "updated_at": person_model.updated_at.isoformat(),
        }

    def get_person(self, person_id: UUID, user_id: UUID) -> Optional[dict]:
        """
        Get a person by ID.

        Args:
            person_id: Person ID
            user_id: User ID (for ownership verification)

        Returns:
            Person dict or None
        """
        person_model = self.person_repo.get_person(person_id, user_id)

        if not person_model:
            return None

        return {
            "id": str(person_model.id),
            "user_id": str(person_model.user_id),
            "name": person_model.name,
            "email": person_model.email,
            "phone_number": person_model.phone_number,
            "created_at": person_model.created_at.isoformat(),
            "updated_at": person_model.updated_at.isoformat(),
        }

    def list_persons(
        self,
        user_id: UUID,
        limit: int = 100,
        offset: int = 0,
    ) -> List[dict]:
        """
        List all persons for a user.

        Args:
            user_id: User ID
            limit: Maximum number of results
            offset: Offset for pagination

        Returns:
            List of person dicts
        """
        persons = self.person_repo.get_user_persons(user_id, limit, offset)

        return [
            {
                "id": str(p.id),
                "user_id": str(p.user_id),
                "name": p.name,
                "email": p.email,
                "phone_number": p.phone_number,
                "created_at": p.created_at.isoformat(),
                "updated_at": p.updated_at.isoformat(),
            }
            for p in persons
        ]

    def find_person_by_name(self, user_id: UUID, name: str) -> Optional[dict]:
        """
        Find a person by name (case-insensitive).

        Args:
            user_id: User ID
            name: Person name to search

        Returns:
            Person dict or None
        """
        person_model = self.person_repo.find_person_by_name(user_id, name)

        if not person_model:
            return None

        return {
            "id": str(person_model.id),
            "user_id": str(person_model.user_id),
            "name": person_model.name,
            "email": person_model.email,
            "phone_number": person_model.phone_number,
            "created_at": person_model.created_at.isoformat(),
            "updated_at": person_model.updated_at.isoformat(),
        }

    def update_person(
        self,
        person_id: UUID,
        user_id: UUID,
        name: Optional[str] = None,
        email: Optional[str] = None,
        phone_number: Optional[str] = None,
    ) -> Optional[dict]:
        """
        Update a person.

        Args:
            person_id: Person ID
            user_id: User ID (for ownership verification)
            name: New name
            email: New email
            phone_number: New phone number

        Returns:
            Updated person dict or None
        """
        # Verify ownership
        existing = self.person_repo.get_person(person_id, user_id)
        if not existing:
            return None

        # Convert to entity and validate updates
        person_entity = self.person_repo.person_to_entity(existing)
        person_entity.update(name=name, email=email, phone_number=phone_number)

        # Update in database
        person_model = self.person_repo.update_person(
            person_id=person_id,
            name=person_entity.name if name is not None else None,
            email=person_entity.email if email is not None else None,
            phone_number=person_entity.phone_number if phone_number is not None else None,
        )

        if not person_model:
            return None

        return {
            "id": str(person_model.id),
            "user_id": str(person_model.user_id),
            "name": person_model.name,
            "email": person_model.email,
            "phone_number": person_model.phone_number,
            "created_at": person_model.created_at.isoformat(),
            "updated_at": person_model.updated_at.isoformat(),
        }

    def delete_person(self, person_id: UUID, user_id: UUID) -> bool:
        """
        Delete a person.

        Args:
            person_id: Person ID
            user_id: User ID (for ownership verification)

        Returns:
            True if deleted, False if not found
        """
        # Verify ownership
        existing = self.person_repo.get_person(person_id, user_id)
        if not existing:
            return False

        return self.person_repo.delete_person(person_id)
