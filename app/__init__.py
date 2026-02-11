from flask import Flask, jsonify, render_template
from app.config import Config
from app.models.database import init_db
from app.utils.errors import register_error_handlers
from app.utils.logger import logger


def create_app() -> Flask:
    """Application factory – creates and configures the Flask app."""
    app = Flask(__name__)

    # Load config
    app.config.from_object(Config)

    # Initialize database
    init_db()

    # Register error handlers
    register_error_handlers(app)

    # Register blueprints
    from app.routes.languages import languages_bp
    from app.routes.translations import translations_bp
    from app.routes.grammar_rules import grammar_rules_bp
    from app.routes.ai import ai_bp

    app.register_blueprint(languages_bp)
    app.register_blueprint(translations_bp)
    app.register_blueprint(grammar_rules_bp)
    app.register_blueprint(ai_bp)

    # Root route – serve frontend
    @app.route("/", methods=["GET"])
    def index():
        return render_template("index.html")

    # Health check
    @app.route("/api/health", methods=["GET"])
    def health_check():
        return jsonify({
            "status": "healthy",
            "service": "SpeakSmart",
            "version": "1.0.0",
        })

    logger.info("SpeakSmart app created successfully")
    return app
