from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import engine, get_db
from app.schemas.contracts import AskAIRequest, AskAIResponse
from app.services.ai_assistant import answer_question
router = APIRouter(tags=["ai"])
@router.post("/ask-ai", response_model=AskAIResponse)
def ask_ai(payload: AskAIRequest, db: Session = Depends(get_db)):
    return answer_question(db, engine, payload.question)
