from pathlib import Path
import os

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL

from data_processing import add_risk_bands, clean_loan_data, default_rate

ROOT = Path(__file__).parent
DATA_PATH = ROOT / "data" / "loan_applications_demo.csv"

st.set_page_config(page_title="Loan Default Risk Dashboard", page_icon="📊", layout="wide")
st.title("Loan Default Risk Analysis Dashboard")
st.caption(
    "Explore borrower and loan characteristics associated with observed defaults. "
    "The bundled dataset is synthetic and is not suitable for real lending decisions."
)


@st.cache_data
def load_csv(path: str) -> pd.DataFrame:
    return pd.read_csv(path)


def load_mysql() -> pd.DataFrame:
    config = st.secrets.get("mysql", {})
    host = config.get("host", os.getenv("MYSQL_HOST", ""))
    user = config.get("user", os.getenv("MYSQL_USER", ""))
    password = config.get("password", os.getenv("MYSQL_PASSWORD", ""))
    database = config.get("database", os.getenv("MYSQL_DATABASE", ""))
    port = int(config.get("port", os.getenv("MYSQL_PORT", "3306")))

    if not all([host, user, password, database]):
        raise ValueError(
            "Set MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, and MYSQL_DATABASE, "
            "or configure .streamlit/secrets.toml."
        )

    url = URL.create(
        "mysql+mysqlconnector",
        username=user,
        password=password,
        host=host,
        port=port,
        database=database,
    )
    engine = create_engine(url, pool_pre_ping=True)
    try:
        with engine.connect() as connection:
            return pd.read_sql(text("SELECT * FROM loan_applications"), connection)
    finally:
        engine.dispose()


with st.sidebar:
    st.header("Data source")
    source = st.radio("Load data from", ["Bundled demo CSV", "MySQL database"])
    st.caption("MySQL mode expects a table named loan_applications. See sql/schema.sql.")
    st.divider()
    st.header("Filters")

try:
    raw = load_csv(str(DATA_PATH)) if source == "Bundled demo CSV" else load_mysql()
    df = add_risk_bands(clean_loan_data(raw))
except Exception as exc:
    st.error(f"Could not load data: {exc}")
    st.stop()

if df.empty:
    st.warning("No valid records are available after cleaning.")
    st.stop()

with st.sidebar:
    income_min = int(df["annual_income"].min())
    income_max = int(df["annual_income"].max())
    if income_min < income_max:
        income_range = st.slider(
            "Annual income",
            min_value=income_min,
            max_value=income_max,
            value=(income_min, income_max),
            step=max(1, (income_max - income_min) // 100),
        )
        df = df[df["annual_income"].between(*income_range)]

    credit_options = ["All"] + sorted(df["credit_history"].dropna().astype(str).unique().tolist())
    selected_credit = st.selectbox("Credit history", credit_options)
    if selected_credit != "All":
        df = df[df["credit_history"].astype(str) == selected_credit]

    loan_options = ["All"] + sorted(df["loan_amount_band"].dropna().unique().tolist())
    selected_loan_band = st.selectbox("Loan amount band", loan_options)
    if selected_loan_band != "All":
        df = df[df["loan_amount_band"] == selected_loan_band]

if df.empty:
    st.warning("No records match the selected filters.")
    st.stop()

applications = len(df)
defaults = int(df["default"].sum())
rate = defaults / applications * 100 if applications else 0
average_loan = df["loan_amount"].mean()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Applications", f"{applications:,}")
col2.metric("Observed defaults", f"{defaults:,}")
col3.metric("Default rate", f"{rate:.1f}%")
col4.metric("Average loan amount", f"{average_loan:,.0f}")

st.divider()
left, right = st.columns(2)

with left:
    st.subheader("Default rate by annual income band")
    summary = default_rate(df, "income_band")
    fig, ax = plt.subplots()
    valid = summary.dropna(subset=["default_rate_pct"])
    if not valid.empty:
        ax.bar(valid["segment"].astype(str), valid["default_rate_pct"])
    ax.set_ylabel("Default rate (%)")
    ax.set_xlabel("Annual income band")
    ax.tick_params(axis="x", rotation=25)
    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

with right:
    st.subheader("Default rate by loan amount band")
    summary = default_rate(df, "loan_amount_band")
    fig, ax = plt.subplots()
    valid = summary.dropna(subset=["default_rate_pct"])
    if not valid.empty:
        ax.bar(valid["segment"].astype(str), valid["default_rate_pct"])
    ax.set_ylabel("Default rate (%)")
    ax.set_xlabel("Loan amount band")
    ax.tick_params(axis="x", rotation=25)
    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

left, right = st.columns(2)
with left:
    st.subheader("Default rate by credit history")
    summary = default_rate(df, "credit_history")
    fig, ax = plt.subplots()
    valid = summary.dropna(subset=["default_rate_pct"])
    if not valid.empty:
        ax.bar(valid["segment"].astype(str), valid["default_rate_pct"])
    ax.set_ylabel("Default rate (%)")
    ax.set_xlabel("Credit history")
    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

with right:
    st.subheader("Income vs. loan amount")
    fig, ax = plt.subplots()
    point_colors = df["default"].map({0: "tab:blue", 1: "tab:red"})
    ax.scatter(df["annual_income"], df["loan_amount"], c=point_colors, alpha=0.6)
    ax.set_xlabel("Annual income")
    ax.set_ylabel("Loan amount")
    ax.legend(handles=[
        plt.Line2D([0], [0], marker="o", color="w", markerfacecolor="tab:blue",
                   label="No default", markersize=8),
        plt.Line2D([0], [0], marker="o", color="w", markerfacecolor="tab:red",
                   label="Default", markersize=8),
    ])
    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

st.subheader("Segment summary")
summary = default_rate(df, "loan_amount_band").rename(columns={
    "segment": "Loan amount band",
    "applications": "Applications",
    "defaults": "Defaults",
    "default_rate_pct": "Default rate (%)",
})
st.dataframe(summary, use_container_width=True, hide_index=True)

st.subheader("Data quality")
quality = pd.DataFrame({
    "Metric": [
        "Rows after cleaning",
        "Missing annual income",
        "Missing loan amount",
        "Missing credit history",
    ],
    "Value": [
        len(df),
        int(df["annual_income"].isna().sum()),
        int(df["loan_amount"].isna().sum()),
        int(df["credit_history"].isna().sum()),
    ],
})
st.dataframe(quality, use_container_width=True, hide_index=True)

st.download_button(
    "Download filtered records as CSV",
    data=df.to_csv(index=False).encode("utf-8"),
    file_name="filtered_loan_applications.csv",
    mime="text/csv",
)
st.caption(
    "Interpretation note: observed associations are descriptive, not causal. "
    "Do not use this demonstration to make real credit decisions."
)
