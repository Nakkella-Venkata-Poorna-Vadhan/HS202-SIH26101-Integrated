# Start native PostgreSQL 18 server daemon on port 54329 (Local Loopback)
$pgBin = "C:\Program Files\PostgreSQL\18\bin"
$pgData = "D:\Projects\SIH26101\SIH26101-Integrated-Phase1\backend\data\pgdata"

if (-not (Test-Path $pgData)) {
    Write-Host "Initializing PostgreSQL cluster at $pgData..."
    & "$pgBin\initdb.exe" -D $pgData -U postgres -E UTF8 --auth-local=scram-sha-256 --auth-host=scram-sha-256
    Add-Content -Path "$pgData\postgresql.conf" -Value "`nport = 54329`nlisten_addresses = '127.0.0.1'`npassword_encryption = scram-sha-256"
}

Write-Host "Starting PostgreSQL daemon on port 54329..."
& "$pgBin\pg_ctl.exe" -D $pgData -l "$pgData\server.log" start
Start-Sleep -Seconds 2
& "$pgBin\pg_ctl.exe" -D $pgData status