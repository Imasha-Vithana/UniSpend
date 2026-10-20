
import sqlite3
from contextlib import closing
from datetime import date, timedelta
from pathlib import Path
import os

import pandas as pd
import plotly.express as px
import streamlit as st
import math


# 1. CONFIGURATION

st.set_page_config(
    page_title="UniSpend | Student Finance",
    layout="wide",
    initial_sidebar_state="expanded",
)

DB_PATH = Path(
    os.environ.get(
        "UNISPEND_DB_PATH",
        str(Path(__file__).resolve().parent / "unispends.db"),
    )
)

CATEGORIES = [
    "Food & Drinks",
    "Transport",
    "Education",
    "Data & Internet",
    "Personal Care",
    "Shopping",
    "Bills",
    "Other",
]

CHART_COLORS = [
    "#24563D",
    "#6B9B78",
    "#A6C4A8",
    "#D3A76C",
    "#7696A5",
    "#B7A1C7",
    "#D98C79",
    "#87958B",
]

FOREST = "#18392B"
GREEN = "#24563D"
TEXT = "#24382D"
MUTED = "#607366"
BORDER = "#DCE6DE"



# 2. CUSTOM CSS — UNISPEND PROFESSIONAL THEME

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;500;600;700;800&display=swap');

    :root {
        --forest: #173D2B;
        --forest-hover: #214F38;
        --green: #2E6848;
        --sage: #E7EFE7;
        --page: #F5F7F4;
        --card: #FFFFFF;
        --text: #25372D;
        --muted: #66766B;
        --border: #DCE5DD;
        --input-bg: #FFFFFF;
        --shadow: 0 4px 18px rgba(23, 61, 43, 0.055);
    }

    /* Sample data information card */
    .sample-info-card {
        background: linear-gradient(135deg, #EAF2EB 0%, #F7FAF7 100%);
        border: 1px solid #D2E2D4;
        border-left: 4px solid #397451;
        border-radius: 12px;
        padding: 16px 17px;
        margin: 8px 0 14px 0;
    }

    .sample-info-title {
        color: #244B35 !important;
        -webkit-text-fill-color: #244B35 !important;
        font-size: 14px;
        font-weight: 700;
        margin-bottom: 6px;
        opacity: 1 !important;
    }

    .sample-info-description {
        color: #52685A !important;
        -webkit-text-fill-color: #52685A !important;
        font-size: 12px;
        line-height: 1.7;
        opacity: 1 !important;
    }

    .sample-info-status {
        display: inline-block;
        background: #D8E9DB;
        color: #24563D !important;
        -webkit-text-fill-color: #24563D !important;
        font-size: 10px;
        font-weight: 700;
        padding: 4px 8px;
        border-radius: 20px;
        margin-top: 10px;
        opacity: 1 !important;
    }

    /* Global */
    html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif;
    }

    .stApp,
    [data-testid="stAppViewContainer"] {
        background: var(--page) !important;
        color: var(--text) !important;
    }

    [data-testid="stHeader"] {
        background: rgba(245, 247, 244, 0.98) !important;
    }

    [data-testid="stAppViewContainer"] .main .block-container {
        max-width: 1450px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    .main h1, .main h2, .main h3, .main h4 {
        color: var(--forest) !important;
        -webkit-text-fill-color: var(--forest) !important;
        font-family: 'Manrope', sans-serif !important;
        font-weight: 800 !important;
    }

    .main p, .main li, .main label,
    .main [data-testid="stMarkdownContainer"] p {
        color: var(--text);
    }

    [data-testid="stCaptionContainer"],
    [data-testid="stCaptionContainer"] p {
        color: var(--muted) !important;
        -webkit-text-fill-color: var(--muted) !important;
        opacity: 1 !important;
    }

    /* Hero */
    .hero {
        background: linear-gradient(120deg, #173D2B 0%, #24563D 60%, #397451 100%) !important;
        padding: 38px;
        border-radius: 22px;
        margin-bottom: 28px;
        box-shadow: 0 12px 30px rgba(23, 61, 43, 0.13);
    }

    .hero .eyebrow {
        color: #D7E8DA !important;
        -webkit-text-fill-color: #D7E8DA !important;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 2px;
        text-transform: uppercase;
        margin-bottom: 12px;
    }

    .hero h1 {
        color: #FFFFFF !important;
        -webkit-text-fill-color: #FFFFFF !important;
        font-family: 'Manrope', sans-serif !important;
        font-size: clamp(28px, 3vw, 43px);
        line-height: 1.2;
        margin: 0 0 14px 0;
    }

    .hero p {
        color: #EDF4EE !important;
        -webkit-text-fill-color: #EDF4EE !important;
        font-size: 15px;
        line-height: 1.8;
        max-width: 700px;
    }

    /* Headings and cards */
    .section-heading {
        color: var(--forest) !important;
        -webkit-text-fill-color: var(--forest) !important;
        font-family: 'Manrope', sans-serif !important;
        font-size: 22px;
        font-weight: 800;
        margin: 30px 0 5px 0;
    }

    .section-subtitle {
        color: var(--muted) !important;
        -webkit-text-fill-color: var(--muted) !important;
        font-size: 13px;
        line-height: 1.7;
        margin-bottom: 18px;
    }

    .metric-card, .panel {
        background: var(--card) !important;
        color: var(--text) !important;
        border: 1px solid var(--border);
        border-radius: 17px;
        box-shadow: var(--shadow);
    }

    .metric-card {
        padding: 22px;
        min-height: 140px;
    }

    .metric-label {
        color: var(--muted) !important;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 0.7px;
        text-transform: uppercase;
        margin-bottom: 13px;
    }

    .metric-value {
        color: var(--forest) !important;
        font-family: 'Manrope', sans-serif !important;
        font-size: clamp(22px, 2vw, 30px);
        font-weight: 800;
        line-height: 1.3;
        overflow-wrap: anywhere;
    }

    .metric-note {
        color: var(--muted) !important;
        font-size: 12px;
        margin-top: 9px;
    }

    .panel {
        padding: 23px;
        margin-bottom: 18px;
    }

    /* Streamlit metrics */
    [data-testid="stMetric"] {
        background: #FFFFFF !important;
        border: 1px solid var(--border) !important;
        border-radius: 13px !important;
        padding: 15px 17px !important;
    }

    [data-testid="stMetricLabel"],
    [data-testid="stMetricLabel"] p {
        color: var(--muted) !important;
        -webkit-text-fill-color: var(--muted) !important;
        opacity: 1 !important;
    }

    [data-testid="stMetricValue"],
    [data-testid="stMetricValue"] div {
        color: var(--forest) !important;
        -webkit-text-fill-color: var(--forest) !important;
        font-family: 'Manrope', sans-serif !important;
        font-weight: 800 !important;
        opacity: 1 !important;
    }

    /* Forms and inputs */
    [data-testid="stForm"] {
        background: #FFFFFF !important;
        border: 1px solid var(--border) !important;
        border-radius: 17px !important;
        padding: 23px !important;
        box-shadow: var(--shadow);
    }

    [data-testid="stWidgetLabel"],
    [data-testid="stWidgetLabel"] p,
    [data-testid="stWidgetLabel"] label {
        color: var(--text) !important;
        -webkit-text-fill-color: var(--text) !important;
        font-weight: 600 !important;
        opacity: 1 !important;
    }

    .stApp input, .stApp textarea {
        background: #FFFFFF !important;
        color: #25372D !important;
        -webkit-text-fill-color: #25372D !important;
        caret-color: #24563D !important;
        border-radius: 9px !important;
        opacity: 1 !important;
    }

    .stApp input::placeholder,
    .stApp textarea::placeholder {
        color: #7A897E !important;
        -webkit-text-fill-color: #7A897E !important;
        opacity: 1 !important;
    }

    .stApp [data-baseweb="input"],
    .stApp [data-baseweb="textarea"] {
        background: #FFFFFF !important;
        border-color: #CAD8CC !important;
        border-radius: 9px !important;
    }

    .stApp [data-baseweb="input"]:focus-within,
    .stApp [data-baseweb="textarea"]:focus-within {
        border-color: #397451 !important;
        box-shadow: 0 0 0 1px #397451 !important;
    }

    /* Select boxes */
    .stApp [data-baseweb="select"] > div {
        background: #FFFFFF !important;
        border-color: #CAD8CC !important;
        border-radius: 9px !important;
    }

    .stApp [data-baseweb="select"] input,
    .stApp [data-baseweb="select"] div,
    .stApp [data-baseweb="select"] span {
        color: #25372D !important;
        -webkit-text-fill-color: #25372D !important;
        opacity: 1 !important;
    }

    [data-baseweb="popover"], [data-baseweb="menu"],
    [role="listbox"], [role="option"] {
        background: #FFFFFF !important;
        color: #25372D !important;
    }

    [role="option"]:hover {
        background: #E7EFE7 !important;
    }

    /* Date picker */
    [data-baseweb="calendar"],
    [data-baseweb="calendar"] * {
        color: #25372D !important;
    }

    [data-baseweb="calendar"] {
        background: #FFFFFF !important;
    }

    /* Buttons — original dark-green styling */
    .stButton > button,
    .stFormSubmitButton > button,
    [data-testid="stDownloadButton"] > button {
        background: #24563D !important;
        color: #FFFFFF !important;
        -webkit-text-fill-color: #FFFFFF !important;
        border: 1px solid #24563D !important;
        border-radius: 10px !important;
        min-height: 42px;
        font-weight: 700 !important;
        box-shadow: none !important;
        opacity: 1 !important;
        transition: background 0.2s ease;
    }

    .stButton > button *,
    .stFormSubmitButton > button *,
    [data-testid="stDownloadButton"] > button * {
        color: #FFFFFF !important;
        -webkit-text-fill-color: #FFFFFF !important;
        font-weight: 700 !important;
        opacity: 1 !important;
    }

    .stButton > button:hover,
    .stFormSubmitButton > button:hover,
    [data-testid="stDownloadButton"] > button:hover {
        background: #173D2B !important;
        border-color: #173D2B !important;
    }

    .stButton > button:disabled,
    .stFormSubmitButton > button:disabled {
        background: #E1E8E1 !important;
        color: #66766B !important;
        -webkit-text-fill-color: #66766B !important;
        border-color: #E1E8E1 !important;
    }

    /* Checkboxes and radio buttons */
    [data-testid="stCheckbox"] label,
    [data-testid="stRadio"] label,
    [data-testid="stCheckbox"] p,
    [data-testid="stRadio"] p {
        color: var(--text) !important;
        -webkit-text-fill-color: var(--text) !important;
        opacity: 1 !important;
    }

    /* Expanders */
    [data-testid="stExpander"] {
        background: #FFFFFF !important;
        color: #173D2B !important;
        border: 1px solid var(--border) !important;
        border-radius: 13px !important;
        overflow: hidden;
        opacity: 1 !important;
    }

    [data-testid="stExpander"] details,
    [data-testid="stExpander"] summary {
        background: #FFFFFF !important;
        color: #173D2B !important;
        -webkit-text-fill-color: #173D2B !important;
        font-weight: 700 !important;
        opacity: 1 !important;
    }

    [data-testid="stExpander"] summary *,
    [data-testid="stExpander"] summary p,
    [data-testid="stExpander"] summary span,
    [data-testid="stExpander"] summary svg {
        color: #173D2B !important;
        -webkit-text-fill-color: #173D2B !important;
        fill: #173D2B !important;
        opacity: 1 !important;
        visibility: visible !important;
    }

    [data-testid="stExpander"] [data-testid="stMarkdownContainer"],
    [data-testid="stExpander"] [data-testid="stMarkdownContainer"] p {
        color: #25372D !important;
        -webkit-text-fill-color: #25372D !important;
        opacity: 1 !important;
    }

    /* Progress bars */
    .stProgress > div {
        background: #E5ECE5 !important;
        border-radius: 99px !important;
    }

    .stProgress > div > div > div > div {
        background: #397451 !important;
        border-radius: 99px !important;
    }

    /* Tables and alerts */
    [data-testid="stDataFrame"], [data-testid="stTable"] {
        background: #FFFFFF !important;
        border: 1px solid var(--border) !important;
        border-radius: 12px !important;
        overflow: hidden;
    }

    [data-testid="stAlert"] {
        border-radius: 12px !important;
    }

    [data-testid="stAlert"] p {
        color: #25372D !important;
        -webkit-text-fill-color: #25372D !important;
        opacity: 1 !important;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: #173D2B !important;
        border-right: 1px solid #2C533C;
    }

    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] h4 {
        color: #FFFFFF !important;
        -webkit-text-fill-color: #FFFFFF !important;
        opacity: 1 !important;
    }

    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
        color: #F0F5F0 !important;
        -webkit-text-fill-color: #F0F5F0 !important;
        opacity: 1 !important;
    }

    /* Sidebar caption */
    section[data-testid="stSidebar"] [data-testid="stCaptionContainer"],
    section[data-testid="stSidebar"] [data-testid="stCaptionContainer"] * {
        color: #D0DFD2 !important;
        -webkit-text-fill-color: #D0DFD2 !important;
        opacity: 1 !important;
        visibility: visible !important;
    }

    section[data-testid="stSidebar"] input,
    section[data-testid="stSidebar"] textarea {
        background: #FFFFFF !important;
        color: #25372D !important;
        -webkit-text-fill-color: #25372D !important;
        opacity: 1 !important;
    }

    section[data-testid="stSidebar"] [data-baseweb="select"] > div {
        background: #FFFFFF !important;
    }

    section[data-testid="stSidebar"] [data-baseweb="select"] * {
        color: #25372D !important;
        -webkit-text-fill-color: #25372D !important;
        opacity: 1 !important;
    }

    

