from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.database import get_db
from app.modules.proposal.service import generate_proposal

router = APIRouter(prefix="/api/v1/proposal", tags=["proposal"])


class ProposalRequest(BaseModel):
    company_name: str
    industry: str
    budget: float
    requirements: str
    preferences: list[str] = []


@router.post("/generate")
def generate(req: ProposalRequest, db: Session = Depends(get_db)):
    try:
        return generate_proposal(
            db, req.company_name, req.industry, req.budget,
            req.requirements, req.preferences,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
