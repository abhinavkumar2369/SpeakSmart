from flask import Blueprint, request, jsonify, abort
from app.models.grammar_rule import GrammarRule
from app.models.language import Language
from app.utils.logger import logger

grammar_rules_bp = Blueprint("grammar_rules", __name__)


@grammar_rules_bp.route("/api/grammar-rules", methods=["GET"])
def get_grammar_rules():
    """List all grammar rules."""
    rules = GrammarRule.get_all()
    return jsonify({"grammar_rules": rules, "count": len(rules)})


@grammar_rules_bp.route("/api/grammar-rules/<int:rule_id>", methods=["GET"])
def get_grammar_rule(rule_id):
    """Get a single grammar rule by ID."""
    rule = GrammarRule.get_by_id(rule_id)
    if not rule:
        abort(404, description=f"Grammar rule with id {rule_id} not found")
    return jsonify(rule)


@grammar_rules_bp.route("/api/grammar-rules", methods=["POST"])
def create_grammar_rule():
    """Create a new grammar rule."""
    data = request.get_json()
    if not data:
        abort(400, description="Request body must be JSON")

    language_id = data.get("language_id")
    rule_name = data.get("rule_name")
    description = data.get("description")

    if not all([language_id, rule_name, description]):
        abort(400, description="Fields 'language_id', 'rule_name', and 'description' are required")

    if not Language.get_by_id(language_id):
        abort(404, description=f"Language with id {language_id} not found")

    try:
        rule = GrammarRule.create(
            language_id=language_id,
            rule_name=rule_name,
            description=description,
            example_correct=data.get("example_correct"),
            example_incorrect=data.get("example_incorrect"),
        )
        return jsonify(rule), 201
    except Exception as e:
        logger.error("Error creating grammar rule: %s", e)
        raise


@grammar_rules_bp.route("/api/grammar-rules/<int:rule_id>", methods=["PUT"])
def update_grammar_rule(rule_id):
    """Update an existing grammar rule."""
    existing = GrammarRule.get_by_id(rule_id)
    if not existing:
        abort(404, description=f"Grammar rule with id {rule_id} not found")

    data = request.get_json()
    if not data:
        abort(400, description="Request body must be JSON")

    language_id = data.get("language_id", existing["language_id"])
    rule_name = data.get("rule_name", existing["rule_name"])
    description = data.get("description", existing["description"])
    example_correct = data.get("example_correct", existing["example_correct"])
    example_incorrect = data.get("example_incorrect", existing["example_incorrect"])

    try:
        rule = GrammarRule.update(
            rule_id,
            language_id=language_id,
            rule_name=rule_name,
            description=description,
            example_correct=example_correct,
            example_incorrect=example_incorrect,
        )
        return jsonify(rule)
    except Exception as e:
        logger.error("Error updating grammar rule: %s", e)
        raise


@grammar_rules_bp.route("/api/grammar-rules/<int:rule_id>", methods=["DELETE"])
def delete_grammar_rule(rule_id):
    """Delete a grammar rule."""
    deleted = GrammarRule.delete(rule_id)
    if not deleted:
        abort(404, description=f"Grammar rule with id {rule_id} not found")
    return jsonify({"message": f"Grammar rule {rule_id} deleted successfully"}), 200
