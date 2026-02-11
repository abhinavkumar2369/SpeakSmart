from flask import jsonify
from app.utils.logger import logger


def register_error_handlers(app):
    """Register global error handlers on the Flask app."""

    @app.errorhandler(400)
    def bad_request(error):
        logger.warning("Bad request: %s", error)
        return jsonify({"error": "Bad request", "message": str(error)}), 400

    @app.errorhandler(404)
    def not_found(error):
        logger.warning("Not found: %s", error)
        return jsonify({"error": "Not found", "message": str(error)}), 404

    @app.errorhandler(422)
    def unprocessable(error):
        logger.warning("Unprocessable entity: %s", error)
        return jsonify({"error": "Unprocessable entity", "message": str(error)}), 422

    @app.errorhandler(500)
    def internal_error(error):
        logger.error("Internal server error: %s", error)
        return jsonify({"error": "Internal server error", "message": str(error)}), 500

    @app.errorhandler(Exception)
    def handle_unexpected(error):
        logger.exception("Unhandled exception: %s", error)
        return (
            jsonify({"error": "Internal server error", "message": "An unexpected error occurred"}),
            500,
        )
