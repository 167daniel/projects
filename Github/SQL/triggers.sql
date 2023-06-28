-- Check if the trigger already exists and drop it if it does
IF EXISTS (
    SELECT *
    FROM sys.triggers
    WHERE name = 'PreventFutureDates'
)
BEGIN
    DROP TRIGGER PreventFutureDates
END
GO

-- Create the trigger
CREATE TRIGGER PreventFutureDates
ON dbo.[tbl.stock_spots]
AFTER INSERT, UPDATE
AS
BEGIN
    -- Check for future dates in the inserted or updated rows
    IF EXISTS (
        SELECT *
        FROM inserted
        WHERE [date] > GETDATE()
    )
    BEGIN
        -- Rollback the transaction and raise an error
        ROLLBACK TRANSACTION;
        RAISERROR('Future dates are not allowed - the operation was cancelled.', 16, 1);
    END
END;

----------------------------------------------------------------------------------

-- Drop and create 'trg_check_valid_email' trigger
IF OBJECT_ID('trg_check_valid_email') IS NOT NULL
    DROP TRIGGER trg_check_valid_email;
GO


/**
 * Trigger that checks email validation and allows new emails according to the format.
 */
CREATE TRIGGER trg_check_valid_email
ON dbo.[tbl.investors]
AFTER INSERT, UPDATE
AS
BEGIN
    SET NOCOUNT ON;

    -- Variable to store the invalid email records
    DECLARE @InvalidEmails TABLE (investor_id INT, email VARCHAR(255));

    -- Check for invalid email formats
    INSERT INTO @InvalidEmails (investor_id, email)
    SELECT investor_id, email
    FROM inserted
    WHERE email NOT LIKE '%@%.com';

    -- Check if there are any invalid email records
    IF EXISTS (SELECT 1 FROM @InvalidEmails)
    BEGIN
        -- Invalid email format found
        -- Raise error and set email to NULL
        RAISERROR('non-valid-email', 16, 1);
        UPDATE dbo.tbl.investors
        SET email = NULL
        WHERE investor_id IN (SELECT investor_id FROM @InvalidEmails);
    END
    ELSE
    BEGIN
        -- Valid email format
        -- Add prefix to the prefix table
        INSERT INTO dbo.[meta.valid_emails] (email_prefix)
        SELECT SUBSTRING(email, CHARINDEX('@', email) + 1, LEN(email))
        FROM inserted
        WHERE email LIKE '%@%.com';
    END;
END;
GO
-----------------------------------------------------------------------

-- Drop the trigger if it already exists
IF EXISTS (SELECT * FROM sys.triggers WHERE name = 'check_stock_type')
BEGIN
    DROP TRIGGER check_stock_type
END
GO

-- Create the trigger
CREATE TRIGGER check_stock_type
ON dbo.[tbl.stocks]
AFTER INSERT
AS
BEGIN

    -- Check if the inserted record has a value in the type column
    IF EXISTS (SELECT 1 FROM inserted WHERE [type] IS NULL)
    BEGIN
        -- Raise an error and rollback the transaction
        RAISERROR ('Cannot insert record without a value in the type column.', 16, 1)
        ROLLBACK TRANSACTION
    END
END
GO