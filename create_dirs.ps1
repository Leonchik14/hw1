# PowerShell script for creating necessary directories

Write-Host "Creating necessary directories..." -ForegroundColor Yellow

$directories = @(
    "app/models",
    "app/data",
    "models",
    "data"
)

foreach ($dir in $directories) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Host "Created directory: $dir" -ForegroundColor Green
    } else {
        Write-Host "Directory already exists: $dir" -ForegroundColor Gray
    }
}

Write-Host "`nDone!" -ForegroundColor Green

