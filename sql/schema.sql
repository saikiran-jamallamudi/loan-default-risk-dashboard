CREATE DATABASE IF NOT EXISTS loan_risk;
USE loan_risk;

CREATE TABLE IF NOT EXISTS loan_applications (
    application_id BIGINT PRIMARY KEY,
    annual_income DECIMAL(14,2) NOT NULL,
    loan_amount DECIMAL(14,2) NOT NULL,
    credit_history TINYINT NULL COMMENT '1 = good, 0 = limited/poor',
    `default` TINYINT NOT NULL COMMENT '1 = default, 0 = no default',
    application_date DATE NULL,
    employment_type VARCHAR(60) NULL,
    CHECK (annual_income >= 0),
    CHECK (loan_amount >= 0),
    CHECK (credit_history IN (0,1) OR credit_history IS NULL),
    CHECK (`default` IN (0,1))
);
