# OSCAR Local Setup & Installation Guide

**Project**: OSCAR (Operational Statement Classification, Analysis & Reconciliation)  
**Product Descriptor**: Financial Document Intelligence  
**Environment Support**: Windows 10/11, macOS, Linux (Ubuntu 22.04+)  

---

## 1. Quickstart: One-Click Windows Launchers

OSCAR provides ready-to-run Windows batch launchers that automatically verify prerequisites, manage ports, prevent duplicate instances, track process ownership, and redirect runtime operations to `F:\Projects\OSCAR\.runtime\`:

```cmd
:: Start OSCAR (Launches FastAPI backend on :8000, Vite frontend on :5173, and opens browser)
start_oscar.bat

:: Safely stop OSCAR (Terminates only launcher-spawned processes and preserves SQLite data)
stop_oscar.bat
```

When you double-click `start_oscar.bat`:
1. It validates the Python virtual environment (`.venv\Scripts\python.exe`) and frontend dependencies.
2. It detects whether ports 8000 or 5173 are already occupied.
3. If an existing OSCAR instance is healthy, it reuses it and opens the browser without spawning duplicates.
4. It starts backend and frontend in separate visible terminal windows so logs can be monitored.
5. It polls the health endpoint (`/api/v1/health`) and frontend port, then launches `http://localhost:5173`.

---

## 2. Prerequisites

Before installing OSCAR, verify that the following system tools are available:

| Component | Minimum Version | Recommended Version | Verification Command |
| :--- | :--- | :--- | :--- |
| **Python** | 3.11.0+ | 3.11.15 | `python --version` |
| **Node.js** | 18.0.0+ | 20.0.0+ | `node --version` |
| **npm** | 9.0.0+ | 11.0.0+ | `npm --version` |
| **Tesseract OCR** | 5.0.0+ | 5.5.0.20241111 | `tesseract --version` |

---

## 3. Physical Tesseract OCR Setup on Windows

Tesseract OCR is required for scanned raster bank statements without embedded text layers. Digital text PDFs (Layouts A, B, and C) are extracted directly via PyMuPDF and pdfplumber without OCR.

### Step 3.1: Download & Install Binary
1. Download the Windows installer from [UB-Mannheim Tesseract](https://github.com/UB-Mannheim/tesseract/wiki).
2. Install to the standard directory:
   `C:\Program Files\Tesseract-OCR\tesseract.exe`
3. In the installer, ensure the English (`eng`) and Script/Orientation (`osd`) language packs are selected.

### Step 3.2: Verify Installation
```cmd
"C:\Program Files\Tesseract-OCR\tesseract.exe" --version
"C:\Program Files\Tesseract-OCR\tesseract.exe" --list-langs
```
Expected output:
```text
tesseract v5.5.0.20241111
 leptonica-1.84.1
List of available languages in "C:\Program Files\Tesseract-OCR/tessdata/" (2):
eng
osd
```

### Step 3.3: Configuration & Discovery
OSCAR's configuration system (`backend/app/core/config.py`) automatically discovers Tesseract:
1. Checks `TESSERACT_CMD` environment variable.
2. Probes `C:\Program Files\Tesseract-OCR\tesseract.exe` if `TESSERACT_CMD` is unset.
3. Falls back to system `PATH`.

> [!NOTE]
> Python's `pytesseract` library is merely a Python wrapper. The underlying physical Tesseract executable and language training data must be installed on the host system.

---

## 4. Manual Installation & Development Setup

If you prefer to start services manually instead of using `start_oscar.bat`:

### Step 4.1: Python Virtual Environment & Dependencies
From the project root (`F:\Projects\OSCAR`):
```powershell
# Create Python 3.11 virtual environment
python -m venv .venv

# Activate virtual environment (Windows PowerShell)
.\.venv\Scripts\Activate.ps1

# Upgrade pip and install backend dependencies
python -m pip install --upgrade pip
pip install -r backend/requirements.txt
```

### Step 4.2: Frontend Dependencies
```powershell
# Install React 19 + TypeScript dependencies
npm --prefix frontend install
```

### Step 4.3: Terminal 1 — FastAPI Backend (Port 8000)
```powershell
$env:TEMP = "F:\Projects\OSCAR\.runtime\tmp"
$env:TMP = "F:\Projects\OSCAR\.runtime\tmp"
& .venv\Scripts\python.exe -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000
```
- API Base URL: `http://localhost:8000`
- Interactive OpenAPI Docs: `http://localhost:8000/docs`
- Health Endpoint: `http://localhost:8000/api/v1/health`

### Step 4.4: Terminal 2 — React Frontend (Port 5173)
```powershell
$env:TEMP = "F:\Projects\OSCAR\.runtime\tmp"
$env:TMP = "F:\Projects\OSCAR\.runtime\tmp"
npm --prefix frontend run dev -- --host 127.0.0.1 --port 5173 --cache "F:\Projects\OSCAR\.runtime\npm-cache"
```
- Application UI: `http://localhost:5173`

---

## 5. Verification & Test Execution

### 5.1 Full Backend Pytest Suite (47/47 Tests Passing)
```powershell
& .venv\Scripts\python.exe -m pytest backend\tests -v
```
All 47 tests across analytics, classification, financial engineering, multi-layout OCR, persistence lifecycle, statement details, and vertical slice pass in ~30 seconds.

### 5.2 Frontend Production Build
```powershell
npm --prefix frontend run build
```
Invokes `tsc -b && vite build` and confirms zero TypeScript compilation or linting errors.

### 5.3 Physical Tesseract OCR Benchmark
```powershell
& .venv\Scripts\python.exe scripts\verify_scanned_ocr_e2e.py
```
Tests end-to-end scanned statement extraction, coordinate transformation, and accuracy benchmarking against ground truth (15/15 txns, 100% precision/recall, 98.67% field accuracy, ₹0.00 variance).

### 5.4 Export Centre & Viewport Verification
```powershell
& .venv\Scripts\python.exe scripts\verify_export_centre_interactive.py
```
Tests responsive layout across 5 viewports (1920x1080, 1440x900, 1366x768, 768x1024, 390x844), dropdown interaction, and zero horizontal scroll.

### 5.5 Machine Learning Leakage Audit
```powershell
& .venv\Scripts\python.exe scripts\evaluate_ml_and_leakage.py
```
Validates zero data leakage between train and held-out test sets.

---

## 6. Troubleshooting & Diagnostics

- **Port Conflict (8000 or 5173)**:
  Run `Get-NetTCPConnection -LocalPort 8000, 5173 -State Listen` to find the occupying process ID.
- **Tesseract Not Detected**:
  Verify `C:\Program Files\Tesseract-OCR\tesseract.exe` exists or set `TESSERACT_CMD=C:\Program Files\Tesseract-OCR\tesseract.exe` in `.env`.
- **Low Disk Space on C:**:
  OSCAR automatically redirects runtime temporary operations and npm caches to `F:\Projects\OSCAR\.runtime\`.
