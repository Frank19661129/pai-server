"""
SQLAlchemy database models.
Part of Infrastructure layer - persistence models.
"""
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from app.infrastructure.database.session import Base


class UserModel(Base):
    """
    User database model (SQLAlchemy ORM).
    Maps to the 'users' table in PostgreSQL.
    """

    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    full_name = Column(String(255), nullable=False)
    provider = Column(String(50), nullable=False)  # google, microsoft, local
    hashed_password = Column(String(255), nullable=True)  # Only for local users
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    oauth_tokens = relationship("OAuthTokenModel", back_populates="user", cascade="all, delete-orphan")
    settings = relationship("UserSettingsModel", back_populates="user", uselist=False, cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<UserModel(id={self.id}, email={self.email}, provider={self.provider})>"


class OAuthTokenModel(Base):
    """
    OAuth token storage for calendar providers.
    Maps to the 'oauth_tokens' table in PostgreSQL.
    """

    __tablename__ = "oauth_tokens"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    provider = Column(String(50), nullable=False)  # google, microsoft
    access_token = Column(Text, nullable=False)  # Encrypted in production
    refresh_token = Column(Text, nullable=True)  # Encrypted in production
    token_type = Column(String(50), default="Bearer", nullable=False)
    expires_at = Column(DateTime, nullable=True)
    scope = Column(Text, nullable=True)  # Space-separated scopes
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("UserModel", back_populates="oauth_tokens")

    def __repr__(self) -> str:
        return f"<OAuthTokenModel(user_id={self.user_id}, provider={self.provider})>"


class UserSettingsModel(Base):
    """
    User settings for calendar and other preferences.
    Maps to the 'user_settings' table in PostgreSQL.
    """

    __tablename__ = "user_settings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), unique=True, nullable=False, index=True)
    primary_calendar_provider = Column(String(50), nullable=True)  # google or microsoft
    language = Column(String(10), default="nl", nullable=False)  # nl, en
    timezone = Column(String(50), default="Europe/Amsterdam", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("UserModel", back_populates="settings")

    def __repr__(self) -> str:
        return f"<UserSettingsModel(user_id={self.user_id}, primary_provider={self.primary_calendar_provider})>"
