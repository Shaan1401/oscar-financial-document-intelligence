from fastapi import APIRouter
from app.api.v1.endpoints import health, statements, transactions, exports

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(health.router)
api_router.include_router(statements.router)
api_router.include_router(transactions.router)
api_router.include_router(exports.router)
