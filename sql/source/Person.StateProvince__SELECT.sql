SELECT [StateProvinceID]
      ,[StateProvinceCode]
      ,[CountryRegionCode]
      ,[IsOnlyStateProvinceFlag] = CAST(CAST(IsOnlyStateProvinceFlag AS BIT) AS CHAR(1))
      ,[Name]
      ,[TerritoryID]
      ,[rowguid] = CONVERT(VARCHAR(36),rowguid)
      ,[ModifiedDate] = CONVERT(VARCHAR,ModifiedDate,120)
  FROM [Person].[StateProvince]