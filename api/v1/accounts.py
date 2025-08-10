from flask import Blueprint, request, jsonify
from src.models.service_provider import ServiceProvider
from src.models.service_consumer import ServiceConsumer
from src.db.queries import AccountQueries
from src.db.connection import get_db

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

        # Get database connection and create queries instance
        db = get_db()
        queries = AccountQueries(db)

        # Query the database
        accounts_data = queries.get_all_accounts(account_type=account_type, tags=tags if tags else None)

        # Format response data
        formatted_accounts = []
        for account in accounts_data:
            response_data = {
                "id": account["id"],
                "name": account["name"],
                "email": account["email"],
                "address": account["address"],
                "tags": account["tags"],
                "account_type": account["account_type"],
                "created_at": account["created_at"].isoformat(),
                "updated_at": account["updated_at"].isoformat(),
            }

            # Add type-specific fields
            if account["account_type"] == "service_provider":
                if account["hourly_rate"]:
                    response_data["hourly_rate"] = float(account["hourly_rate"])
                if account["availability"]:
                    response_data["availability"] = account["availability"]

            elif account["account_type"] == "service_consumer":
                if account["preferred_budget"]:
                    response_data["preferred_budget"] = float(account["preferred_budget"])
                if account["service_history"]:
                    response_data["service_history"] = account["service_history"]

            formatted_accounts.append(response_data)

        return jsonify({"message": f"Found {len(formatted_accounts)} accounts", "data": formatted_accounts}), 200

    except Exception as e:
        return jsonify({"error": "Failed to list accounts", "details": str(e)}), 500


@accounts_bp.route("/<account_id>", methods=["GET"])
def get_account_by_id(account_id):
    """Get account details by ID"""
    try:
        # Get database connection and create queries instance
        db = get_db()
        queries = AccountQueries(db)

        # Query the database
        account_data = queries.get_account_by_id(account_id)

        if not account_data:
            return jsonify({"error": "Account not found"}), 404

        # Convert database result to response format
        response_data = {
            "id": account_data["id"],
            "name": account_data["name"],
            "email": account_data["email"],
            "address": account_data["address"],
            "tags": account_data["tags"],
            "account_type": account_data["account_type"],
            "created_at": account_data["created_at"].isoformat(),
            "updated_at": account_data["updated_at"].isoformat(),
        }

        # Add type-specific fields
        if account_data["account_type"] == "service_provider":
            if account_data["hourly_rate"]:
                response_data["hourly_rate"] = float(account_data["hourly_rate"])
            if account_data["availability"]:
                response_data["availability"] = account_data["availability"]

        elif account_data["account_type"] == "service_consumer":
            if account_data["preferred_budget"]:
                response_data["preferred_budget"] = float(account_data["preferred_budget"])
            if account_data["service_history"]:
                response_data["service_history"] = account_data["service_history"]

        return jsonify({"message": "Account found", "data": response_data}), 200

    except Exception as e:
        return jsonify({"error": "Failed to retrieve account", "details": str(e)}), 500


@accounts_bp.route("/<account_id>", methods=["DELETE"])
def delete_account_by_id(account_id):
    """Delete account by ID"""
    try:
        db = get_db()
        queries = AccountQueries(db)

        # Check if account exists
        existing_account = queries.get_account_by_id(account_id)
        if not existing_account:
            return jsonify({"error": "Account not found"}), 404

        # Delete the account
        success = queries.delete_account_by_id(account_id)
        if success:
            return jsonify({"message": "Account deleted successfully"}), 200
        else:
            return jsonify({"error": "Failed to delete account"}), 500

    except Exception as e:
        return jsonify({"error": "Failed to delete account", "details": str(e)}), 500


