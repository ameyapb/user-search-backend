# src/db/run_migration.py

import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()


def run_migration():
    """Run the initial database migration"""

    # Database connection parameters
    conn_params = {
        "host": os.getenv("DB_HOST"),
        "port": os.getenv("DB_PORT"),
        "dbname": os.getenv("DB_NAME"),
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASSWORD"),
    }

    # Read the migration file
    migration_file = os.path.join(os.path.dirname(__file__), "migrations", "001_create_accounts_schema.sql")

    try:
        with open(migration_file, "r") as f:
            migration_sql = f.read()

        # Connect and execute
        conn = psycopg2.connect(**conn_params)
        conn.autocommit = True

        with conn.cursor() as cursor:
            cursor.execute(migration_sql)

        print("Database schema created successfully!")

        # Verify tables were created
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                AND table_name IN ('accounts', 'service_providers', 'service_consumers');
            """
            )
            tables = cursor.fetchall()
            print(f"Created tables: {[t[0] for t in tables]}")

        conn.close()

    except Exception as e:
        print(f"Migration failed: {e}")
        raise


if __name__ == "__main__":
    run_migration()
