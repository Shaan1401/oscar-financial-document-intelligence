# OSCAR — Test Results & Verification Log

This document records the actual commands executed, outcomes, test metrics, and verification steps.

---

## 1. Environment & Runtime Verification (Phase 0)

| Test ID | Item Tested | Command Executed | Outcome | Status |
|---|---|---|---|---|
| ENV-01 | Drive F: & Directory | `Get-PSDrive F; Test-Path 'F:\Projects'` | F: 60.4GB free; F:\Projects exists | **PASS** |
| ENV-02 | Python 3.11 Runtime | `& '...\cpython-3.11.15...\python.exe' --version` | Python 3.11.15 | **PASS** |
| ENV-03 | Virtualenv Creation | `uv venv --python 3.11 .venv` | `.venv` initialized with CPython 3.11.15 | **PASS** |
| ENV-04 | Backend Dependencies | `uv pip install -r backend\requirements.txt` | 56 packages resolved & installed cleanly | **PASS** |
| ENV-05 | Core Library Import | `python -c "import fastapi, fitz, ..."` | `ALL CORE LIBRARIES IMPORTED SUCCESSFULLY` | **PASS** |
| ENV-06 | Git Repository Setup | `git init; git status` | Initialized cleanly; `.venv` and caches excluded | **PASS** |

---

## 2. Core Working Vertical Slice (Phase 1)

**Execution Command**:  
`pytest backend/tests/test_vertical_slice.py -v`

| Test ID | Test Case | Target Tested | Result | Duration |
|---|---|---|---|---|
| VS-01 | `test_health_check` | `GET /api/v1/health` (app name, status, OCR detection) | **PASSED** | 0.05s |
| VS-02 | `test_pdf_validator_rejects_invalid_bytes` | PDF magic bytes validation (`%PDF-`) | **PASSED** | 0.01s |
| VS-03 | `test_pdf_validator_accepts_valid_pdf` | SHA-256 computation, page count, safe filename | **PASSED** | 0.08s |
| VS-04 | `test_text_and_table_extraction` | Bank name, holder, account number, masked number, IFSC | **PASSED** | 0.94s |
| VS-05 | `test_generic_bank_parser` | Separate debit/credit table extraction, running balance | **PASSED** | 0.42s |
| VS-06 | `test_statement_processing_vertical_slice` | End-to-end API upload, persistence, Excel & CSV export, PNG preview | **PASSED** | 1.85s |

**Summary**: 6 passed in 5.58s (100% pass rate).