/* Sidebar widget labels — targeted fix only */
section[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p,
section[data-testid="stSidebar"] [data-testid="stWidgetLabel"] label,
section[data-testid="stSidebar"] [data-testid="stWidgetLabel"] span {
    color: #F0F5F0 !important;
    -webkit-text-fill-color: #F0F5F0 !important;
    opacity: 1 !important;
    visibility: visible !important;
    font-weight: 600 !important;
}



    /* FIX: Sample data expander label */
    section[data-testid="stSidebar"] [data-testid="stExpander"] summary,
    section[data-testid="stSidebar"] [data-testid="stExpander"] summary *,
    section[data-testid="stSidebar"] [data-testid="stExpander"] summary p,
    section[data-testid="stSidebar"] [data-testid="stExpander"] summary span {
        color: #173D2B !important;
        -webkit-text-fill-color: #173D2B !important;
        opacity: 1 !important;
        visibility: visible !important;
    }

    /* FIX: Input text and placeholders */
    section[data-testid="stSidebar"] input,
    section[data-testid="stSidebar"] textarea {
        color: #25372D !important;
        -webkit-text-fill-color: #25372D !important;
        opacity: 1 !important;
    }

    section[data-testid="stSidebar"] input::placeholder,
    section[data-testid="stSidebar"] textarea::placeholder {
        color: #7A897E !important;
        -webkit-text-fill-color: #7A897E !important;
        opacity: 1 !important;
    }

    /* Divider and footer */
    hr {
        border-color: var(--border) !important;
        margin: 28px 0 !important;
    }

    .footer {
        text-align: center;
        padding: 28px 10px 8px;
        color: #66766B !important;
        -webkit-text-fill-color: #66766B !important;
        font-size: 12px;
        line-height: 1.9;
        opacity: 1 !important;
    }

    .footer strong {
        color: #24563D !important;
        -webkit-text-fill-color: #24563D !important;
    }

/* Mobile layout */
@media (max-width: 768px) {
    [data-testid="stAppViewContainer"] .main .block-container {
        padding: 1rem 1rem 2rem;
    }

    .hero {
        padding: 25px 22px;
        border-radius: 16px;
    }

    .metric-card, .panel {
        padding: 16px;
    }

    .section-heading {
        font-size: 20px;
    }

} /* Mobile layout eka methanin close wenawa */


/* FINAL FIX: Sidebar labels */
section[data-testid="stSidebar"] [data-testid="stWidgetLabel"],
section[data-testid="stSidebar"] [data-testid="stWidgetLabel"] *,
section[data-testid="stSidebar"] .stTextInput label,
section[data-testid="stSidebar"] .stNumberInput label,
section[data-testid="stSidebar"] .stSelectbox label,
section[data-testid="stSidebar"] .stTextArea label,
section[data-testid="stSidebar"] .stDateInput label {
    color: #F0F5F0 !important;
    -webkit-text-fill-color: #F0F5F0 !important;
    opacity: 1 !important;
    visibility: visible !important;
}

/* Sample data label */
section[data-testid="stSidebar"] [data-testid="stExpander"] summary,
section[data-testid="stSidebar"] [data-testid="stExpander"] summary * {
    color: #173D2B !important;
    -webkit-text-fill-color: #173D2B !important;
    opacity: 1 !important;
    visibility: visible !important;
}

/* Sidebar caption */
section[data-testid="stSidebar"] [data-testid="stCaptionContainer"],
section[data-testid="stSidebar"] [data-testid="stCaptionContainer"] * {
    color: #D0DFD2 !important;
    -webkit-text-fill-color: #D0DFD2 !important;
    opacity: 1 !important;
    visibility: visible !important;
}

/* UniSpend — Sidebar Widget Label Colours */
section[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p,
section[data-testid="stSidebar"] [data-testid="stWidgetLabel"] label,
section[data-testid="stSidebar"] [data-testid="stWidgetLabel"] span {
    color: #8BC9A5 !important;
    -webkit-text-fill-color: #8BC9A5 !important;
    opacity: 1 !important;
    visibility: visible !important;
    font-weight: 600 !important;
}
    
    </style>
    """,
    unsafe_allow_html=True,
)

# 3. DATABASE CONNECTION

def get_connection():
    conn = sqlite3.connect(str(DB_PATH), timeout=10)
    conn.row_factory = sqlite3.Row
    return conn


def init_database():
    with closing(get_connection()) as conn:

        conn.execute("""
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                amount REAL NOT NULL,
                expense_date TEXT NOT NULL,
                note TEXT DEFAULT ''
            )
        """)

        # Use a new settings table so the existing settings table
        # is not destructively changed.
        conn.execute("""
            CREATE TABLE IF NOT EXISTS app_settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS savings_goals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                target_amount REAL NOT NULL,
                saved_amount REAL DEFAULT 0,
                deadline TEXT DEFAULT '',
                created_at TEXT NOT NULL
            )
        """)

        # Preserve an existing budget setting where possible.
        existing_budget = conn.execute("""
            SELECT value
            FROM app_settings
            WHERE key = 'monthly_budget'
        """).fetchone()

        if existing_budget is None:
            old_settings = conn.execute(
                "PRAGMA table_info(settings)"
            ).fetchall()

            old_columns = [row["name"] for row in old_settings]
            recovered_budget = None

            if old_columns:
                value_column = next(
                    (
                        column for column in
                        ["value", "setting_value", "monthly_budget", "budget"]
                        if column in old_columns
                    ),
                    None,
                )

                key_column = next(
                    (
                        column for column in
                        ["key", "setting_key", "name", "setting"]
                        if column in old_columns
                    ),
                    None,
                )

                if value_column:
                    if key_column:
                        try:
                            row = conn.execute(
                                f"""
                                SELECT "{value_column}"
                                FROM settings
                                WHERE "{key_column}" = ?
                                LIMIT 1
                                """,
                                ("monthly_budget",),
                            ).fetchone()

                            if row is not None:
                                recovered_budget = float(row[0])
                        except (ValueError, TypeError, sqlite3.Error):
                            recovered_budget = None

                    if recovered_budget is None and value_column in [
                        "monthly_budget", "budget"
                    ]:
                        try:
                            row = conn.execute(
                                f"""
                                SELECT "{value_column}"
                                FROM settings
                                LIMIT 1
                                """
                            ).fetchone()

                            if row is not None:
                                recovered_budget = float(row[0])
                        except (ValueError, TypeError, sqlite3.Error):
                            recovered_budget = None

            if recovered_budget is None or recovered_budget < 0:
                recovered_budget = 15000.0

            conn.execute("""
                INSERT OR IGNORE INTO app_settings (key, value)
                VALUES (?, ?)
            """, ("monthly_budget", str(recovered_budget)))

        conn.commit()


# =========================================================
# 4. SETTINGS AND EXPENSE FUNCTIONS
# =========================================================

def get_monthly_budget():
    with closing(get_connection()) as conn:
        row = conn.execute("""
            SELECT value
            FROM app_settings
            WHERE key = 'monthly_budget'
        """).fetchone()

    if row is None:
        return 15000.0

    try:
        return max(float(row["value"]), 0.0)
    except (ValueError, TypeError):
        return 15000.0


def save_monthly_budget(amount):
    with closing(get_connection()) as conn:
        conn.execute("""
            INSERT INTO app_settings (key, value)
            VALUES ('monthly_budget', ?)
            ON CONFLICT(key)
            DO UPDATE SET value = excluded.value
        """, (str(float(amount)),))
        conn.commit()


def get_expenses():
    with closing(get_connection()) as conn:
        rows = conn.execute("""
            SELECT id, name, category, amount, expense_date, note
            FROM expenses
            ORDER BY expense_date DESC, id DESC
        """).fetchall()

    columns = [
        "id", "name", "category", "amount", "expense_date", "note"
    ]

    df = pd.DataFrame([dict(row) for row in rows], columns=columns)

    if df.empty:
        return df

    df["amount"] = pd.to_numeric(
        df["amount"], errors="coerce"
    ).fillna(0)

    df["expense_date"] = pd.to_datetime(
        df["expense_date"], errors="coerce"
    )

    return df.dropna(subset=["expense_date"])



def add_expense(name, category, amount, expense_date, note):
    name = str(name).strip()

    if not name:
        raise ValueError("Expense name cannot be empty.")

    amount = float(amount)

    if not math.isfinite(amount) or amount <= 0:
        raise ValueError("Expense amount must be greater than zero.")

    if category not in CATEGORIES:
        raise ValueError("Please select a valid expense category.")

    if expense_date > date.today():
        raise ValueError("Expense date cannot be in the future.")

    with closing(get_connection()) as conn:
        conn.execute("""
            INSERT INTO expenses
            (name, category, amount, expense_date, note)
            VALUES (?, ?, ?, ?, ?)
        """, (
            name,
            category,
            amount,
            expense_date.isoformat(),
            str(note or "").strip(),
        ))
        conn.commit()



def update_expense(
    expense_id, name, category, amount, expense_date, note
):
    with closing(get_connection()) as conn:
        conn.execute("""
            UPDATE expenses
            SET name = ?,
                category = ?,
                amount = ?,
                expense_date = ?,
                note = ?
            WHERE id = ?
        """, (
            name.strip(),
            category,
            float(amount),
            expense_date.isoformat(),
            note.strip(),
            int(expense_id),
        ))
        conn.commit()


def delete_expense(expense_id):
    with closing(get_connection()) as conn:
        conn.execute(
            "DELETE FROM expenses WHERE id = ?",
            (int(expense_id),),
        )
        conn.commit()


# =========================================================
# 5. SAVINGS GOALS
# =========================================================

def get_savings_goals():
    with closing(get_connection()) as conn:
        rows = conn.execute("""
            SELECT id, name, target_amount, saved_amount,
                   deadline, created_at
            FROM savings_goals
            ORDER BY id DESC
        """).fetchall()

    return pd.DataFrame([dict(row) for row in rows])



def add_savings_goal(name, target_amount, saved_amount, deadline):
    name = str(name).strip()
    target_amount = float(target_amount)
    saved_amount = float(saved_amount)

    if not name:
        raise ValueError("Goal name cannot be empty.")

    if not math.isfinite(target_amount) or target_amount <= 0:
        raise ValueError("Target amount must be greater than zero.")

    if not math.isfinite(saved_amount) or saved_amount < 0:
        raise ValueError("Saved amount cannot be negative.")

    if saved_amount > target_amount:
        raise ValueError("Saved amount cannot exceed the target amount.")

    deadline_value = str(deadline or "").strip()

    with closing(get_connection()) as conn:
        duplicate = conn.execute(
            """
            SELECT 1
            FROM savings_goals
            WHERE lower(trim(name)) = lower(trim(?))
              AND target_amount = ?
              AND saved_amount < target_amount
            LIMIT 1
            """,
            (name, target_amount),
        ).fetchone()

        if duplicate:
            return False

        conn.execute(
            """
            INSERT INTO savings_goals
            (name, target_amount, saved_amount, deadline, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                name,
                target_amount,
                saved_amount,
                deadline_value,
                date.today().isoformat(),
            ),
        )
        conn.commit()

    return True



