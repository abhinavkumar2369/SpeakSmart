from app.models.database import get_db
from app.utils.logger import logger


class GrammarRule:
    """Data-access layer for the grammar_rules table."""

    @staticmethod
    def get_all():
        conn = get_db()
        rows = conn.execute(
            """
            SELECT g.*, l.name AS language_name, l.code AS language_code
            FROM grammar_rules g
            JOIN languages l ON g.language_id = l.id
            ORDER BY g.id
            """
        ).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    @staticmethod
    def get_by_id(rule_id: int):
        conn = get_db()
        row = conn.execute(
            """
            SELECT g.*, l.name AS language_name, l.code AS language_code
            FROM grammar_rules g
            JOIN languages l ON g.language_id = l.id
            WHERE g.id = ?
            """,
            (rule_id,),
        ).fetchone()
        conn.close()
        return dict(row) if row else None

    @staticmethod
    def create(language_id: int, rule_name: str, description: str, example_correct: str = None, example_incorrect: str = None):
        conn = get_db()
        try:
            cursor = conn.execute(
                """INSERT INTO grammar_rules 
                   (language_id, rule_name, description, example_correct, example_incorrect)
                   VALUES (?, ?, ?, ?, ?)""",
                (language_id, rule_name, description, example_correct, example_incorrect),
            )
            conn.commit()
            rid = cursor.lastrowid
            logger.info("Created grammar rule id=%s name=%s", rid, rule_name)
        finally:
            conn.close()
        return GrammarRule.get_by_id(rid)

    @staticmethod
    def update(rule_id: int, language_id: int, rule_name: str, description: str, example_correct: str = None, example_incorrect: str = None):
        conn = get_db()
        try:
            conn.execute(
                """UPDATE grammar_rules 
                   SET language_id = ?, rule_name = ?, description = ?, 
                       example_correct = ?, example_incorrect = ?
                   WHERE id = ?""",
                (language_id, rule_name, description, example_correct, example_incorrect, rule_id),
            )
            conn.commit()
            logger.info("Updated grammar rule id=%s", rule_id)
        finally:
            conn.close()
        return GrammarRule.get_by_id(rule_id)

    @staticmethod
    def delete(rule_id: int) -> bool:
        conn = get_db()
        try:
            cursor = conn.execute("DELETE FROM grammar_rules WHERE id = ?", (rule_id,))
            conn.commit()
            deleted = cursor.rowcount > 0
            if deleted:
                logger.info("Deleted grammar rule id=%s", rule_id)
        finally:
            conn.close()
        return deleted
