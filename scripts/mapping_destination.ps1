$csvData = Import-Csv -Path "C:\demos\python-etl-sql-postgres\sql\mapping.csv"
$csvData = $csvData | Where-Object Is_App_Table -eq 1 | Select-Object destination_query_create, destination_query_insert, execution_order | Sort-Object execution_order, destination_query_create
$jsonData = $csvData | ConvertTo-Json
$jsonData | Set-Content -Path "C:\demos\python-etl-sql-postgres\sql\mapping_destination.json"