def update_savings_progress(goal_id, saved_amount):
    saved_amount = float(saved_amount)

    if not math.isfinite(saved_amount) or saved_amount < 0:
        raise ValueError(
            "Saved amount must be a valid, non-negative number."
        )

    with closing(get_connection()) as conn:
        goal = conn.execute(
            """
            SELECT target_amount
            FROM savings_goals
            WHERE id = ?
            """,
            (int(goal_id),),
        ).fetchone()

        if goal is None:
            raise ValueError("Savings goal not found.")

        target_amount = float(goal["target_amount"])

        if saved_amount > target_amount:
            raise ValueError(
                "Saved amount cannot exceed the target amount."
            )

        conn.execute(
            """
            UPDATE savings_goals
            SET saved_amount = ?
            WHERE id = ?
            """,
            (saved_amount, int(goal_id)),
        )
        conn.commit()


# 6. HELPER FUNCTIONS

def money(value):
    return f"Rs. {float(value):,.2f}"


def current_month_expenses(df):
    if df.empty:
        return df.copy()

    today = date.today()

    return df[
        (df["expense_date"].dt.year == today.year)
        & (df["expense_date"].dt.month == today.month)
    ].copy()


def section_heading(title, subtitle=""):
    st.markdown(
        f'<div class="section-heading">{title}</div>',
        unsafe_allow_html=True,
    )

    if subtitle:
        st.markdown(
            f'<div class="section-subtitle">{subtitle}</div>',
            unsafe_allow_html=True,
        )


