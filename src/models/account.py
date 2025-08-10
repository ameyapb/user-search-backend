from abc import ABC, abstractmethod  # This will make sure - one cannot directly initialise Account.
from datetime import datetime, timezone
from enum import Enum
from typing import Set, Dict, Optional
import uuid


class AccountType(Enum):
    SERVICE_PROVIDER = "service_provider"
    SERVICE_CONSUMER = "service_consumer"
    ADMIN = "admin"


class Account(ABC):
    """Base Account class for all user types"""

    def __init__(
        self,
        name: str,
        email: str,
        account_type: AccountType,
        address: Optional[Dict[str, str]] = None,
        tags: Optional[Set[str]] = None,
    ):
        self.id = self._generate_id()
        self.name = name
        self.email = email
        self.account_type = account_type
        self.address = address or {}
        self.tags = tags or set()  # Very important! Search is dependant on this
        self.created_at = datetime.now(timezone.utc)
        self.updated_at = datetime.now(timezone.utc)

    @abstractmethod
    def get_role_specific_info(self) -> Dict:
        """Each account type must implement role-specific information"""
        pass

    def _generate_id(self) -> str:
        """Generate a unique ID for the account"""
        return str(uuid.uuid4())

    def add_tag(self, tag: str) -> None:
        """Add a tag if it doesn't already exist"""
        if tag:
            self.tags.add(tag)
            self.updated_at = datetime.now(timezone.utc)

    def remove_tag(self, tag: str) -> None:
        """Remove a tag if it exists"""
        self.tags.discard(tag)
        self.updated_at = datetime.now(timezone.utc)

    def update_tags(self, new_tags: Set[str]) -> None:
        """Replace all tags with new set"""
        self.tags = new_tags or set()
        self.updated_at = datetime.now(timezone.utc)

    def to_dict(self) -> Dict:
        """Convert account to dictionary"""
        return {
            "name": self.name,
            "email": self.email,
            "address": self.address,
            "tags": list(self.tags),  # Convert set to list for JSON serialization
            "account_type": self.account_type.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    def __repr__(self) -> str:
        account_type_str = self.account_type.value
        return f"<Account {self.name} ({account_type_str})>"
