-- Showing peak hours
CREATE OR REPLACE  VIEW peak_hours AS 
SELECT hour_of_day, COUNT(*) AS transaction_count
FROM transactions
GROUP BY hour_of_day
ORDER BY transaction_count DESC;

-- Day of Week Trends
CREATE OR REPLACE VIEW day_of_week_trends AS 
SELECT day_of_week, COUNT(*) AS transaction_count
FROM transactions
GROUP BY day_of_week
ORDER BY transaction_count DESC;




-- Sender VS Reciever Relation
CREATE OR REPLACE VIEW sender_vs_reciever AS 
SELECT sender_bank, receiver_bank, COUNT(*) AS transaction_count
FROM transactions
GROUP BY sender_bank, receiver_bank
ORDER BY transaction_count DESC;

-- Fraud Detection by transaction type
CREATE OR REPLACE VIEW fraud_transaction_type AS 
SELECT transaction_type,
	   COUNT(*) AS total_transactions, 
	   SUM(fraud_flag::INT) AS fraud_transactions
FROM transactions
GROUP BY transaction_type
ORDER BY fraud_transactions DESC;


-- Fraud Detection by Merchant Category
CREATE OR REPLACE VIEW fraud_merchant_category AS 
SELECT merchant_category, COUNT(*) AS total_transactions, SUM(fraud_flag::INT) AS fraud_transactions
FROM transactions
GROUP BY merchant_category
ORDER BY fraud_transactions DESC;


-- Fraud Detection by Device type 
CREATE OR REPLACE VIEW fraud_device_type AS 
SELECT device_type, network_type, COUNT(*) AS total_transactions, SUM(fraud_flag::INT) AS fraud_transactions
FROM transactions
GROUP BY device_type, network_type
ORDER BY fraud_transactions DESC;


-- Age Group Analysis
CREATE OR REPLACE VIEW age_group AS 
SELECT sender_age_group, receiver_age_group, COUNT(*) AS transaction_count
FROM transactions
GROUP BY sender_age_group, receiver_age_group
ORDER BY transaction_count DESC;

-- Bank Prefrences
CREATE OR REPLACE VIEW bank_prefrences AS 
SELECT sender_bank, receiver_bank, COUNT(*) AS transaction_count
FROM transactions
GROUP BY sender_bank, receiver_bank
ORDER BY transaction_count DESC;

-- Transactions by sender state
CREATE OR REPLACE VIEW sender_state_transactions AS 
SELECT sender_state, COUNT(*) AS transaction_count
FROM transactions
GROUP BY sender_state
ORDER BY transaction_count DESC;

-- Network Type Analysis
CREATE OR REPLACE VIEW betwork_type_anaysis AS 
SELECT network_type, COUNT(*) AS transaction_count
FROM transactions
GROUP BY network_type
ORDER BY transaction_count DESC;

-- hour_of_day_trends
CREATE OR REPLACE VIEW hour_of_day_trends AS 
SELECT 
    hour_of_day,
    SUM(amount_inr::INT) AS total_amount,
    COUNT(*) AS total_transactions,
    ROUND(SUM(amount_inr::INT) * 1.0 / SUM(SUM(amount_inr::INT)) OVER (), 4) * 100 AS percentage_of_total_amount,
    SUM(COUNT(*)) OVER (ORDER BY hour_of_day) AS cumulative_transactions
FROM transactions
GROUP BY hour_of_day
ORDER BY hour_of_day;

-- sender_state_bank_amount
CREATE OR REPLACE VIEW sender_state_bank_amount AS 
SELECT 
    sender_state,
    sender_bank,
    SUM(amount_inr::INT) AS total_amount,
    RANK() OVER (PARTITION BY sender_state ORDER BY SUM(amount_inr::INT) DESC) AS rank_in_state
FROM transactions
GROUP BY sender_state, sender_bank
HAVING SUM(amount_inr::INT) > 0
ORDER BY sender_state, rank_in_state

-- Device & Network Usage Patterns (Fraud Rate Included)
CREATE OR REPLACE VIEW device_network_usage AS 
SELECT
    device_type,
    network_type,
    COUNT(*) AS total_transactions,
    SUM(fraud_flag::int) AS total_frauds,
    ROUND(AVG(fraud_flag::int) * 100, 2) AS fraud_rate_percentage,
    RANK() OVER (ORDER BY ROUND(AVG(fraud_flag::int) * 100, 2) DESC) AS fraud_risk_rank
FROM transactions
GROUP BY device_type, network_type
ORDER BY fraud_risk_rank;


-- Merchant Categories with Above-Average Transaction Amount
CREATE OR REPLACE VIEW merchant_transaction_amount AS 
SELECT 
    merchant_category,
    AVG(amount_inr::INT) AS avg_amount,
    COUNT(*) AS total_transactions
FROM transactions
WHERE amount_inr > (
        SELECT AVG(amount_inr::INT) FROM transactions
    )
GROUP BY merchant_category
ORDER BY avg_amount DESC;

-- Weekday vs Weekend Transaction Comparison
CREATE OR REPLACE VIEW weekday_vs_weekend AS 
SELECT 
    is_weekend,
    COUNT(*) AS total_transactions,
    SUM(amount_inr::INT) AS total_amount,
    ROUND(AVG(amount_inr::INT), 2) AS avg_transaction_amount,
    SUM(fraud_flag::int) AS fraud_transactions,
    ROUND(SUM(fraud_flag::int) * 100.0 / COUNT(*), 2) AS fraud_rate_percentage
FROM transactions
GROUP BY is_weekend
ORDER BY is_weekend;

-- Cohort: Sender Age Group Fraud Analysis
CREATE OR REPLACE VIEW sender_age_group AS 
SELECT
    sender_age_group,
    COUNT(*) AS total_transactions,
    SUM(fraud_flag::int) AS total_frauds,
    ROUND(AVG(fraud_flag::int) * 100, 2) AS fraud_rate_percentage,
    RANK() OVER (ORDER BY ROUND(AVG(fraud_flag::int) * 100, 2) DESC) AS fraud_risk_rank
FROM transactions
GROUP BY sender_age_group
ORDER BY fraud_risk_rank;


-- Top High-Risk Merchant Categories (Fraud Weighted by Amount)
CREATE OR REPLACE VIEW high_risk_merchant_categories AS 
SELECT
    merchant_category,
    SUM(amount_inr::int) AS total_amount,
    SUM(fraud_flag::int) AS total_fraud_transactions,
    ROUND(SUM(CASE WHEN fraud_flag THEN amount_inr ELSE 0 END) * 100.0 / SUM(amount_inr::int), 2) AS fraud_amount_percentage,
    RANK() OVER (ORDER BY 
        ROUND(SUM(CASE WHEN fraud_flag THEN amount_inr ELSE 0 END) * 100.0 / SUM(amount_inr::int), 2) DESC
    ) AS risk_rank
FROM transactions
GROUP BY merchant_category
ORDER BY risk_rank

