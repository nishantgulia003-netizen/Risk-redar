from fastapi import APIRouter
from app.schemas.contracts import HealthResponse
router = APIRouter(tags=["system"])
@router.get("/health", response_model=HealthResponse)
def health() -> dict[str, str]:
    return {"status": "ok", "service": "riskradar-api"}
