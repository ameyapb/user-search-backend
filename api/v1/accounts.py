from flask import Blueprint, request, jsonify
from src.models.service_provider import ServiceProvider
from src.models.service_consumer import ServiceConsumer

accounts_bp = Blueprint("accounts", __name__)

# In-memory storage (for prototype)
accounts_storage = {}


# GENERAL ACCOUNT ENDPOINTS
@accounts_bp.route("/", methods=["GET"])
def list_all_accounts():
    """List all accounts with optional filters"""
    try:
        account_type = request.args.get("account_type")
        tags = request.args.getlist("tags")

        filtered_accounts = []
        for account in accounts_storage.values():
            # Filter by account_type
            if account_type and account.account_type.value != account_type:
                continue

            # Filter by tags
            if tags and not any(tag in account.tags for tag in tags):
                continue

            filtered_accounts.append(account.to_dict())

        return jsonify({"message": f"Found {len(filtered_accounts)} accounts", "data": filtered_accounts}), 200

    except Exception as e:
        return jsonify({"error": "Failed to list accounts", "details": str(e)}), 500


@accounts_bp.route("/<account_id>", methods=["GET"])
def get_account_by_id(account_id):
    """Get account details by ID"""
    try:
        if account_id not in accounts_storage:
            return jsonify({"error": "Account not found"}), 404

        account = accounts_storage[account_id]
        return jsonify({"message": "Account found", "data": account.to_dict()}), 200

    except Exception as e:
        return jsonify({"error": "Failed to retrieve account", "details": str(e)}), 500


@accounts_bp.route("/<account_id>", methods=["DELETE"])
def delete_account_by_id(account_id):
    """Delete account by ID"""
    try:
        if account_id not in accounts_storage:
            return jsonify({"error": "Account not found"}), 404

        del accounts_storage[account_id]
        return jsonify({"message": "Account deleted successfully"}), 200

    except Exception as e:
        return jsonify({"error": "Failed to delete account", "details": str(e)}), 500


# SERVICE PROVIDER ENDPOINTS
@accounts_bp.route("/providers", methods=["POST"])
def create_service_provider():
    """Create a new ServiceProvider"""
    try:
        data = request.get_json()

        if not data or not all(k in data for k in ["name", "email"]):
            return jsonify({"error": "Missing required fields", "required": ["name", "email"]}), 400

        provider = ServiceProvider(
            name=data["name"],
            email=data["email"],
            address=data.get("address"),
            tags=set(data.get("tags", [])),
            hourly_rate=data.get("hourly_rate"),
            availability=data.get("availability"),
        )

        accounts_storage[provider.id] = provider

        return jsonify({"message": "ServiceProvider created successfully", "data": provider.to_dict()}), 201

    except Exception as e:
        return jsonify({"error": "Failed to create ServiceProvider", "details": str(e)}), 500


@accounts_bp.route("/providers/<account_id>", methods=["GET"])
def get_service_provider_by_id(account_id):
    """Get ServiceProvider details by ID"""
    try:
        if account_id not in accounts_storage:
            return jsonify({"error": "ServiceProvider not found"}), 404

        account = accounts_storage[account_id]
        if not isinstance(account, ServiceProvider):
            return jsonify({"error": "Account is not a ServiceProvider"}), 400

        return jsonify({"message": "ServiceProvider found", "data": account.to_dict()}), 200

    except Exception as e:
        return jsonify({"error": "Failed to retrieve ServiceProvider", "details": str(e)}), 500


@accounts_bp.route("/providers/<account_id>", methods=["PUT"])
def update_service_provider(account_id):
    """Update ServiceProvider"""
    try:
        if account_id not in accounts_storage:
            return jsonify({"error": "ServiceProvider not found"}), 404

        account = accounts_storage[account_id]
        if not isinstance(account, ServiceProvider):
            return jsonify({"error": "Account is not a ServiceProvider"}), 400

        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        # Update basic fields
        if "name" in data:
            account.name = data["name"]
        if "email" in data:
            account.email = data["email"]
        if "address" in data:
            account.address = data["address"]
        if "tags" in data:
            account.tags = set(data["tags"])

        # Update provider-specific fields
        if "hourly_rate" in data:
            account.set_hourly_rate(data["hourly_rate"])
        if "availability" in data:
            account.update_availability(data["availability"])

        return jsonify({"message": "ServiceProvider updated successfully", "data": account.to_dict()}), 200

    except Exception as e:
        return jsonify({"error": "Failed to update ServiceProvider", "details": str(e)}), 500


