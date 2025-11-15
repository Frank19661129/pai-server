"""
InboxItem domain entity.
Part of Domain layer - contains business logic and rules.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID
from enum import Enum


class InboxItemType(str, Enum):
    """Types of inbox items."""
    EMAIL = "email"
    CALENDAR_EVENT = "calendar_event"
    MESSAGE = "message"
    NOTIFICATION = "notification"
    WEB_CLIP = "web_clip"
    FILE = "file"
    MANUAL = "manual"


class InboxStatus(str, Enum):
    """Status of inbox item processing."""
    UNPROCESSED = "unprocessed"
    PENDING_REVIEW = "pending_review"
    ACCEPTED = "accepted"
    MODIFIED = "modified"
    REJECTED = "rejected"
    ARCHIVED = "archived"


class Priority(str, Enum):
    """Priority levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


@dataclass
class AISuggestion:
    """AI suggestion for processing an inbox item."""
    action: str  # create_task, create_note, create_event, archive, delegate
    confidence: float  # 0.0 to 1.0
    reasoning: str
    suggested_data: Dict[str, Any]
    alternative_actions: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class LinkedItem:
    """Reference to an item created from inbox."""
    target_type: str  # task, note, event
    target_id: UUID
    created_at: datetime


@dataclass
class InboxItem:
    """
    InboxItem domain entity.
    Represents an item in the inbox that needs to be processed.
    """

    id: Optional[UUID]
    user_id: UUID
    type: InboxItemType
    source: str
    status: InboxStatus
    priority: Priority
    subject: Optional[str]
    content: Optional[str]
    raw_data: Dict[str, Any] = field(default_factory=dict)
    ai_suggestion: Optional[Dict[str, Any]] = None
    user_decision: Optional[Dict[str, Any]] = None
    linked_items: List[Dict[str, Any]] = field(default_factory=list)
    processed_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    @classmethod
    def create(
        cls,
        user_id: UUID,
        type: InboxItemType,
        source: str,
        subject: Optional[str] = None,
        content: Optional[str] = None,
        raw_data: Optional[Dict[str, Any]] = None,
        priority: Priority = Priority.MEDIUM,
    ) -> "InboxItem":
        """
        Factory method to create a new inbox item.
        Enforces business rules at creation time.
        """
        if not subject and not content:
            raise ValueError("Inbox item must have either subject or content")

        return cls(
            id=None,  # Will be set by repository
            user_id=user_id,
            type=type,
            source=source,
            status=InboxStatus.UNPROCESSED,
            priority=priority,
            subject=subject,
            content=content,
            raw_data=raw_data or {},
            ai_suggestion=None,
            user_decision=None,
            linked_items=[],
            processed_at=None,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

    def set_ai_suggestion(self, suggestion: Dict[str, Any]) -> None:
        """Set AI suggestion for processing."""
        self.ai_suggestion = suggestion
        self.status = InboxStatus.PENDING_REVIEW
        self.updated_at = datetime.utcnow()

    def accept_suggestion(self) -> None:
        """Accept the AI suggestion."""
        if not self.ai_suggestion:
            raise ValueError("No AI suggestion to accept")

        self.status = InboxStatus.ACCEPTED
        self.user_decision = {"action": "accepted", "timestamp": datetime.utcnow().isoformat()}
        self.processed_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def modify_and_accept(self, modifications: Dict[str, Any]) -> None:
        """Accept with modifications."""
        self.status = InboxStatus.MODIFIED
        self.user_decision = {
            "action": "modified",
            "modifications": modifications,
            "timestamp": datetime.utcnow().isoformat()
        }
        self.processed_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def reject(self, reason: Optional[str] = None) -> None:
        """Reject the item/suggestion."""
        self.status = InboxStatus.REJECTED
        self.user_decision = {
            "action": "rejected",
            "reason": reason,
            "timestamp": datetime.utcnow().isoformat()
        }
        self.processed_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def archive(self) -> None:
        """Archive the item without processing."""
        self.status = InboxStatus.ARCHIVED
        self.processed_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def add_linked_item(self, target_type: str, target_id: UUID) -> None:
        """Add a reference to a created item."""
        linked_item = {
            "target_type": target_type,
            "target_id": str(target_id),
            "created_at": datetime.utcnow().isoformat()
        }
        self.linked_items.append(linked_item)
        self.updated_at = datetime.utcnow()

    def is_processed(self) -> bool:
        """Check if the item has been processed."""
        return self.status in [
            InboxStatus.ACCEPTED,
            InboxStatus.MODIFIED,
            InboxStatus.REJECTED,
            InboxStatus.ARCHIVED
        ]
