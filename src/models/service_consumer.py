# src/models/service_consumer.py
from typing import Set, Dict, Optional, List
from datetime import datetime, timezone
from .account import Account, AccountType


class ServiceConsumer(Account):
    """Service Consumer account with additional consumer-specific fields"""

    def __init__(
        self,
        name: str,
        email: str,
        address: Dict[str, str] = None,
        tags: Set[str] = None,
        preferred_budget: Optional[float] = None,
        service_history: Optional[List[Dict]] = None,
    ):
        super().__init__(name, email, AccountType.SERVICE_CONSUMER, address, tags)
        self.preferred_budget = preferred_budget
        self.service_history = service_history or []

    def set_preferred_budget(self, budget: float) -> None:
        """Set preferred budget"""
        if budget >= 0:
            self.preferred_budget = budget
            self.updated_at = datetime.now(timezone.utc)
        else:
            raise ValueError("Budget must be non-negative")

    def add_service_to_history(self, service_data: Dict) -> None:
        """Add a service to the history"""
        if service_data:
            service_entry = {**service_data, "added_at": datetime.now(timezone.utc).isoformat()}
            self.service_history.append(service_entry)
            self.updated_at = datetime.now(timezone.utc)

    def to_dict(self) -> Dict:
        """Override parent to include consumer-specific fields"""
        data = super().to_dict()
        data.update({"preferred_budget": self.preferred_budget, "service_history": self.service_history})
        return data

    def __repr__(self) -> str:
        budget_str = f"Budget: ${self.preferred_budget}" if self.preferred_budget else "No budget set"
        return f"<ServiceConsumer {self.name} - {budget_str}>"

    def get_role_specific_info(self) -> Dict:
        """Return consumer-specific information"""
        return {
            "role": "service_consumer",
            "preferred_budget": self.preferred_budget,
            "service_history_count": len(self.service_history),
            "interests": list(self.tags),
        }