# SERVICE PROVIDER ENDPOINTS
@accounts_bp.route("/providers", methods=["POST"])
def create_service_provider():
    """Create a new ServiceProvider"""
    try:
        data = request.get_json()

        # comprehensive validation
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        if not all(k in data for k in ["name", "email", "address"]):
            return jsonify({"error": "Missing required fields", "required": ["name", "email", "address"]}), 400

        if not isinstance(data["address"], dict):
            return jsonify({"error": "Address must be a dictionary"}), 400

        # Get database connection and create queries instance
        db = get_db()
        queries = AccountQueries(db)

        # Create the service provider
        account_id = queries.create_service_provider(
            name=data["name"],
            email=data["email"],
            address=data["address"],
            tags=data.get("tags", []),
            hourly_rate=data.get("hourly_rate"),
            availability=data.get("availability"),
        )

        # Get the created account to return full data
        account_data = queries.get_account_by_id(account_id)

        # Format response
        response_data = {
            "id": account_data["id"],
            "name": account_data["name"],
            "email": account_data["email"],
            "address": account_data["address"],
            "tags": account_data["tags"],
            "account_type": account_data["account_type"],
            "created_at": account_data["created_at"].isoformat(),
            "updated_at": account_data["updated_at"].isoformat(),
        }

        # Add provider-specific fields
        if account_data["hourly_rate"]:
            response_data["hourly_rate"] = float(account_data["hourly_rate"])
        if account_data["availability"]:
            response_data["availability"] = account_data["availability"]

        return jsonify({"message": "ServiceProvider created successfully", "data": response_data}), 201

    except ValueError as ve:
        return jsonify({"error": "Validation error", "details": str(ve)}), 400
    except Exception as e:
        return jsonify({"error": "Failed to create ServiceProvider", "details": str(e)}), 500


@accounts_bp.route("/providers/<account_id>", methods=["GET"])
def get_service_provider_by_id(account_id):
    """Get ServiceProvider details by ID"""
    try:
        db = get_db()
        queries = AccountQueries(db)

        account_data = queries.get_account_by_id(account_id)

        if not account_data:
            return jsonify({"error": "ServiceProvider not found"}), 404

        if account_data["account_type"] != "service_provider":
            return jsonify({"error": "Account is not a ServiceProvider"}), 400

        # Format response
        response_data = {
            "id": account_data["id"],
            "name": account_data["name"],
            "email": account_data["email"],
            "address": account_data["address"],
            "tags": account_data["tags"],
            "account_type": account_data["account_type"],
            "created_at": account_data["created_at"].isoformat(),
            "updated_at": account_data["updated_at"].isoformat(),
        }

        # Add provider-specific fields
        if account_data["hourly_rate"]:
            response_data["hourly_rate"] = float(account_data["hourly_rate"])
        if account_data["availability"]:
            response_data["availability"] = account_data["availability"]

        return jsonify({"message": "ServiceProvider found", "data": response_data}), 200

    except Exception as e:
        return jsonify({"error": "Failed to retrieve ServiceProvider", "details": str(e)}), 500


@accounts_bp.route("/providers/<account_id>", methods=["PUT"])
def update_service_provider(account_id):
    """Update ServiceProvider"""
    try:
        # Get database connection and create queries instance
        db = get_db()
        queries = AccountQueries(db)

        # Check if account exists and is a service provider
        existing_account = queries.get_account_by_id(account_id)
        if not existing_account:
            return jsonify({"error": "ServiceProvider not found"}), 404

        if existing_account["account_type"] != "service_provider":
            return jsonify({"error": "Account is not a ServiceProvider"}), 400

        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        # Update the service provider
        queries.update_service_provider(account_id, **data)

        # Get updated account data
        updated_account = queries.get_account_by_id(account_id)

        # Format response
        response_data = {
            "id": updated_account["id"],
            "name": updated_account["name"],
            "email": updated_account["email"],
            "address": updated_account["address"],
            "tags": updated_account["tags"],
            "account_type": updated_account["account_type"],
            "created_at": updated_account["created_at"].isoformat(),
            "updated_at": updated_account["updated_at"].isoformat(),
        }

        # Add provider-specific fields
        if updated_account["hourly_rate"]:
            response_data["hourly_rate"] = float(updated_account["hourly_rate"])
        if updated_account["availability"]:
            response_data["availability"] = updated_account["availability"]

        return jsonify({"message": "ServiceProvider updated successfully", "data": response_data}), 200

    except Exception as e:
        return jsonify({"error": "Failed to update ServiceProvider", "details": str(e)}), 500


