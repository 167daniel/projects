-- Create the brokers table and change column names
CREATE TABLE dbo.[tbl.brokers] (
  id INT PRIMARY KEY,
  name VARCHAR(255),
  managerid INT,
  bdate DATE
);

-- Populate the brokers table from the grs.brokers table
INSERT INTO dbo.[tbl.brokers] (id, name, managerid, bdate)
SELECT num, name, managerid, bdate
FROM dbo.[grs.brokers];

-- Create the meta.stocks_code_to_name table
CREATE TABLE dbo.[meta.stocks_code_to_name] (
  code INT PRIMARY KEY,
  name VARCHAR(255)
);

-- Populate the meta.stocks_code_to_name table from the grs.stocks table
INSERT INTO dbo.[meta.stocks_code_to_name] (code, name)
SELECT num, name
FROM dbo.[grs.stocks];

-- Create the meta.stock_type_code table
CREATE TABLE dbo.[meta.stock_type_code] (
  code INT PRIMARY KEY,
  type VARCHAR(255)
);

-- Insert distinct stock types into the meta.stock_type_code table
INSERT INTO dbo.[meta.stock_type_code] (code, type)
SELECT ROW_NUMBER() OVER (ORDER BY NEWID()), type
FROM (
  SELECT DISTINCT type
  FROM dbo.[grs.stocks]
) AS subquery;

-- Create the tbl.stocks table
CREATE TABLE dbo.[tbl.stocks] (
  id INT PRIMARY KEY,
  type INT,
  FOREIGN KEY (id) REFERENCES dbo.[meta.stocks_code_to_name] (code)
);

-- Populate the tbl.stocks table with stock IDs and corresponding types
INSERT INTO dbo.[tbl.stocks] (id, type)
SELECT dbo.[grs.stocks].num, dbo.[meta.stock_type_code].code
FROM dbo.[grs.stocks]
JOIN dbo.[meta.stocks_code_to_name]
  ON dbo.[meta.stocks_code_to_name].name = dbo.[grs.stocks].name
JOIN dbo.[meta.stock_type_code]
  ON dbo.[meta.stock_type_code].type = dbo.[grs.stocks].type;

-- Create the tbl.stock_spots table
CREATE TABLE dbo.[tbl.stock_spots] (
  id INT,
  date DATE,
  value FLOAT,
  PRIMARY KEY (id, date),
  FOREIGN KEY (id) REFERENCES dbo.[tbl.stocks] (id)
);

-- Populate the tbl.stock_spots table with stock spot data
INSERT INTO dbo.[tbl.stock_spots] (id, date, value)
SELECT num, time, [value]
FROM dbo.[grs.stock_spots];

-- Create the tbl.exchangerates table
CREATE TABLE dbo.[tbl.exchangerates] (
  date DATE PRIMARY KEY,
  shekel_to_dollar FLOAT,
  euro_to_dollar FLOAT
);

-- Populate the tbl.exchangerates table with exchange rate data
INSERT INTO dbo.[tbl.exchangerates] (date, shekel_to_dollar, euro_to_dollar)
SELECT [date], s_to_d, e_to_d
FROM dbo.[grs.exchangerates];

-- Create the tbl.investors table
DROP TABLE IF EXISTS dbo.[tbl.investors];
CREATE TABLE dbo.[tbl.investors] (
  investor_id INT PRIMARY KEY,
  name VARCHAR(255),
  email VARCHAR(255),
  state VARCHAR(255),
  phone VARCHAR(255),
  salary DECIMAL(10, 2),
  is_new BIT
);

-- Insert values from grs.past_investors as existing investors
INSERT INTO dbo.[tbl.investors] (investor_id, name, email, state, phone, salary, is_new)
SELECT num, name, email, state, phone, annual_salary, 0
FROM dbo.[grs.past_investors];
/*
This query inserts existing investors from the 'grs.past_investors' table into the 'dbo.[tbl.investors]' table.
It selects the columns 'num', 'name', 'email', 'state', 'phone', 'annual_salary' from 'grs.past_investors' and inserts them into the corresponding columns in 'dbo.[tbl.investors]'.
The 'is_new' column is set to 0 for existing investors.
*/

