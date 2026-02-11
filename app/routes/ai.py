import uuid
from flask import Blueprint, request, jsonify, abort
from app.services.ai_service import ai_service
from app.models.history import History
from app.utils.logger import logger

ai_bp = Blueprint("ai", __name__)


@ai_bp.route("/api/ai/translate", methods=["POST"])
def ai_translate():
    """Translate text using AI (Gemini).

    Expects JSON: { "text": str, "source_language": str, "target_language": str }
    """
    data = request.get_json()
    if not data:
        abort(400, description="Request body must be JSON")

    text = data.get("text")
    source_lang = data.get("source_language")
    target_lang = data.get("target_language")

    if not all([text, source_lang, target_lang]):
        abort(400, description="Fields 'text', 'source_language', and 'target_language' are required")

    try:
        result = ai_service.translate(text, source_lang, target_lang)

        # Save to history
        History.create(
            session_id=data.get("session_id", str(uuid.uuid4())),
            source_language=source_lang,
            target_language=target_lang,
            source_text=text,
            translated_text=result.get("translated_text", ""),
            grammar_score=result.get("confidence"),
        )

        return jsonify({"status": "success", "data": result})
    except Exception as e:
        logger.error("AI translation error: %s", e)
        abort(500, description=f"AI translation failed: {str(e)}")


@ai_bp.route("/api/ai/grammar-check", methods=["POST"])
def ai_grammar_check():
    """Check grammar using AI (Gemini).

    Expects JSON: { "text": str, "language": str (optional, default "English") }
    """
    data = request.get_json()
    if not data:
        abort(400, description="Request body must be JSON")

    text = data.get("text")
    if not text:
        abort(400, description="Field 'text' is required")

    language = data.get("language", "English")

    try:
        result = ai_service.grammar_check(text, language)
        return jsonify({"status": "success", "data": result})
    except Exception as e:
        logger.error("AI grammar check error: %s", e)
        abort(500, description=f"AI grammar check failed: {str(e)}")


@ai_bp.route("/api/ai/summarize", methods=["POST"])
def ai_summarize():
    """Summarize text using AI (Gemini).

    Expects JSON: { "text": str, "target_language": str (optional), "max_sentences": int (optional) }
    """
    data = request.get_json()
    if not data:
        abort(400, description="Request body must be JSON")

    text = data.get("text")
    if not text:
        abort(400, description="Field 'text' is required")

    target_language = data.get("target_language")
    max_sentences = data.get("max_sentences", 3)

    try:
        result = ai_service.summarize(text, target_language, max_sentences)
        return jsonify({"status": "success", "data": result})
    except Exception as e:
        logger.error("AI summarize error: %s", e)
        abort(500, description=f"AI summarization failed: {str(e)}")


@ai_bp.route("/api/ai/language-detect", methods=["POST"])
def ai_language_detect():
    """Detect the language of text using AI (Gemini).

    Expects JSON: { "text": str }
    """
    data = request.get_json()
    if not data:
        abort(400, description="Request body must be JSON")

    text = data.get("text")
    if not text:
        abort(400, description="Field 'text' is required")

    try:
        result = ai_service.detect_language(text)
        return jsonify({"status": "success", "data": result})
    except Exception as e:
        logger.error("AI language detection error: %s", e)
        abort(500, description=f"AI language detection failed: {str(e)}")


@ai_bp.route("/api/ai/history", methods=["GET"])
def ai_history():
    """Get recent AI translation history."""
    limit = request.args.get("limit", 50, type=int)
    history = History.get_all(limit=limit)
    return jsonify({"history": history, "count": len(history)})