@accounts_bp.route("/providers/<account_id>", methods=["DELETE"])
def delete_service_provider(account_id):
    """Delete ServiceProvider"""
    try:
        db = get_db()
        queries = AccountQueries(db)

        # Check if account exists and is a service provider
        existing_account = queries.get_account_by_id(account_id)
        if not existing_account:
            return jsonify({"error": "ServiceProvider not found"}), 404

        if existing_account["account_type"] != "service_provider":
            return jsonify({"error": "Account is not a ServiceProvider"}), 400

        # Delete the account
        success = queries.delete_account_by_id(account_id)
        if success:
            return jsonify({"message": "ServiceProvider deleted successfully"}), 200
        else:
            return jsonify({"error": "Failed to delete ServiceProvider"}), 500

    except Exception as e:
        return jsonify({"error": "Failed to delete ServiceProvider", "details": str(e)}), 500


# SERVICE CONSUMER ENDPOINTS
@accounts_bp.route("/consumers", methods=["POST"])
def create_service_consumer():
    """Create a new ServiceConsumer"""
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        if not all(k in data for k in ["name", "email", "address"]):
            return jsonify({"error": "Missing required fields", "required": ["name", "email", "address"]}), 400

        if not isinstance(data["address"], dict):
            return jsonify({"error": "Address must be a dictionary"}), 400

        # Get database connection and create queries instance
        db = get_db()
        queries = AccountQueries(db)

        # Create the service consumer
        account_id = queries.create_service_consumer(
            name=data["name"],
            email=data["email"],
            address=data["address"],
            tags=data.get("tags", []),
            preferred_budget=data.get("preferred_budget"),
            service_history=data.get("service_history", []),
        )

        # Get the created account to return full data
        account_data = queries.get_account_by_id(account_id)

        # Format response
        response_data = {
            "id": account_data["id"],
            "name": account_data["name"],
            "email": account_data["email"],
            "address": account_data["address"],
            "tags": account_data["tags"],
            "account_type": account_data["account_type"],
            "created_at": account_data["created_at"].isoformat(),
            "updated_at": account_data["updated_at"].isoformat(),
        }

        # Add consumer-specific fields
        if account_data["preferred_budget"]:
            response_data["preferred_budget"] = float(account_data["preferred_budget"])
        if account_data["service_history"]:
            response_data["service_history"] = account_data["service_history"]

        return jsonify({"message": "ServiceConsumer created successfully", "data": response_data}), 201

    except ValueError as ve:
        return jsonify({"error": "Validation error", "details": str(ve)}), 400
    except Exception as e:
        return jsonify({"error": "Failed to create ServiceConsumer", "details": str(e)}), 500


@accounts_bp.route("/consumers/<account_id>", methods=["GET"])
def get_service_consumer_by_id(account_id):
    """Get ServiceConsumer details by ID"""
    try:
        db = get_db()
        queries = AccountQueries(db)

        account_data = queries.get_account_by_id(account_id)

        if not account_data:
            return jsonify({"error": "ServiceConsumer not found"}), 404

        if account_data["account_type"] != "service_consumer":
            return jsonify({"error": "Account is not a ServiceConsumer"}), 400

        # Format response
        response_data = {
            "id": account_data["id"],
            "name": account_data["name"],
            "email": account_data["email"],
            "address": account_data["address"],
            "tags": account_data["tags"],
            "account_type": account_data["account_type"],
            "created_at": account_data["created_at"].isoformat(),
            "updated_at": account_data["updated_at"].isoformat(),
        }

        # Add consumer-specific fields
        if account_data["preferred_budget"]:
            response_data["preferred_budget"] = float(account_data["preferred_budget"])
        if account_data["service_history"]:
            response_data["service_history"] = account_data["service_history"]

        return jsonify({"message": "ServiceConsumer found", "data": response_data}), 200

    except Exception as e:
        return jsonify({"error": "Failed to retrieve ServiceConsumer", "details": str(e)}), 500