-- Insert values from grs.newinvestors as new investors
INSERT INTO dbo.[tbl.investors] (investor_id, name, email, state, phone, salary, is_new)
SELECT ROW_NUMBER() OVER (ORDER BY Investor_name) + (SELECT MAX(num) FROM dbo.[grs.past_investors]), Investor_name, Email,
    CASE
        WHEN State = 'israeli' THEN 'Israel'
        ELSE State
    END,
    CASE
        WHEN State = 'israeli' THEN SUBSTRING(Phone, 2, LEN(Phone) - 1)
        ELSE Phone
    END,
    income, 1
FROM dbo.[grs.newinvestors];
/*
This query inserts new investors from the 'grs.newinvestors' table into the 'dbo.[tbl.investors]' table.
It selects the columns 'Investor_name', 'Email', 'State', 'Phone', 'income' from 'grs.newinvestors' and inserts them into the corresponding columns in 'dbo.[tbl.investors]'.
The 'is_new' column is set to 1 for new investors.
The expression 'ROW_NUMBER() OVER (ORDER BY Investor_name) + (SELECT MAX(num) FROM dbo.[grs.past_investors])' assigns a new 'investor_id' to each new investor.
It adds the maximum value of 'num' from 'dbo.[grs.past_investors]' to ensure uniqueness in the 'investor_id' values.
The 'CASE' statements modify the values of 'State' and 'Phone' columns based on specific conditions.
*/

-- Add the 'area_code' and 'phone_n' columns to the 'dbo.[tbl.investors]' table
ALTER TABLE dbo.[tbl.investors]
ADD area_code VARCHAR(10),
    phone_n VARCHAR(255);
/*
This query adds the 'area_code' and 'phone_n' columns to the 'dbo.[tbl.investors]' table.
The 'area_code' column is defined as VARCHAR(10) and 'phone_n' column is defined as VARCHAR(255).
*/

-- Update the 'area_code' and 'phone_n' columns based on the 'phone' column
UPDATE dbo.[tbl.investors]
SET area_code = CASE
                    WHEN CHARINDEX('-', phone) > 0 THEN SUBSTRING(phone, 1, CHARINDEX('-', phone))
                    ELSE ''
                END,
    phone_n = CASE
                 WHEN CHARINDEX('-', phone) > 0 THEN SUBSTRING(phone, CHARINDEX('-', phone) + 1, 1000)
                 ELSE phone
               END;
/*
This query updates the 'area_code' and 'phone_n' columns in the 'dbo.[tbl.investors]' table based on the values in the 'phone' column.
It uses the 'CASE' statement to check if the 'phone' column contains a hyphen ('-').
If it does, it splits the 'phone' value into 'area_code' and 'phone_n' parts by extracting substrings.
If the 'phone' column doesn't contain a hyphen, the 'area_code' is set to an empty string ('') and 'phone_n' is set to the original 'phone' value.
*/

-- Remove any additional hyphens in the 'phone_n' column
UPDATE dbo.[tbl.investors]
SET phone_n = REPLACE(phone_n, '-', '');
/*
This query removes any additional hyphens in the 'phone_n' column of the 'dbo.[tbl.investors]' table.
It uses the 'REPLACE' function to replace hyphens with an empty string ('') in the 'phone_n' column.
*/

-- Remove the old 'phone' column from the 'dbo.[tbl.investors]' table
ALTER TABLE dbo.[tbl.investors]
DROP COLUMN phone;
/*
This query removes the old 'phone' column from the 'dbo.[tbl.investors]' table.
The 'DROP COLUMN' statement is used to remove the 'phone' column from the table.
*/

-- Create the 'state' table
CREATE TABLE dbo.[tbl.state] (
  state_code INT PRIMARY KEY,
  name VARCHAR(255) UNIQUE,
  area_code VARCHAR(10),
  currency VARCHAR(50)
);
/*
This query creates the 'dbo.[tbl.state]' table with columns 'state_code', 'name', 'area_code', and 'currency'.
The 'state_code' column is defined as an INT primary key.
The 'name' column is defined as VARCHAR(255) with the UNIQUE constraint.
The 'area_code' column is defined as VARCHAR(10).
The 'currency' column is defined as VARCHAR(50).
*/

-- Insert data into the 'state' table
INSERT INTO dbo.[tbl.state] (state_code, name, area_code, currency)
SELECT ROW_NUMBER() OVER (ORDER BY dbo.[tbl.investors].state) AS state_code,
       dbo.[tbl.investors].state AS name,
       MAX(dbo.[tbl.investors].area_code) AS area_code,
       MAX(dbo.[grs.past_investors].cur) AS currency
