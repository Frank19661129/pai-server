"""
User settings repository for database operations.
Part of Infrastructure layer.
"""
from typing import Optional
from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Session
from app.infrastructure.database.models import UserSettingsModel


class UserSettingsRepository:
    """
    Repository for user settings operations.
    Manages calendar preferences and other user settings.
    """

    def __init__(self, db: Session):
        self.db = db

    def create_default_settings(self, user_id: UUID) -> UserSettingsModel:
        """
        Create default settings for a new user.

        Args:
            user_id: User's UUID

        Returns:
            Created UserSettingsModel
        """
        settings = UserSettingsModel(
            user_id=user_id,
            primary_calendar_provider=None,
            language="nl",
            timezone="Europe/Amsterdam",
        )

        self.db.add(settings)
        self.db.commit()
        self.db.refresh(settings)
        return settings

    def get_settings(self, user_id: UUID) -> Optional[UserSettingsModel]:
        """
        Get settings for a user.

        Args:
            user_id: User's UUID

        Returns:
            UserSettingsModel if found, None otherwise
        """
        return (
            self.db.query(UserSettingsModel)
            .filter(UserSettingsModel.user_id == user_id)
            .first()
        )

    def get_or_create_settings(self, user_id: UUID) -> UserSettingsModel:
        """
        Get settings for a user, creating default if not exists.

        Args:
            user_id: User's UUID

        Returns:
            UserSettingsModel
        """
        settings = self.get_settings(user_id)
        if not settings:
            settings = self.create_default_settings(user_id)
        return settings

    def update_primary_provider(
        self, user_id: UUID, provider: Optional[str]
    ) -> UserSettingsModel:
        """
        Update primary calendar provider for a user.

        Args:
            user_id: User's UUID
            provider: Provider name (google, microsoft, or None)

        Returns:
            Updated UserSettingsModel
        """
        settings = self.get_or_create_settings(user_id)
        settings.primary_calendar_provider = provider
        settings.updated_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(settings)
        return settings

    def update_language(self, user_id: UUID, language: str) -> UserSettingsModel:
        """
        Update language preference for a user.

        Args:
            user_id: User's UUID
            language: Language code (nl, en)

        Returns:
            Updated UserSettingsModel
        """
        settings = self.get_or_create_settings(user_id)
        settings.language = language
        settings.updated_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(settings)
        return settings

    def update_timezone(self, user_id: UUID, timezone: str) -> UserSettingsModel:
        """
        Update timezone preference for a user.

        Args:
            user_id: User's UUID
            timezone: Timezone string (e.g., "Europe/Amsterdam")

        Returns:
            Updated UserSettingsModel
        """
        settings = self.get_or_create_settings(user_id)
        settings.timezone = timezone
        settings.updated_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(settings)
        return settings