@accounts_bp.route("/consumers/<account_id>", methods=["PUT"])
def update_service_consumer(account_id):
    """Update ServiceConsumer"""
    try:
        db = get_db()
        queries = AccountQueries(db)

        # Check if account exists and is a service consumer
        existing_account = queries.get_account_by_id(account_id)
        if not existing_account:
            return jsonify({"error": "ServiceConsumer not found"}), 404

        if existing_account["account_type"] != "service_consumer":
            return jsonify({"error": "Account is not a ServiceConsumer"}), 400

        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        # Update the service consumer
        queries.update_service_consumer(account_id, **data)

        # Get updated account data
        updated_account = queries.get_account_by_id(account_id)

        # Format response
        response_data = {
            "id": updated_account["id"],
            "name": updated_account["name"],
            "email": updated_account["email"],
            "address": updated_account["address"],
            "tags": updated_account["tags"],
            "account_type": updated_account["account_type"],
            "created_at": updated_account["created_at"].isoformat(),
            "updated_at": updated_account["updated_at"].isoformat(),
        }

        # Add consumer-specific fields
        if updated_account["preferred_budget"]:
            response_data["preferred_budget"] = float(updated_account["preferred_budget"])
        if updated_account["service_history"]:
            response_data["service_history"] = updated_account["service_history"]

        return jsonify({"message": "ServiceConsumer updated successfully", "data": response_data}), 200

    except Exception as e:
        return jsonify({"error": "Failed to update ServiceConsumer", "details": str(e)}), 500


@accounts_bp.route("/consumers/<account_id>/service-history", methods=["POST"])
def add_service_to_history(account_id):
    """Add service to ServiceConsumer history"""
    try:
        db = get_db()
        queries = AccountQueries(db)

        # Check if account exists and is a service consumer
        existing_account = queries.get_account_by_id(account_id)
        if not existing_account:
            return jsonify({"error": "ServiceConsumer not found"}), 404

        if existing_account["account_type"] != "service_consumer":
            return jsonify({"error": "Account is not a ServiceConsumer"}), 400

        data = request.get_json()
        if not data:
            return jsonify({"error": "No service data provided"}), 400

        # Add service to history
        success = queries.add_service_to_consumer_history(account_id, data)

        if not success:
            return jsonify({"error": "Failed to add service to history"}), 500

        # Get updated account data
        updated_account = queries.get_account_by_id(account_id)

        # Format response
        response_data = {
            "id": updated_account["id"],
            "name": updated_account["name"],
            "email": updated_account["email"],
            "address": updated_account["address"],
            "tags": updated_account["tags"],
            "account_type": updated_account["account_type"],
            "created_at": updated_account["created_at"].isoformat(),
            "updated_at": updated_account["updated_at"].isoformat(),
        }

        # Add consumer-specific fields
        if updated_account["preferred_budget"]:
            response_data["preferred_budget"] = float(updated_account["preferred_budget"])
        if updated_account["service_history"]:
            response_data["service_history"] = updated_account["service_history"]

        return jsonify({"message": "Service added to history successfully", "data": response_data}), 200

    except Exception as e:
        return jsonify({"error": "Failed to add service to history", "details": str(e)}), 500


@accounts_bp.route("/consumers/<account_id>", methods=["DELETE"])
def delete_service_consumer(account_id):
    """Delete ServiceConsumer"""
    try:
        db = get_db()
        queries = AccountQueries(db)

        # Check if account exists and is a service consumer
        existing_account = queries.get_account_by_id(account_id)
        if not existing_account:
            return jsonify({"error": "ServiceConsumer not found"}), 404

        if existing_account["account_type"] != "service_consumer":
            return jsonify({"error": "Account is not a ServiceConsumer"}), 400

        # Delete the account
        success = queries.delete_account_by_id(account_id)
        if success:
            return jsonify({"message": "ServiceConsumer deleted successfully"}), 200
        else:
            return jsonify({"error": "Failed to delete ServiceConsumer"}), 500

    except Exception as e:
        return jsonify({"error": "Failed to delete ServiceConsumer", "details": str(e)}), 500
