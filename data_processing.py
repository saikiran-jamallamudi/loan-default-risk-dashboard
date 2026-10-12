import pandas as pd

REQUIRED_COLUMNS = {"annual_income", "loan_amount", "credit_history", "default"}


def clean_loan_data(data: pd.DataFrame) -> pd.DataFrame:
    """Normalize fields and remove rows that cannot support the core analysis."""
    df = data.copy()
    df.columns = [str(column).strip().lower() for column in df.columns]

    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(sorted(missing))}")

    for column in ("annual_income", "loan_amount", "credit_history", "default"):
        df[column] = pd.to_numeric(df[column], errors="coerce")

    df = df.dropna(subset=["annual_income", "loan_amount", "default"])
    df = df[(df["annual_income"] >= 0) & (df["loan_amount"] >= 0)]
    df = df[df["default"].isin([0, 1])]
    df["credit_history"] = (
        df["credit_history"].map({1: "Good", 0: "Limited/poor"}).fillna("Unknown")
    )

    if "application_id" not in df.columns:
        df.insert(0, "application_id", range(1, len(df) + 1))

    return df.reset_index(drop=True)


def add_risk_bands(df: pd.DataFrame) -> pd.DataFrame:
    """Add fixed descriptive bands for segment comparisons."""
    result = df.copy()
    result["income_band"] = pd.cut(
        result["annual_income"],
        bins=[-0.01, 30000, 60000, 100000, float("inf")],
        labels=["Under 30k", "30k-60k", "60k-100k", "100k+"],
    )
    result["loan_amount_band"] = pd.cut(
        result["loan_amount"],
        bins=[-0.01, 10000, 25000, 50000, float("inf")],
        labels=["Under 10k", "10k-25k", "25k-50k", "50k+"],
    )
    return result


def default_rate(df: pd.DataFrame, group_col: str) -> pd.DataFrame:
    """Return application count, default count, and observed default rate per segment."""
    if group_col not in df.columns:
        raise ValueError(f"Unknown grouping column: {group_col}")

    summary = (
        df.groupby(group_col, observed=False, dropna=False)
        .agg(applications=("default", "size"), defaults=("default", "sum"))
        .reset_index()
        .rename(columns={group_col: "segment"})
    )
    summary["default_rate_pct"] = (
        summary["defaults"] / summary["applications"] * 100
    ).round(2)
    return summary
