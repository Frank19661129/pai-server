"""
Person domain entity.
Part of Domain layer - contains business logic and rules.
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID


@dataclass
class Person:
    """
    Person domain entity.
    Represents a person who can be assigned/delegated tasks.
    """

    id: Optional[UUID]
    user_id: UUID
    name: str
    email: Optional[str]
    phone_number: Optional[str]
    created_at: datetime
    updated_at: datetime

    @classmethod
    def create(
        cls,
        user_id: UUID,
        name: str,
        email: Optional[str] = None,
        phone_number: Optional[str] = None,
    ) -> "Person":
        """
        Factory method to create a new person.
        Enforces business rules at creation time.
        """
        # Validate name
        if not name or len(name.strip()) == 0:
            raise ValueError("Person name cannot be empty")

        if len(name) > 200:
            raise ValueError("Person name cannot exceed 200 characters")

        # Validate email if provided
        if email and len(email.strip()) > 0:
            email = email.strip()
            if len(email) > 255:
                raise ValueError("Email cannot exceed 255 characters")
            # Basic email validation
            if "@" not in email or "." not in email.split("@")[-1]:
                raise ValueError("Invalid email format")
        else:
            email = None

        # Validate phone number if provided
        if phone_number and len(phone_number.strip()) > 0:
            phone_number = phone_number.strip()
            if len(phone_number) > 50:
                raise ValueError("Phone number cannot exceed 50 characters")
        else:
            phone_number = None

        now = datetime.utcnow()

        return cls(
            id=None,  # Will be set by repository
            user_id=user_id,
            name=name.strip(),
            email=email,
            phone_number=phone_number,
            created_at=now,
            updated_at=now,
        )

    def update(
        self,
        name: Optional[str] = None,
        email: Optional[str] = None,
        phone_number: Optional[str] = None,
    ) -> None:
        """Update person details with validation."""
        if name is not None:
            if not name or len(name.strip()) == 0:
                raise ValueError("Person name cannot be empty")
            if len(name) > 200:
                raise ValueError("Person name cannot exceed 200 characters")
            self.name = name.strip()

        if email is not None:
            if email and len(email.strip()) > 0:
                email = email.strip()
                if len(email) > 255:
                    raise ValueError("Email cannot exceed 255 characters")
                if "@" not in email or "." not in email.split("@")[-1]:
                    raise ValueError("Invalid email format")
                self.email = email
            else:
                self.email = None

        if phone_number is not None:
            if phone_number and len(phone_number.strip()) > 0:
                phone_number = phone_number.strip()
                if len(phone_number) > 50:
                    raise ValueError("Phone number cannot exceed 50 characters")
                self.phone_number = phone_number
            else:
                self.phone_number = None

        self.updated_at = datetime.utcnow()
