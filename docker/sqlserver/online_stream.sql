-- Tabel ringan untuk menampung transaksi online "baru" yang dibuat faker.
-- Data historis online 2011-2014 tetap dibaca dari Sales.SalesOrderHeader asli;
-- tabel ini hanya untuk simulasi transaksi yang terus mengalir (incremental).
-- Ingestion (Anggota 2) membaca delta-nya lewat watermark pada kolom ModifiedDate.

IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'OnlineOrderStream')
BEGIN
    CREATE TABLE dbo.OnlineOrderStream (
        OrderStreamID INT IDENTITY(1,1) PRIMARY KEY,
        OrderDate     DATETIME2 NOT NULL DEFAULT SYSDATETIME(),
        CustomerID    INT       NOT NULL,
        ProductID     INT       NOT NULL,
        OrderQty      INT       NOT NULL,
        UnitPrice     MONEY     NOT NULL,
        Channel       VARCHAR(20) NOT NULL DEFAULT 'Online',
        ModifiedDate  DATETIME2 NOT NULL DEFAULT SYSDATETIME()
    );
    PRINT 'Tabel dbo.OnlineOrderStream dibuat.';
END
ELSE
    PRINT 'Tabel dbo.OnlineOrderStream sudah ada.';