FROM dbo.[tbl.investors]
LEFT JOIN dbo.[grs.past_investors] ON dbo.[tbl.investors].state = dbo.[grs.past_investors].state
GROUP BY dbo.[tbl.investors].state;
/*
This query inserts data into the 'dbo.[tbl.state]' table based on data from the 'dbo.[tbl.investors]' and 'dbo.[grs.past_investors]' tables.
It selects the 'state_code', 'name', 'area_code', and 'currency' values for each state from the 'dbo.[tbl.investors]' and 'dbo.[grs.past_investors]' tables.
The 'ROW_NUMBER() OVER (ORDER BY dbo.[tbl.investors].state)' expression generates a unique number for each row based on the order of the 'state' column in 'dbo.[tbl.investors]'.
The 'LEFT JOIN' is used to match the 'state' column in 'dbo.[tbl.investors]' with the 'state' column in 'dbo.[grs.past_investors]'.
The 'GROUP BY' clause groups the data by the 'state' column.
*/

ALTER TABLE dbo.[tbl.investors]
ADD state_code INT;

UPDATE dbo.[tbl.investors]
SET state_code = dbo.[tbl.state].state_code
FROM dbo.[tbl.state]
WHERE dbo.[tbl.investors].state = dbo.[tbl.state].name;
/*
This block of code adds the 'state_code' column to the 'dbo.[tbl.investors]' table and populates it with values.
First, the 'state_code' column is added to the 'dbo.[tbl.investors]' table using the 'ALTER TABLE' statement.
Then, the 'state_code' column in 'dbo.[tbl.investors]' is updated with values from the 'state_code' column in 'dbo.[tbl.state]'.
The update is performed by matching the 'state' column in 'dbo.[tbl.investors]' with the 'name' column in 'dbo.[tbl.state]'.
*/

-- Add foreign key constraint between 'state_code' column in 'dbo.[tbl.investors]' and 'state_code' column in 'dbo.[tbl.state]'
ALTER TABLE dbo.[tbl.investors]
ADD CONSTRAINT FK_investor_state FOREIGN KEY (state_code) REFERENCES dbo.[tbl.state] (state_code);
/*
This query adds a foreign key constraint between the 'state_code' column in 'dbo.[tbl.investors]' and the 'state_code' column in 'dbo.[tbl.state]'.
The 'CONSTRAINT' statement defines a foreign key constraint named 'FK_investor_state'.
It specifies that the 'state_code' column in 'dbo.[tbl.investors]' references the 'state_code' column in 'dbo.[tbl.state]'.
*/

-- Create the 'dbo.[meta.valid_emails]' table
-- This table is used to store valid email prefixes.
CREATE TABLE dbo.[meta.valid_emails] (
  email_prefix VARCHAR(255)
);

-- Check and handle invalid email formats in 'dbo.[tbl.investors]'
IF EXISTS (
    SELECT *
    FROM dbo.[tbl.investors]
    WHERE email NOT LIKE '%@%.com'
)
BEGIN
    -- Invalid email format found
    -- Raise error and set email to NULL
    RAISERROR('non-valid-email', 16, 1);
    UPDATE dbo.[tbl.investors]
    SET email = NULL
    WHERE email NOT LIKE '%@%.com';
END
ELSE
BEGIN
    -- Valid email format
    -- Add unique prefixes to the prefix table
    INSERT INTO dbo.[meta.valid_emails] (email_prefix)
    SELECT DISTINCT SUBSTRING(email, CHARINDEX('@', email) + 1, LEN(email))
    FROM dbo.[tbl.investors]
    WHERE email LIKE '%@%.com'
    AND RIGHT(email, 4) = '.com'
    AND SUBSTRING(email, CHARINDEX('@', email) + 1, LEN(email)) NOT IN (
        SELECT email_prefix
        FROM dbo.[meta.valid_emails]
    );
END;

-- Create [tbl.transactions] table
-- This table is used to store transaction information.
CREATE TABLE dbo.[tbl.transactions] (
  broker_id INT,
  date DATE,
  stock_id INT,
  value VARCHAR(255),
  investor_id INT,
  is_sell BIT,
  transaction_value FLOAT,
  FOREIGN KEY (broker_id) REFERENCES dbo.[tbl.brokers] (id),
  FOREIGN KEY (stock_id, date) REFERENCES dbo.[tbl.stock_spots] (id, date),
  FOREIGN KEY (investor_id) REFERENCES dbo.[tbl.investors] (investor_id)
);

