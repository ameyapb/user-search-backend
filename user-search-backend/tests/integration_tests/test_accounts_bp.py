import pytest
from app import create_app
from api.v1.accounts import accounts_storage


@pytest.fixture(autouse=True)
def reset_storage():
    """Reset the in-memory storage before each test"""
    accounts_storage.clear()


@pytest.fixture
def client():
    """Fixture to create a test client for the app"""
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        with app.app_context():
            yield client


def test_create_service_provider(client):
    response = client.post(
        "/api/v1/providers",
        json={
            "name": "Test Provider",
            "email": "test@provider.com",
            "address": {"street": "123 Main St", "city": "Test City"},
            "tags": ["plumber", "emergency"],
            "hourly_rate": 75.0,
        },
    )
    assert response.status_code == 201
    data = response.get_json()
    assert data["message"] == "ServiceProvider created successfully"
    assert data["data"]["name"] == "Test Provider"
    assert data["data"]["email"] == "test@provider.com"
    assert "id" in data["data"]


def test_create_service_consumer(client):
    response = client.post(
        "/api/v1/consumers",
        json={
            "name": "Test Consumer",
            "email": "test@consumer.com",
            "address": {"street": "123 Main St", "city": "Test City"},
            "tags": ["homeowner"],
            "preferred_budget": 200.0,
        },
    )
    assert response.status_code == 201
    data = response.get_json()
    assert data["message"] == "ServiceConsumer created successfully"
    assert data["data"]["name"] == "Test Consumer"
    assert data["data"]["account_type"] == "service_consumer"


def test_list_all_accounts(client):
    client.post(
        "/api/v1/providers",
        json={
            "name": "Provider 1",
            "email": "p1@test.com",
            "address": {"street": "789 Pine St", "city": "Provider City"},
        },
    )
    response = client.get("/api/v1/")
    assert response.status_code == 200
    data = response.get_json()
    assert len(data["data"]) >= 1
    assert data["data"][0]["name"] == "Provider 1"


def test_get_account_by_id(client):
    create_response = client.post(
        "/api/v1/providers",
        json={
            "name": "Get Test",
            "email": "get@test.com",
            "address": {"street": "123 Main St", "city": "Test City"},
        },
    )
    provider_id = create_response.get_json()["data"]["id"]
    response = client.get(f"/api/v1/{provider_id}")
    assert response.status_code == 200
    data = response.get_json()
    assert data["data"]["name"] == "Get Test"
    assert data["data"]["id"] == provider_id


def test_update_service_provider(client):
    create_response = client.post(
        "/api/v1/providers",
        json={
            "name": "Update Test",
            "email": "update@test.com",
            "address": {"street": "123 Update St", "city": "Update City"},
        },
    )
    provider_id = create_response.get_json()["data"]["id"]
    response = client.put(
        f"/api/v1/providers/{provider_id}",
        json={
            "name": "Updated Name",
            "hourly_rate": 100.0,
        },
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["data"]["name"] == "Updated Name"
    assert data["data"]["hourly_rate"] == 100.0


def test_delete_account(client):
    create_response = client.post(
        "/api/v1/providers",
        json={
            "name": "Delete Test",
            "email": "delete@test.com",
            "address": {"street": "123 Delete St", "city": "Delete City"},
        },
    )
    provider_id = create_response.get_json()["data"]["id"]
    response = client.delete(f"/api/v1/{provider_id}")
    assert response.status_code == 200
    assert "deleted successfully" in response.get_json()["message"]
    get_response = client.get(f"/api/v1/{provider_id}")
    assert get_response.status_code == 404


def test_add_service_to_history(client):
    create_response = client.post(
        "/api/v1/consumers",
        json={
            "name": "History Test",
            "email": "history@test.com",
            "address": {"street": "123 Delete St", "city": "Delete City"},
        },
    )
    consumer_id = create_response.get_json()["data"]["id"]
    response = client.post(
        f"/api/v1/consumers/{consumer_id}/service-history",
        json={
            "service": "plumbing repair",
            "cost": 150.0,
            "date": "2024-08-10",
        },
    )
    assert response.status_code == 200
    data = response.get_json()
    assert len(data["data"]["service_history"]) == 1
    assert data["data"]["service_history"][0]["service"] == "plumbing repair"


def test_filter_by_account_type(client):
    client.post(
        "/api/v1/providers",
        json={
            "name": "History Test",
            "email": "history@test.com",
            "address": {"street": "123 History St", "city": "History City"},
        },
    )
    client.post(
        "/api/v1/consumers",
        json={
            "name": "Filter Consumer",
            "email": "fc@test.com",
        },
    )
    response = client.get("/api/v1/?account_type=service_provider")
    assert response.status_code == 200
    data = response.get_json()
    for account in data["data"]:
        assert account["account_type"] == "service_provider"


def test_missing_required_fields(client):
    response = client.post("/api/v1/providers", json={"name": "No Email Provider"})
    assert response.status_code == 400
    data = response.get_json()
    assert "Missing required fields" in data["error"]


def test_account_not_found(client):
    response = client.get("/api/v1/non-existent-id")
    assert response.status_code == 404
    data = response.get_json()
    assert "not found" in data["error"]
