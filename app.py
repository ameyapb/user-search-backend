# app.py
from flask import Flask
from api.routes import api_bp


def create_app():
    app = Flask(__name__)

    # Register API blueprint
    app.register_blueprint(api_bp, url_prefix="/api")

    @app.route("/")
    def health_check():
        return {"message": "USER-SEARCH-BACKEND API is running!", "status": "healthy"}

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, host="0.0.0.0", port=3000)
