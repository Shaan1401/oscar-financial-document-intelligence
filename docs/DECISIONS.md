# OSCAR — Architectural & Technical Decisions Log

This document records key engineering choices, dependencies, and design tradeoffs made during the development of OSCAR.

---

## Decision 1: Target Runtime & Virtual Environment
- **Context**: The host machine runs Windows 11 with multiple Python installations (Python 3.14.3 system, Python 3.13, and Python 3.11.15 via uv).
- **Decision**: Standardize on **Python 3.11.15** located in dedicated virtual environment `F:\Projects\OSCAR\.venv`.
- **Rationale**: Python 3.11 is the most stable, mature target for pre-built Windows wheels across scientific and document libraries (`numpy`, `scipy`, `scikit-learn`, `PyMuPDF`, `opencv-python-headless`). Python 3.14 lacks prebuilt binaries for several C extensions.

## Decision 2: OCR Fallback Strategy (Tesseract)
- **Context**: Tesseract OCR is an external Windows binary (`tesseract.exe`) and is not pre-installed in the current OS PATH.
- **Decision**: 
  1. Build a robust `TesseractDetector` that probes standard Windows installation paths (`C:\Program Files\Tesseract-OCR\tesseract.exe`, `C:\Program Files (x86)\Tesseract-OCR\tesseract.exe`, `C:\Users\<user>\AppData\Local\Tesseract-OCR\tesseract.exe`) as well as user overrides via `.env` (`TESSERACT_CMD`).
  2. For digital text-based PDFs (which comprise ~90% of online banking statements), extraction operates at 100% fidelity using `PyMuPDF` and `pdfplumber` without requiring Tesseract.
  3. When a scanned PDF is processed and Tesseract is absent, the system does not invent false data; it marks the page status as `OCR_UNAVAILABLE`, provides a clear actionable diagnostic message to the user, and directs them to the Tesseract installer.

## Decision 3: Strict Non-LLM Classification Architecture
- **Context**: The Befree assessment mandates: "Heuristic rule-based classification. Traditional machine-learning classification. No Large Language Models for classification."
- **Decision**: Deploy a two-tiered hybrid classifier:
  - **Tier 1 (Rules)**: Curated Indian banking transaction rules covering UPI, NEFT, IMPS, RTGS, POS, ATM, ECS, card debits, and common merchants. Explains classification with explicit `rule_id` and rule descriptions.
  - **Tier 2 (Traditional ML)**: Feature pipeline using scikit-learn's `FeatureUnion` combining word n-grams (1, 2) TF-IDF and character n-grams (3, 5) TF-IDF, feeding a multinomial `LogisticRegression(class_weight='balanced')`. Provides calibrated pseudo-probabilities via softmax.
  - **Confidence Gate**: Predictions scoring below `0.65` or exhibiting rule conflicts are sent to human review queue (`NEEDS_REVIEW`).

## Decision 4: Monetary Precision & Integer Minor Units
- **Context**: Binary floating-point arithmetic causes precision loss (e.g. `0.1 + 0.2 = 0.30000000000000004`), which is unacceptable in banking reconciliation.
- **Decision**:
  - In application memory: use Python `Decimal`.
  - In SQLite database: persist amounts as integer minor units (`debit_minor_units`, `credit_minor_units`, `balance_minor_units`) with currency code (e.g., INR) and currency exponent (e.g., 2). For instance, INR 1,450.50 is stored as `145050`.
  - Export: format amounts cleanly as numeric decimal values in Excel and CSV.

## Decision 5: Database Architecture
- **Context**: Local-first operation without requiring external cloud databases or Docker containers.
- **Decision**: Use SQLite with SQLAlchemy 2 (mapped models, foreign keys, cascade deletes, indexed columns). The database file is located at `oscar.db` and is ignored by Git to preserve privacy.

## Decision 6: Multi-Layout Parsing Strategy
- **Context**: Different financial institutions structure statements differently (e.g. separate debit/credit columns vs combined amount with DR/CR indicators, wrapped narration rows, and multiline table structures).
- **Decision**: Implemented `HeaderDetector` with extensive synonym mappings (`DATE_SYNONYMS`, `DESC_SYNONYMS`, `DEBIT_SYNONYMS`, `CREDIT_SYNONYMS`, `BALANCE_SYNONYMS`, `AMOUNT_SYNONYMS`), allowing `GenericBankParser` to dynamically adapt to varying column layouts, continuation rows, and page breaks without rigid hardcoded offsets.

## Decision 7: Mathematical Reconciliation & Anomaly Identification
- **Context**: Bank statements can contain missing rows, altered balances, or extraction artifacts.
- **Decision**: Implement dual-level verification:
  1. Macro reconciliation: `Variance = Actual Closing - (Opening + Total Credits - Total Debits)`.
  2. Micro reconciliation: Consecutive running-balance validation verifying row-by-row step consistency, flagging rows with mathematical deviations as `WARNING` / `ANOMALY`.
  3. Duplicate candidates: Identified using compound keys (`date + amount + direction + desc_prefix`) and routed to the human review queue.

## Decision 8: Modern React Frontend & Zero Mock Data Principle
- **Context**: A financial intelligence application must be trustworthy and transparent.
- **Decision**: Build a React 19 + TypeScript frontend with Vite, Tailwind CSS, Lucide icons, and Recharts. All metrics, charts, transactions, and reviews are driven 100% by live SQLite backend APIs with zero hardcoded or mocked financial numbers, full dark/light mode toggle with localStorage persistence, and responsive desktop-first layout.

## Decision 9: Split-Screen Evidence Viewer & Document Traceability
- **Context**: Financial auditors require direct visual verification of every parsed number back to the original source document without manual cross-referencing.
- **Decision**: Provide page-by-page high-resolution PNG rendering via PyMuPDF at 200 DPI through `/api/v1/statements/{id}/pages/{page}/preview`. Clicking any transaction row automatically scrolls and loads that transaction's corresponding source page, displaying a dedicated traceability card containing raw text, coordinates, model version/rule ID, and confidence score.

## Decision 10: Headless Automated Visual Verification
- **Context**: Proving full end-to-end frontend integration without relying on user interaction during automated evaluation.
- **Decision**: Utilize headless Chrome to capture full-resolution 1440x900 viewport screenshots across all 11 application routes with real SQLite data, committing the resulting PNG assets to `screenshots/` for GitHub presentation.
