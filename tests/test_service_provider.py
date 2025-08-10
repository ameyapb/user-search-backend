import pytest
from datetime import datetime, timezone
from src.models.service_provider import ServiceProvider
from src.models.account import AccountType

TEST_ADDRESS = {"city": "Test City"}


def test_service_provider_creation():
    provider = ServiceProvider(
        name="Jane Smith",
        email="jane@example.com",
        address=TEST_ADDRESS,
        hourly_rate=25.0,
    )

    assert provider.name == "Jane Smith"
    assert provider.email == "jane@example.com"
    assert provider.account_type == AccountType.SERVICE_PROVIDER
    assert provider.hourly_rate == 25.0
    assert provider.address == TEST_ADDRESS
    assert isinstance(provider.created_at, datetime)


def test_service_provider_methods():
    provider = ServiceProvider(name="Test", email="test@example.com", address=TEST_ADDRESS)

    provider.set_hourly_rate(30.0)
    assert provider.hourly_rate == 30.0

    provider.update_availability("24/7")
    assert provider.availability == "24/7"


def test_negative_hourly_rate():
    provider = ServiceProvider(name="Rate Test", email="rate@example.com", address=TEST_ADDRESS)
    with pytest.raises(ValueError):
        provider.set_hourly_rate(-50)


def test_provider_to_dict():
    provider = ServiceProvider(name="Bob", email="bob@example.com", address=TEST_ADDRESS, tags={"plumbing"}, hourly_rate=40.0, availability="Weekdays")
    data = provider.to_dict()

    assert data["name"] == "Bob"
    assert data["account_type"] == "service_provider"
    assert data["hourly_rate"] == 40.0
    assert data["availability"] == "Weekdays"
    assert "plumbing" in data["tags"]


def test_provider_role_specific_info():
    provider = ServiceProvider(
        name="Bob", email="bob@example.com", address=TEST_ADDRESS, tags={"plumbing", "electrician"}, hourly_rate=40.0, availability="24/7"
    )
    role_info = provider.get_role_specific_info()

    assert role_info["role"] == "service_provider"
    assert role_info["hourly_rate"] == 40.0
    assert role_info["availability"] == "24/7"
    assert set(role_info["services_offered"]) == {"plumbing", "electrician"}


def test_provider_role_specific_info_edge_cases():
    provider = ServiceProvider(name="Role Test", email="role@example.com", address=TEST_ADDRESS)
    role_info = provider.get_role_specific_info()
    assert role_info["hourly_rate"] is None
    assert role_info["availability"] is None


def test_provider_repr():
    provider = ServiceProvider(name="Repr Test", email="repr@example.com", address=TEST_ADDRESS)
    assert "ServiceProvider" in repr(provider)
    assert "Repr Test" in repr(provider)

    provider.set_hourly_rate(45.0)
    assert "$45.0/hr" in repr(provider)

    # Test when hourly_rate is None
    provider.set_hourly_rate(None)
    assert "Rate not set" in repr(provider)

    # Test when hourly_rate is 0
    provider.set_hourly_rate(0.0)
    assert "$0.0/hr" in repr(provider)


def test_provider_to_dict_with_full_data():
    provider = ServiceProvider(
        name="Full Data",
        email="full@example.com",
        address={"country": "USA"},
        tags={"urgent", "verified"},
        hourly_rate=99.99,
        availability="24/7",
    )
    data = provider.to_dict()

    assert set(data["tags"]) == {"urgent", "verified"}
    assert data["hourly_rate"] == 99.99
    assert data["availability"] == "24/7"
    assert "created_at" in data
    assert "updated_at" in data
    assert isinstance(data["created_at"], str)
    assert datetime.fromisoformat(data["created_at"]).tzinfo == timezone.utc


def test_availability_edge_cases():
    provider = ServiceProvider(name="Availability Test", email="avail@example.com", address=TEST_ADDRESS)

    # Test empty availability
    provider.update_availability("")
    assert provider.availability == ""

    # Test long availability string
    long_avail = "Available 24/7 including holidays and weekends with emergency support options"
    provider.update_availability(long_avail)
    assert provider.availability == long_avail

    # Test special characters
    provider.update_availability("Mon-Fri: 9am-5pm, Sat: 10am-2pm, Sun: closed")
    assert "Sat: 10am-2pm" in provider.availability


def test_hourly_rate_edge_values():
    provider = ServiceProvider(name="Rate Test", email="rate@example.com", address=TEST_ADDRESS)

    # Test zero rate
    provider.set_hourly_rate(0.0)
    assert provider.hourly_rate == 0.0

    # Test very high rate
    high_rate = 9999.99
    provider.set_hourly_rate(high_rate)
    assert provider.hourly_rate == high_rate

    # Test fractional values
    provider.set_hourly_rate(49.95)
    assert provider.hourly_rate == 49.95


def test_provider_with_max_tags():
    provider = ServiceProvider(name="Tag Test", email="tags@example.com", address=TEST_ADDRESS)

    # Add large number of tags
    for i in range(1000):
        provider.add_tag(f"service_{i}")

    assert len(provider.tags) == 1000
    assert "service_999" in provider.tags


def test_role_info_without_rates():
    provider = ServiceProvider(name="Role Test", email="role@example.com", address=TEST_ADDRESS, availability="Part-time")
    provider.add_tag("plumbing")
    provider.add_tag("emergency")

    role_info = provider.get_role_specific_info()

    assert role_info["hourly_rate"] is None
    assert role_info["availability"] == "Part-time"
    assert set(role_info["services_offered"]) == {"plumbing", "emergency"}


def test_to_dict_with_null_values():
    provider = ServiceProvider(name="Null Test", email="null@example.com", address=TEST_ADDRESS, hourly_rate=None, availability=None)
    data = provider.to_dict()

    assert data["hourly_rate"] is None
    assert data["availability"] is None
    assert data["tags"] == []
    assert data["address"] == TEST_ADDRESS
