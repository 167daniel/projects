USE grs;
GO


-- Drop and create 'new_customers' table
IF OBJECT_ID('new_customers') IS NOT NULL
    DROP TABLE new_customers;
GO



-- Drop and create 'dbo.ValidateNewCustomersFormat' function
IF OBJECT_ID('dbo.add_new_customers') IS NOT NULL
    DROP FUNCTION dbo.add_new_customers;
GO

CREATE TABLE new_customers (
    Investor_Name VARCHAR(255),
    Email VARCHAR(255),
    Phone VARCHAR(255),
    State VARCHAR(255),
    income DECIMAL(18, 2)
);
GO

/**
 * Stores information about new customers.
 */
CREATE FUNCTION add_new_customers()
RETURNS @UpdatedNewInvestors TABLE (
    name VARCHAR(255),
    email VARCHAR(255),
    state VARCHAR(255),
    salary DECIMAL(18, 2),
    phone_n VARCHAR(255)
)
AS
BEGIN
    -- Declare a table variable to hold the replica of dbo.[grs.newinvestors]
    DECLARE @TempNewInvestors TABLE (
        Investor_Name VARCHAR(255),
        Email VARCHAR(255),
        Phone VARCHAR(255),
        State VARCHAR(255),
        income DECIMAL(18, 2)
    );

    -- Insert data from dbo.[grs.newinvestors] into the table variable
    INSERT INTO @TempNewInvestors (Investor_Name, Email, Phone, State, income)
    SELECT Investor_Name, Email, Phone, State, income
    FROM new_customers;

    -- Add the phone_n column to the table variable
    INSERT INTO @UpdatedNewInvestors (name, email, state, salary, phone_n)
    SELECT
        Investor_Name,
        Email,
        CASE
            WHEN State = 'israeli' THEN 'Israel'
            ELSE State
        END,
        income,
        CASE
            WHEN State = 'israeli' THEN SUBSTRING(Phone, 2, LEN(Phone) - 1)
            ELSE Phone
        END
    FROM @TempNewInvestors;

    -- Update the phone_n column based on the phone column
    UPDATE @UpdatedNewInvestors
    SET phone_n = REPLACE(phone_n, '-', '');
	 UPDATE u
    SET u.state = s.state_code
    FROM @UpdatedNewInvestors u
    JOIN dbo.[tbl.state] s ON u.state = s.name;

    RETURN;
END;
GO


-- Drop and create 'dbo.ValidateNewCustomersFormat' function
IF OBJECT_ID('dbo.ValidateNewCustomersFormat') IS NOT NULL
    DROP FUNCTION dbo.ValidateNewCustomersFormat;
GO

/**
 * Validates the format of new customer records.
 *
 * @param Investor_Name - Investor name
 * @param Email - Email address
 * @param Phone - Phone number
 * @param State - State name
 * @param Income - Income amount
 * @return VARCHAR(5) - 'TRUE' if format is valid, 'error' otherwise.
 */
CREATE FUNCTION dbo.ValidateNewCustomersFormat(
    @Investor_Name VARCHAR(255),
    @Email VARCHAR(255),
    @Phone VARCHAR(255),
    @State VARCHAR(255),
    @Income DECIMAL(18, 2)
)
RETURNS VARCHAR(5)
AS
BEGIN
    DECLARE @IsValidFormat VARCHAR(5);

    -- Validate format rules here
    -- Replace with your own validation logic

    IF (LEN(@Investor_Name) > 0
        AND LEN(@Email) > 0
        AND LEN(@Phone) > 0
        AND LEN(@State) > 0
        AND @Income > 0)
    BEGIN
        SET @IsValidFormat = 'TRUE';
    END
    ELSE
    BEGIN
        SET @IsValidFormat = 'error';
    END;

    RETURN @IsValidFormat;
END;
GO

-- Drop and create 'dbo.ProcessNewCustomersValidation' function
IF OBJECT_ID('dbo.ProcessNewCustomersValidation') IS NOT NULL
    DROP FUNCTION dbo.ProcessNewCustomersValidation;
GO

/**
 * Processes the validation of new customer records.
 *
 * @return Table - Valid new customer records.
 */
CREATE FUNCTION dbo.ProcessNewCustomersValidation()
RETURNS TABLE
AS
RETURN
(
    SELECT
        Investor_Name,
        Email,
        Phone,
        State,
        Income
    FROM
        dbo.[new_customers]
    WHERE
        dbo.ValidateNewCustomersFormat(Investor_Name, Email, Phone, State, Income) = 'TRUE'
);
GO

-- Drop and create 'load_new_customers' procedure
IF OBJECT_ID('load_new_customers') IS NOT NULL
    DROP PROCEDURE load_new_customers;
GO

-- Documentation for 'load_new_customers' procedure
/**
 * Loads new customers into the system.
 */
CREATE PROCEDURE load_new_customers
AS
BEGIN
    -- Create a temporary table to hold the data from 'new_customers.tbl'
    CREATE TABLE #TempInvestors (
        Investor_Name VARCHAR(255),
        Email VARCHAR(255),
        Phone VARCHAR(255),
        State VARCHAR(255),
        income DECIMAL(18, 2)
    );

    -- Insert data from 'new_customers.tbl' into the temporary table
    INSERT INTO #TempInvestors (Investor_Name, Email, Phone, State, income)
    SELECT Investor_Name, Email, Phone, State, income
    FROM dbo.[new_customers];

    -- Transform the data in the temporary table
    UPDATE #TempInvestors
    SET
        State = CASE
                    WHEN State = 'israeli' THEN 'Israel'
                    ELSE State
                END,
        Phone = CASE
                    WHEN State = 'israeli' THEN SUBSTRING(Phone, 2, LEN(Phone) - 1)
                    ELSE Phone
                END;

    -- Merge the transformed data into 'tbl.investors'
    MERGE INTO dbo.[tbl.investors] AS target
    USING #TempInvestors AS source
    ON (target.email = source.Email)
    WHEN MATCHED THEN
        UPDATE
        SET
            target.name = source.Investor_Name,
            target.phone_n = source.Phone,
            target.state = source.State,
            target.salary = source.income;

    -- Drop the temporary table
    DROP TABLE #TempInvestors;
END;
GO

------------------------------------------------------------------------------------------------------------------------
--ETL PROCESS RUN


INSERT INTO new_customers (Investor_Name, Email, Phone, State, income)
VALUES ('elad', 'elad@example.com', '1234567890', 'Israel', 50000.00);

INSERT INTO new_customers (Investor_Name, Email, Phone, State, income)
VALUES ('elad1', 'elad1@example.com', '9876543210', 'England', 60000.00);

INSERT INTO new_customers (Investor_Name, Email, Phone, State, income)
VALUES ('elad3', 'elad3@example.com', '4567890123', 'USA', 70000.00);


-- Call the 'add_new_customers' function
SELECT name, email, state, Salary, phone_n
FROM add_new_customers();

---use test
SELECT
  Investor_Name,
  Email,
  Phone,
  State,
  Income,
  dbo.ValidateNewCustomersFormat(Investor_Name, Email, Phone, State, Income) AS ValidationResult
FROM
  [grs].[dbo].[new_customers];

SELECT *
FROM dbo.ProcessNewCustomersValidation();

EXEC load_new_customers;
