"""
Flask application factory
"""
from flask import Flask
from flask_cors import CORS
import logging
from datetime import datetime

from app.config import settings


def create_app():
    """Create and configure Flask application"""

    app = Flask(__name__)

    # Configuration
    app.config['SECRET_KEY'] = settings.secret_key
    app.config['JSON_AS_ASCII'] = False  # For Korean text support

    # CORS
    CORS(app, resources={
        r"/api/*": {
            "origins": settings.frontend_url,
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })

    # Logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Initialize services
    from app.services.database_service import db_service, mongodb_service
    from app.services.pgvector_service import pgvector_service
    from app.services.ontology_service import ontology_service
    from app.services.cache_service import cache_service

    db_service.initialize()
    mongodb_service.initialize()
    pgvector_service.initialize()
    ontology_service.initialize()
    cache_service.initialize()

    # Register blueprints
    from app.routes.chat import chat_bp
    from app.routes.conversation import conversation_bp
    from app.routes.feedback import feedback_bp
    from app.routes.settings import settings_bp
    from app.routes.export import export_bp

    app.register_blueprint(chat_bp)
    app.register_blueprint(conversation_bp)
    app.register_blueprint(feedback_bp)
    app.register_blueprint(settings_bp)
    app.register_blueprint(export_bp)

    # Health check endpoint
    @app.route('/health')
    def health():
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "version": "1.0.0"
        }

    # Root endpoint
    @app.route('/')
    def index():
        return {
            "message": "Chatbot API",
            "version": "1.0.0",
            "endpoints": {
                "health": "/health",
                "chat": "/api/chat",
                "conversations": "/api/conversations",
                "feedback": "/api/feedback",
                "settings": "/api/settings",
                "export": "/api/export"
            }
        }

    return app
