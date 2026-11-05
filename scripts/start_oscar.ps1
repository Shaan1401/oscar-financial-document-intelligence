# OSCAR — One-Click Windows Launcher (scripts/start_oscar.ps1)
# Operational Statement Classification, Analysis and Reconciliation

$ErrorActionPreference = "Stop"
$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
Set-Location $ProjectRoot

Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "  OSCAR -- Operational Statement Classification, Analysis and Reconciliation" -ForegroundColor Yellow
Write-Host "  Financial Document Intelligence | Tagline: Every transaction deserves an explanation." -ForegroundColor DarkGray
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "Project Root: $ProjectRoot" -ForegroundColor Gray

# 1. Setup Runtime Directories on F:
$RuntimeDir = Join-Path $ProjectRoot ".runtime"
$RuntimeTmp = Join-Path $RuntimeDir "tmp"
$RuntimeNpm = Join-Path $RuntimeDir "npm-cache"
$RuntimeLogs = Join-Path $RuntimeDir "logs"
$ServicesFile = Join-Path $RuntimeDir "oscar_services.json"

foreach ($d in @($RuntimeTmp, $RuntimeNpm, $RuntimeLogs)) {
    if (-not (Test-Path $d)) {
        New-Item -ItemType Directory -Force -Path $d | Out-Null
    }
}

# Process-level Temp redirection
$env:TEMP = $RuntimeTmp
$env:TMP = $RuntimeTmp
$env:npm_config_cache = $RuntimeNpm

# 2. Prerequisites Verification
Write-Host ""
Write-Host "[1/4] Checking prerequisites..." -ForegroundColor White
$VenvPython = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $VenvPython)) {
    Write-Host "ERROR: Python virtual environment not found at: $VenvPython" -ForegroundColor Red
    Write-Host "Please set up .venv before launching OSCAR." -ForegroundColor Yellow
    exit 1
}

$PackageJson = Join-Path $ProjectRoot "frontend\package.json"
if (-not (Test-Path $PackageJson)) {
    Write-Host "ERROR: Frontend package.json not found at: $PackageJson" -ForegroundColor Red
    exit 1
}

try {
    $nodeVer = & node -v
    $npmVer = & npm -v
    Write-Host "  * Python Venv : $VenvPython" -ForegroundColor Green
    Write-Host "  * Node.js     : $nodeVer" -ForegroundColor Green
    Write-Host "  * npm         : $npmVer" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Node.js or npm is not available in PATH." -ForegroundColor Red
    exit 1
}

# 3. Port and Duplicate Instance Inspection
Write-Host ""
Write-Host "[2/4] Inspecting ports (8000, 5173)..." -ForegroundColor White

function Test-PortOccupied([int]$Port) {
    $conn = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
    if ($conn) {
        return $conn.OwningProcess
    }
    return $null
}

$backendPid = Test-PortOccupied 8000
$frontendPid = Test-PortOccupied 5173

# Check if OSCAR is already running and healthy
if ($backendPid -and $frontendPid) {
    try {
        $health = Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/v1/health" -TimeoutSec 3 -ErrorAction Stop
        if ($health.status -eq "healthy") {
            Write-Host ""
            Write-Host "[NOTE] OSCAR is already running and healthy!" -ForegroundColor Green
            Write-Host "  * Backend PID  : $backendPid (Port 8000)" -ForegroundColor Green
            Write-Host "  * Frontend PID : $frontendPid (Port 5173)" -ForegroundColor Green
            Write-Host "  * OCR Active   : $($health.ocr_available) (Version: $($health.tesseract_version))" -ForegroundColor Green
            Write-Host ""
            Write-Host "Opening http://localhost:5173 in your default browser..." -ForegroundColor Yellow
            Start-Process "http://localhost:5173"
            exit 0
        }
    } catch {}
}

if ($backendPid) {
    Write-Host "WARNING: Port 8000 is occupied by Process PID $backendPid." -ForegroundColor Yellow
    Write-Host "If this is not OSCAR, please free port 8000 or terminate the process." -ForegroundColor Yellow
}
if ($frontendPid) {
    Write-Host "WARNING: Port 5173 is occupied by Process PID $frontendPid." -ForegroundColor Yellow
    Write-Host "If this is not OSCAR, please free port 5173 or terminate the process." -ForegroundColor Yellow
}

