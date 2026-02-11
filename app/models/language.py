from app.models.database import get_db
from app.utils.logger import logger


class Language:
    """Data-access layer for the languages table."""

    @staticmethod
    def get_all():
        conn = get_db()
        rows = conn.execute("SELECT * FROM languages ORDER BY id").fetchall()
        conn.close()
        return [dict(r) for r in rows]

    @staticmethod
    def get_by_id(language_id: int):
        conn = get_db()
        row = conn.execute("SELECT * FROM languages WHERE id = ?", (language_id,)).fetchone()
        conn.close()
        return dict(row) if row else None

    @staticmethod
    def create(name: str, code: str):
        conn = get_db()
        try:
            cursor = conn.execute(
                "INSERT INTO languages (name, code) VALUES (?, ?)",
                (name, code),
            )
            conn.commit()
            language_id = cursor.lastrowid
            logger.info("Created language id=%s name=%s", language_id, name)
        finally:
            conn.close()
        return Language.get_by_id(language_id)

    @staticmethod
    def update(language_id: int, name: str, code: str):
        conn = get_db()
        try:
            conn.execute(
                "UPDATE languages SET name = ?, code = ? WHERE id = ?",
                (name, code, language_id),
            )
            conn.commit()
            logger.info("Updated language id=%s", language_id)
        finally:
            conn.close()
        return Language.get_by_id(language_id)

    @staticmethod
    def delete(language_id: int) -> bool:
        conn = get_db()
        try:
            cursor = conn.execute("DELETE FROM languages WHERE id = ?", (language_id,))
            conn.commit()
            deleted = cursor.rowcount > 0
            if deleted:
                logger.info("Deleted language id=%s", language_id)
        finally:
            conn.close()
        return deleted
