from flask import Blueprint, request, jsonify, abort
from app.models.translation import Translation
from app.models.language import Language
from app.utils.logger import logger

translations_bp = Blueprint("translations", __name__)


@translations_bp.route("/api/translations", methods=["GET"])
def get_translations():
    """List all translations."""
    translations = Translation.get_all()
    return jsonify({"translations": translations, "count": len(translations)})


@translations_bp.route("/api/translations/<int:translation_id>", methods=["GET"])
def get_translation(translation_id):
    """Get a single translation by ID."""
    translation = Translation.get_by_id(translation_id)
    if not translation:
        abort(404, description=f"Translation with id {translation_id} not found")
    return jsonify(translation)


@translations_bp.route("/api/translations", methods=["POST"])
def create_translation():
    """Create a new translation record."""
    data = request.get_json()
    if not data:
        abort(400, description="Request body must be JSON")

    source_language_id = data.get("source_language_id")
    target_language_id = data.get("target_language_id")
    source_text = data.get("source_text")
    translated_text = data.get("translated_text")

    if not all([source_language_id, target_language_id, source_text, translated_text]):
        abort(400, description="Fields 'source_language_id', 'target_language_id', 'source_text', and 'translated_text' are required")

    # Validate language IDs exist
    if not Language.get_by_id(source_language_id):
        abort(404, description=f"Source language with id {source_language_id} not found")
    if not Language.get_by_id(target_language_id):
        abort(404, description=f"Target language with id {target_language_id} not found")

    try:
        translation = Translation.create(
            source_language_id=source_language_id,
            target_language_id=target_language_id,
            source_text=source_text,
            translated_text=translated_text,
        )
        return jsonify(translation), 201
    except Exception as e:
        logger.error("Error creating translation: %s", e)
        raise


@translations_bp.route("/api/translations/<int:translation_id>", methods=["PUT"])
def update_translation(translation_id):
    """Update an existing translation."""
    existing = Translation.get_by_id(translation_id)
    if not existing:
        abort(404, description=f"Translation with id {translation_id} not found")

    data = request.get_json()
    if not data:
        abort(400, description="Request body must be JSON")

    source_language_id = data.get("source_language_id", existing["source_language_id"])
    target_language_id = data.get("target_language_id", existing["target_language_id"])
    source_text = data.get("source_text", existing["source_text"])
    translated_text = data.get("translated_text", existing["translated_text"])

    try:
        translation = Translation.update(
            translation_id,
            source_language_id=source_language_id,
            target_language_id=target_language_id,
            source_text=source_text,
            translated_text=translated_text,
        )
        return jsonify(translation)
    except Exception as e:
        logger.error("Error updating translation: %s", e)
        raise


@translations_bp.route("/api/translations/<int:translation_id>", methods=["DELETE"])
def delete_translation(translation_id):
    """Delete a translation."""
    deleted = Translation.delete(translation_id)
    if not deleted:
        abort(404, description=f"Translation with id {translation_id} not found")
    return jsonify({"message": f"Translation {translation_id} deleted successfully"}), 200
