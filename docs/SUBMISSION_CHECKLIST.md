# OSCAR — Submission & Requirements Checklist

| Requirement Category | Specific Specification | Status | Evidence / Verification Reference |
|---|---|:---:|---|
| **Brand Identity** | Complete full form visible inside application | **PASS** | Displayed in Dashboard Hero, Sidebar, and Settings About card |
| **Brand Identity** | Product name: OSCAR | **PASS** | Applied consistently throughout frontend, backend, and documentation |
| **Brand Identity** | Letter mapping: O-S-C-A-R decomposition | **PASS** | 5-card grid in Settings $\to$ About OSCAR, README.md, and Reviewer Guide |
| **Brand Identity** | Descriptor: Financial Document Intelligence | **PASS** | Visible in Navbar, Sidebar, Dashboard, Settings, README |
| **Brand Identity** | Tagline: "Every transaction deserves an explanation." | **PASS** | Prominently displayed in Sidebar footer, Dashboard, Settings, README |
| **Architecture** | Strict Non-LLM Classification | **PASS** | Rule engine + Word/Char TF-IDF Logistic Regression; zero cloud APIs |
| **Architecture** | Local-First & Zero Egress | **PASS** | 100% self-contained SQLite WAL database; zero external network calls |
| **Architecture** | Decimal Precision Arithmetic | **PASS** | Python Decimal + integer minor units (`paise`); zero float drift |
| **Extraction** | Multi-Layout Bank Ingestion | **PASS** | Layout A (separate DR/CR), Layout B (combined DR/CR), Layout C (wrapped) |
| **Extraction** | Scanned PDF & OCR Integration | **PASS** | PyMuPDF bitmap detection, OpenCV deskewing, Tesseract fallback |
| **Evidence** | PDF Document Preview | **PASS** | High-resolution 200 DPI PyMuPDF page rendering |
| **Evidence** | Synchronized Bounding Box Highlighting | **PASS** | Pulsating SVG/CSS highlight over exact row coordinates on source PDF |
| **Evidence** | 4-Step Traceability Inspector | **PASS** | Source Document $\to$ Extracted Row $\to$ Classification $\to$ Validation |
| **Reconciliation** | Mathematical Integrity Equation | **PASS** | $\text{Opening} + \text{Inflow} - \text{Outflow} = \text{Expected Closing vs Actual}$ |
| **Reconciliation** | Step-by-Step Running Balance | **PASS** | Row-by-row ledger balance consistency check |
| **Governance** | Human Review Queue | **PASS** | Status filtering, interactive correction modal, approval workflow |
| **Governance** | Immutable Audit Trail | **PASS** | Chronological log of uploads, classifications, reviews, exports |
| **Analytics** | Cash Flow Intelligence | **PASS** | Interactive dual-axis ComposedChart with drill-down |
| **Analytics** | Running Balance Trajectory | **PASS** | Liquidity AreaChart over sequence chronology |
| **Analytics** | Daily Activity Heatmap | **PASS** | 365-day calendar grid with Count/Volume toggles |
| **Analytics** | Merchant Pareto Concentration | **PASS** | 80/20 cumulative spending curve |
| **Analytics** | Payment Channel Breakdown | **PASS** | Automated categorization into UPI, NEFT, IMPS, RTGS, POS, ATM |
| **Analytics** | Extraction Completeness Audit | **PASS** | 100% field availability audit (dates, descriptions, amounts, bboxes) |
| **Analytics** | Multi-Statement Ledger | **PASS** | Strictly currency-partitioned comparative table |
| **Exports** | Multi-tab Excel (.xlsx) Export | **PASS** | openpyxl workbook with Transactions, Account, Reconciliation, Audit tabs |
| **Exports** | CSV Export | **PASS** | Standard CSV with formula injection protection |
| **UI/UX** | Dark and Light Theme Persistence | **PASS** | Instant toggle with local storage persistence |
| **Verification** | Backend Automated Tests | **PASS** | 36/36 tests passing in pytest (100% pass rate in ~14.4s) |
| **Verification** | Frontend TypeScript & Build | **PASS** | `tsc -b && vite build` passing with exit code 0 |
| **Artifacts** | High-Resolution Screenshots | **PASS** | 14 genuine screenshots in `screenshots/` and `docs/screenshots/` (Light & Dark modes) |
| **Reports** | Requirements Traceability | **PASS** | `docs/REQUIREMENTS_TRACEABILITY.md` (9 Befree requirements fully traced) |
| **Reports** | Extraction Evaluation Benchmark | **PASS** | `docs/EXTRACTION_EVALUATION_REPORT.md` (100% precision & recall across Layouts A, B, C) |
| **Reports** | ML Leakage Audit & Evaluation | **PASS** | `docs/ML_EVALUATION_REPORT.md` (0.00% leakage, 100% test accuracy, $T=0.65$ gating) |
