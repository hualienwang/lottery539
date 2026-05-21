# -*- coding: utf-8 -*-
"""SQLite storage helpers for 539 lottery draw data."""

import os
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Iterable, List, Optional


DEFAULT_DB_NAME = "lotto.db"


def ensure_db_schema(db_path: os.PathLike | str = DEFAULT_DB_NAME) -> None:
    """Create the lottery_results table when the database is new."""
    path = Path(db_path)
    if path.parent and str(path.parent) != ".":
        path.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(path)
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS lottery_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                period TEXT NOT NULL UNIQUE,
                numbers TEXT NOT NULL,
                draw_date TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.commit()
    finally:
        conn.close()


def parse_numbers(numbers_text: str) -> List[int]:
    """Parse comma-separated DB numbers into sorted integers."""
    numbers = [int(part.strip()) for part in numbers_text.split(",") if part.strip()]
    return sorted(numbers)


def format_numbers(numbers: Iterable[int]) -> str:
    """Format numbers with the same two-digit comma style used by lotto.db."""
    return ",".join(f"{num:02d}" for num in sorted(numbers))


def _default_period(date: str) -> str:
    draw_date = datetime.strptime(date, "%Y-%m-%d")
    roc_year = draw_date.year - 1911
    return f"{roc_year:03d}{draw_date.month:02d}{draw_date.day:02d}"


def load_draws_from_db(db_path: os.PathLike | str = DEFAULT_DB_NAME, limit: Optional[int] = None) -> List[dict]:
    """Load lottery draw history from SQLite in chronological order."""
    path = Path(db_path)
    if not path.exists():
        return []

    conn = sqlite3.connect(path)
    try:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            """
            SELECT period, numbers, draw_date, created_at
            FROM lottery_results
            ORDER BY draw_date ASC, id ASC
            """
        ).fetchall()
    finally:
        conn.close()

    if limit is not None:
        rows = rows[-limit:]

    return [
        {
            "date": row["draw_date"],
            "numbers": parse_numbers(row["numbers"]),
            "period": row["period"],
        }
        for row in rows
    ]


def save_draw_to_db(
    db_path: os.PathLike | str,
    numbers: Iterable[int],
    date: Optional[str] = None,
    period: Optional[str] = None,
) -> bool:
    """Insert one lottery draw into SQLite. Returns False on duplicate period."""
    ensure_db_schema(db_path)
    draw_date = date or datetime.now().strftime("%Y-%m-%d")
    draw_period = period or _default_period(draw_date)

    try:
        conn = sqlite3.connect(db_path)
        try:
            conn.execute(
                """
                INSERT INTO lottery_results (period, numbers, draw_date)
                VALUES (?, ?, ?)
                """,
                (draw_period, format_numbers(numbers), draw_date),
            )
            conn.commit()
        finally:
            conn.close()
        return True
    except sqlite3.IntegrityError:
        return False


def clear_draws_from_db(db_path: os.PathLike | str = DEFAULT_DB_NAME) -> None:
    """Delete all draw history from SQLite."""
    ensure_db_schema(db_path)
    conn = sqlite3.connect(db_path)
    try:
        conn.execute("DELETE FROM lottery_results")
        conn.commit()
    finally:
        conn.close()
