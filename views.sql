-- Create the "mart" schema if it doesn't exist
IF NOT EXISTS (SELECT schema_name FROM information_schema.schemata WHERE schema_name = 'mart')
BEGIN
    EXEC('CREATE SCHEMA mart');
END;

DECLARE @manager_id INT;
DECLARE @manager_name NVARCHAR(50);
DECLARE @sql NVARCHAR(MAX);

-- Declare a cursor to iterate over managers
DECLARE manager_cursor CURSOR FOR
SELECT id, name
FROM dbo.[tbl.brokers]
WHERE managerid = id; -- Assuming the manager's ID is the same as their own ID

OPEN manager_cursor;
FETCH NEXT FROM manager_cursor INTO @manager_id, @manager_name;

WHILE @@FETCH_STATUS = 0
BEGIN
    -- Generate the SQL statement to create the view
    SET @sql = N'CREATE VIEW mart.' + REPLACE(@manager_name, ' ', '_') + '_view AS ' +
               N'SELECT b.id AS broker_id, b.name AS broker_name, ' +
               -- Calculate the total number of investors
               N'CAST(COUNT(DISTINCT t.investor_id) AS DECIMAL(10, 2)) AS total_investors, ' +
               -- Calculate the total buy value
               N'CAST(SUM(CASE WHEN t.is_sell = 0 THEN t.transaction_value ELSE 0 END) AS DECIMAL(18, 2)) AS total_buy_value, ' +
               -- Calculate the total sell value
               N'CAST(SUM(CASE WHEN t.is_sell = 1 THEN t.transaction_value ELSE 0 END) AS DECIMAL(18, 2)) AS total_sell_value, ' +
               -- Calculate the average transaction value
               N'CAST(AVG(t.transaction_value) AS DECIMAL(18, 2)) AS average_transaction_value, ' +
               -- Calculate the total value
               N'CAST(SUM(t.transaction_value) AS DECIMAL(18, 2)) AS total_value, ' +
               -- Calculate the number of total transactions
               N'CAST(COUNT(t.transaction_value) AS DECIMAL(10, 2)) AS Num_of_total_transactions, ' +
               -- Calculate the largest sell transaction
               N'CAST(MAX(CASE WHEN t.is_sell = 1 THEN t.transaction_value END) AS DECIMAL(18, 2)) AS Largest_sell_transaction, ' +
               -- Calculate the largest buy transaction
               N'CAST(MAX(CASE WHEN t.is_sell = 0 THEN t.transaction_value END) AS DECIMAL(18, 2)) AS Largest_buy_transaction, ' +
               -- Calculate the average number of daily transactions
               N'CAST(CAST(COUNT(t.transaction_value) AS DECIMAL) / COUNT(DISTINCT CONVERT(DATE, t.date)) AS DECIMAL(10, 2)) AS average_num_daily_transactions, ' +
               -- Calculate the average sum of daily transactions
               N'CAST(CAST(SUM(t.transaction_value) AS DECIMAL) / COUNT(DISTINCT CONVERT(DATE, t.date)) AS DECIMAL(10, 2)) AS average_sum_daily_transactions, ' +			   
			   -- Calculate the transaction success rate
               N'CAST((COUNT(t.transaction_value) * 100.0 / (COUNT(t.transaction_value) + (SELECT COUNT(*) FROM dbo.[tbl.failed_transactions] ft WHERE ft.broker_id = b.id))) AS DECIMAL(10, 2)) AS Transaction_Success_Rate, ' +
               -- Calculate the broker investor retention rate
               N'CAST((SELECT COUNT(DISTINCT investor_id) * 100.0 / COUNT(DISTINCT t.investor_id) FROM dbo.[tbl.transactions] WHERE broker_id = b.id) AS DECIMAL(10, 2)) AS Broker_Investor_Retention_Rate, ' +
               -- Calculate the worker tenure in months
               N'DATEDIFF(MONTH, (SELECT MIN(date) FROM dbo.[tbl.transactions] WHERE broker_id = b.id), GETDATE()) AS Worker_Tenure_Months ' +
               N'FROM dbo.[tbl.brokers] b ' +
               N'LEFT JOIN dbo.[tbl.transactions] t ON t.broker_id = b.id ' +
               N'WHERE b.managerid = ' + CAST(@manager_id AS NVARCHAR(50)) +
               N' GROUP BY b.id, b.name;';

    -- Execute the dynamic SQL statement
    EXEC sp_executesql @sql;

    FETCH NEXT FROM manager_cursor INTO @manager_id, @manager_name;
