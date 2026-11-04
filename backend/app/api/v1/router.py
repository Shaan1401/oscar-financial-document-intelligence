from fastapi import APIRouter
from app.api.v1.endpoints import (
    health, statements, transactions, exports,
    classification, reconciliation, reviews, analytics, audit
)

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(health.router)
api_router.include_router(statements.router)
api_router.include_router(transactions.router)
api_router.include_router(exports.router)
api_router.include_router(classification.router)
api_router.include_router(reconciliation.router)
api_router.include_router(reviews.router)
api_router.include_router(analytics.router)
api_router.include_router(audit.router)