# 4. Launching Backend and Frontend Services in Separate Windows
Write-Host ""
Write-Host "[3/4] Starting services..." -ForegroundColor White
$services = @()

if (-not $backendPid) {
    Write-Host "  * Launching FastAPI Backend on port 8000..." -ForegroundColor Cyan
    $bBat = Join-Path $PSScriptRoot "run_backend.bat"
    $bCmd = "cmd.exe /k `"$bBat`""
    $bProc = Invoke-CimMethod -ClassName Win32_Process -MethodName Create -Arguments @{CommandLine=$bCmd; CurrentDirectory=$ProjectRoot}
    $services += @{
        service = "backend"
        pid = $bProc.ProcessId
        startTime = (Get-Date).ToString("o")
        port = 8000
    }
} else {
    Write-Host "  * Reusing existing backend on port 8000 (PID: $backendPid)" -ForegroundColor DarkGray
}

if (-not $frontendPid) {
    Write-Host "  * Launching Vite Frontend on port 5173..." -ForegroundColor Cyan
    $fBat = Join-Path $PSScriptRoot "run_frontend.bat"
    $fCmd = "cmd.exe /k `"$fBat`""
    $fProc = Invoke-CimMethod -ClassName Win32_Process -MethodName Create -Arguments @{CommandLine=$fCmd; CurrentDirectory=$ProjectRoot}
    $services += @{
        service = "frontend"
        pid = $fProc.ProcessId
        startTime = (Get-Date).ToString("o")
        port = 5173
    }
} else {
    Write-Host "  * Reusing existing frontend on port 5173 (PID: $frontendPid)" -ForegroundColor DarkGray
}

if ($services.Count -gt 0) {
    $services | ConvertTo-Json | Set-Content -Path $ServicesFile -Encoding UTF8
}

# 5. Health Check and Ready State Polling
Write-Host ""
Write-Host "[4/4] Polling service health..." -ForegroundColor White

$backendHealthy = $false
$healthData = $null
for ($i = 1; $i -le 30; $i++) {
    try {
        $resp = Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/v1/health" -TimeoutSec 2 -ErrorAction Stop
        if ($resp.status -eq "healthy") {
            $backendHealthy = $true
            $healthData = $resp
            break
        }
    } catch {
        Start-Sleep -Milliseconds 800
    }
}

$frontendReady = $false
for ($i = 1; $i -le 30; $i++) {
    try {
        $web = Invoke-WebRequest -Uri "http://127.0.0.1:5173" -UseBasicParsing -TimeoutSec 2 -ErrorAction Stop
        if ($web.StatusCode -eq 200) {
            $frontendReady = $true
            break
        }
    } catch {
        Start-Sleep -Milliseconds 800
    }
}

Write-Host ""
Write-Host "======================================================================" -ForegroundColor Cyan
if ($backendHealthy -and $frontendReady) {
    Write-Host "  OSCAR SYSTEM READY!" -ForegroundColor Green
    Write-Host "  * Backend API : http://127.0.0.1:8000/api/v1/health (HEALTHY)" -ForegroundColor Green
    Write-Host "  * Frontend UI : http://localhost:5173 (ACTIVE)" -ForegroundColor Green
    if ($healthData) {
        Write-Host "  * OCR Engine  : Tesseract $($healthData.tesseract_version) (Available: $($healthData.ocr_available))" -ForegroundColor Green
    }
    Write-Host ""
    Write-Host "Opening http://localhost:5173 in default browser..." -ForegroundColor Yellow
    Start-Process "http://localhost:5173"
    Write-Host ""
    Write-Host "To stop OSCAR safely, double-click: stop_oscar.bat" -ForegroundColor Cyan
} else {
    Write-Host "  WARNING: One or more services did not respond in time." -ForegroundColor Yellow
    Write-Host "  Backend Healthy : $backendHealthy" -ForegroundColor Yellow
    Write-Host "  Frontend Ready  : $frontendReady" -ForegroundColor Yellow
    Write-Host "  Inspect terminal windows for detailed startup logs." -ForegroundColor Yellow
}
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ""
