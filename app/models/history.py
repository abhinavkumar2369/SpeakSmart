from app.models.database import get_db
from app.utils.logger import logger


class History:
    """Data-access layer for the translation_history table."""

    @staticmethod
    def get_all(limit: int = 50):
        conn = get_db()
        rows = conn.execute(
            "SELECT * FROM translation_history ORDER BY created_at DESC LIMIT ?",
            (limit,),
        ).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    @staticmethod
    def create(
        session_id: str,
        source_language: str,
        target_language: str,
        source_text: str,
        translated_text: str,
        grammar_score: float = None,
        ai_provider: str = "gemini",
    ):
        conn = get_db()
        try:
            cursor = conn.execute(
                """INSERT INTO translation_history 
                   (session_id, source_language, target_language, 
                    source_text, translated_text, grammar_score, ai_provider)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (session_id, source_language, target_language, source_text, translated_text, grammar_score, ai_provider),
            )
            conn.commit()
            logger.info("Saved history record id=%s", cursor.lastrowid)
        finally:
            conn.close()
