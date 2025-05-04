CREATE PROCEDURE CalculateClientRiskAssessment
AS
BEGIN
    SELECT
        c.ClientID,
        c.Name AS ClientName,
        p.PortfolioID,
        p.Name AS PortfolioName,
        p.RiskLevel,
        SUM(a.CurrentValue * pa.Allocation / 100.0) AS TotalAllocatedValue
    FROM
        Clients c
    JOIN
        Portfolios p ON c.ClientID = p.ClientID
    JOIN
        PortfolioAssets pa ON p.PortfolioID = pa.PortfolioID
    JOIN
        Assets a ON pa.AssetID = a.AssetID
    GROUP BY
        c.ClientID, c.Name, p.PortfolioID, p.Name, p.RiskLevel;
END;



CREATE PROCEDURE CalculateTotalPortfolioValue
AS
BEGIN
    SELECT
        c.ClientID,
        c.Name AS ClientName,
        p.PortfolioID,
        p.Name AS PortfolioName,
        SUM(pa.Allocation * a.CurrentValue / 100.0) AS TotalPortfolioValue
    FROM
        Clients c
    JOIN
        Portfolios p ON c.ClientID = p.ClientID
    JOIN
        PortfolioAssets pa ON p.PortfolioID = pa.PortfolioID
    JOIN
        Assets a ON pa.AssetID = a.AssetID
    GROUP BY
        c.ClientID, c.Name, p.PortfolioID, p.Name;
END;


CREATE PROCEDURE IdentifyUnderperformingAssets
    @Threshold DECIMAL(18,2),
    @DaysInterval INT
AS
BEGIN
    SELECT
        a.AssetID,
        a.Name AS AssetName,
        a.CurrentValue,
        COUNT(t.TransactionID) AS NumTransactions
    FROM
        Assets a
    LEFT JOIN
        Transactions t ON a.AssetID = t.AssetID
    WHERE
        t.Date >= DATEADD(DAY, -@DaysInterval, GETDATE())
    GROUP BY
        a.AssetID, a.Name, a.CurrentValue
    HAVING
        COUNT(t.TransactionID) < @Threshold;
END;


CREATE PROCEDURE GetPortfolioPerformanceOverTime
    @ClientID INT
AS
BEGIN
    SELECT
        p.PortfolioID,
        p.Name AS PortfolioName,
        t.Date,
        SUM(t.Amount) AS TotalTransactionValue,
        SUM(pa.Allocation * a.CurrentValue / 100.0) AS CurrentPortfolioValue
    FROM
        Clients c
    JOIN
        Portfolios p ON c.ClientID = p.ClientID
    JOIN
        PortfolioAssets pa ON p.PortfolioID = pa.PortfolioID
    JOIN
        Assets a ON pa.AssetID = a.AssetID
    LEFT JOIN
        Transactions t ON t.AssetID = a.AssetID
    WHERE
        c.ClientID = @ClientID
    GROUP BY
        p.PortfolioID, p.Name, t.Date;
END;


CREATE PROCEDURE AnalyzeAssetAllocation
AS
BEGIN
    SELECT
        a.AssetID,
        a.Name AS AssetName,
        SUM(pa.Allocation) AS TotalAllocationAcrossPortfolios
    FROM
        Assets a
    JOIN
        PortfolioAssets pa ON a.AssetID = pa.AssetID
    GROUP BY
        a.AssetID, a.Name;
END;
