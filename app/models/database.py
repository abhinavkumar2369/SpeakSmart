import sqlite3
import os
from app.config import Config
from app.utils.logger import logger


def get_db() -> sqlite3.Connection:
    """Return a connection to the SQLite database with row_factory set."""
    conn = sqlite3.connect(Config.DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """Create all tables if they do not exist."""
    logger.info("Initializing database at %s", Config.DATABASE_PATH)
    conn = get_db()
    cursor = conn.cursor()

    cursor.executescript(
        """
        CREATE TABLE IF NOT EXISTS languages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            code TEXT NOT NULL UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS translations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_language_id INTEGER NOT NULL,
            target_language_id INTEGER NOT NULL,
            source_text TEXT NOT NULL,
            translated_text TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (source_language_id) REFERENCES languages (id) ON DELETE CASCADE,
            FOREIGN KEY (target_language_id) REFERENCES languages (id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS grammar_rules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            language_id INTEGER NOT NULL,
            rule_name TEXT NOT NULL,
            description TEXT NOT NULL,
            example_correct TEXT,
            example_incorrect TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (language_id) REFERENCES languages (id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS translation_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            source_language TEXT,
            target_language TEXT,
            source_text TEXT,
            translated_text TEXT,
            grammar_score REAL,
            ai_provider TEXT DEFAULT 'gemini',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
    )
    conn.commit()
    conn.close()
    logger.info("Database initialized successfully")
