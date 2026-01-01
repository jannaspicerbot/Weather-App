"""
Database session management
Provides connection pooling and query execution
"""

import sqlite3
from typing import Optional
from weather_app.config import DB_PATH


class DatabaseConnection:
    """Manages SQLite database connections"""
    
    @staticmethod
    def get_connection() -> sqlite3.Connection:
        """Create and return a database connection"""
        try:
            conn = sqlite3.connect(DB_PATH)
            conn.row_factory = sqlite3.Row
            return conn
        except sqlite3.Error as e:
            raise RuntimeError(f"Database connection error: {str(e)}")
    
    @staticmethod
    def close_connection(conn: sqlite3.Connection) -> None:
        """Close a database connection"""
        if conn:
            conn.close()


def row_to_dict(row: Optional[sqlite3.Row]) -> Optional[dict]:
    """Convert SQLite row to dictionary"""
    return dict(row) if row else None
