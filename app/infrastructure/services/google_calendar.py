"""
Google Calendar API service.
Part of Infrastructure layer.
"""
import httpx
from typing import Optional
from datetime import datetime
from app.domain.entities.calendar_event import CalendarEvent


class GoogleCalendarService:
    """
    Google Calendar API service.
    Provides calendar operations using Google Calendar API v3.
    """

    BASE_URL = "https://www.googleapis.com/calendar/v3"

    def __init__(self, access_token: str):
        self.access_token = access_token
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

    async def list_calendars(self) -> list[dict]:
        """List all calendars for the authenticated user."""
        url = f"{self.BASE_URL}/users/me/calendarList"

        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers)

            if response.status_code != 200:
                raise Exception(f"Failed to list calendars: {response.text}")

            data = response.json()
            return data.get("items", [])

    async def list_events(
        self,
        calendar_id: str = "primary",
        max_results: int = 100,
        time_min: Optional[datetime] = None,
    ) -> list[CalendarEvent]:
        """List events from a calendar."""
        url = f"{self.BASE_URL}/calendars/{calendar_id}/events"

        params = {
            "maxResults": max_results,
            "singleEvents": "true",
            "orderBy": "startTime",
        }

        if time_min:
            params["timeMin"] = time_min.isoformat() + "Z"

        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers, params=params)

            if response.status_code != 200:
                raise Exception(f"Failed to list events: {response.text}")

            data = response.json()
            events = []

            for item in data.get("items", []):
                event = self._parse_event(item, calendar_id)
                if event:
                    events.append(event)

            return events

    async def create_event(
        self,
        event: CalendarEvent,
        calendar_id: str = "primary",
    ) -> CalendarEvent:
        """Create a new calendar event."""
        url = f"{self.BASE_URL}/calendars/{calendar_id}/events"

        body = {
            "summary": event.title,
            "start": {
                "dateTime": event.start_time.isoformat(),
                "timeZone": "Europe/Amsterdam",
            },
            "end": {
                "dateTime": event.end_time.isoformat(),
                "timeZone": "Europe/Amsterdam",
            },
        }

        if event.description:
            body["description"] = event.description

        if event.location:
            body["location"] = event.location

        if event.attendees:
            body["attendees"] = [{"email": email} for email in event.attendees]

        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=self.headers, json=body)

            if response.status_code not in [200, 201]:
                raise Exception(f"Failed to create event: {response.text}")

            data = response.json()
            return self._parse_event(data, calendar_id)

    async def update_event(
        self,
        event_id: str,
        event: CalendarEvent,
        calendar_id: str = "primary",
    ) -> CalendarEvent:
        """Update an existing calendar event."""
        url = f"{self.BASE_URL}/calendars/{calendar_id}/events/{event_id}"

        body = {
            "summary": event.title,
            "start": {
                "dateTime": event.start_time.isoformat(),
                "timeZone": "Europe/Amsterdam",
            },
            "end": {
                "dateTime": event.end_time.isoformat(),
                "timeZone": "Europe/Amsterdam",
            },
        }

        if event.description:
            body["description"] = event.description

        if event.location:
            body["location"] = event.location

        async with httpx.AsyncClient() as client:
            response = await client.put(url, headers=self.headers, json=body)

            if response.status_code != 200:
                raise Exception(f"Failed to update event: {response.text}")

            data = response.json()
            return self._parse_event(data, calendar_id)

    async def delete_event(
        self,
        event_id: str,
        calendar_id: str = "primary",
    ) -> bool:
        """Delete a calendar event."""
        url = f"{self.BASE_URL}/calendars/{calendar_id}/events/{event_id}"

        async with httpx.AsyncClient() as client:
            response = await client.delete(url, headers=self.headers)

            return response.status_code == 204

    def _parse_event(self, data: dict, calendar_id: str) -> Optional[CalendarEvent]:
        """Parse Google Calendar event data to domain entity."""
        try:
            # Get start/end times
            start = data.get("start", {})
            end = data.get("end", {})

            # Handle dateTime vs date (all-day events)
            if "dateTime" in start:
                start_time = datetime.fromisoformat(start["dateTime"].replace("Z", "+00:00"))
                end_time = datetime.fromisoformat(end["dateTime"].replace("Z", "+00:00"))
                is_all_day = False
            else:
                # All-day event
                start_time = datetime.fromisoformat(start["date"])
                end_time = datetime.fromisoformat(end["date"])
                is_all_day = True

            # Parse attendees
            attendees = []
            for attendee in data.get("attendees", []):
                attendees.append(attendee.get("email"))

            return CalendarEvent(
                id=data.get("id"),
                title=data.get("summary", "(No title)"),
                description=data.get("description"),
                start_time=start_time,
                end_time=end_time,
                location=data.get("location"),
                provider="google",
                provider_calendar_id=calendar_id,
                attendees=attendees,
                is_all_day=is_all_day,
            )
        except Exception:
            # Skip events that can't be parsed
            return None
