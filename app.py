import sqlite3
from contextlib import closing
from datetime import date, timedelta

import pandas as pd
import plotly.express as px
import streamlit as st


# 1. PAGE CONFIGURATION
st.set_page_config(
    page_title="UniSpend | Student Finance",
    layout="wide",
    initial_sidebar_state="expanded",
)

DB_PATH = "unispends.db"

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

# Professional forest-green and sage palette
CHART_COLORS = [
    "#24563D",
    "#4E8065",
    "#87A891",
    "#C4D5C5",
    "#B6A27A",
    "#7E9BA0",
    "#A7B3A8",
    "#6D806F",
]

# 2. DATABASE FUNCTIONS
def init_database():
    """Create the database tables if they do not exist."""
    with closing(sqlite3.connect(DB_PATH)) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                amount REAL NOT NULL CHECK(amount > 0),
                expense_date TEXT NOT NULL,
                note TEXT DEFAULT ''
            )
            """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS settings (
                setting_key TEXT PRIMARY KEY,
                setting_value TEXT NOT NULL
            )
            """
        )

        conn.execute(
            """
            INSERT OR IGNORE INTO settings (setting_key, setting_value)
            VALUES (?, ?)
            """,
            ("monthly_budget", "15000"),
        )
        conn.commit()


def get_monthly_budget():
    """Return the saved monthly budget."""
    with closing(sqlite3.connect(DB_PATH)) as conn:
        result = conn.execute(
            "SELECT setting_value FROM settings WHERE setting_key = ?",
            ("monthly_budget",),
        ).fetchone()

    return int(result[0]) if result else 15000


def save_monthly_budget(amount):
    """Save the monthly budget."""
    with closing(sqlite3.connect(DB_PATH)) as conn:
        conn.execute(
            """
            INSERT INTO settings (setting_key, setting_value)
            VALUES (?, ?)
            ON CONFLICT(setting_key)
            DO UPDATE SET setting_value = excluded.setting_value
            """,
            ("monthly_budget", str(amount)),
        )
        conn.commit()


def get_expenses():
    """Return all saved expenses, newest first."""
    with closing(sqlite3.connect(DB_PATH)) as conn:
        conn.row_factory = sqlite3.Row
        records = conn.execute(
            """
            SELECT id, name, category, amount, expense_date, note
            FROM expenses
            ORDER BY expense_date DESC, id DESC
            """
        ).fetchall()

    return [dict(record) for record in records]


def add_expense(name, category, amount, expense_date, note):
    """Save a new expense."""
    with closing(sqlite3.connect(DB_PATH)) as conn:
        conn.execute(
            """
            INSERT INTO expenses (name, category, amount, expense_date, note)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                name.strip(),
                category,
                float(amount),
                expense_date.isoformat(),
                note.strip(),
            ),
        )
        conn.commit()


def delete_expense(expense_id):
    """Delete an expense using its ID."""
    with closing(sqlite3.connect(DB_PATH)) as conn:
        conn.execute("DELETE FROM expenses WHERE id = ?", (int(expense_id),))
        conn.commit()


def load_demo_data():
    """Add example expenses to help preview the dashboard."""
    today = date.today()
    demo_expenses = [
        ("Campus lunch", "Food & Drinks", 450, today.isoformat(), "Lunch between lectures"),
        ("Bus fare", "Transport", 180, (today - timedelta(days=1)).isoformat(), "Travel to campus"),
        ("Mobile data", "Data & Internet", 399, (today - timedelta(days=2)).isoformat(), "Data package"),
        ("Printed notes", "Education", 250, (today - timedelta(days=3)).isoformat(), "Study materials"),
        ("Coffee", "Food & Drinks", 350, (today - timedelta(days=4)).isoformat(), "Coffee break"),
        ("Personal items", "Personal Care", 750, (today - timedelta(days=5)).isoformat(), "Essential items"),
    ]

    with closing(sqlite3.connect(DB_PATH)) as conn:
        for item in demo_expenses:
            # Avoid inserting the same sample transaction repeatedly.
            existing = conn.execute(
                """
                SELECT 1 FROM expenses
                WHERE name = ? AND category = ? AND expense_date = ? AND note = ?
                LIMIT 1
                """,
                (item[0], item[1], item[3], item[4]),
            ).fetchone()
            if not existing:
                conn.execute(
                    """
                    INSERT INTO expenses (name, category, amount, expense_date, note)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    item,
                )
        conn.commit()


# Make sure the required database tables exist before loading the app.
init_database()


