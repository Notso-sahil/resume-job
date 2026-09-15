# NexusAI One-Click Build & Host Registration for Windows (PowerShell)
# Builds all packages topologically and installs Native Messaging Host

$ErrorActionPreference = "Stop"

Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host "     NexusAI One-Click Build & Registration         " -ForegroundColor Cyan
Write-Host "=====================================================" -ForegroundColor Cyan

# 1. Build all packages
Write-Host "`n[Step 1/2] Building all NexusAI packages..." -ForegroundColor Yellow
node scripts/build-all.mjs
if ($LASTEXITCODE -ne 0) {
    Write-Host "`nBuild failed with exit code $LASTEXITCODE" -ForegroundColor Red
    exit $LASTEXITCODE
}

# 2. Register Native Messaging host
Write-Host "`n[Step 2/2] Registering Native Messaging Host..." -ForegroundColor Yellow
node scripts/install-host.mjs
if ($LASTEXITCODE -ne 0) {
    Write-Host "`nRegistration failed with exit code $LASTEXITCODE" -ForegroundColor Red
    exit $LASTEXITCODE
}

Write-Host "`n=====================================================" -ForegroundColor Green
Write-Host "   NexusAI is ready to run on Windows!               " -ForegroundColor Green
Write-Host "=====================================================" -ForegroundColor Green
Write-Host "`nTo load the extension:" -ForegroundColor Cyan
Write-Host "1. Open Google Chrome and go to chrome://extensions"
Write-Host "2. Enable 'Developer mode' in top-right"
Write-Host "3. Click 'Load unpacked' and select:"
Write-Host "   $PSScriptRoot\packages\extension\.output\chrome-mv3" -ForegroundColor Yellow
Write-Host "4. Open the popup to test connection.`n"
