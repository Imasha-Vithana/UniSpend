
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "unispends.db"

KEEP_IDS = {6, 7}

with sqlite3.connect(DB_PATH) as conn:
    goals = conn.execute("""
        SELECT id, name, target_amount, saved_amount, deadline
        FROM savings_goals
        ORDER BY id
    """).fetchall()

    print("\nCurrent savings goals:")
    for goal in goals:
        print(goal)

    delete_ids = [
        goal[0] for goal in goals
        if goal[0] not in KEEP_IDS
        and goal[1].strip().lower() == "buy a laptop"
    ]

    print("\nGoals selected for deletion:", delete_ids)

    confirm = input(
        "\nType DELETE to confirm removing only these goal IDs: "
    )

    if confirm == "DELETE":
        conn.executemany(
            "DELETE FROM savings_goals WHERE id = ?",
            [(goal_id,) for goal_id in delete_ids]
        )
        conn.commit()
        print("Selected duplicate goals deleted successfully.")
    else:
        print("Cancelled. No goals were deleted.")
