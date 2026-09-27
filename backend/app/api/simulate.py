from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import engine, get_db
from app.schemas.contracts import SimulationRequest, SimulationResponse
from app.services.simulation import run_simulation
router = APIRouter(tags=["simulation"])
@router.post("/simulate", response_model=SimulationResponse)
def simulate(payload: SimulationRequest, db: Session = Depends(get_db)):
    return run_simulation(db, engine, payload.hazard, payload.increase_pct)