END

CLOSE manager_cursor;
DEALLOCATE manager_cursor;

--------------------------------------------------------------------------------------------------------------------
-- MONTHLY SALARY VIEW FOR ACCOUNTING MART AND CALC
-- This view calculates the monthly salary for brokers in the Accounting Mart and total salaries for the Calc department
CREATE VIEW mart.accounting_view AS
SELECT
    COALESCE(ACC.month, CALC.month) AS month,
    ACC.broker AS broker_id,
    ACC.salary_p_month AS salary
FROM
    (
        SELECT
            MONTH(tr.date) AS month,
            tr.broker_id AS broker,
            (COUNT(DISTINCT tr.date) * 100 + SUM(
                CASE
                    WHEN s.type = 1 THEN tr.transaction_value * 0.01
                    WHEN s.type = 2 THEN tr.transaction_value * 0.5
                END
            )) AS salary_p_month
        FROM
            dbo.[tbl.transactions] AS tr
        INNER JOIN
            dbo.[tbl.stocks] AS s ON tr.stock_id = s.id
        GROUP BY
            MONTH(tr.date),
            tr.broker_id
    ) AS ACC
FULL JOIN
    (
        SELECT
            MONTH(tr.date) AS month,
            (COUNT(DISTINCT tr.date) * 100 + SUM(
                CASE
                    WHEN s.type = 1 THEN tr.transaction_value * 0.01
                    WHEN s.type = 2 THEN tr.transaction_value * 0.5
                END
            )) AS salary_p_month
        FROM
            dbo.[tbl.transactions] AS tr
        INNER JOIN
            dbo.[tbl.stocks] AS s ON tr.stock_id = s.id
        GROUP BY
            MONTH(tr.date)
    ) AS CALC ON ACC.month = CALC.month;

----------------------------------------------------------------------------------------------------------
-- MONTHLY REVENUE AND PROFIT VIEW FOR CFO MART
-- This view calculates the monthly revenue and profit for the CFO Mart based on transaction data
CREATE VIEW mart.CFO_view AS
SELECT
    COF.month,
    COF.total_income,
    (COF.total_income - ACC.salary_p_month) AS profit_p_month
FROM
    (
        SELECT
            MONTH(transactions.date) AS month,
            SUM(
                CASE
                    WHEN stocks.type = 1 AND states.currency = 'Dollar' THEN 0.25 * transactions.transaction_value
                    WHEN stocks.type = 1 AND states.currency = 'Euro' AND transactions.is_sell = 1 THEN (0.25 * transactions.transaction_value) * 0.99
                    WHEN stocks.type = 1 AND states.currency = 'Euro' AND transactions.is_sell = 0 THEN (0.25 * transactions.transaction_value) * 1.01
                    WHEN stocks.type = 1 AND states.currency = 'Shekel' AND transactions.is_sell = 1 THEN (0.25 * transactions.transaction_value) * 0.98
                    WHEN stocks.type = 1 AND states.currency = 'Shekel' AND transactions.is_sell = 0 THEN (0.25 * transactions.transaction_value) * 1.02
                    WHEN stocks.type = 2 AND states.currency = 'Dollar' THEN 0.5 * transactions.transaction_value
                    WHEN stocks.type = 2 AND states.currency = 'Euro' AND transactions.is_sell = 1 THEN (0.5 * transactions.transaction_value) * 0.99
                    WHEN stocks.type = 2 AND states.currency = 'Euro' AND transactions.is_sell = 0 THEN (0.5 * transactions.transaction_value) * 1.01
                    WHEN stocks.type = 2 AND states.currency = 'Shekel' AND transactions.is_sell = 1 THEN (0.5 * transactions.transaction_value) * 0.98
                    WHEN stocks.type = 2 AND states.currency = 'Shekel' AND transactions.is_sell = 0 THEN (0.5 * transactions.transaction_value) * 1.02
                    ELSE NULL
                END
            ) AS total_income
        FROM
            dbo.[tbl.transactions] AS transactions,
            dbo.[tbl.investors] AS investors,
            dbo.[tbl.state] AS states,
            dbo.[tbl.stocks] AS stocks
        WHERE
            transactions.stock_id = stocks.id
            AND transactions.investor_id = investors.investor_id
            AND investors.state_code = states.state_code
        GROUP BY
            MONTH(transactions.date)
    ) AS COF
