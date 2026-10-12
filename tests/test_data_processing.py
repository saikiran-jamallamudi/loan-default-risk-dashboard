import pandas as pd
import pytest

from data_processing import add_risk_bands, clean_loan_data, default_rate


def sample_data():
    return pd.DataFrame({
        "application_id": [1, 2, 3, 4],
        "annual_income": [25000, 50000, 80000, None],
        "loan_amount": [8000, 20000, 40000, 5000],
        "credit_history": [0, 1, 1, 0],
        "default": [1, 0, 0, 1],
    })


def test_clean_removes_rows_with_missing_required_numeric_values():
    df = clean_loan_data(sample_data())
    assert len(df) == 3
    assert set(df["default"]) == {0, 1}


def test_risk_bands_are_added():
    df = add_risk_bands(clean_loan_data(sample_data()))
    assert "income_band" in df.columns
    assert "loan_amount_band" in df.columns
    assert df.iloc[0]["loan_amount_band"] == "Under 10k"


def test_default_rate_aggregates_applications():
    df = add_risk_bands(clean_loan_data(sample_data()))
    summary = default_rate(df, "income_band")
    assert "default_rate_pct" in summary.columns
    assert summary["applications"].sum() == 3


def test_required_columns_are_checked():
    with pytest.raises(ValueError, match="Missing required columns"):
        clean_loan_data(pd.DataFrame({"annual_income": [1000]}))
