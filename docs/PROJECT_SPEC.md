# OSCAR — Product Specification
## Operational Statement Classification, Analysis & Reconciliation
### Financial Document Intelligence Platform

**Tagline**: *Every transaction deserves an explanation.*  
**Target Submission**: Befree AI & Automation Internship Assessment  
**Project Path**: `F:\Projects\OSCAR`  
**Repository Name**: `oscar-bank-statement-intelligence`

---

## 1. Executive Summary & Vision

OSCAR is a local-first, privacy-preserving financial document intelligence platform engineered for automated bank statement processing. It solves the critical bottleneck in accounting and financial automation: converting unstructured, multi-bank, multi-layout statement PDFs (both text-based and scanned) into auditable, reconciled, categorized financial data records with complete lineage back to the source document.

Crucially, OSCAR operates under a **Strict Non-LLM Requirement**: transaction categorization is powered entirely by a hybrid architecture combining a high-precision deterministic financial rule engine with traditional machine learning (character + word n-gram TF-IDF and Logistic Regression / LinearSVC). No data leaves the local workstation.

---

## 2. Core Functional Capabilities

### A. Input Handling & Document Management
- **Format Support**: Multi-bank PDFs (digital text-based, scanned/image-based, and mixed).
- **Validation**: Strict PDF header magic byte validation (`%PDF-`), SHA-256 deduplication, 20 MB size threshold.
- **Privacy & Storage**: Documents stored in isolated local storage (`backend/storage/statements`), never exposed publicly. Controlled lifecycle deletion.

### B. Extraction & Multi-Layout Parsing
- **Page-Level Detection**: Inspects character density and image blocks per page. Dispatches digital pages to direct text extraction and scanned pages to image preprocessing and OCR.
- **Account Metadata Extraction**: Context-aware regex and layout bounding boxes extract Bank Name, Account Holder Name, Account Number (with frontend masking), IFSC Code, Branch, and Statement Period.
- **Transaction Table Parsing**:
  - Recognizes standard debit/credit column layouts.
  - Recognizes combined amount layouts with DR/CR indicators.
  - Handles wrapped narration lines, multi-page continuation, varying date formats (`DD/MM/YYYY`, `YYYY-MM-DD`, `DD-Mon-YYYY`), thousands separators, and currency symbols.
- **Lineage**: Every transaction record tracks `statement_id`, `source_page`, `raw_description`, `extraction_method`, and row index.

### C. Financial Normalization & Integrity
- **Decimal Precision**: All arithmetic utilizes Python `Decimal`. Monetary values are persisted in integer minor units (e.g., paise for INR, cents for USD) with explicit currency code and exponent.
- **Zero Floating-Point Drift**: Strict avoidance of standard binary floating-point representation for balances or movements.

### D. Explainable Non-LLM Classification
- **Rule Engine**: Pattern matching (token, phrase, regex) across 20 canonical Indian banking categories (Salary & Income, Food & Dining, Utilities, Shopping, Transfers, ATM, Banking Charges, etc.). Detects conflicts and assigns explicit rule IDs and explanations.
- **Traditional ML Pipeline**: Dual TF-IDF vectorizer (word n-grams (1,2) + sub-word character n-grams (3,5)) paired with balanced Logistic Regression. Persisted via joblib.
- **Hybrid Orchestrator**: Rule engine takes precedence for high-precision matches; fallback to ML with confidence thresholding (default: 0.65). Uncertain predictions or conflicts are flagged for Human Review (`NEEDS_REVIEW`).

### E. Financial Reconciliation & Anomaly Engine
- **Reconciliation Equation**:
  $$\text{Expected Closing Balance} = \text{Opening Balance} + \sum \text{Credits} - \sum \text{Debits}$$
  $$\text{Variance} = \text{Actual Closing Balance} - \text{Expected Closing Balance}$$
- **Status Classification**: `RECONCILED` ($\text{Variance} = 0$), `MISMATCH`, `INSUFFICIENT_DATA`, `REVIEW_REQUIRED`.
- **Running Balance Validation**: Step-by-step verification across ordered transaction chronologies.
- **Anomaly Flags**: Potential duplicates (date + description + amount match), unusually large transactions (Z-score outlier), missing narration, and reversal detection.

### F. Human-in-the-Loop Review & Audit Trail
- **Review Queue**: Dedicated UI workflow to filter unclassified, low-confidence, or conflicting records. Allows human correction, approval, and reclassification.
- **Audit Logging**: Comprehensive, immutable timestamped audit log capturing file uploads, processing jobs, user corrections (storing old and new values), reconciliation runs, and exports.

### G. Professional Export
- **Excel (.xlsx)**: Multi-tab formatted workbook (Transactions, Account Summary, Category Breakdown, Reconciliation Summary, Audit Info) with auto-filters, frozen panes, numeric currency formats, and conditional formatting.
- **CSV (.csv)**: Clean UTF-8 CSV with all required extracted fields and assigned classification categories. Protected against CSV injection (formula sanitization).

---

## 3. System Architecture & Tech Stack

```
[ PDF Upload ]
      │
      ▼
[ File Validation & SHA-256 ] ──► [ Local Secure Storage ]
      │
      ▼
[ Page-by-Page Classifier ]
      ├── Text-dense ──► [ PyMuPDF / pdfplumber Text Extractor ]
      └── Image-dense ──► [ Image Preprocessing + Tesseract OCR ]
      │
      ▼
[ Layout Profile & Table Parser ] ──► [ Account & Metadata Extractor ]
      │
      ▼
[ Transaction Normalization (Decimal / Minor Units) ]
      │
      ▼
[ Hybrid Classification Engine ]
      ├── 1. Rule Engine (Regex, Narration Aliases)
      └── 2. ML Engine (Word/Char TF-IDF + Logistic Regression)
      │
      ▼
[ Confidence Assessment & Review Routing ]
      │
      ▼
[ Reconciliation & Running Balance Engine ]
      │
      ▼
[ SQLite 3 (SQLAlchemy 2 Core & ORM) ]
      │
      ▼
[ REST API (FastAPI) ] ◄──► [ Frontend (React 19 + TypeScript + Vite + Tailwind) ]
      │
      ▼
[ Multi-Sheet Excel & CSV Export ]
```

- **Backend**: Python 3.11, FastAPI, Pydantic v2, SQLAlchemy 2, SQLite3, PyMuPDF, pdfplumber, pytesseract, Pillow, OpenCV, scikit-learn, pandas, numpy, openpyxl, reportlab.
- **Frontend**: React 19, TypeScript, Vite, Tailwind CSS, Lucide React, Recharts.
- **Target Ports**: Backend `127.0.0.1:8000`, Frontend `localhost:5173`.