JOIN
    (
        SELECT
            MONTH(tr.date) AS month,
            (COUNT(DISTINCT tr.date) * 100 + SUM(
                CASE
                    WHEN s.type = 1 THEN tr.transaction_value * 0.01 -- Calculate salary based on transaction value for type 1 stocks
                    WHEN s.type = 2 THEN tr.transaction_value * 0.5 -- Calculate salary based on transaction value for type 2 stocks
                END
            )) AS salary_p_month
        FROM
            dbo.[tbl.transactions] AS tr
        INNER JOIN
            dbo.[tbl.stocks] AS s ON tr.stock_id = s.id
        GROUP BY
            MONTH(tr.date)
    ) AS ACC ON COF.month = ACC.month;
--------------------------------------------------------------------------------------------------------------------
IF OBJECT_ID('mart.CEO_view', 'V') IS NOT NULL
  DROP VIEW mart.CEO_view;
GO

-- Create a view to provide metrics for the CEO's view of the broker company
CREATE VIEW mart.CEO_view
AS
/*
    This view retrieves key metrics for the CEO's view of the broker company.

    Metrics included:
    - Manager Name: Name of the manager (broker or manager) associated with the brokers
    - Total Brokers: Count of distinct broker IDs
    - Total Sales: Sum of transaction values for all successful transactions
    - Average Sale: Average transaction value for all successful transactions
    - Highest Sale: Highest transaction value among all successful transactions
    - Lowest Sale: Lowest transaction value among all successful transactions
    - Avg Transaction Value per Broker: Average transaction value per broker
    - Total New Investors: Count of distinct investor IDs for successful transactions
    - Success Percentage: Percentage of successful transactions among all transactions
    - Transaction per Broker: Sum of transaction values divided by the count of distinct broker IDs
    - Sum of Transactions per Broker: Sum of transaction values divided by the count of distinct brokers

    Note: The success percentage is calculated as the count of successful transactions
    (transactions with positive transaction values) divided by the total count of transactions.

*/

SELECT
  CASE WHEN broker.managerid = broker.id THEN broker.name ELSE manager.name END AS manager_name,
  COUNT(DISTINCT broker.id) AS total_brokers,
  ROUND(SUM(trans.transaction_value), 2) AS total_sales,
  ROUND(AVG(trans.transaction_value), 2) AS average_sale,
  ROUND(MAX(trans.transaction_value), 2) AS highest_sale,
  ROUND(MIN(trans.transaction_value), 2) AS lowest_sale,
  ROUND(SUM(trans.transaction_value) / COUNT(DISTINCT broker.id), 2) AS avg_transaction_value_per_broker,
  COUNT(DISTINCT inv.investor_id) AS total_new_investors,
  ROUND(SUM(trans.transaction_value) / COUNT(DISTINCT trans.broker_id), 2) AS transaction_per_broker
FROM
  dbo.[tbl.brokers] AS broker
JOIN
  dbo.[tbl.brokers] AS manager ON manager.id = broker.managerid
JOIN
  dbo.[tbl.transactions] AS trans ON trans.broker_id = broker.id
JOIN
  dbo.[tbl.investors] AS inv ON inv.investor_id = trans.investor_id
GROUP BY
  CASE WHEN broker.managerid = broker.id THEN broker.name ELSE manager.name END;