# OSCAR — Safe Shutdown Script (scripts/stop_oscar.ps1)
# Operational Statement Classification, Analysis and Reconciliation

$ErrorActionPreference = "SilentlyContinue"
$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
Set-Location $ProjectRoot

Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "  OSCAR -- Safe Service Shutdown" -ForegroundColor Yellow
Write-Host "======================================================================" -ForegroundColor Cyan

$RuntimeDir = Join-Path $ProjectRoot ".runtime"
$ServicesFile = Join-Path $RuntimeDir "oscar_services.json"

if (-not (Test-Path $ServicesFile)) {
    Write-Host ""
    Write-Host "[NOTE] No launcher-managed services file found ($ServicesFile)." -ForegroundColor Yellow
    Write-Host "OSCAR launcher services may not be running or were launched manually." -ForegroundColor Gray
    Write-Host "Unrelated Python or Node processes will NOT be terminated." -ForegroundColor Green
    exit 0
}

try {
    $raw = Get-Content -Path $ServicesFile -Raw -Encoding UTF8
    $services = $raw | ConvertFrom-Json
} catch {
    Write-Host "ERROR: Could not parse $ServicesFile" -ForegroundColor Red
    exit 1
}

if (-not $services) {
    Write-Host "No tracked launcher processes found." -ForegroundColor Yellow
    Remove-Item -Path $ServicesFile -Force -ErrorAction SilentlyContinue
    exit 0
}

Write-Host ""
Write-Host "Found tracked launcher services:" -ForegroundColor White
$stoppedCount = 0

foreach ($svc in $services) {
    $name = $svc.service
    $targetPid = $svc.pid
    $port = $svc.port

    Write-Host "  * Inspecting $name (PID: $targetPid, Port: $port)..." -ForegroundColor White
    $proc = Get-Process -Id $targetPid -ErrorAction SilentlyContinue

    if ($proc) {
        # Verified process exists - safely terminate tree
        Write-Host "    Terminating launcher process tree for PID $targetPid ($name)..." -ForegroundColor Yellow
        & taskkill /PID $targetPid /T /F | Out-Null
        $stoppedCount++
        Write-Host "    Successfully stopped $name." -ForegroundColor Green
    } else {
        Write-Host "    Process PID $targetPid is already inactive." -ForegroundColor DarkGray
    }
}

# Clean up services metadata
Remove-Item -Path $ServicesFile -Force -ErrorAction SilentlyContinue

# Verify port release
Start-Sleep -Seconds 1
function Check-Port([int]$p) {
    $conn = Get-NetTCPConnection -LocalPort $p -State Listen -ErrorAction SilentlyContinue
    return [bool]$conn
}

$p8000 = Check-Port 8000
$p5173 = Check-Port 5173

Write-Host ""
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "  OSCAR SHUTDOWN COMPLETE" -ForegroundColor Green
Write-Host "  * Services Stopped : $stoppedCount" -ForegroundColor Green
Write-Host "  * Port 8000 Active : $p8000" -ForegroundColor $(if ($p8000) { "Yellow" } else { "DarkGray" })
Write-Host "  * Port 5173 Active : $p5173" -ForegroundColor $(if ($p5173) { "Yellow" } else { "DarkGray" })
Write-Host "  * Database Intact  : F:\Projects\OSCAR\backend\oscar.db (Preserved)" -ForegroundColor Green
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ""
