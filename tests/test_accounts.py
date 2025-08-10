import pytest
from datetime import datetime, timezone
from src.models.account import Account, AccountType
from src.models.service_consumer import ServiceConsumer
from src.models.service_provider import ServiceProvider

TEST_ADDRESS = {"city": "Test City"}


def test_cannot_instantiate_abstract_account():
    with pytest.raises(TypeError) as excinfo:
        Account("Invalid", "invalid@example.com", AccountType.ADMIN)
    assert "Can't instantiate abstract class" in str(excinfo.value)


def test_empty_name_email():
    with pytest.raises(ValueError):
        ServiceConsumer(name="", email="test@example.com", address=TEST_ADDRESS)
    with pytest.raises(ValueError):
        ServiceProvider(name="Test", email="", address=TEST_ADDRESS)


def test_invalid_email_format():
    with pytest.raises(ValueError):
        ServiceConsumer(name="Test", email="invalid-email", address=TEST_ADDRESS)


def test_tag_operations():
    account = ServiceConsumer(
        name="Test",
        email="test@example.com",
        address=TEST_ADDRESS,
    )

    account.add_tag("urgent")
    assert "urgent" in account.tags

    account.add_tag("repeat")
    assert "urgent" in account.tags
    assert "repeat" in account.tags

    account.remove_tag("urgent")
    assert "urgent" not in account.tags

    account.update_tags({"new", "customer"})
    assert account.tags == {"new", "customer"}


def test_tag_edge_cases():
    consumer = ServiceConsumer(name="Tag Test", email="tags@example.com", address=TEST_ADDRESS)

    # Test empty tag
    consumer.add_tag("")
    assert len(consumer.tags) == 0

    # Test duplicate tag
    consumer.add_tag("duplicate")
    consumer.add_tag("duplicate")
    assert len(consumer.tags) == 1

    # Test removing non-existent tag
    consumer.remove_tag("ghost-tag")
    assert "ghost-tag" not in consumer.tags

    # Test updating with None
    consumer.update_tags(None)
    assert consumer.tags == set()

    # Test updating with empty set
    consumer.update_tags(set())
    assert consumer.tags == set()


def test_updated_at_changes():
    consumer = ServiceConsumer(name="Time Test", email="time@example.com", address=TEST_ADDRESS)
    initial_update = consumer.updated_at

    # Modify account
    consumer.add_tag("update-test")
    assert consumer.updated_at > initial_update

    # Verify no change when removing non-existent tag
    initial_update = consumer.updated_at
    consumer.remove_tag("non-existent")
    assert consumer.updated_at == initial_update


def test_address_handling():
    # Test missing address for both account types
    with pytest.raises(TypeError):
        ServiceProvider(name="Address Test", email="address@example.com")
    with pytest.raises(TypeError):
        ServiceConsumer(name="Address Test", email="address@example.com")

    # Test invalid address types
    with pytest.raises(ValueError):
        ServiceProvider(name="Address Test", email="address@example.com", address="123 Main St")
    with pytest.raises(ValueError):
        ServiceConsumer(name="Address Test", email="address@example.com", address=None)

    # Test empty address dictionary
    with pytest.raises(ValueError):
        ServiceProvider(name="Address Test", email="address@example.com", address={})
    with pytest.raises(ValueError):
        ServiceConsumer(name="Address Test", email="address@example.com", address={})

    # Test valid address updates
    provider = ServiceProvider(name="Address Test", email="address@example.com", address={"street": "123 Main"})
    provider.address = {"city": "New York"}
    assert provider.address == {"city": "New York"}

    # Test address in to_dict()
    data = provider.to_dict()
    assert data["address"] == {"city": "New York"}


def test_id_uniqueness():
    ids = set()
    for _ in range(100):
        consumer = ServiceConsumer(name=f"Consumer {_}", email=f"c{_}@example.com", address=TEST_ADDRESS)
        ids.add(consumer.id)
    assert len(ids) == 100


def test_account_type_enforcement():
    consumer = ServiceConsumer(name="Type Test", email="type@example.com", address=TEST_ADDRESS)
    provider = ServiceProvider(name="Type Test", email="type@example.com", address=TEST_ADDRESS)

    assert consumer.account_type == AccountType.SERVICE_CONSUMER
    assert provider.account_type == AccountType.SERVICE_PROVIDER

    # Verify type can't be changed
    with pytest.raises(AttributeError):
        consumer.account_type = AccountType.SERVICE_PROVIDER


def test_account_to_dict():
    # Create a minimal account (using ServiceConsumer as base)
    consumer = ServiceConsumer(name="Minimal", email="minimal@example.com", address=TEST_ADDRESS)
    data = consumer.to_dict()

    # Test common fields
    assert data["name"] == "Minimal"
    assert data["email"] == "minimal@example.com"
    assert data["account_type"] == "service_consumer"
    assert data["address"] == TEST_ADDRESS
    assert data["tags"] == []
    assert "created_at" in data
    assert "updated_at" in data
    assert isinstance(data["created_at"], str)
    assert datetime.fromisoformat(data["created_at"]).tzinfo == timezone.utc


def test_created_at_before_updated_at():
    account = ServiceConsumer(name="Time Test", email="time@example.com", address=TEST_ADDRESS)
    assert account.created_at <= account.updated_at

    # After modification
    account.add_tag("test")
    assert account.created_at < account.updated_at


def test_case_insensitive_email_normalization():
    # Should store in lowercase
    email = "John.Doe@Example.COM"
    account = ServiceConsumer(name="John", email=email, address=TEST_ADDRESS)
    assert account.email == email.lower()


def test_address_immutable_types():
    # Should only accept dict
    with pytest.raises(ValueError):
        ServiceConsumer(name="Test", email="test@example.com", address="123 Main St")

    with pytest.raises(ValueError):
        ServiceConsumer(name="Test", email="test@example.com", address=["123", "Main"])


def test_tag_operations_with_special_chars():
    account = ServiceConsumer(name="Test", email="test@example.com", address=TEST_ADDRESS)

    # Test special characters
    account.add_tag("urgent!")
    account.add_tag("high-priority")
    account.add_tag("client_123")

    assert "urgent!" in account.tags
    assert "high-priority" in account.tags
    assert "client_123" in account.tags

    # Test very long tag
    long_tag = "a" * 1000
    account.add_tag(long_tag)
    assert long_tag in account.tags


def test_updated_at_unchanged_on_noop():
    account = ServiceConsumer(name="Test", email="test@example.com", address=TEST_ADDRESS)
    original_updated_at = account.updated_at

    # Operations that shouldn't change updated_at
    account.remove_tag("non-existent")
    account.update_tags(set(account.tags))  # Same tags

    assert account.updated_at == original_updated_at