def metric_card(label, value, note):
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-note">{note}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def style_chart(fig, height=330):
    fig.update_layout(
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={
            "family": "DM Sans, sans-serif",
            "color": TEXT,
            "size": 12,
        },
        margin={"l": 12, "r": 12, "t": 25, "b": 12},
        legend={"bgcolor": "rgba(0,0,0,0)"},
    )

    fig.update_xaxes(
        showgrid=False,
        linecolor=BORDER,
        tickfont={"color": MUTED},
    )

    fig.update_yaxes(
        gridcolor="#E8EEE9",
        zerolinecolor=BORDER,
        tickfont={"color": MUTED},
    )

    return fig


# 7. INITIALIZE APP

init_database()

df = get_expenses()
month_df = current_month_expenses(df)

budget = get_monthly_budget()
monthly_spent = (
    float(month_df["amount"].sum())
    if not month_df.empty else 0.0
)
remaining = budget - monthly_spent
transaction_count = len(month_df)

budget_used = (
    monthly_spent / budget * 100
    if budget > 0 else 0.0
)




# 8. SIDEBAR

with st.sidebar:
    st.title("UniSpend")
    st.caption("Student Finance Manager")

    # MONTHLY BUDGET FORM
    st.subheader("Monthly Budget")

    with st.form("monthly_budget_form"):
        new_budget = st.number_input(
            "Monthly budget (Rs.)",
            min_value=0.0,
            value=float(get_monthly_budget()),
            step=500.0,
        )

        save_budget = st.form_submit_button(
            "Save monthly budget",
            use_container_width=True,
        )

    if save_budget:
        if not math.isfinite(new_budget) or new_budget < 0:
            st.error("Enter a valid monthly budget.")
        else:
            save_monthly_budget(new_budget)
            st.success("Monthly budget saved!")
            st.rerun()

    st.divider()

    # ADD EXPENSE FORM
    st.subheader("Add Expense")

    with st.form("add_expense_form", clear_on_submit=True):
        expense_name = st.text_input(
            "Expense name",
            placeholder="e.g. Lunch",
        )

        expense_amount = st.number_input(
            "Amount (Rs.)",
            min_value=0.01,
            value=100.0,
            step=50.0,
        )

        expense_category = st.selectbox(
            "Category",
            CATEGORIES,
        )

        expense_date = st.date_input(
            "Expense date",
            value=date.today(),
            max_value=date.today(),
        )

        expense_note = st.text_input(
            "Note (optional)",
            placeholder="e.g. Lunch at campus",
        )

        add_expense_button = st.form_submit_button(
            "Add expense",
            use_container_width=True,
        )

    if add_expense_button:
        try:
            add_expense(
                expense_name,
                expense_category,
                expense_amount,
                expense_date,
                expense_note,
            )
            st.success("Expense added successfully!")
            st.rerun()
        except (ValueError, OverflowError) as error:
            st.error(str(error))

    st.divider()

    # SAMPLE DATA
    with st.expander("Sample data", expanded=False):
        st.markdown(
            """
            <div class="sample-info-card">
                <div class="sample-info-title">
                    Demo transactions
                </div>
                <div class="sample-info-description">
                    Explore UniSpend with example expenses when
                    your database has no transactions yet.
                    Demo entries can be managed like regular
                    transactions.
                </div>
                <div class="sample-info-status">
                    OPTIONAL DEMO DATA
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button(
            "Load demo data",
            use_container_width=True,
            key="load_demo_data",
        ):
            if get_expenses().empty:
                today = date.today()

                samples = [
                    ("Lunch", "Food & Drinks", 450, 1, "Campus lunch"),
                    ("Bus fare", "Transport", 180, 1, "Travel"),
                    ("Mobile data", "Data & Internet", 650, 2, "Data package"),
                    ("Notebook", "Education", 320, 3, "Study supplies"),
                    ("Groceries", "Food & Drinks", 1250, 4, "Weekly groceries"),
                    ("Personal items", "Personal Care", 540, 5, ""),
                ]

                for name, category, amount, days_ago, note in samples:
                    add_expense(
                        name,
                        category,
                        amount,
                        today - timedelta(days=days_ago),
                        note,
                    )

                st.success("Demo expenses added successfully.")
                st.rerun()
            else:
                st.info(
                    "Your database already contains transactions. "
                    "No demo expenses were added."
                )

    st.divider()
    st.caption("Spend mindfully. Save consistently.")


# 9. HERO

st.markdown(
    """
    <div class="hero">
        <div class="eyebrow">YOUR MONEY, YOUR FUTURE</div>
        <h1>Make every rupee count.</h1>
        <p>
            Understand your spending, stay within your monthly budget,
            and build better money habits one day at a time.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(f"**Overview for {date.today().strftime('%B %Y')}**")
st.caption("Your financial snapshot for the current month.")


# 10. DASHBOARD METRICS

col1, col2, col3, col4 = st.columns(4, gap="medium")

with col1:
    metric_card("Monthly budget", money(budget), "Your spending limit")

with col2:
    metric_card(
        "Total spent",
        money(monthly_spent),
        f"{budget_used:.1f}% of your budget used",
    )

with col3:
    metric_card(
        "Remaining balance",
        money(remaining),
        "Budget minus spending",
    )

with col4:
    metric_card(
        "Transactions",
        f"{transaction_count:,}",
        "Expenses recorded this month",
    )



# 11. BUDGET HEALTH

section_heading(
    "Budget health",
    "Track how much of your monthly budget you have used.",
)

st.markdown('<div class="panel">', unsafe_allow_html=True)

progress_value = (
    min(max(budget_used / 100, 0), 1)
    if budget > 0 else 0
)

st.progress(progress_value)

p1, p2 = st.columns(2)

with p1:
    st.markdown(f"**{budget_used:.1f}% used**")
    st.caption(f"Spent: {money(monthly_spent)}")

with p2:
    if remaining >= 0:
        st.markdown(f"**{money(remaining)} remaining**")
    else:
        st.markdown(f"**{money(abs(remaining))} over budget**")

    st.caption(f"Budget: {money(budget)}")

if budget <= 0:
    st.info("Set a monthly budget in the sidebar to track spending.")
elif remaining < 0:
    st.error(
        f"You have exceeded your budget by {money(abs(remaining))}. "
        "Review your recent expenses."
    )
elif budget_used >= 80:
    st.warning(
        "You have used at least 80% of your monthly budget."
    )
else:
    st.success("You are within your monthly budget.")

st.markdown("</div>", unsafe_allow_html=True)


# 12. SPENDING INSIGHTS

section_heading(
    "Spending insights",
    "Understand where your money goes and how spending changes.",
)

chart_left, chart_right = st.columns(2, gap="large")

with chart_left:
    st.markdown("#### Spending by category")

    if month_df.empty:
        st.info("Add expenses to see your category breakdown.")
    else:
        category_data = (
            month_df.groupby("category", as_index=False)["amount"]
            .sum()
            .sort_values("amount", ascending=False)
        )

        fig = px.pie(
            category_data,
            names="category",
            values="amount",
            hole=0.62,
            color_discrete_sequence=CHART_COLORS,
        )

        fig.update_traces(
            textposition="inside",
            textinfo="percent",
            marker={"line": {"color": "#FFFFFF", "width": 2}},
            hovertemplate=(
                "%{label}<br>Rs. %{value:,.2f}<extra></extra>"
            ),
        )

        fig = style_chart(fig, 340)
        fig.update_layout(
            legend={"orientation": "h", "y": -0.12, "x": 0}
        )

        st.plotly_chart(fig, use_container_width=True)

        top_category = category_data.iloc[0]

        st.caption(
            f"Highest spending category: {top_category['category']} "
            f"({money(top_category['amount'])})"
        )

with chart_right:
    st.markdown("#### Spending over the last 7 days")

    today = date.today()
    seven_days_ago = today - timedelta(days=6)

    if df.empty:
        st.info("Your daily spending chart will appear here.")
    else:
        recent = df[
            (df["expense_date"].dt.date >= seven_days_ago)
            & (df["expense_date"].dt.date <= today)
        ].copy()

        daily_dates = [
            seven_days_ago + timedelta(days=i)
            for i in range(7)
        ]

        daily_data = (
            recent.groupby(recent["expense_date"].dt.date)["amount"]
            .sum()
            .reindex(daily_dates, fill_value=0)
            .rename_axis("date")
            .reset_index(name="amount")
        )

        daily_data["day"] = pd.to_datetime(
            daily_data["date"]
        ).dt.strftime("%a")

        fig = px.bar(
            daily_data,
            x="day",
            y="amount",
            labels={"day": "Day", "amount": "Spending (Rs.)"},
            color_discrete_sequence=["#477B58"],
        )

        fig.update_traces(
            hovertemplate=(
                "%{x}<br>Rs. %{y:,.2f}<extra></extra>"
            )
        )

        fig = style_chart(fig, 340)
        st.plotly_chart(fig, use_container_width=True)

        st.caption(
            "Total in the last 7 days: "
            f"{money(daily_data['amount'].sum())}"
        )


# 13. ADVANCED ANALYTICS

section_heading(
    "Advanced analytics",
    "Explore monthly trends and useful spending indicators.",
)

analytics_left, analytics_right = st.columns(2, gap="large")

with analytics_left:
    st.markdown("#### Monthly spending trend")

    if df.empty:
        st.info("Your monthly trend will appear after recording expenses.")
    else:
        today = date.today()

        month_periods = pd.period_range(
            end=pd.Period(today, freq="M"),
            periods=6,
            freq="M",
        )

        first_month = month_periods[0]

        trend_df = df[
            df["expense_date"].dt.to_period("M") >= first_month
        ].copy()

        trend_df["month"] = (
            trend_df["expense_date"].dt.to_period("M").astype(str)
        )

        trend = trend_df.groupby(
            "month", as_index=False
        )["amount"].sum()

        all_months = pd.DataFrame({
            "month": [str(period) for period in month_periods]
        })

        trend = all_months.merge(
            trend, on="month", how="left"
        )

        trend["amount"] = trend["amount"].fillna(0)

        trend["month_label"] = pd.to_datetime(
            trend["month"] + "-01"
        ).dt.strftime("%b %Y")

        fig = px.line(
            trend,
            x="month_label",
            y="amount",
            markers=True,
            labels={
                "month_label": "Month",
                "amount": "Spending (Rs.)",
            },
            color_discrete_sequence=["#24563D"],
        )

        fig.update_traces(
            line={"width": 3},
            marker={"size": 8},
            hovertemplate=(
                "%{x}<br>Rs. %{y:,.2f}<extra></extra>"
            ),
        )

        fig = style_chart(fig, 330)
        st.plotly_chart(fig, use_container_width=True)

with analytics_right:
    st.markdown("#### This month's insights")

    if month_df.empty:
        st.info("Add expenses to generate monthly insights.")
    else:
        category_totals = (
            month_df.groupby("category")["amount"]
            .sum()
            .sort_values(ascending=False)
        )

        highest_category = category_totals.index[0]
        highest_amount = float(category_totals.iloc[0])

        today = date.today()

        days_in_month = (
            (today.replace(day=28) + timedelta(days=4))
            .replace(day=1)
            - timedelta(days=1)
        ).day

        average_daily = monthly_spent / max(today.day, 1)
        projected_spend = average_daily * days_in_month

        st.markdown('<div class="panel">', unsafe_allow_html=True)

        st.markdown("**Highest spending category**")
        st.markdown(f"### {highest_category}")
        st.caption(money(highest_amount))

        st.divider()

        st.markdown("**Average daily spending**")
        st.markdown(f"### {money(average_daily)}")

        st.divider()

        st.markdown("**Estimated spending by month-end**")
        st.markdown(f"### {money(projected_spend)}")

        if budget > 0 and projected_spend > budget:
            st.warning(
                "At your current pace, you may exceed your budget."
            )
        else:
            st.caption(
                "The projection is an estimate based on spending so far."
            )

        st.markdown("</div>", unsafe_allow_html=True)


# 14. TRANSACTIONS

section_heading(
    "Transactions",
    "Review, filter, export, edit, or delete expense records.",
)

if df.empty:
    st.info(
        "No expenses recorded yet. Use the sidebar to add your first expense."
    )
else:
    filter1, filter2, filter3 = st.columns([1.3, 1, 1])

    with filter1:
        month_options = sorted(
            df["expense_date"].dt.to_period("M").astype(str).unique(),
            reverse=True,
        )

        selected_month = st.selectbox(
            "Filter by month",
            ["All months"] + month_options,
        )

    with filter2:
        category_options = ["All categories"] + sorted(
            df["category"].dropna().unique().tolist()
        )

        selected_category = st.selectbox(
            "Filter by category",
            category_options,
        )

    with filter3:
        search_term = st.text_input(
            "Search transactions",
            placeholder="Search by name or note",
        )

    filtered_df = df.copy()

    if selected_month != "All months":
        filtered_df = filtered_df[
            filtered_df["expense_date"].dt.to_period("M").astype(str)
            == selected_month
        ]

    if selected_category != "All categories":
        filtered_df = filtered_df[
            filtered_df["category"] == selected_category
        ]

    if search_term.strip():
        search = search_term.strip().lower()

        filtered_df = filtered_df[
            filtered_df["name"].str.lower().str.contains(
                search, na=False
            )
            | filtered_df["note"].fillna("").str.lower().str.contains(
                search, na=False
            )
        ]

    st.caption(
        f"{len(filtered_df)} transaction(s) found. "
        f"Total: {money(filtered_df['amount'].sum())}"
    )

    if filtered_df.empty:
        st.info("No transactions match the selected filters.")
    else:
        display_df = filtered_df.copy()

        display_df["expense_date"] = (
            display_df["expense_date"].dt.strftime("%Y-%m-%d")
        )

        display_df["amount"] = display_df["amount"].apply(money)

        display_df = display_df[
            ["expense_date", "name", "category", "amount", "note"]
        ].rename(columns={
            "expense_date": "Date",
            "name": "Expense",
            "category": "Category",
            "amount": "Amount",
            "note": "Note",
        })

        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
        )

        csv_df = filtered_df.copy()
        csv_df["expense_date"] = (
            csv_df["expense_date"].dt.strftime("%Y-%m-%d")
        )

        csv_data = csv_df[
            ["expense_date", "name", "category", "amount", "note"]
        ].to_csv(index=False).encode("utf-8-sig")

        st.download_button(
            "Download filtered transactions (CSV)",
            data=csv_data,
            file_name="unispent_transactions.csv",
            mime="text/csv",
        )

    with st.expander("Edit a transaction"):
        transaction_options = {
            (
                f"#{int(row['id'])} | {row['name']} | "
                f"{money(row['amount'])} | "
                f"{row['expense_date'].strftime('%Y-%m-%d')}"
            ): int(row["id"])
            for _, row in df.iterrows()
        }

        selected_edit_label = st.selectbox(
            "Select a transaction to edit",
            list(transaction_options.keys()),
            key="edit_transaction_select",
        )

        selected_edit_id = transaction_options[selected_edit_label]

        edit_row = df[df["id"] == selected_edit_id].iloc[0]
        edit_date = min(edit_row["expense_date"].date(), date.today())

        with st.form("edit_expense_form"):
            edit_name = st.text_input(
                "Expense name",
                value=str(edit_row["name"]),
            )

            edit_amount = st.number_input(
                "Amount (Rs.)",
                min_value=0.01,
                value=max(float(edit_row["amount"]), 0.01),
                step=50.0,
            )

            edit_category = st.selectbox(
                "Category",
                CATEGORIES,
                index=(
                    CATEGORIES.index(edit_row["category"])
                    if edit_row["category"] in CATEGORIES
                    else CATEGORIES.index("Other")
                ),
            )

            edit_expense_date = st.date_input(
                "Date",
                value=edit_date,
                max_value=date.today(),
            )

            edit_note = st.text_area(
                "Note",
                value=str(edit_row["note"] or ""),
            )

            save_edit = st.form_submit_button(
                "Save changes",
                use_container_width=True,
            )

            if save_edit:
                if not edit_name.strip():
                    st.error("Expense name cannot be empty.")
                elif edit_amount <= 0:
                    st.error("Amount must be greater than zero.")
                else:
                    update_expense(
                        selected_edit_id,
                        edit_name,
                        edit_category,
                        edit_amount,
                        edit_expense_date,
                        edit_note,
                    )

                    st.success("Transaction updated.")
                    st.rerun()

    with st.expander("Delete a transaction"):
        delete_options = {
            (
                f"#{int(row['id'])} | {row['name']} | "
                f"{money(row['amount'])} | "
                f"{row['expense_date'].strftime('%Y-%m-%d')}"
            ): int(row["id"])
            for _, row in df.iterrows()
        }

        delete_label = st.selectbox(
            "Select a transaction to delete",
            list(delete_options.keys()),
            key="delete_transaction_select",
        )

        confirm_delete = st.checkbox(
            "I understand this will permanently delete the selected transaction."
        )

        if st.button("Delete selected transaction"):
            if confirm_delete:
                delete_expense(delete_options[delete_label])
                st.success("Transaction deleted.")
                st.rerun()
            else:
                st.warning("Confirm the deletion before continuing.")




