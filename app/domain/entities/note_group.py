"""
NoteGroup domain entity.
Part of Domain layer - contains business logic and rules.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from uuid import UUID


@dataclass
class NoteGroup:
    """
    NoteGroup domain entity.
    Represents a folder/category for organizing notes.
    """

    id: Optional[UUID]
    user_id: UUID
    name: str
    color: str
    icon: Optional[str]
    sort_order: int
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    # Valid color values
    VALID_COLORS = ["blue", "red", "green", "yellow", "purple", "orange", "pink", "gray"]

    @classmethod
    def create(
        cls,
        user_id: UUID,
        name: str,
        color: str = "blue",
        icon: Optional[str] = None,
        sort_order: int = 0,
    ) -> "NoteGroup":
        """
        Factory method to create a new note group.
        Enforces business rules at creation time.
        """
        # Validate name
        if not name or len(name.strip()) == 0:
            raise ValueError("Note group name cannot be empty")

        if len(name) > 255:
            raise ValueError("Note group name cannot exceed 255 characters")

        # Validate color
        if color not in cls.VALID_COLORS:
            raise ValueError(
                f"Invalid color: {color}. Must be one of: {', '.join(cls.VALID_COLORS)}"
            )

        # Validate icon length if provided
        if icon and len(icon) > 50:
            raise ValueError("Icon cannot exceed 50 characters")

        return cls(
            id=None,  # Will be set by repository
            user_id=user_id,
            name=name.strip(),
            color=color,
            icon=icon,
            sort_order=sort_order,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

    def update_name(self, new_name: str) -> None:
        """Update the group name."""
        if not new_name or len(new_name.strip()) == 0:
            raise ValueError("Note group name cannot be empty")

        if len(new_name) > 255:
            raise ValueError("Note group name cannot exceed 255 characters")

        self.name = new_name.strip()
        self.updated_at = datetime.utcnow()

    def update_color(self, new_color: str) -> None:
        """Update the group color."""
        if new_color not in self.VALID_COLORS:
            raise ValueError(
                f"Invalid color: {new_color}. Must be one of: {', '.join(self.VALID_COLORS)}"
            )

        self.color = new_color
        self.updated_at = datetime.utcnow()

    def update_icon(self, new_icon: Optional[str]) -> None:
        """Update the group icon."""
        if new_icon and len(new_icon) > 50:
            raise ValueError("Icon cannot exceed 50 characters")

        self.icon = new_icon
        self.updated_at = datetime.utcnow()

    def update_sort_order(self, new_order: int) -> None:
        """Update the sort order."""
        self.sort_order = new_order
        self.updated_at = datetime.utcnow()
