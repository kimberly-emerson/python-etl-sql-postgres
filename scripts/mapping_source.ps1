$csvData = Import-Csv -Path "C:\demos\python-etl-sql-postgres\sql\mapping.csv"
$csvData = $csvData | Where-Object Is_App_Table -eq 1 | Select-Object source_query_select, table_id, execution_order | Sort-Object execution_order, source_query_select
$jsonData = $csvData | ConvertTo-Json
$jsonData | Set-Content -Path "C:\demos\python-etl-sql-postgres\sql\mapping_source.json"