# 15. SAVINGS GOALS

st.divider()

section_heading(
    "Savings Goals",
    "Set a target, track your progress, and build better saving habits.",
)

goal_col1, goal_col2 = st.columns([0.9, 1.1], gap="large")

# LEFT COLUMN: CREATE A NEW GOAL
with goal_col1:
    st.markdown("#### Create a savings goal")

    with st.form("add_savings_goal_form", clear_on_submit=True):
        goal_name = st.text_input(
            "Goal name",
            placeholder="e.g. New laptop",
        )

        goal_target = st.number_input(
            "Target amount (Rs.)",
            min_value=1.0,
            value=10000.0,
            step=500.0,
        )

        goal_saved = st.number_input(
            "Already saved (Rs.)",
            min_value=0.0,
            value=0.0,
            step=500.0,
        )

        has_deadline = st.checkbox("Set a target date")

        goal_deadline = None

        if has_deadline:
            goal_deadline = st.date_input(
                "Target date",
                value=date.today() + timedelta(days=30),
                min_value=date.today(),
            )

        create_goal = st.form_submit_button(
            "Create savings goal",
            use_container_width=True,
        )

    if create_goal:
        if not goal_name.strip():
            st.error("Please enter a name for your goal.")
        elif goal_target <= 0:
            st.error("Target amount must be greater than zero.")
        elif goal_saved < 0:
            st.error("Saved amount cannot be negative.")
        elif goal_saved > goal_target:
            st.error(
                "The amount already saved cannot exceed the target amount."
            )
        else:
            deadline_value = (
                goal_deadline.isoformat()
                if goal_deadline is not None
                else ""
            )

            try:
                created = add_savings_goal(
                    goal_name.strip(),
                    float(goal_target),
                    float(goal_saved),
                    deadline_value,
                )

                if created:
                    st.success("Savings goal created successfully!")
                    st.rerun()
                else:
                    st.warning(
                        "An active goal with the same name and target "
                        "already exists. Update the existing goal instead."
                    )
            except (ValueError, OverflowError) as error:
                st.error(str(error))