# 3. PROFESSIONAL GREEN DESIGN
st.markdown(
    """
    <style>
        .stApp {
            background-color: #F3F6F3;
        }

        [data-testid="stHeader"] {
            background-color: rgba(243, 246, 243, 0.96);
        }

        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
            max-width: 1500px;
        }

        section[data-testid="stSidebar"] {
            background-color: #18392B;
        }

        section[data-testid="stSidebar"] h1,
        section[data-testid="stSidebar"] h2,
        section[data-testid="stSidebar"] h3,
        section[data-testid="stSidebar"] p,
        section[data-testid="stSidebar"] label,
        section[data-testid="stSidebar"] [data-testid="stCaptionContainer"] {
            color: #EDF3EE;
        }

        .hero {
            background: linear-gradient(120deg, #18392B 0%, #2F6950 100%);
            padding: 32px 34px;
            border-radius: 18px;
            color: #FFFFFF;
            margin-bottom: 26px;
            box-shadow: 0 8px 24px rgba(24, 57, 43, 0.10);
        }

        .hero-kicker {
            font-size: 11px;
            font-weight: 600;
            letter-spacing: 2px;
            color: #C7DCCB;
            margin-bottom: 12px;
        }

        .hero h1 {
            color: #FFFFFF;
            font-size: 34px;
            line-height: 1.25;
            margin: 0 0 10px 0;
        }

        .hero-description {
            color: #E3EEE6;
            font-size: 15px;
            line-height: 1.7;
            margin: 0;
        }

        .section-heading {
            color: #20382B;
            font-size: 21px;
            font-weight: 650;
            margin: 22px 0 8px 0;
        }

        [data-testid="stMetric"] {
            background: #FFFFFF;
            border: 1px solid #DDE6DE;
            border-radius: 14px;
            padding: 18px 20px;
            min-height: 118px;
            box-shadow: 0 4px 14px rgba(24, 57, 43, 0.04);
        }

        [data-testid="stMetricLabel"] {
            color: #607366;
            font-size: 13px;
        }

        [data-testid="stMetricValue"] {
            color: #20382B;
            font-weight: 700;
            font-size: 25px;
        }

        .stButton > button,
        [data-testid="stFormSubmitButton"] > button {
            background-color: #24563D;
            color: #FFFFFF;
            border: 1px solid #24563D;
            border-radius: 9px;
            font-weight: 600;
            min-height: 42px;
            transition: background-color 0.2s ease;
        }

        .stButton > button:hover,
        [data-testid="stFormSubmitButton"] > button:hover {
            background-color: #18392B;
            color: #FFFFFF;
            border-color: #18392B;
        }

        [data-testid="stProgress"] > div > div {
            background-color: #2F6950;
        }

        div[data-testid="stPlotlyChart"] {
            background-color: transparent;
        }

        div[data-testid="stDataFrame"] {
            border: 1px solid #DDE6DE;
            border-radius: 12px;
            overflow: hidden;
        }

        .footer-note {
            color: #718075;
            font-size: 12px;
            text-align: center;
            padding: 22px 0 6px 0;
            border-top: 1px solid #DDE6DE;
            margin-top: 28px;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# 4. SIDEBAR: BUDGET AND EXPENSE FORM
with st.sidebar:
    st.markdown("# UniSpend")
    st.caption("STUDENT FINANCE MANAGER")
    st.divider()

    st.subheader("Monthly budget")
    saved_budget = get_monthly_budget()

    monthly_budget = st.number_input(
        "Budget (LKR)",
        min_value=0,
        max_value=10_000_000,
        value=saved_budget,
        step=500,
        key="monthly_budget_input",
    )

    if monthly_budget != saved_budget:
        save_monthly_budget(monthly_budget)

    st.caption("Your budget is saved automatically.")
    st.divider()

    st.subheader("＋ Add an expense")

    with st.form("expense_form", clear_on_submit=True):
        expense_name = st.text_input(
            "Expense name",
            placeholder="e.g. Campus lunch",
        )

        expense_amount = st.number_input(
            "Amount (LKR)",
            min_value=1,
            max_value=10_000_000,
            value=100,
            step=50,
        )

        expense_category = st.selectbox("Category", CATEGORIES)

        expense_date = st.date_input(
            "Date",
            value=date.today(),
            max_value=date.today(),
        )

        expense_note = st.text_input(
            "Note (optional)",
            placeholder="e.g. Lunch after lectures",
        )

        submitted = st.form_submit_button(
            "＋ Add expense",
            use_container_width=True,
        )

        if submitted:
            if not expense_name.strip():
                st.error("Please enter an expense name.")
            else:
                add_expense(
                    expense_name,
                    expense_category,
                    expense_amount,
                    expense_date,
                    expense_note,
                )
                st.rerun()

    st.divider()

    with st.expander("Demo data"):
        st.caption(
            "Add example transactions to preview the dashboard. "
            "Existing example transactions will not be duplicated."
        )
        if st.button("Load sample transactions", use_container_width=True):
            load_demo_data()
            st.rerun()


# 5. PREPARE DASHBOARD DATA
all_expenses = get_expenses()
today = date.today()

if all_expenses:
    df = pd.DataFrame(all_expenses)
    df["date_parsed"] = pd.to_datetime(df["expense_date"])

    current_month_df = df[
        (df["date_parsed"].dt.year == today.year)
        & (df["date_parsed"].dt.month == today.month)
    ].copy()
else:
    df = pd.DataFrame(
        columns=["id", "name", "category", "amount", "expense_date", "note", "date_parsed"]
    )
    current_month_df = df.copy()

if not current_month_df.empty:
    total_spent = float(current_month_df["amount"].sum())
else:
    total_spent = 0.0

remaining = monthly_budget - total_spent
transaction_count = len(current_month_df)

if monthly_budget > 0:
    usage_percent = (total_spent / monthly_budget) * 100
    progress_value = min(total_spent / monthly_budget, 1.0)
else:
    usage_percent = 0.0
    progress_value = 0.0


def currency(amount):
    """Format an amount as Sri Lankan rupees."""
    return f"LKR {amount:,.0f}"

# 6. DASHBOARD HEADER
st.markdown(
    """
    <div class="hero">
        <div class="hero-kicker">STUDENT FINANCE · CONTROL CENTER</div>
        <h1>Make every rupee count.</h1>
        <p class="hero-description">
            Understand your spending, stay within your budget, and build smarter financial habits.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="section-heading">Financial overview</div>', unsafe_allow_html=True)
st.caption(today.strftime("%A, %d %B %Y"))


# 7. SUMMARY METRICS
budget_col, spent_col, balance_col, transactions_col = st.columns(4, gap="medium")

with budget_col:
    st.metric(
        label="Monthly budget",
        value=currency(monthly_budget),
        help="Your monthly spending limit",
    )

with spent_col:
    st.metric(
        label="Total spent",
        value=currency(total_spent),
        help="Expenses recorded during this calendar month",
    )

with balance_col:
    balance_display = currency(remaining) if remaining >= 0 else f"-{currency(abs(remaining))}"
    st.metric(
        label="Remaining balance",
        value=balance_display,
        help="Money remaining after recorded expenses",
    )

with transactions_col:
    st.metric(
        label="Transactions",
        value=transaction_count,
        help="Expenses recorded during this calendar month",
    )


# 8. BUDGET HEALTH
st.markdown('<div class="section-heading">Budget health</div>', unsafe_allow_html=True)

if monthly_budget > 0:
    st.progress(progress_value)

    if total_spent > monthly_budget:
        st.warning(
            f"You have exceeded your monthly budget by {currency(total_spent - monthly_budget)}."
        )
    elif usage_percent >= 80:
        st.warning(
            f"You have used {usage_percent:.1f}% of your budget. "
            "Consider limiting non-essential expenses."
        )
    else:
        st.success(f"You have used {usage_percent:.1f}% of your monthly budget.")
else:
    st.info("Your monthly budget is LKR 0. Set a budget in the sidebar to activate budget tracking.")



# 9. SPENDING INSIGHTS
st.markdown(
    '<div class="section-heading">Spending insights</div>',
    unsafe_allow_html=True,
)

chart_left, chart_right = st.columns(2, gap="large")


# CATEGORY-WISE SPENDING
with chart_left:
    with st.container(border=True):
        st.subheader("Spending by category")
        st.caption("How your money is distributed this month.")

        if not current_month_df.empty:
            category_totals = (
                current_month_df
                .groupby("category", as_index=False)["amount"]
                .sum()
                .sort_values("amount", ascending=False)
            )

            pie_chart = px.pie(
                category_totals,
                names="category",
                values="amount",
                hole=0.60,
                color_discrete_sequence=CHART_COLORS,
            )

            pie_chart.update_traces(
                textposition="inside",
                textinfo="percent",
                hovertemplate=(
                    "%{label}<br>"
                    "LKR %{value:,.2f}"
                    "<extra></extra>"
                ),
            )

            pie_chart.update_layout(
                showlegend=True,
                legend=dict(
                    orientation="h",
                    yanchor="top",
                    y=-0.10,
                    xanchor="center",
                    x=0.5,
                    font=dict(size=11),
                ),
                margin=dict(t=15, b=65, l=10, r=10),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(
                    family="Arial, sans-serif",
                    color="#33483C",
                ),
            )

            st.plotly_chart(
                pie_chart,
                use_container_width=True,
                config={"displayModeBar": False},
            )
        else:
            st.info(
                "Add expenses this month to view your category-wise spending."
            )


# SPENDING DURING THE LAST SEVEN DAYS
with chart_right:
    with st.container(border=True):
        st.subheader("Last 7 days")
        st.caption("Track your daily spending trend.")

        week_start = today - timedelta(days=6)
        date_range = pd.date_range(
            start=week_start,
            end=today,
            freq="D",
        )

        if not df.empty:
            week_df = df[
                df["date_parsed"].dt.date.between(week_start, today)
            ].copy()
        else:
            week_df = pd.DataFrame()

        if not week_df.empty:
            daily_spending = (
                week_df
                .groupby(week_df["date_parsed"].dt.date)["amount"]
                .sum()
            )
        else:
            daily_spending = pd.Series(dtype="float64")

        # Retain all seven dates, including days without expenses.
        daily_chart_df = pd.DataFrame({
            "date": date_range,
            "amount": [
                float(daily_spending.get(day.date(), 0))
                for day in date_range
            ],
        })

        bar_chart = px.bar(
            daily_chart_df,
            x="date",
            y="amount",
            labels={
                "date": "Date",
                "amount": "Amount (LKR)",
            },
            color_discrete_sequence=["#2F6950"],
        )

        bar_chart.update_traces(
            marker_line_width=0,
            hovertemplate=(
                "%{x|%d %b %Y}<br>"
                "LKR %{y:,.2f}"
                "<extra></extra>"
            ),
        )

        bar_chart.update_layout(
            margin=dict(t=20, b=15, l=10, r=10),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(
                family="Arial, sans-serif",
                color="#33483C",
            ),
            showlegend=False,
            xaxis=dict(
                title=None,
                showgrid=False,
                tickformat="%d %b",
                dtick=24 * 60 * 60 * 1000,
            ),
            yaxis=dict(
                title="Amount (LKR)",
                showgrid=True,
                gridcolor="#E5ECE6",
                zeroline=False,
                rangemode="tozero",
            ),
        )

        st.plotly_chart(
            bar_chart,
            use_container_width=True,
            config={"displayModeBar": False},
        )


# 10. RECENT TRANSACTIONS
st.markdown('<div class="section-heading">Recent transactions</div>', unsafe_allow_html=True)
st.caption("Your saved expenses, newest first.")

if not df.empty:
    display_df = df.sort_values(["date_parsed", "id"], ascending=[False, False]).copy()
    display_df["Date"] = display_df["date_parsed"].dt.strftime("%d %b %Y")
    display_df["Amount (LKR)"] = display_df["amount"].map(lambda amount: f"{amount:,.2f}")
    display_df = display_df[["Date", "name", "category", "Amount (LKR)", "note"]]
    display_df.columns = ["Date", "Expense", "Category", "Amount (LKR)", "Note"]

    st.dataframe(
        display_df,
        hide_index=True,
        use_container_width=True,
    )

    with st.expander("Manage transactions"):
        expenses_for_delete = get_expenses()
        expense_labels = {
            expense["id"]: (
                f'{expense["expense_date"]} · {expense["name"]} · '
                f'LKR {expense["amount"]:,.2f}'
            )
            for expense in expenses_for_delete
        }

        if expense_labels:
            selected_id = st.selectbox(
                "Select an expense to remove",
                options=list(expense_labels.keys()),
                format_func=lambda expense_id: expense_labels[expense_id],
            )
            confirm_delete = st.checkbox("I want to delete this transaction.")

            if st.button("Delete selected transaction", disabled=not confirm_delete):
                delete_expense(selected_id)
                st.rerun()
else:
    st.info("No expenses recorded yet. Add your first expense from the sidebar, or load sample transactions to preview the dashboard.")


# 11. FOOTER
st.markdown(
    """
    <div class="footer-note">
        UniSpend · Spend mindfully. Save consistently. Grow financially.
    </div>
    """,
    unsafe_allow_html=True,
)
