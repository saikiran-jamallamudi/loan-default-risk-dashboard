# Loan Default Risk Analysis Dashboard

A portfolio project for exploring loan default patterns with Python, Pandas, SQL, MySQL, Matplotlib, and Streamlit.

> **Data notice:** `data/loan_applications_demo.csv` contains synthetic demonstration records. The dashboard is not a credit-scoring model and must not be used for actual lending decisions.

## Features

- Clean numeric fields, handle missing values, and validate binary default labels with Pandas.
- Analyze observed default rates across income bands, loan amount bands, and credit history.
- View summary metrics and Matplotlib charts in an interactive Streamlit dashboard.
- Filter by income, credit history, and loan amount.
- Export the currently filtered records as CSV.
- Use a bundled synthetic CSV immediately, or connect to a MySQL database.

## Run locally

Python 3.10+ is recommended.

### Windows PowerShell

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Choose **Bundled demo CSV** in the sidebar to start without MySQL.

## Connect MySQL

1. Create a database and table using `sql/schema.sql`.
2. Import records that follow the schema into `loan_applications`.
3. Set the environment variables shown in `.env.example`. Do not commit passwords or credentials.
4. Start the app and choose **MySQL database**.

The database table should contain `annual_income`, `loan_amount`, `credit_history`, and `default`. See the SQL files for the full schema and example aggregations.

## Run tests

```bash
pytest -q
```

## Analysis definitions

- **Default rate** = number of rows with `default = 1` divided by the number of valid applications in that segment.
- `credit_history = 1` maps to `Good`; `credit_history = 0` maps to `Limited/poor`.
- Missing or non-numeric credit-history values map to `Unknown`.
- Income and loan amount bands are fixed for easy comparison and can be adjusted in `data_processing.py`.

## Responsible interpretation

These charts describe patterns in the supplied data; they do not establish causation or predict an individual applicant's future. Check data quality, sample size, time period, and potential bias before interpreting any segment. Synthetic demo results are only for demonstrating the workflow.