# RIGHT COLUMN: VIEW AND MANAGE GOALS
with goal_col2:
    st.markdown("#### Your savings goals")

    goals_df = get_savings_goals()

    if goals_df.empty:
        st.info(
            "You haven't created any savings goals yet. "
            "Create your first goal using the form."
        )
    else:
        goals_df = goals_df.copy()

        goals_df["deadline"] = (
            goals_df["deadline"]
            .fillna("")
            .astype(str)
            .str.strip()
        )

        for _, goal in goals_df.iterrows():
            goal_id = int(goal["id"])
            goal_name_value = str(goal["name"])
            target = float(goal["target_amount"])
            saved = float(goal["saved_amount"])
            deadline = goal["deadline"]

            progress = min(saved / target, 1.0) if target > 0 else 0.0
            remaining_goal = max(target - saved, 0.0)

            with st.container(border=True):
                st.markdown(f"**{goal_name_value}**")

                st.progress(progress)

                metric_col1, metric_col2 = st.columns(2)

                with metric_col1:
                    st.metric("Saved", f"Rs. {saved:,.2f}")

                with metric_col2:
                    st.metric("Target", f"Rs. {target:,.2f}")

                st.caption(
                    f"{progress * 100:.1f}% completed · "
                    f"Rs. {remaining_goal:,.2f} remaining"
                )

                if deadline and deadline.lower() != "nan":
                    st.caption(f"Target date: {deadline}")

                if progress >= 1:
                    st.success("Goal completed!")

                with st.expander("Manage goal"):
                    with st.form(f"update_goal_form_{goal_id}"):
                        updated_saved = st.number_input(
                            "Update amount saved (Rs.)",
                            min_value=0.0,
                            max_value=target,
                            value=min(max(saved, 0.0), target),
                            step=500.0,
                            key=f"saved_amount_{goal_id}",
                        )

                        update_goal = st.form_submit_button(
                            "Update progress",
                            use_container_width=True,
                        )

                    if update_goal:
                        try:
                            update_savings_progress(
                                goal_id,
                                updated_saved,
                            )
                            st.success("Savings progress updated.")
                            st.rerun()
                        except (ValueError, OverflowError) as error:
                            st.error(str(error))

                    st.divider()

                    confirm_delete = st.checkbox(
                        "I want to delete this goal",
                        key=f"confirm_delete_{goal_id}",
                    )

                    if st.button(
                        "Delete goal",
                        key=f"delete_goal_{goal_id}",
                        use_container_width=True,
                        disabled=not confirm_delete,
                    ):
                        with closing(get_connection()) as conn:
                            conn.execute(
                                "DELETE FROM savings_goals WHERE id = ?",
                                (goal_id,),
                            )
                            conn.commit()

                        st.success("Savings goal deleted.")
                        st.rerun()


# 16. FOOTER

st.markdown(
    """
    <div class="footer">
        <strong>UniSpend</strong><br>
        Spend mindfully. Save consistently. Grow financially.<br>
        Made for students, one rupee at a time.
    </div>
    """,
    unsafe_allow_html=True,
)
