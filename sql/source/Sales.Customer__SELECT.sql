SELECT [CustomerID]
      ,[PersonID]
      ,[StoreID]
      ,[TerritoryID]
      ,[AccountNumber]
      ,[rowguid] = CONVERT(VARCHAR(36),rowguid)
      ,[ModifiedDate] = CONVERT(VARCHAR,ModifiedDate,120)
  FROM [Sales].[Customer]