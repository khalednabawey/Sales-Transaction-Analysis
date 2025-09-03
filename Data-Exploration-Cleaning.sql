-- Check for Missing Values
SELECT COUNT(*) AS total_rows,
       COUNT(transaction_id) AS id_count,
       COUNT(timestamp) AS timestamp_count,
       COUNT(transaction_type) AS type_count,
       COUNT(amount_inr) AS amount_count,
       COUNT(fraud_flag) AS fraud_count
FROM transactions;

-- Check for duplicates
SELECT transaction_id, COUNT(transaction_id)
FROM transactions
GROUP BY transaction_id
HAVING COUNT(transaction_id) > 1;

-- Check for feature ranges
SELECT MIN(amount_inr) AS min_amount,
       MAX(amount_inr) AS max_amount,
       AVG(amount_inr) AS avg_amount
FROM transactions;

SELECT MIN(timestamp) AS first_transaction,
       MAX(timestamp) AS last_transaction
FROM transactions;

-- Remove Duplicates
DELETE FROM transactions
WHERE transaction_id IN (
    SELECT transaction_id
    FROM transactions
    GROUP BY transaction_id
    HAVING COUNT(transaction_id) > 1
);

-- Removing Null Values
UPDATE transactions
SET amount_inr = 0
WHERE amount_inr IS NULL;

-- Removing Critical Null Values
DELETE FROM transactions
WHERE transaction_id IS NULL OR timestamp IS NULL

-- Outlier Detection
SELECT *
FROM transactions
WHERE amount_inr > (SELECT AVG(amount_inr) + 3 * STDDEV(amount_inr) FROM transactions)
   OR amount_inr < (SELECT AVG(amount_inr) - 3 * STDDEV(amount_inr) FROM transactions);


