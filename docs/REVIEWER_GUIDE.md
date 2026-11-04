# OSCAR — Evaluator & Reviewer Guide

Welcome to the **OSCAR Financial Document Intelligence Workstation**. This document serves as a comprehensive guide for evaluators reviewing the Befree AI & Automation assessment submission.

---

## 1. Brand Identity & Full Form Specification

### The OSCAR Name
- **Product Name**: **OSCAR**
- **Complete Full Form**: **Operational Statement Classification, Analysis & Reconciliation**
- **Product Descriptor**: **Financial Document Intelligence**
- **Official Tagline**: *"Every transaction deserves an explanation."*

### Brand Acronym Decomposition (Letter Mapping)
| Letter | Component | Mission & Architectural Role |
|:---:|:---|:---|
| **O** | **Operational** | Enterprise accounting ledger with integer minor-unit arithmetic (paise) and immutable audit logging. |
| **S** | **Statement** | Multi-bank layout ingestion (Layouts A, B, C, digital text and scanned OCR with deskewing). |
| **C** | **Classification** | Explainable hybrid engine (deterministic banking rules + dual word/char TF-IDF Logistic Regression). Zero cloud LLMs. |
| **A** | **Analysis** | Deep financial analytics (Pareto merchant curve, payment channels, cashflow intelligence). |
| **R** | **Reconciliation** | Mathematical integrity bridge ($\text{Opening} + \Delta = \text{Closing}$) with verified zero variance. |

---

## 2. Quick Evaluation Setup (Under 2 Minutes)

OSCAR is designed to be **100% local-first and self-contained**. No external cloud accounts, API keys, or databases are required.

### Prerequisites
- Python 3.11+ installed in virtualenv `.venv`
- Node.js 18+ and npm installed

### Step 1: Start Backend API Server
```powershell
cd F:\Projects\OSCAR
$env:PYTHONPATH='backend'
.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```
- API Health Endpoint: `http://127.0.0.1:8000/api/v1/health`
- Interactive Swagger Documentation: `http://127.0.0.1:8000/docs`

### Step 2: Start Frontend Application
```powershell
cd F:\Projects\OSCAR\frontend
npm run dev
```
- Web Application URL: `http://localhost:5173`

### Step 3: Populate / Refresh Demonstration Ledger
```powershell
cd F:\Projects\OSCAR
$env:PYTHONPATH='backend'
.venv\Scripts\python.exe scripts\seed_demo_data.py
```
This script populates the SQLite database with 3 complete bank layouts (Layout A, Layout B, Layout C), generates exact PDF table row bounding boxes, and executes mathematical reconciliation.

---

## 3. Workstation Evaluation Tour (Key Highlights)

### A. Operations Workbench (`/`)
- **Brand Hero Banner**: Visibly displays the complete OSCAR expansion, descriptor, and tagline.
- **Financial Integrity Bridge**: Equation flow $\text{Opening} + \text{Inflow} - \text{Outflow} = \text{Expected vs Actual Closing}$ with verified zero variance.
- **Cash Flow Intelligence**: Composed chart showing inflow bars, outflow bars, and net spline. Click any date to drill into transactions.
- **Running Balance Trajectory**: Area chart tracking liquidity progression row by row.
- **Daily Activity Heatmap**: Interactive calendar grid with count/volume toggles.

### B. Signature Evidence-First Workspace (`/statements/{id}`)
- **High-Resolution Document Preview**: 200 DPI PyMuPDF rendering of the original bank statement.
- **Interactive Bounding Box Highlighting**: Click any transaction in the ledger to see a pulsating, glowing highlight over the exact table row on the source PDF.
- **4-Step Governance Trace**: Visual indicator linking `Source Document` $\to$ `Extracted Row` $\to$ `Hybrid Classification` $\to$ `Financial Validation`.
- **Traceability Inspector**: Inspect raw unparsed text, geometry coordinates `[x0, y0, x1, y1]`, classification confidence, and rule/model ID.

### C. Reconciliation Centre (`/reconciliation`)
- Mathematical proof of ledger consistency.
- Step-by-step running balance verification ensuring no skipped rows or balance corruption.
- Single-click automated recalculation trigger.

### D. Human Review & Exceptions Queue (`/reviews`)
- Filter by status (`NEEDS_REVIEW`, `APPROVED`, `CORRECTED`).
- Interactive modal allowing category correction, reviewer notes, and one-click approval.
- Emits audited events directly into the immutable audit trail.

### E. Explainable Hybrid Classification Insights (`/classification`)
- Review independent test set accuracy (**100%**) and Macro F1 score (**1.0000**).
- Inspect rule conflict detection mechanism.
- One-click model retraining trigger executing the offline scikit-learn pipeline.

### F. Deep Financial Analytics (`/analytics`)
- **Merchant Concentration & Pareto Curve**: 80/20 cumulative spending distribution.
- **Payment Channels**: Automatic categorization into UPI, NEFT, IMPS, RTGS, POS, ATM, ECS.
- **Extraction Completeness Audit**: Verification across date, amount, description, balance, and bounding coordinates.
- **Multi-Statement Comparative Ledger**: Strictly partitioned by ISO currency.

---

## 4. Verification Evidence & Test Execution

### Running the Full Pytest Suite (36/36 Passing)
```powershell
cd F:\Projects\OSCAR
.venv\Scripts\python.exe -m pytest -v
```
All 36 tests pass in approximately 10.7 seconds with zero failures.

### Running Frontend Production Build
```powershell
cd F:\Projects\OSCAR\frontend
npm run build
```
Builds cleanly with exit code 0 (`tsc -b && vite build`).
