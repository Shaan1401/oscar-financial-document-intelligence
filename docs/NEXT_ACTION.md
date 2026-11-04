# OSCAR — Next Actions & Handoff Guide

## Status Overview
All agreed core features across Phases 0 through 7 have been fully implemented, integrated, and verified against the comprehensive project specification.

- **Automated Tests**: 25/25 passing in pytest (`test_vertical_slice.py`, `test_multi_layout_and_ocr.py`, `test_classification.py`, `test_financial_engineering.py`).
- **Frontend**: 12 pages implemented in React 19 + TypeScript + Tailwind CSS; builds cleanly (`tsc -b && vite build` exits with code 0).
- **Screenshots**: 11 full-resolution screenshots captured in `screenshots/`.
- **Database & Seeding**: Automated script `scripts/seed_demo_data.py` available to populate and reconcile all demonstration layouts.
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
