import json
import sqlite3
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_ROOT / "careercompass.db"


def get_connection():
    """Create a connection to the SQLite database."""
    return sqlite3.connect(DB_PATH)


def initialize_database():
    """Create the required database tables if they do not exist."""
    with get_connection() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS student_profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                education TEXT NOT NULL,
                skills TEXT NOT NULL,
                interests TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        connection.execute("""
            CREATE TABLE IF NOT EXISTS recommendations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                profile_id INTEGER NOT NULL,
                career TEXT NOT NULL,
                match_score REAL NOT NULL,
                details TEXT NOT NULL,
                FOREIGN KEY (profile_id)
                    REFERENCES student_profiles(id)
            )
        """)


def save_profile(name, education, skills, interests, results):
    """Save a student profile and its recommendations."""
    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO student_profiles
                (name, education, skills, interests)
            VALUES (?, ?, ?, ?)
            """,
            (
                name.strip(),
                education,
                json.dumps(skills),
                json.dumps(interests),
            ),
        )

        profile_id = cursor.lastrowid

        for result in results:
            connection.execute(
                """
                INSERT INTO recommendations
                    (profile_id, career, match_score, details)
                VALUES (?, ?, ?, ?)
                """,
                (
                    profile_id,
                    result["career"],
                    result["match_score"],
                    json.dumps(result),
                ),
            )

    return profile_id