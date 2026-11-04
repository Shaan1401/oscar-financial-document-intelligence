# OSCAR — Next Actions & Handoff Guide

## Status Overview
All agreed core features across Phases 0 through 7 have been fully implemented, enhanced, and verified against the comprehensive project specification and the Evidence-First Financial Intelligence requirements.

- **Automated Tests**: 36/36 passing in pytest (`test_vertical_slice.py`, `test_multi_layout_and_ocr.py`, `test_classification.py`, `test_financial_engineering.py`, `test_statement_details.py`, `test_analytics.py`).
- **Frontend**: 12 pages in React 19 + TypeScript + Tailwind CSS; production build passing (`tsc -b && vite build` exits with code 0).
- **Workbench & Evidence Viewer**: Evidence-First Workbench with Financial Integrity Bridge, Processing Journey, Cash Flow ComposedChart, Running Balance AreaChart, Spending Distribution, and Daily Heatmap. Interactive split-screen Evidence Viewer with exact PyMuPDF preview, table-row bounding-box highlight overlay, and deep Traceability & Evidence Inspector card.
- **Analytics API**: 8 specialized database-backed aggregation endpoints (running balance, activity heatmap, merchant Pareto concentration, payment channels, confidence bins, field completeness, currency-partitioned multi-statement comparison, and chronological category trends).
- **Screenshots**: 13 genuine screenshots captured in `screenshots/` covering all key views and light/dark modes.
- **Database & Seeding**: Automated script `scripts/seed_demo_data.py` available to populate, reprocess, and reconcile all demonstration layouts with exact bounding box geometry.
- **Documentation**: Comprehensive `README.md`, `docs/PROJECT_SPEC.md`, `docs/DECISIONS.md`, `docs/CURRENT_STATUS.md`, and `docs/TEST_RESULTS.md`.

---

## Instructions for Running the Demonstration

### 1. Backend Server
```powershell
cd F:\Projects\OSCAR
$env:PYTHONPATH='backend'
.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
Interactive Swagger API docs: `http://127.0.0.1:8000/docs`.

### 2. Frontend Development Server
```powershell
cd F:\Projects\OSCAR\frontend
npm run dev
```
Interactive UI: `http://localhost:5173`.

### 3. Running Automated Tests
```powershell
cd F:\Projects\OSCAR
.venv\Scripts\python.exe -m pytest -v
```

### 4. Reseeding Demonstration Statements
```powershell
cd F:\Projects\OSCAR
$env:PYTHONPATH='backend'
.venv\Scripts\python.exe scripts\seed_demo_data.py
```

---

## Future Roadmap & Extension Points (Post-Submission)

1. **Additional Bank Layout Profiles**:
   - Add specialized parsers in `backend/app/bank_parsers/` for regional banks with unusual multi-column formats.
2. **GPU-Accelerated Local OCR**:
   - If Windows OCR or EasyOCR is preferred over Tesseract, create an adapter implementing the same `extract_image_text_and_blocks` signature.
3. **Multi-User RBAC & Authentication**:
   - Add JWT-based user session authentication and reviewer roles to further partition the audit trail.
4. **Cloud Storage S3/GCS Connectors**:
   - For enterprise deployment outside local workstation environments, add an S3/GCS driver to `settings.STORAGE_DIR`.
