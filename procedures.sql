-- Drop the 'AddState' procedure if it already exists
IF OBJECT_ID('AddState', 'P') IS NOT NULL
    DROP PROCEDURE AddState;
GO

-- Procedure: AddState
-- Description: Adds a new state to the database.
IF OBJECT_ID('AddState', 'P') IS NOT NULL
    DROP PROCEDURE AddState
GO

CREATE PROCEDURE AddState
    @state_code INT,
    @name VARCHAR(50),
    @area_code VARCHAR(10),
    @currency VARCHAR(20)
AS
BEGIN
    -- Check if the state code already exists
    IF EXISTS (SELECT 1 FROM dbo.[tbl.state] WHERE state_code = @state_code)
    BEGIN
        RAISERROR('State with state_code %d already exists.', 16, 1, @state_code)
        RETURN
    END
    
    -- Check if the state name already exists
    IF EXISTS (SELECT 1 FROM dbo.[tbl.state] WHERE name = @name)
    BEGIN
        RAISERROR('State with name %s already exists.', 16, 1, @name)
        RETURN
    END
    
    -- Check if the area code already exists
    IF EXISTS (SELECT 1 FROM dbo.[tbl.state] WHERE area_code = CONCAT(@area_code, '-'))
    BEGIN
        RAISERROR('State with area code %s already exists.', 16, 1, @area_code)
        RETURN
    END

    -- Format the area code
    SET @area_code = CONCAT(@area_code, '-')

    -- Insert the new state
    INSERT INTO dbo.[tbl.state] (state_code, name, area_code, currency)
    VALUES (@state_code, @name, @area_code, @currency)
END
