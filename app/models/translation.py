from app.models.database import get_db
from app.utils.logger import logger


class Translation:
    """Data-access layer for the translations table."""

    @staticmethod
    def get_all():
        conn = get_db()
        rows = conn.execute(
            """
            SELECT t.*, 
                   sl.name AS source_language_name, sl.code AS source_language_code,
                   tl.name AS target_language_name, tl.code AS target_language_code
            FROM translations t
            JOIN languages sl ON t.source_language_id = sl.id
            JOIN languages tl ON t.target_language_id = tl.id
            ORDER BY t.id
            """
        ).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    @staticmethod
    def get_by_id(translation_id: int):
        conn = get_db()
        row = conn.execute(
            """
            SELECT t.*, 
                   sl.name AS source_language_name, sl.code AS source_language_code,
                   tl.name AS target_language_name, tl.code AS target_language_code
            FROM translations t
            JOIN languages sl ON t.source_language_id = sl.id
            JOIN languages tl ON t.target_language_id = tl.id
            WHERE t.id = ?
            """,
            (translation_id,),
        ).fetchone()
        conn.close()
        return dict(row) if row else None

    @staticmethod
    def create(source_language_id: int, target_language_id: int, source_text: str, translated_text: str):
        conn = get_db()
        try:
            cursor = conn.execute(
                """INSERT INTO translations 
                   (source_language_id, target_language_id, source_text, translated_text)
                   VALUES (?, ?, ?, ?)""",
                (source_language_id, target_language_id, source_text, translated_text),
            )
            conn.commit()
            tid = cursor.lastrowid
            logger.info("Created translation id=%s", tid)
        finally:
            conn.close()
        return Translation.get_by_id(tid)

    @staticmethod
    def update(translation_id: int, source_language_id: int, target_language_id: int, source_text: str, translated_text: str):
        conn = get_db()
        try:
            conn.execute(
                """UPDATE translations 
                   SET source_language_id = ?, target_language_id = ?, 
                       source_text = ?, translated_text = ?
                   WHERE id = ?""",
                (source_language_id, target_language_id, source_text, translated_text, translation_id),
            )
            conn.commit()
            logger.info("Updated translation id=%s", translation_id)
        finally:
            conn.close()
        return Translation.get_by_id(translation_id)

    @staticmethod
    def delete(translation_id: int) -> bool:
        conn = get_db()
        try:
            cursor = conn.execute("DELETE FROM translations WHERE id = ?", (translation_id,))
            conn.commit()
            deleted = cursor.rowcount > 0
            if deleted:
                logger.info("Deleted translation id=%s", translation_id)
        finally:
            conn.close()
        return deleted
