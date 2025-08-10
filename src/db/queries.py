import uuid
from psycopg2.extras import RealDictCursor, Json
from typing import Optional, List, Dict, Any


class AccountQueries:
    """Database queries for account operations"""

    def __init__(self, db_connection):
        self.db = db_connection

    # ============ GENERAL ACCOUNT OPERATIONS ============

    def get_all_accounts(
        self,
        account_type: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """Get all accounts with optional filters"""
        with self.db.cursor(cursor_factory=RealDictCursor) as cursor:
            query = """
                SELECT a.*,
                       sp.hourly_rate, sp.availability,
                       sc.preferred_budget, sc.service_history
                FROM accounts a
                LEFT JOIN service_providers sp ON a.id = sp.account_id
                LEFT JOIN service_consumers sc ON a.id = sc.account_id
                WHERE 1=1
            """
            params = []

            # Filter by account type
            if account_type:
                query += " AND a.account_type = %s"
                params.append(account_type)

            # Filter by tags (accounts that have ANY of the specified tags)
            if tags:
                query += " AND a.tags && %s"
                params.append(tags)

            query += " ORDER BY a.created_at DESC"

            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]

    def get_account_by_id(self, account_id: str) -> Optional[Dict[str, Any]]:
        """Get account by ID with all related data"""
        with self.db.cursor(cursor_factory=RealDictCursor) as cursor:
            query = """
                SELECT a.*,
                       sp.hourly_rate, sp.availability,
                       sc.preferred_budget, sc.service_history
                FROM accounts a
                LEFT JOIN service_providers sp ON a.id = sp.account_id
                LEFT JOIN service_consumers sc ON a.id = sc.account_id
                WHERE a.id = %s
            """
            cursor.execute(query, [account_id])
            result = cursor.fetchone()
            return dict(result) if result else None

    def delete_account_by_id(self, account_id: str) -> bool:
        """Delete account by ID (CASCADE will handle related tables)"""
        with self.db.cursor() as cursor:
            cursor.execute("DELETE FROM accounts WHERE id = %s", [account_id])
            return cursor.rowcount > 0

    # ============ SERVICE PROVIDER OPERATIONS ============

    def create_service_provider(
        self,
        name: str,
        email: str,
        address: Dict,
        tags: Optional[List[str]] = None,
        hourly_rate: Optional[float] = None,
        availability: Optional[Dict] = None,
    ) -> str:
        """Create a new service provider account"""
        account_id = str(uuid.uuid4())

        with self.db.cursor() as cursor:
            # Insert into accounts table
            cursor.execute(
                """
                INSERT INTO accounts (id, name, email, address, tags, account_type)
                VALUES (%s, %s, %s, %s, %s, 'service_provider')
            """,
                [account_id, name, email, Json(address), tags or []],
            )

            # Insert into service_providers table
            cursor.execute(
                """
                INSERT INTO service_providers (account_id, hourly_rate, availability)
                VALUES (%s, %s, %s)
            """,
                [account_id, hourly_rate, Json(availability) if availability else None],
            )

            self.db.commit()

        return account_id

    def update_service_provider(self, account_id: str, **updates) -> bool:
        """Update service provider account"""
        with self.db.cursor() as cursor:
            # Update accounts table if basic fields are provided
            account_updates = {k: v for k, v in updates.items() if k in ["name", "email", "address", "tags"]}

            if account_updates:
                # Convert address to Json if provided
                if "address" in account_updates:
                    account_updates["address"] = Json(account_updates["address"])

                set_clause = ", ".join([f"{k} = %s" for k in account_updates.keys()])
                values = list(account_updates.values()) + [account_id]
                cursor.execute(
                    f"""
                    UPDATE accounts
                    SET {set_clause}, updated_at = CURRENT_TIMESTAMP
                    WHERE id = %s
                """,
                    values,
                )

            # Update service_providers table if provider-specific fields are provided
            provider_updates = {k: v for k, v in updates.items() if k in ["hourly_rate", "availability"]}

            if provider_updates:
                # Convert availability to Json if provided
                if "availability" in provider_updates:
                    provider_updates["availability"] = Json(provider_updates["availability"])

                set_clause = ", ".join([f"{k} = %s" for k in provider_updates.keys()])
                values = list(provider_updates.values()) + [account_id]
                cursor.execute(
                    f"""
                    UPDATE service_providers
                    SET {set_clause}, updated_at = CURRENT_TIMESTAMP
                    WHERE account_id = %s
                """,
                    values,
                )

            self.db.commit()
            return True

    # ============ SERVICE CONSUMER OPERATIONS ============

    def create_service_consumer(
        self,
        name: str,
        email: str,
        address: Dict,
        tags: Optional[List[str]] = None,
        preferred_budget: Optional[float] = None,
        service_history: Optional[List] = None,
    ) -> str:
        """Create a new service consumer account"""
        account_id = str(uuid.uuid4())

        with self.db.cursor() as cursor:
            # Insert into accounts table
            cursor.execute(
                """
                INSERT INTO accounts (id, name, email, address, tags, account_type)
                VALUES (%s, %s, %s, %s, %s, 'service_consumer')
            """,
                [account_id, name, email, Json(address), tags or []],
            )

            # Insert into service_consumers table
            cursor.execute(
                """
                INSERT INTO service_consumers (account_id, preferred_budget, service_history)
                VALUES (%s, %s, %s)
            """,
                [account_id, preferred_budget, Json(service_history or [])],
            )

            self.db.commit()

        return account_id

    def update_service_consumer(self, account_id: str, **updates) -> bool:
        """Update service consumer account"""
        with self.db.cursor() as cursor:
            # Update accounts table if basic fields are provided
            account_updates = {k: v for k, v in updates.items() if k in ["name", "email", "address", "tags"]}

            if account_updates:
                # Convert address to Json if provided
                if "address" in account_updates:
                    account_updates["address"] = Json(account_updates["address"])

                set_clause = ", ".join([f"{k} = %s" for k in account_updates.keys()])
                values = list(account_updates.values()) + [account_id]
                cursor.execute(
                    f"""
                    UPDATE accounts
                    SET {set_clause}, updated_at = CURRENT_TIMESTAMP
                    WHERE id = %s
                """,
                    values,
                )

            # Update service_consumers table if consumer-specific fields are provided
            consumer_updates = {k: v for k, v in updates.items() if k in ["preferred_budget", "service_history"]}

            if consumer_updates:
                # Convert service_history to Json if provided
                if "service_history" in consumer_updates:
                    consumer_updates["service_history"] = Json(consumer_updates["service_history"])

                set_clause = ", ".join([f"{k} = %s" for k in consumer_updates.keys()])
                values = list(consumer_updates.values()) + [account_id]
                cursor.execute(
                    f"""
                    UPDATE service_consumers
                    SET {set_clause}, updated_at = CURRENT_TIMESTAMP
                    WHERE account_id = %s
                """,
                    values,
                )

            self.db.commit()
            return True

    def add_service_to_consumer_history(self, account_id: str, service_data: Dict) -> bool:
        """Add a service to consumer's service history"""
        with self.db.cursor() as cursor:
            cursor.execute(
                """
                UPDATE service_consumers
                SET service_history = service_history || %s::jsonb,
                    updated_at = CURRENT_TIMESTAMP
                WHERE account_id = %s
            """,
                [Json([service_data]), account_id],
            )

            self.db.commit()
            return cursor.rowcount > 0