@accounts_bp.route("/providers/<account_id>", methods=["DELETE"])
def delete_service_provider(account_id):
    """Delete ServiceProvider"""
    try:
        if account_id not in accounts_storage:
            return jsonify({"error": "ServiceProvider not found"}), 404

        account = accounts_storage[account_id]
        if not isinstance(account, ServiceProvider):
            return jsonify({"error": "Account is not a ServiceProvider"}), 400

        del accounts_storage[account_id]
        return jsonify({"message": "ServiceProvider deleted successfully"}), 200

    except Exception as e:
        return jsonify({"error": "Failed to delete ServiceProvider", "details": str(e)}), 500


# SERVICE CONSUMER ENDPOINTS
@accounts_bp.route("/consumers", methods=["POST"])
def create_service_consumer():
    """Create a new ServiceConsumer"""
    try:
        data = request.get_json()

        if not data or not all(k in data for k in ["name", "email"]):
            return jsonify({"error": "Missing required fields", "required": ["name", "email"]}), 400

        consumer = ServiceConsumer(
            name=data["name"],
            email=data["email"],
            address=data.get("address"),
            tags=set(data.get("tags", [])),
            preferred_budget=data.get("preferred_budget"),
            service_history=data.get("service_history", []),
        )

        accounts_storage[consumer.id] = consumer

        return jsonify({"message": "ServiceConsumer created successfully", "data": consumer.to_dict()}), 201

    except Exception as e:
        return jsonify({"error": "Failed to create ServiceConsumer", "details": str(e)}), 500


@accounts_bp.route("/consumers/<account_id>", methods=["GET"])
def get_service_consumer_by_id(account_id):
    """Get ServiceConsumer details by ID"""
    try:
        if account_id not in accounts_storage:
            return jsonify({"error": "ServiceConsumer not found"}), 404

        account = accounts_storage[account_id]
        if not isinstance(account, ServiceConsumer):
            return jsonify({"error": "Account is not a ServiceConsumer"}), 400

        return jsonify({"message": "ServiceConsumer found", "data": account.to_dict()}), 200

    except Exception as e:
        return jsonify({"error": "Failed to retrieve ServiceConsumer", "details": str(e)}), 500


@accounts_bp.route("/consumers/<account_id>", methods=["PUT"])
def update_service_consumer(account_id):
    """Update ServiceConsumer"""
    try:
        if account_id not in accounts_storage:
            return jsonify({"error": "ServiceConsumer not found"}), 404

        account = accounts_storage[account_id]
        if not isinstance(account, ServiceConsumer):
            return jsonify({"error": "Account is not a ServiceConsumer"}), 400

        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        # Update basic fields
        if "name" in data:
            account.name = data["name"]
        if "email" in data:
            account.email = data["email"]
        if "address" in data:
            account.address = data["address"]
        if "tags" in data:
            account.tags = set(data["tags"])

        # Update consumer-specific fields
        if "preferred_budget" in data:
            account.set_preferred_budget(data["preferred_budget"])

        return jsonify({"message": "ServiceConsumer updated successfully", "data": account.to_dict()}), 200

    except Exception as e:
        return jsonify({"error": "Failed to update ServiceConsumer", "details": str(e)}), 500


@accounts_bp.route("/consumers/<account_id>/service-history", methods=["POST"])
def add_service_to_history(account_id):
    """Add service to ServiceConsumer history"""
    try:
        if account_id not in accounts_storage:
            return jsonify({"error": "ServiceConsumer not found"}), 404

        account = accounts_storage[account_id]
        if not isinstance(account, ServiceConsumer):
            return jsonify({"error": "Account is not a ServiceConsumer"}), 400

        data = request.get_json()
        if not data:
            return jsonify({"error": "No service data provided"}), 400

        account.add_service_to_history(data)

        return jsonify({"message": "Service added to history successfully", "data": account.to_dict()}), 200

    except Exception as e:
        return jsonify({"error": "Failed to add service to history", "details": str(e)}), 500


@accounts_bp.route("/consumers/<account_id>", methods=["DELETE"])
def delete_service_consumer(account_id):
    """Delete ServiceConsumer"""
    try:
        if account_id not in accounts_storage:
            return jsonify({"error": "ServiceConsumer not found"}), 404

        account = accounts_storage[account_id]
        if not isinstance(account, ServiceConsumer):
            return jsonify({"error": "Account is not a ServiceConsumer"}), 400

        del accounts_storage[account_id]
        return jsonify({"message": "ServiceConsumer deleted successfully"}), 200

    except Exception as e:
        return jsonify({"error": "Failed to delete ServiceConsumer", "details": str(e)}), 500
