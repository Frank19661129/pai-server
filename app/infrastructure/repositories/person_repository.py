"""
Person repository - data access layer.
Part of Infrastructure layer.
"""
from typing import Optional, List
from uuid import UUID
from sqlalchemy.orm import Session

from app.infrastructure.database.models import PersonModel
from app.domain.entities.person import Person


class PersonRepository:
    """Repository for person persistence operations."""

    def __init__(self, db: Session):
        self.db = db

    def create_person(
        self,
        user_id: UUID,
        name: str,
        email: Optional[str] = None,
        phone_number: Optional[str] = None,
    ) -> PersonModel:
        """
        Create a new person.

        Args:
            user_id: User ID
            name: Person name
            email: Email address
            phone_number: Phone number

        Returns:
            Created PersonModel
        """
        person = PersonModel(
            user_id=user_id,
            name=name,
            email=email,
            phone_number=phone_number,
        )

        self.db.add(person)
        self.db.commit()
        self.db.refresh(person)

        return person

    def get_person(
        self,
        person_id: UUID,
        user_id: Optional[UUID] = None,
    ) -> Optional[PersonModel]:
        """
        Get a person by ID.

        Args:
            person_id: Person ID
            user_id: Optional user ID to verify ownership

        Returns:
            PersonModel or None
        """
        query = self.db.query(PersonModel).filter(PersonModel.id == person_id)

        if user_id:
            query = query.filter(PersonModel.user_id == user_id)

        return query.first()

    def get_user_persons(
        self,
        user_id: UUID,
        limit: int = 100,
        offset: int = 0,
    ) -> List[PersonModel]:
        """
        Get all persons for a user.

        Args:
            user_id: User ID
            limit: Maximum number of results
            offset: Offset for pagination

        Returns:
            List of PersonModel
        """
        persons = (
            self.db.query(PersonModel)
            .filter(PersonModel.user_id == user_id)
            .order_by(PersonModel.name)
            .limit(limit)
            .offset(offset)
            .all()
        )

        return persons

    def find_person_by_name(
        self,
        user_id: UUID,
        name: str,
    ) -> Optional[PersonModel]:
        """
        Find a person by name (case-insensitive).

        Args:
            user_id: User ID
            name: Person name to search

        Returns:
            PersonModel or None
        """
        return (
            self.db.query(PersonModel)
            .filter(PersonModel.user_id == user_id)
            .filter(PersonModel.name.ilike(name))
            .first()
        )

    def update_person(
        self,
        person_id: UUID,
        name: Optional[str] = None,
        email: Optional[str] = None,
        phone_number: Optional[str] = None,
    ) -> Optional[PersonModel]:
        """
        Update a person.

        Args:
            person_id: Person ID
            name: New name
            email: New email
            phone_number: New phone number

        Returns:
            Updated PersonModel or None
        """
        person = self.db.query(PersonModel).filter(PersonModel.id == person_id).first()

        if not person:
            return None

        if name is not None:
            person.name = name

        if email is not None:
            person.email = email

        if phone_number is not None:
            person.phone_number = phone_number

        self.db.commit()
        self.db.refresh(person)

        return person

    def delete_person(self, person_id: UUID) -> bool:
        """
        Delete a person.

        Args:
            person_id: Person ID

        Returns:
            True if deleted, False if not found
        """
        person = self.db.query(PersonModel).filter(PersonModel.id == person_id).first()

        if not person:
            return False

        self.db.delete(person)
        self.db.commit()

        return True

    def person_to_entity(self, model: PersonModel) -> Person:
        """
        Convert PersonModel to domain entity.

        Args:
            model: PersonModel from database

        Returns:
            Person domain entity
        """
        return Person(
            id=model.id,
            user_id=model.user_id,
            name=model.name,
            email=model.email,
            phone_number=model.phone_number,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
