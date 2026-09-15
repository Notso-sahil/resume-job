# Verify NexusAI Bridge connectivity (Windows PowerShell)

Write-Host "Checking NexusAI Bridge status..." -ForegroundColor Cyan

# Check if port 12307 is listening
$portCheck = netstat -ano | Select-String "12307" | Select-String "LISTENING"

if ($portCheck) {
    Write-Host "[OK] Port 12307 is listening" -ForegroundColor Green
} else {
    Write-Host "[FAIL] Port 12307 is NOT listening. Make sure:" -ForegroundColor Red
    Write-Host "  1. Chrome is open" -ForegroundColor Yellow
    Write-Host "  2. The NexusAI Browser Agent extension is loaded and Connected" -ForegroundColor Yellow
    Write-Host "  3. Run: nexus-bridge register" -ForegroundColor Yellow
    exit 1
}

# Check if HTTP health endpoint responds
try {
    $response = Invoke-RestMethod -Uri "http://127.0.0.1:12307/ping" -Method GET -TimeoutSec 3 -ErrorAction Stop
    if ($response.status -eq "ok") {
        Write-Host "[OK] Bridge health check passed (http://127.0.0.1:12307/ping)" -ForegroundColor Green
    } else {
        Write-Host "[OK] Bridge server reachable" -ForegroundColor Green
    }
} catch {
    Write-Host "[WARN] Health check ping returned: $($_.Exception.Message)" -ForegroundColor Yellow
}

# Check nexus-bridge CLI
$globalCmd = Get-Command nexus-bridge -ErrorAction SilentlyContinue
if ($globalCmd) {
    $bridgeVersion = & nexus-bridge --version 2>&1
    Write-Host "[OK] Global nexus-bridge installed: $bridgeVersion" -ForegroundColor Green
} else {
    $localCli = Join-Path $PSScriptRoot "..\packages\bridge\dist\cli.js"
    if (Test-Path $localCli) {
        $bridgeVersion = & node $localCli --version 2>&1
        Write-Host "[OK] Local nexus-bridge ready (v$bridgeVersion)" -ForegroundColor Green
        Write-Host "[TIP] To make nexus-bridge accessible globally, run: pnpm link:bridge" -ForegroundColor Gray
    } else {
        Write-Host "[ERROR] nexus-bridge CLI is not found in PATH and local build is missing." -ForegroundColor Red
        Write-Host "        Run 'pnpm --filter @nexusai/bridge build' then 'pnpm link:bridge'" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""
Write-Host "NexusAI Browser Agent looks ready! Test with Antigravity:" -ForegroundColor Cyan
Write-Host "  'Look at my active Chrome tab and tell me what you see.'" -ForegroundColor White
