import os

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import SQLAlchemyError

from app.api import ai, health, population, relocation, reports, responder, risk, routes, shelters, simulate

app = FastAPI(title="RiskRadar API", version="0.1.0", description="Disaster-management decision-support API")
cors_origins = [origin.strip() for origin in os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:5173").split(",") if origin.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(SQLAlchemyError)
async def database_unavailable(_: Request, __: SQLAlchemyError) -> JSONResponse:
    """Avoid exposing database internals when PostGIS is unavailable."""
    return JSONResponse(status_code=503, content={"detail": "Database temporarily unavailable. Please retry shortly."})

for router in (health.router, risk.router, population.router, shelters.router, routes.router, relocation.router, simulate.router, reports.router, responder.router, ai.router):
    app.include_router(router)
