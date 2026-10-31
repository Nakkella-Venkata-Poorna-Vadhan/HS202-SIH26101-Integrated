# Stop native PostgreSQL 18 server daemon on port 54329
$pgBin = "C:\Program Files\PostgreSQL\18\bin"
$pgData = "D:\Projects\SIH26101\SIH26101-Integrated-Phase1\backend\data\pgdata"

Write-Host "Stopping PostgreSQL daemon on port 54329..."
& "$pgBin\pg_ctl.exe" -D $pgData stop -m fast