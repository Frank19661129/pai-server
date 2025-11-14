"""
OAuth token repository for database operations.
Part of Infrastructure layer.
"""
from typing import Optional
from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Session
from app.infrastructure.database.models import OAuthTokenModel


class OAuthTokenRepository:
    """
    Repository for OAuth token storage operations.
    Manages calendar provider tokens per user.
    """

    def __init__(self, db: Session):
        self.db = db

    def save_token(
        self,
        user_id: UUID,
        provider: str,
        access_token: str,
        refresh_token: Optional[str] = None,
        expires_at: Optional[datetime] = None,
        scope: Optional[str] = None,
    ) -> OAuthTokenModel:
        """
        Save or update OAuth token for a user and provider.

        Args:
            user_id: User's UUID
            provider: Provider name (google, microsoft)
            access_token: OAuth access token
            refresh_token: OAuth refresh token (optional)
            expires_at: Token expiration datetime (optional)
            scope: Space-separated scopes (optional)

        Returns:
            Saved OAuthTokenModel
        """
        # Check if token already exists
        existing = self.get_token(user_id, provider)

        if existing:
            # Update existing token
            existing.access_token = access_token
            existing.refresh_token = refresh_token
            existing.expires_at = expires_at
            existing.scope = scope
            existing.updated_at = datetime.utcnow()
            token = existing
        else:
            # Create new token
            token = OAuthTokenModel(
                user_id=user_id,
                provider=provider,
                access_token=access_token,
                refresh_token=refresh_token,
                expires_at=expires_at,
                scope=scope,
            )
            self.db.add(token)

        self.db.commit()
        self.db.refresh(token)
        return token

    def get_token(self, user_id: UUID, provider: str) -> Optional[OAuthTokenModel]:
        """
        Get OAuth token for a user and provider.

        Args:
            user_id: User's UUID
            provider: Provider name (google, microsoft)

        Returns:
            OAuthTokenModel if found, None otherwise
        """
        return (
            self.db.query(OAuthTokenModel)
            .filter(
                OAuthTokenModel.user_id == user_id,
                OAuthTokenModel.provider == provider,
            )
            .first()
        )

    def delete_token(self, user_id: UUID, provider: str) -> bool:
        """
        Delete OAuth token for a user and provider.

        Args:
            user_id: User's UUID
            provider: Provider name (google, microsoft)

        Returns:
            True if deleted, False if not found
        """
        token = self.get_token(user_id, provider)
        if not token:
            return False

        self.db.delete(token)
        self.db.commit()
        return True

    def get_all_tokens(self, user_id: UUID) -> list[OAuthTokenModel]:
        """
        Get all OAuth tokens for a user.

        Args:
            user_id: User's UUID

        Returns:
            List of OAuthTokenModel
        """
        return (
            self.db.query(OAuthTokenModel)
            .filter(OAuthTokenModel.user_id == user_id)
            .all()
        )

    def is_token_expired(self, token: OAuthTokenModel) -> bool:
        """
        Check if a token is expired.

        Args:
            token: OAuthTokenModel to check

        Returns:
            True if expired or no expiration set, False otherwise
        """
        if not token.expires_at:
            return False  # No expiration means it doesn't expire

        return datetime.utcnow() >= token.expires_at
