"""
Calendar event domain entity.
Part of Domain layer - contains business logic and rules.
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class CalendarEvent:
    """
    Calendar event domain entity.
    Provider-agnostic representation of a calendar event.
    """

    id: Optional[str]  # Provider-specific ID
    title: str
    description: Optional[str]
    start_time: datetime
    end_time: datetime
    location: Optional[str]
    provider: str  # google or microsoft
    provider_calendar_id: Optional[str]  # Which calendar the event is in
    attendees: list[str] = None  # Email addresses
    is_all_day: bool = False
    recurrence: Optional[str] = None  # Recurrence rule (RRULE format)
    reminder_minutes: Optional[int] = None  # Minutes before event

    def __post_init__(self):
        if self.attendees is None:
            self.attendees = []

    @classmethod
    def create(
        cls,
        title: str,
        start_time: datetime,
        end_time: datetime,
        provider: str,
        description: Optional[str] = None,
        location: Optional[str] = None,
        attendees: Optional[list[str]] = None,
        is_all_day: bool = False,
    ) -> "CalendarEvent":
        """
        Factory method to create a new calendar event.
        Enforces business rules at creation time.
        """
        # Validate title
        if not title or len(title.strip()) == 0:
            raise ValueError("Event title cannot be empty")

        # Validate times
        if end_time <= start_time:
            raise ValueError("End time must be after start time")

        # Validate provider
        if provider not in ["google", "microsoft"]:
            raise ValueError(f"Invalid provider: {provider}")

        return cls(
            id=None,  # Will be set by provider after creation
            title=title.strip(),
            description=description.strip() if description else None,
            start_time=start_time,
            end_time=end_time,
            location=location.strip() if location else None,
            provider=provider,
            provider_calendar_id=None,
            attendees=attendees or [],
            is_all_day=is_all_day,
            recurrence=None,
            reminder_minutes=None,
        )

    def duration_minutes(self) -> int:
        """Calculate event duration in minutes."""
        delta = self.end_time - self.start_time
        return int(delta.total_seconds() / 60)

    def is_in_future(self) -> bool:
        """Check if event is in the future."""
        return self.start_time > datetime.utcnow()

    def is_in_past(self) -> bool:
        """Check if event is in the past."""
        return self.end_time < datetime.utcnow()

    def is_ongoing(self) -> bool:
        """Check if event is currently ongoing."""
        now = datetime.utcnow()
        return self.start_time <= now <= self.end_time
