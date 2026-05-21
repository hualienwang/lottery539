import sqlite3
import tempfile
import unittest
from pathlib import Path

from lotto_data import load_draws_from_db, save_draw_to_db


class LottoDataTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "lotto.db"
        conn = sqlite3.connect(self.db_path)
        try:
            conn.execute(
                """
                CREATE TABLE lottery_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    period TEXT NOT NULL UNIQUE,
                    numbers TEXT NOT NULL,
                    draw_date TEXT NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            conn.executemany(
                "INSERT INTO lottery_results (period, numbers, draw_date) VALUES (?, ?, ?)",
                [
                    ("1150203", "03,05,11,15,23", "2026-02-03"),
                    ("1150202", "06,08,31,37,38", "2026-02-02"),
                ],
            )
            conn.commit()
        finally:
            conn.close()

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_load_draws_from_db_returns_json_compatible_draws_in_date_order(self):
        draws = load_draws_from_db(self.db_path)

        self.assertEqual(
            draws,
            [
                {"date": "2026-02-02", "numbers": [6, 8, 31, 37, 38], "period": "1150202"},
                {"date": "2026-02-03", "numbers": [3, 5, 11, 15, 23], "period": "1150203"},
            ],
        )

    def test_save_draw_to_db_inserts_sorted_numbers(self):
        saved = save_draw_to_db(self.db_path, [22, 3, 15, 11, 5], date="2026-02-04")

        self.assertTrue(saved)
        rows = load_draws_from_db(self.db_path)
        self.assertEqual(rows[-1]["date"], "2026-02-04")
        self.assertEqual(rows[-1]["numbers"], [3, 5, 11, 15, 22])


if __name__ == "__main__":
    unittest.main()
