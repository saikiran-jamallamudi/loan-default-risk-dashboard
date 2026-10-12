USE loan_risk;

-- Overall portfolio summary
SELECT
    COUNT(*) AS applications,
    SUM(`default`) AS defaults,
    ROUND(100.0 * SUM(`default`) / NULLIF(COUNT(*), 0), 2) AS default_rate_pct,
    ROUND(AVG(annual_income), 2) AS avg_annual_income,
    ROUND(AVG(loan_amount), 2) AS avg_loan_amount
FROM loan_applications;

-- Default rate by annual income band
SELECT
    CASE
        WHEN annual_income < 30000 THEN 'Under 30k'
        WHEN annual_income < 60000 THEN '30k-60k'
        WHEN annual_income < 100000 THEN '60k-100k'
        ELSE '100k+'
    END AS income_band,
    COUNT(*) AS applications,
    SUM(`default`) AS defaults,
    ROUND(100.0 * SUM(`default`) / NULLIF(COUNT(*), 0), 2) AS default_rate_pct
FROM loan_applications
GROUP BY income_band
ORDER BY MIN(annual_income);

-- Default rate by loan amount band
SELECT
    CASE
        WHEN loan_amount < 10000 THEN 'Under 10k'
        WHEN loan_amount < 25000 THEN '10k-25k'
        WHEN loan_amount < 50000 THEN '25k-50k'
        ELSE '50k+'
    END AS loan_amount_band,
    COUNT(*) AS applications,
    SUM(`default`) AS defaults,
    ROUND(100.0 * SUM(`default`) / NULLIF(COUNT(*), 0), 2) AS default_rate_pct
FROM loan_applications
GROUP BY loan_amount_band
ORDER BY MIN(loan_amount);

-- Default rate by credit history
SELECT
    CASE
        WHEN credit_history = 1 THEN 'Good'
        WHEN credit_history = 0 THEN 'Limited/poor'
        ELSE 'Unknown'
    END AS credit_history_group,
    COUNT(*) AS applications,
    SUM(`default`) AS defaults,
    ROUND(100.0 * SUM(`default`) / NULLIF(COUNT(*), 0), 2) AS default_rate_pct
FROM loan_applications
GROUP BY credit_history_group;
