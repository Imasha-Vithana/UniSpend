
import sqlite3
from datetime import date, timedelta
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest


@pytest.fixture
def app_test(tmp_path, monkeypatch):
    """Run UniSpend using a separate temporary database."""
    test_db = tmp_path / "test_unispends.db"
    monkeypatch.setenv("UNISPEND_DB_PATH", str(test_db))

    app_file = Path(__file__).resolve().parents[1] / "app.py"
    app = AppTest.from_file(str(app_file)).run()

    assert not app.exception, f"App startup failed: {app.exception}"

    return app, test_db


def test_app_starts_without_errors(app_test):
    app, test_db = app_test

    assert test_db.exists()


def test_database_has_required_tables(app_test):
    app, test_db = app_test

    with sqlite3.connect(test_db) as conn:
        tables = {
            row[0]
            for row in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            )
        }

    assert {"expenses", "app_settings", "savings_goals"} <= tables


def test_expense_functions(app_test):
    app, test_db = app_test

    with sqlite3.connect(test_db) as conn:
        cursor = conn.execute(
            """
            INSERT INTO expenses
            (name, category, amount, expense_date, note)
            VALUES (?, ?, ?, ?, ?)
            """,
            ("Lunch", "Food & Drinks", 450.0, date.today().isoformat(), "")
        )
        expense_id = cursor.lastrowid
        conn.commit()

        expense = conn.execute(
            "SELECT name, amount FROM expenses WHERE id = ?",
            (expense_id,)
        ).fetchone()

        assert expense == ("Lunch", 450.0)

        conn.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
        conn.commit()

        remaining = conn.execute(
            "SELECT COUNT(*) FROM expenses WHERE id = ?",
            (expense_id,)
        ).fetchone()[0]

    assert remaining == 0


def test_default_monthly_budget(app_test):
    app, test_db = app_test

    with sqlite3.connect(test_db) as conn:
        budget = conn.execute(
            "SELECT value FROM app_settings WHERE key = 'monthly_budget'"
        ).fetchone()

    assert budget is not None
    assert float(budget[0]) >= 0
