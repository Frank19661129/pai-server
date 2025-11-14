"""
Calendar event use cases.
Part of Application layer - orchestrates calendar CRUD operations.
"""
from typing import Optional
from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Session

from app.domain.entities.calendar_event import CalendarEvent
from app.infrastructure.services.google_calendar import GoogleCalendarService
from app.infrastructure.services.microsoft_calendar import MicrosoftCalendarService
from app.infrastructure.repositories.oauth_token_repository import OAuthTokenRepository
from app.infrastructure.repositories.user_settings_repository import UserSettingsRepository
from app.application.use_cases.calendar_oauth_use_cases import CalendarOAuthUseCases


class CalendarEventUseCases:
    """
    Use cases for calendar event CRUD operations.
    Handles multi-provider calendar operations.
    """

    def __init__(self, db: Session):
        self.db = db
        self.token_repo = OAuthTokenRepository(db)
        self.settings_repo = UserSettingsRepository(db)
        self.oauth_use_cases = CalendarOAuthUseCases(db)

    async def list_calendars(self, user_id: UUID, provider: Optional[str] = None) -> list[dict]:
        """
        List available calendars for a user.

        Args:
            user_id: User ID
            provider: Specific provider (google/microsoft) or None for primary

        Returns:
            List of calendars with id, name, provider
        """
        # Determine which provider to use
        if provider is None:
            settings = self.settings_repo.get_settings(user_id)
            provider = settings.primary_calendar_provider if settings else None

        if not provider:
            raise ValueError("No provider specified and no primary provider set")

        # Get valid access token
        access_token = await self.oauth_use_cases.refresh_token_if_needed(user_id, provider)

        # Get calendars from provider
        if provider == "google":
            service = GoogleCalendarService(access_token)
            calendars_data = await service.list_calendars()
            return [
                {
                    "id": cal["id"],
                    "name": cal.get("summary", "(No name)"),
                    "provider": "google",
                    "is_primary": cal.get("primary", False),
                }
                for cal in calendars_data
            ]
        elif provider == "microsoft":
            service = MicrosoftCalendarService(access_token)
            calendars_data = await service.list_calendars()
            return [
                {
                    "id": cal["id"],
                    "name": cal.get("name", "(No name)"),
                    "provider": "microsoft",
                    "is_primary": cal.get("isDefaultCalendar", False),
                }
                for cal in calendars_data
            ]
        else:
            raise ValueError(f"Unknown provider: {provider}")

    async def list_events(
        self,
        user_id: UUID,
        provider: Optional[str] = None,
        calendar_id: Optional[str] = None,
        max_results: int = 100,
        time_min: Optional[datetime] = None,
    ) -> list[CalendarEvent]:
        """
        List calendar events.

        Args:
            user_id: User ID
            provider: Specific provider or None for primary
            calendar_id: Specific calendar ID or None for default
            max_results: Maximum number of events to return
            time_min: Filter events starting after this time

        Returns:
            List of CalendarEvent objects
        """
        # Determine which provider to use
        if provider is None:
            settings = self.settings_repo.get_settings(user_id)
            provider = settings.primary_calendar_provider if settings else None

        if not provider:
            raise ValueError("No provider specified and no primary provider set")

        # Get valid access token
        access_token = await self.oauth_use_cases.refresh_token_if_needed(user_id, provider)

        # Get events from provider
        if provider == "google":
            service = GoogleCalendarService(access_token)
            events = await service.list_events(
                calendar_id=calendar_id or "primary",
                max_results=max_results,
                time_min=time_min,
            )
        elif provider == "microsoft":
            service = MicrosoftCalendarService(access_token)
            events = await service.list_events(
                calendar_id=calendar_id,
                max_results=max_results,
                time_min=time_min,
            )
        else:
            raise ValueError(f"Unknown provider: {provider}")

        return events

    async def create_event(
        self,
        user_id: UUID,
        title: str,
        start_time: datetime,
        end_time: datetime,
        description: Optional[str] = None,
        location: Optional[str] = None,
        attendees: Optional[list[str]] = None,
        is_all_day: bool = False,
        provider: Optional[str] = None,
        calendar_id: Optional[str] = None,
    ) -> CalendarEvent:
        """
        Create a new calendar event.

        Args:
            user_id: User ID
            title: Event title
            start_time: Event start time
            end_time: Event end time
            description: Event description
            location: Event location
            attendees: List of attendee email addresses
            is_all_day: Whether event is all-day
            provider: Specific provider or None for primary
            calendar_id: Specific calendar ID or None for default

        Returns:
            Created CalendarEvent
        """
        # Determine which provider to use
        if provider is None:
            settings = self.settings_repo.get_settings(user_id)
            provider = settings.primary_calendar_provider if settings else None

        if not provider:
            raise ValueError("No provider specified and no primary provider set")

        # Create domain entity (validates business rules)
        event = CalendarEvent.create(
            title=title,
            start_time=start_time,
            end_time=end_time,
            provider=provider,
            description=description,
            location=location,
            attendees=attendees,
            is_all_day=is_all_day,
        )

        # Get valid access token
        access_token = await self.oauth_use_cases.refresh_token_if_needed(user_id, provider)

        # Create event in provider
        if provider == "google":
            service = GoogleCalendarService(access_token)
            created_event = await service.create_event(
                event=event,
                calendar_id=calendar_id or "primary",
            )
        elif provider == "microsoft":
            service = MicrosoftCalendarService(access_token)
            created_event = await service.create_event(
                event=event,
                calendar_id=calendar_id,
            )
        else:
            raise ValueError(f"Unknown provider: {provider}")

        return created_event

    async def update_event(
        self,
        user_id: UUID,
        event_id: str,
        title: str,
        start_time: datetime,
        end_time: datetime,
        description: Optional[str] = None,
        location: Optional[str] = None,
        provider: Optional[str] = None,
        calendar_id: Optional[str] = None,
    ) -> CalendarEvent:
        """
        Update an existing calendar event.

        Args:
            user_id: User ID
            event_id: Provider-specific event ID
            title: Event title
            start_time: Event start time
            end_time: Event end time
            description: Event description
            location: Event location
            provider: Specific provider or None for primary
            calendar_id: Specific calendar ID (required for Google)

        Returns:
            Updated CalendarEvent
        """
        # Determine which provider to use
        if provider is None:
            settings = self.settings_repo.get_settings(user_id)
            provider = settings.primary_calendar_provider if settings else None

        if not provider:
            raise ValueError("No provider specified and no primary provider set")

        # Create domain entity (validates business rules)
        event = CalendarEvent.create(
            title=title,
            start_time=start_time,
            end_time=end_time,
            provider=provider,
            description=description,
            location=location,
        )
        event.id = event_id

        # Get valid access token
        access_token = await self.oauth_use_cases.refresh_token_if_needed(user_id, provider)

        # Update event in provider
        if provider == "google":
            service = GoogleCalendarService(access_token)
            updated_event = await service.update_event(
                event_id=event_id,
                event=event,
                calendar_id=calendar_id or "primary",
            )
        elif provider == "microsoft":
            service = MicrosoftCalendarService(access_token)
            updated_event = await service.update_event(
                event_id=event_id,
                event=event,
            )
        else:
            raise ValueError(f"Unknown provider: {provider}")

        return updated_event

    async def delete_event(
        self,
        user_id: UUID,
        event_id: str,
        provider: Optional[str] = None,
        calendar_id: Optional[str] = None,
    ) -> bool:
        """
        Delete a calendar event.

        Args:
            user_id: User ID
            event_id: Provider-specific event ID
            provider: Specific provider or None for primary
            calendar_id: Specific calendar ID (required for Google)

        Returns:
            True if deleted successfully
        """
        # Determine which provider to use
        if provider is None:
            settings = self.settings_repo.get_settings(user_id)
            provider = settings.primary_calendar_provider if settings else None

        if not provider:
            raise ValueError("No provider specified and no primary provider set")

        # Get valid access token
        access_token = await self.oauth_use_cases.refresh_token_if_needed(user_id, provider)

        # Delete event from provider
        if provider == "google":
            service = GoogleCalendarService(access_token)
            success = await service.delete_event(
                event_id=event_id,
                calendar_id=calendar_id or "primary",
            )
        elif provider == "microsoft":
            service = MicrosoftCalendarService(access_token)
            success = await service.delete_event(event_id=event_id)
        else:
            raise ValueError(f"Unknown provider: {provider}")

        return success
