from typing import Set, Dict, Optional
from .account import Account, AccountType
from datetime import datetime, timezone


class ServiceProvider(Account):
    """Service Provider account with additional provider-specific fields"""

    def __init__(
        self,
        name: str,
        email: str,
        address: Dict[str, str],
        tags: Set[str] = None,
        hourly_rate: Optional[float] = None,
        availability: Optional[str] = None,
    ):
        super().__init__(name, email, AccountType.SERVICE_PROVIDER, address, tags)
        self.hourly_rate = hourly_rate
        self.availability = availability

    def set_hourly_rate(self, rate: Optional[float]) -> None:
        """Set hourly rate"""
        if rate is None:
            self.hourly_rate = None
            self.updated_at = datetime.now(timezone.utc)
        elif rate >= 0:
            self.hourly_rate = rate
            self.updated_at = datetime.now(timezone.utc)
        else:
            raise ValueError("Hourly rate must be non-negative")

    def update_availability(self, availability: str) -> None:
        """Update availability information"""
        self.availability = availability
        self.updated_at = datetime.now(timezone.utc)

    def to_dict(self) -> Dict:
        """Override parent to include provider-specific fields"""
        data = super().to_dict()
        data.update({"hourly_rate": self.hourly_rate, "availability": self.availability})
        return data

    def __repr__(self) -> str:
        rate_str = f"${self.hourly_rate}/hr" if self.hourly_rate is not None else "Rate not set"
        return f"<ServiceProvider {self.name} - {rate_str}>"

    def get_role_specific_info(self) -> Dict:
        """Return provider-specific information"""
        return {
            "role": "service_provider",
            "hourly_rate": self.hourly_rate,
            "availability": self.availability,
            "services_offered": list(self.tags),
        }
