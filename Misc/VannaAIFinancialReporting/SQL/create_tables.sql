-- Create Advisors table
CREATE TABLE Advisors (
    AdvisorID INT IDENTITY(1,1) PRIMARY KEY,
    Name NVARCHAR(100) NOT NULL,
    ContactInfo NVARCHAR(100)
);

-- Create Clients table
CREATE TABLE Clients (
    ClientID INT IDENTITY(1,1) PRIMARY KEY,
    Name NVARCHAR(100) NOT NULL,
    ContactInfo NVARCHAR(100),
    AdvisorID INT,
    RiskProfile NVARCHAR(50),
    FOREIGN KEY (AdvisorID) REFERENCES Advisors(AdvisorID)
);

-- Create Accounts table
CREATE TABLE Accounts (
    AccountID INT IDENTITY(1,1) PRIMARY KEY,
    AccountType NVARCHAR(50) NOT NULL,
    ClientID INT,
    FOREIGN KEY (ClientID) REFERENCES Clients(ClientID)
);

-- Create Assets table
CREATE TABLE Assets (
    AssetID INT IDENTITY(1,1) PRIMARY KEY,
    Name NVARCHAR(100) NOT NULL,
    AssetType NVARCHAR(50),
    CurrentValue DECIMAL(18, 2)
);

-- Create Transactions table
CREATE TABLE Transactions (
    TransactionID INT IDENTITY(1,1) PRIMARY KEY,
    AccountID INT,
    AssetID INT,
    Date DATETIME,
    Type NVARCHAR(50),
    Amount DECIMAL(18, 2),
    FOREIGN KEY (AccountID) REFERENCES Accounts(AccountID),
    FOREIGN KEY (AssetID) REFERENCES Assets(AssetID)
);

-- Create Portfolios table
CREATE TABLE Portfolios (
    PortfolioID INT IDENTITY(1,1) PRIMARY KEY,
    ClientID INT,
    Name NVARCHAR(100),
    RiskLevel NVARCHAR(50),
    FOREIGN KEY (ClientID) REFERENCES Clients(ClientID)
);

-- Create PortfolioAssets table
CREATE TABLE PortfolioAssets (
    PortfolioAssetID INT IDENTITY(1,1) PRIMARY KEY,
    PortfolioID INT,
    AssetID INT,
    Allocation DECIMAL(18, 2),
    FOREIGN KEY (PortfolioID) REFERENCES Portfolios(PortfolioID),
    FOREIGN KEY (AssetID) REFERENCES Assets(AssetID)
);

-- Create Projections table
CREATE TABLE Projections ( ProjectionID INT IDENTITY(1,1) PRIMARY KEY, PortfolioID INT,
    FutureValue DECIMAL(18, 2),
    ProjectionDate DATETIME,
    FOREIGN KEY (PortfolioID) REFERENCES Portfolios(PortfolioID)
);
