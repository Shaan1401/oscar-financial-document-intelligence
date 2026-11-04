# OSCAR Local Setup & Installation Guide

**Project**: OSCAR (Operational Statement Classification, Analysis & Reconciliation)  
**Product Descriptor**: Financial Document Intelligence  
**Environment Support**: Windows 10/11, macOS, Linux (Ubuntu 22.04+)  

---

## 1. Prerequisites

Before installing OSCAR, verify that the following system tools are available:

| Component | Minimum Version | Recommended Version | Verification Command |
| :--- | :--- | :--- | :--- |
| **Python** | 3.11.0+ | 3.11.15 | `python --version` |
| **Node.js** | 18.0.0+ | 20.0.0+ | `node --version` |
| **npm** | 9.0.0+ | 10.0.0+ | `npm --version` |
| **Tesseract OCR** *(Optional)* | 5.0.0+ | 5.3.0+ | `tesseract --version` |

> [!NOTE]
> Tesseract OCR is only required if you intend to process scanned bitmap PDFs without digital text layers. Digital text PDFs (Layouts A, B, and C) are extracted directly via PyMuPDF and pdfplumber without external OCR binaries.

---

## 2. One-Time Installation

Clone the repository and set up the Python and Node.js environments:

### Step 2.1: Python Virtual Environment & Dependencies

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

### Step 2.2: Frontend Dependencies

```powershell
# Install React 19 + TypeScript dependencies
npm --prefix frontend install
```

---

## 3. Database Initialization & Demonstration Seeding

Initialize the SQLite database and seed the 3 standard banking statement layouts (Layout A, Layout B, Layout C with 47 verified transactions):

```powershell
# Seed demonstration statements and transactions
& .venv\Scripts\python.exe scripts\seed_demo_data.py
```

Expected output:
```text
--- Initializing OSCAR Demonstration Dataset ---
Ingesting 'synthetic_statement_layout_a.pdf'...
  Successfully extracted 15 transactions.
  Reconciliation: RECONCILED, Variance: INR 0.00
Ingesting 'synthetic_statement_layout_b.pdf'...
  Successfully extracted 12 transactions.
  Reconciliation: RECONCILED, Variance: INR 0.00
Ingesting 'synthetic_statement_layout_c.pdf'...
  Successfully extracted 20 transactions.
  Reconciliation: RECONCILED, Variance: INR 0.00

--- Seeding Complete: 3 Statements, 47 Transactions in Database ---
```

---

## 4. Running the Development Servers

OSCAR runs as a decoupled local client-server workstation:

### Terminal 1: Backend Server (FastAPI on Port 8000)

```powershell
& .venv\Scripts\python.exe -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000 --reload
```
- API Base URL: `http://localhost:8000`
- Interactive OpenAPI Docs: `http://localhost:8000/docs`
- Health Endpoint: `http://localhost:8000/api/v1/health`

### Terminal 2: Frontend Server (Vite + React on Port 5173)

```powershell
npm --prefix frontend run dev
```
- Application UI: `http://localhost:5173`

---

## 5. Verification & Test Execution

### 5.1 Run Full Backend Pytest Suite (36/36 Tests)

```powershell
& .venv\Scripts\python.exe -m pytest -v
```

All 36 tests across analytics, classification, financial engineering, multi-layout OCR, statement details, and vertical slice should pass in approximately 14 seconds.

### 5.2 Run Frontend TypeScript Check & Production Build

```powershell
npm --prefix frontend run build
```

This invokes `tsc -b && vite build` and confirms zero TypeScript compilation or linting errors.

### 5.3 Run Machine Learning Leakage Audit & Retraining

```powershell
& .venv\Scripts\python.exe scripts\evaluate_ml_and_leakage.py
```

### 5.4 Run Extraction & Ground Truth Benchmark

```powershell
& .venv\Scripts\python.exe scripts\evaluate_extraction.py
```

---

## 6. Project Directory Layout

```text
OSCAR/
├── backend/
│   ├── app/
│   │   ├── api/v1/endpoints/       # REST endpoints (statements, analytics, reviews, etc.)
│   │   ├── bank_parsers/           # Multi-layout table parsers (A, B, C)
│   │   ├── classification/         # Non-LLM hybrid engine (Rules + TF-IDF LogReg)
│   │   ├── core/                   # Application settings & logging
│   │   ├── database/               # SQLAlchemy models and session factory
│   │   ├── exports/                # Multi-tab Excel & sanitized CSV generators
│   │   ├── extraction/             # PyMuPDF, pdfplumber & OpenCV/Tesseract OCR
│   │   ├── schemas/                # Pydantic request & response schemas
│   │   ├── services/               # Statement processor, reconciliation, analytics
│   │   └── validation/             # Precision normalizers & extraction benchmarks
│   ├── ml_artifacts/               # Serialized model.joblib, metadata, metrics.json
│   ├── oscar.db                    # Local SQLite database in WAL mode
│   └── tests/                      # Pytest suite (36 tests)
├── frontend/
│   ├── src/
│   │   ├── components/             # Reusable UI components & Layouts (Navbar, Sidebar)
│   │   ├── context/                # ThemeContext (Dark & Light theme state)
│   │   ├── pages/                  # All 12 workstation modules
│   │   ├── services/               # Typed Axios API client
│   │   └── types/                  # TypeScript domain models
│   ├── index.html                  # HTML entry point
│   └── tailwind.config.js          # Midnight-navy & champagne-gold palette configuration
├── docs/                           # Technical documentation & benchmarks
├── sample_data/                    # Synthetic bank statement PDFs & Ground Truth JSONs
├── scripts/                        # Seeding, screenshot capture, and evaluation scripts
└── README.md                       # Master product documentation
```
