SELECT [SalesOrderID]
      ,[SalesOrderDetailID]
      ,[CarrierTrackingNumber]
      ,[OrderQty]
      ,[ProductID]
      ,[SpecialOfferID]
      ,[UnitPrice]
      ,[UnitPriceDiscount]
      ,[LineTotal]
      ,[rowguid] = CONVERT(VARCHAR(36),rowguid)
      ,[ModifiedDate] = CONVERT(VARCHAR,ModifiedDate,120)
  FROM [Sales].[SalesOrderDetail]