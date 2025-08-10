import pytest
from datetime import datetime, timezone
from src.models.service_consumer import ServiceConsumer
from src.models.account import AccountType

TEST_ADDRESS = {"city": "Test City"}


def test_service_consumer_creation():
    consumer = ServiceConsumer(
        name="John Doe",
        email="john@example.com",
        preferred_budget=100.0,
        address=TEST_ADDRESS,
    )

    assert consumer.name == "John Doe"
    assert consumer.email == "john@example.com"
    assert consumer.account_type == AccountType.SERVICE_CONSUMER
    assert consumer.preferred_budget == 100.0
    assert isinstance(consumer.created_at, datetime)
    assert consumer.tags == set()


def test_service_consumer_methods():
    consumer = ServiceConsumer(
        name="Test",
        email="test@example.com",
        address=TEST_ADDRESS,
    )

    consumer.set_preferred_budget(150.0)
    assert consumer.preferred_budget == 150.0

    consumer.add_service_to_history({"service": "cleaning"})
    assert len(consumer.service_history) == 1
    assert "service" in consumer.service_history[0]


def test_negative_budget():
    consumer = ServiceConsumer(name="Budget Test", email="budget@example.com", address=TEST_ADDRESS)
    with pytest.raises(ValueError):
        consumer.set_preferred_budget(-100)


def test_service_history_edge_cases():
    consumer = ServiceConsumer(name="History Test", email="history@example.com", address=TEST_ADDRESS)

    # Test empty service data
    with pytest.raises(ValueError):
        consumer.add_service_to_history({})

    # Test None service data
    with pytest.raises(ValueError):
        consumer.add_service_to_history(None)

    # Test valid service data
    consumer.add_service_to_history({"service": "cleaning", "price": 50})
    assert len(consumer.service_history) == 1
    assert "added_at" in consumer.service_history[0]


def test_consumer_to_dict():
    consumer = ServiceConsumer(
        name="Alice",
        email="alice@example.com",
        tags={"vip"},
        preferred_budget=200.0,
        address=TEST_ADDRESS,
    )
    data = consumer.to_dict()

    assert data["name"] == "Alice"
    assert data["account_type"] == "service_consumer"
    assert data["preferred_budget"] == 200.0
    assert "vip" in data["tags"]
    assert data["service_history"] == []


def test_consumer_role_specific_info():
    consumer = ServiceConsumer(name="Role Test", email="role@example.com", address=TEST_ADDRESS, preferred_budget=150.0)
    consumer.add_service_to_history({"service": "cleaning"})
    role_info = consumer.get_role_specific_info()

    assert role_info["role"] == "service_consumer"
    assert role_info["preferred_budget"] == 150.0
    assert role_info["service_history_count"] == 1
    assert role_info["interests"] == []


def test_consumer_role_specific_info_edge_cases():
    consumer = ServiceConsumer(name="Role Test", email="role@example.com", address=TEST_ADDRESS)
    role_info = consumer.get_role_specific_info()
    assert role_info["preferred_budget"] is None
    assert role_info["service_history_count"] == 0


def test_consumer_repr():
    consumer = ServiceConsumer(name="Repr Test", email="repr@example.com", address=TEST_ADDRESS)
    assert "ServiceConsumer" in repr(consumer)
    assert "Repr Test" in repr(consumer)

    consumer.set_preferred_budget(99.99)
    assert "$99.99" in repr(consumer)


def test_service_history_ordering():
    consumer = ServiceConsumer(name="History Test", email="history@example.com", address=TEST_ADDRESS)

    # Add services in reverse order
    consumer.add_service_to_history({"service": "Cleaning", "date": "2023-01-01"})
    consumer.add_service_to_history({"service": "Repair", "date": "2023-01-02"})

    # Should be in chronological order
    assert consumer.service_history[0]["service"] == "Cleaning"
    assert consumer.service_history[1]["service"] == "Repair"


def test_budget_edge_values():
    consumer = ServiceConsumer(name="Budget Test", email="budget@example.com", address=TEST_ADDRESS)

    # Test zero budget
    consumer.set_preferred_budget(0.0)
    assert consumer.preferred_budget == 0.0

    # Test very large budget
    large_budget = 1_000_000.0
    consumer.set_preferred_budget(large_budget)
    assert consumer.preferred_budget == large_budget

    # Test fractional values
    consumer.set_preferred_budget(99.99)
    assert consumer.preferred_budget == 99.99


def test_service_history_max_entries():
    consumer = ServiceConsumer(name="History Test", email="history@example.com", address=TEST_ADDRESS)

    # Add large number of services
    for i in range(1000):
        consumer.add_service_to_history({"service": f"Service {i}"})

    assert len(consumer.service_history) == 1000
    assert consumer.service_history[-1]["service"] == "Service 999"


def test_role_info_with_services():
    consumer = ServiceConsumer(name="Role Test", email="role@example.com", address=TEST_ADDRESS)

    # Add multiple services
    consumer.add_service_to_history({"service": "Cleaning", "price": 50})
    consumer.add_service_to_history({"service": "Repair", "price": 100})
    consumer.add_tag("vip")

    role_info = consumer.get_role_specific_info()

    assert role_info["service_history_count"] == 2
    assert role_info["preferred_budget"] is None
    assert "vip" in role_info["interests"]


def test_consumer_with_max_tags():
    consumer = ServiceConsumer(name="Tag Test", email="tags@example.com", address=TEST_ADDRESS)

    # Add large number of tags
    for i in range(1000):
        consumer.add_tag(f"tag_{i}")

    assert len(consumer.tags) == 1000
    assert "tag_999" in consumer.tags
