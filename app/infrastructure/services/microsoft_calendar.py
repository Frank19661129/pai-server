"""
Microsoft Calendar API service (Graph API).
Part of Infrastructure layer.
"""
import httpx
from typing import Optional
from datetime import datetime
from app.domain.entities.calendar_event import CalendarEvent


class MicrosoftCalendarService:
    """
    Microsoft Calendar API service using Microsoft Graph API.
    Provides calendar operations for Office 365 calendars.
    """

    BASE_URL = "https://graph.microsoft.com/v1.0"

    def __init__(self, access_token: str):
        self.access_token = access_token
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

    async def list_calendars(self) -> list[dict]:
        """List all calendars for the authenticated user."""
        url = f"{self.BASE_URL}/me/calendars"

        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers)

            if response.status_code != 200:
                raise Exception(f"Failed to list calendars: {response.text}")

            data = response.json()
            return data.get("value", [])

    async def list_events(
        self,
        calendar_id: Optional[str] = None,
        max_results: int = 100,
        time_min: Optional[datetime] = None,
    ) -> list[CalendarEvent]:
        """List events from a calendar."""
        # Use default calendar if not specified
        if calendar_id:
            url = f"{self.BASE_URL}/me/calendars/{calendar_id}/events"
        else:
            url = f"{self.BASE_URL}/me/calendar/events"

        params = {
            "$top": max_results,
            "$orderby": "start/dateTime",
        }

        if time_min:
            # Filter events starting after time_min
            params["$filter"] = f"start/dateTime ge '{time_min.isoformat()}'"

        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers, params=params)

            if response.status_code != 200:
                raise Exception(f"Failed to list events: {response.text}")

            data = response.json()
            events = []

            for item in data.get("value", []):
                event = self._parse_event(item)
                if event:
                    events.append(event)

            return events

    async def create_event(
        self,
        event: CalendarEvent,
        calendar_id: Optional[str] = None,
    ) -> CalendarEvent:
        """Create a new calendar event."""
        if calendar_id:
            url = f"{self.BASE_URL}/me/calendars/{calendar_id}/events"
        else:
            url = f"{self.BASE_URL}/me/calendar/events"

        body = {
            "subject": event.title,
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
            body["body"] = {
                "contentType": "text",
                "content": event.description,
            }

        if event.location:
            body["location"] = {"displayName": event.location}

        if event.attendees:
            body["attendees"] = [
                {
                    "emailAddress": {"address": email},
                    "type": "required",
                }
                for email in event.attendees
            ]

        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=self.headers, json=body)

            if response.status_code not in [200, 201]:
                raise Exception(f"Failed to create event: {response.text}")

            data = response.json()
            return self._parse_event(data)

    async def update_event(
        self,
        event_id: str,
        event: CalendarEvent,
    ) -> CalendarEvent:
        """Update an existing calendar event."""
        url = f"{self.BASE_URL}/me/events/{event_id}"

        body = {
            "subject": event.title,
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
            body["body"] = {
                "contentType": "text",
                "content": event.description,
            }

        if event.location:
            body["location"] = {"displayName": event.location}

        async with httpx.AsyncClient() as client:
            response = await client.patch(url, headers=self.headers, json=body)

            if response.status_code != 200:
                raise Exception(f"Failed to update event: {response.text}")

            data = response.json()
            return self._parse_event(data)

    async def delete_event(self, event_id: str) -> bool:
        """Delete a calendar event."""
        url = f"{self.BASE_URL}/me/events/{event_id}"

        async with httpx.AsyncClient() as client:
            response = await client.delete(url, headers=self.headers)

            return response.status_code == 204

    def _parse_event(self, data: dict) -> Optional[CalendarEvent]:
        """Parse Microsoft Graph event data to domain entity."""
        try:
            # Get start/end times
            start = data.get("start", {})
            end = data.get("end", {})

            start_time = datetime.fromisoformat(start["dateTime"])
            end_time = datetime.fromisoformat(end["dateTime"])

            # Parse attendees
            attendees = []
            for attendee in data.get("attendees", []):
                email_address = attendee.get("emailAddress", {})
                if "address" in email_address:
                    attendees.append(email_address["address"])

            # Parse description
            body = data.get("body", {})
            description = body.get("content") if body.get("contentType") == "text" else None

            # Parse location
            location_data = data.get("location", {})
            location = location_data.get("displayName") if location_data else None

            return CalendarEvent(
                id=data.get("id"),
                title=data.get("subject", "(No title)"),
                description=description,
                start_time=start_time,
                end_time=end_time,
                location=location,
                provider="microsoft",
                provider_calendar_id=None,
                attendees=attendees,
                is_all_day=data.get("isAllDay", False),
            )
        except Exception:
            # Skip events that can't be parsed
            return None
