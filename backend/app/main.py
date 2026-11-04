from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.errors import OscarException
from app.database.session import init_db, SessionLocal
from app.database.init_categories import seed_categories
from app.api.v1.router import api_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: initialize database tables and seed default categories
    init_db()
    db = SessionLocal()
    try:
        seed_categories(db)
    finally:
        db.close()
    yield
    # Shutdown

app = FastAPI(
    title=settings.APP_NAME,
    description=(
        f"{settings.APP_FULL_NAME}\n\n"
        f"**{settings.APP_DESCRIPTOR}** — *\"{settings.APP_TAGLINE}\"*\n\n"
        "A local-first platform for bank statement PDF extraction, "
        "non-LLM transaction classification, financial reconciliation, and Excel/CSV export."
    ),
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

# CORS configuration for local React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        settings.FRONTEND_ORIGIN,
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom exception handling
@app.exception_handler(OscarException)
async def oscar_exception_handler(request: Request, exc: OscarException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.message, "type": exc.__class__.__name__},
    )

# Include API v1 Router
app.include_router(api_router)

@app.get("/", tags=["Root"])
def root():
    return {
        "product": settings.APP_NAME,
        "name": settings.APP_FULL_NAME,
        "descriptor": settings.APP_DESCRIPTOR,
        "tagline": settings.APP_TAGLINE,
        "version": settings.APP_VERSION,
        "docs_url": "/docs",
        "health_check": "/api/v1/health",
    }