-- Insert values into [tbl.transactions]
-- This query inserts values into the [tbl.transactions] table based on specific conditions.
INSERT INTO dbo.[tbl.transactions] (broker_id, date, stock_id, value, is_sell, investor_id)
SELECT
  CASE
    WHEN ISNUMERIC(broker) = 1 THEN CAST(broker AS INT)  -- broker is numeric, use it as ID
    ELSE (SELECT id FROM dbo.[tbl.brokers] WHERE name = broker)  -- broker is name, find corresponding ID
  END AS broker_id,
  date,
  CASE
    WHEN stock NOT LIKE '%[^0-9]%' THEN  -- stock value is already digits
      CASE
        WHEN stock = '0' THEN NULL  -- stock value is zero, set it to NULL
        ELSE stock  -- stock value is non-zero, leave it as it is
      END
    WHEN stock NOT IN (SELECT name FROM dbo.[meta.stocks_code_to_name]) THEN NULL  -- stock value not found in name column, set it to NULL
    ELSE (SELECT code FROM dbo.[meta.stocks_code_to_name] WHERE name = stock)  -- stock value found in name column, replace it with the corresponding code
  END AS stock_id,
  CASE
    WHEN value LIKE '%-%' THEN REPLACE(REPLACE(value, '-', ''), '$', '')  -- Remove '-' and '$' for sell transactions
    ELSE value
  END AS normalized_value,
  CASE
    WHEN value LIKE '%-%' THEN 1  -- Set is_sell to 1 for sell transactions
    ELSE 0
  END AS is_sell,
  iid
FROM dbo.[CALLS_TRADES_IID]
WHERE (ISNUMERIC(broker) = 1 OR broker IN (SELECT name FROM dbo.[tbl.brokers]))  -- Exclude records with non-existent broker names
  AND (stock NOT LIKE '%[^0-9]%' OR stock IN (SELECT name FROM dbo.[meta.stocks_code_to_name]))  -- Exclude records with non-existent stock names
  AND stock <> '0'; -- Exclude records with stock value equal to zero

-- Update transaction values in [tbl.transactions]
-- This query updates the 'transaction_value' column in the [tbl.transactions] table based on specific conditions.
UPDATE t
SET transaction_value = CASE
    WHEN t.value LIKE '%$%' THEN 
        CAST(REPLACE(t.value, '$', '') AS FLOAT)
    ELSE CAST(t.value AS FLOAT) * ss.value
END
FROM dbo.[tbl.transactions] t
JOIN dbo.[tbl.stock_spots] ss ON ss.id = t.stock_id AND ss.date = t.date;

-- Remove 'value' column from [tbl.transactions]
-- This alters the [tbl.transactions] table by dropping the 'value' column.
ALTER TABLE dbo.[tbl.transactions]
DROP COLUMN value;

-- Create [tbl.failed_transactions] table
-- This table is used to store failed transaction information.
CREATE TABLE dbo.[tbl.failed_transactions] (
  broker_id INT,
  date DATE,
  failure_reason VARCHAR(255),
  investor_id INT,
  FOREIGN KEY (broker_id) REFERENCES dbo.[tbl.brokers] (id)
);

-- Insert values into [tbl.failed_transactions]
-- This query inserts values into the [tbl.failed_transactions] table based on specific conditions.
INSERT INTO dbo.[tbl.failed_transactions] (broker_id, date, failure_reason, investor_id)
SELECT
  CASE
    WHEN ISNUMERIC(broker) = 1 THEN CAST(broker AS INT)  -- broker is numeric, use it as ID
    ELSE (SELECT id FROM dbo.[tbl.brokers] WHERE name = broker)  -- broker is name, find corresponding ID
  END AS broker_id,
  date,
  stock AS failure_reason,
  iid
FROM dbo.[CALLS_TRADES_IID]
WHERE (ISNUMERIC(broker) <> 1 AND broker NOT IN (SELECT name FROM dbo.[tbl.brokers]))  -- Include records with non-existent broker names
  OR (stock LIKE '%[^0-9]%' AND stock NOT IN (SELECT name FROM dbo.[meta.stocks_code_to_name]))  -- Include records with non-existent stock names
  OR stock = '0'; -- Include records with stock value equal to zero

-- Drop 'failure_reason' column from [tbl.failed_transactions]
-- This alters the [tbl.failed_transactions] table by dropping the 'failure_reason' column.
ALTER TABLE dbo.[tbl.failed_transactions]
DROP COLUMN failure_reason;