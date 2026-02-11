from flask import Blueprint, request, jsonify, abort
from app.models.language import Language
from app.utils.logger import logger

languages_bp = Blueprint("languages", __name__)


@languages_bp.route("/api/languages", methods=["GET"])
def get_languages():
    """List all languages."""
    languages = Language.get_all()
    return jsonify({"languages": languages, "count": len(languages)})


@languages_bp.route("/api/languages/<int:language_id>", methods=["GET"])
def get_language(language_id):
    """Get a single language by ID."""
    language = Language.get_by_id(language_id)
    if not language:
        abort(404, description=f"Language with id {language_id} not found")
    return jsonify(language)


@languages_bp.route("/api/languages", methods=["POST"])
def create_language():
    """Create a new language."""
    data = request.get_json()
    if not data:
        abort(400, description="Request body must be JSON")

    name = data.get("name")
    code = data.get("code")

    if not name or not code:
        abort(400, description="Both 'name' and 'code' are required")

    try:
        language = Language.create(name=name, code=code)
        return jsonify(language), 201
    except Exception as e:
        logger.error("Error creating language: %s", e)
        if "UNIQUE constraint" in str(e):
            abort(400, description="Language with this name or code already exists")
        raise


@languages_bp.route("/api/languages/<int:language_id>", methods=["PUT"])
def update_language(language_id):
    """Update an existing language."""
    existing = Language.get_by_id(language_id)
    if not existing:
        abort(404, description=f"Language with id {language_id} not found")

    data = request.get_json()
    if not data:
        abort(400, description="Request body must be JSON")

    name = data.get("name", existing["name"])
    code = data.get("code", existing["code"])

    try:
        language = Language.update(language_id, name=name, code=code)
        return jsonify(language)
    except Exception as e:
        logger.error("Error updating language: %s", e)
        if "UNIQUE constraint" in str(e):
            abort(400, description="Language with this name or code already exists")
        raise


@languages_bp.route("/api/languages/<int:language_id>", methods=["DELETE"])
def delete_language(language_id):
    """Delete a language."""
    deleted = Language.delete(language_id)
    if not deleted:
        abort(404, description=f"Language with id {language_id} not found")
    return jsonify({"message": f"Language {language_id} deleted successfully"}), 200
