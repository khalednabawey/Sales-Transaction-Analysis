-- CREATE DATABASE transaction_db;

-- CREATE TABLE transactions (
--     transaction_id VARCHAR(20) PRIMARY KEY,
--     timestamp TIMESTAMP NOT NULL,
--     transaction_type VARCHAR(50),
--     merchant_category VARCHAR(50),
--     amount_inr DECIMAL(10, 2),
--     transaction_status VARCHAR(20),
--     sender_age_group VARCHAR(20),
--     receiver_age_group VARCHAR(20),
--     sender_state VARCHAR(50),
--     sender_bank VARCHAR(50),
--     receiver_bank VARCHAR(50),
--     device_type VARCHAR(50),
--     network_type VARCHAR(50),
--     fraud_flag BOOLEAN,
--     hour_of_day INTEGER,
--     day_of_week VARCHAR(20),
--     is_weekend BOOLEAN
-- );

-- COPY transactions(transaction_id, timestamp, transaction_type, merchant_category, amount_inr, transaction_status, sender_age_group, receiver_age_group, sender_state, sender_bank, receiver_bank, device_type, network_type, fraud_flag, hour_of_day, day_of_week, is_weekend)
-- FROM 'C:\Program Files\PostgreSQL\16\data\upi_transactions_2024.csv'
-- DELIMITER ','
-- CSV HEADER;

SELECT * FROM transactions LIMIT 10;

