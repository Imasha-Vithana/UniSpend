
import sqlite3
from pathlib import Path

db_path = Path(__file__).resolve().parent / "unispends.db"

with sqlite3.connect(db_path) as conn:
    rows = conn.execute("""
        SELECT id, name, target_amount, saved_amount, deadline
        FROM savings_goals
        ORDER BY id
    """).fetchall()

print("\nCurrent savings goals:\n")

for row in rows:
    print(
        f"ID: {row[0]} | Name: {row[1]} | "
        f"Target: Rs. {row[2]} | Saved: Rs. {row[3]} | "
        f"Deadline: {row[4]}"
    )
