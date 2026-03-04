-- AI BI Copilot — SQLite Schema
-- Run after creating the database with data/generate_data.py

CREATE TABLE IF NOT EXISTS transactions (
    transaction_id   TEXT      PRIMARY KEY,
    date             TEXT      NOT NULL,
    region           TEXT      NOT NULL,
    product_category TEXT      NOT NULL,
    customer_segment TEXT      NOT NULL,
    revenue          REAL      NOT NULL,
    cost             REAL      NOT NULL,
    units_sold       INTEGER   NOT NULL,
    sales_rep        TEXT      NOT NULL,
    country          TEXT      NOT NULL
);

CREATE TABLE IF NOT EXISTS process_events (
    event_id         TEXT      PRIMARY KEY,
    case_id          TEXT      NOT NULL,
    activity         TEXT      NOT NULL,
    timestamp        TIMESTAMP NOT NULL,
    resource         TEXT      NOT NULL,
    duration_minutes REAL      NOT NULL
);

CREATE TABLE IF NOT EXISTS customer_reviews (
    review_id        TEXT      PRIMARY KEY,
    date             TEXT      NOT NULL,
    product_category TEXT      NOT NULL,
    customer_segment TEXT      NOT NULL,
    region           TEXT      NOT NULL,
    review_text      TEXT      NOT NULL,
    rating           INTEGER   NOT NULL
);
