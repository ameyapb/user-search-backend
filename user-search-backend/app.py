# app.py
from flask import Flask
from api.routes import api_bp
from src.db.connection import get_db, close_db
from dotenv import load_dotenv
import os
from src import setup_logging
from flask_cors import CORS



def create_app():
    load_dotenv()
    logger = setup_logging()

    app = Flask(__name__)

    CORS(app, origins=["http://localhost:3001"])

    # Register API blueprint
    app.register_blueprint(api_bp, url_prefix="/api")
    app.teardown_appcontext(close_db)

    @app.route("/")
    def health_check():
        return {
            "message": "USER-SEARCH-BACKEND API is running!",
            "status": "healthy",
        }

    try:
        with app.app_context():
            db = get_db()
            db.cursor().execute("SELECT 1;")
        logger.info("Database connection successful at startup.")
    except Exception as e:
        logger.error(f"Database connection failed at startup: {e}")

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, host="0.0.0.0", port=3000)
