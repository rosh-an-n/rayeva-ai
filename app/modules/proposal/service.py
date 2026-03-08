import json
from sqlalchemy.orm import Session
from app.core.ai_client import call_gemini
from app.core.logger import log_ai_call
from app.models import Proposal
from app.modules.proposal.prompts import SYSTEM_PROMPT, build_proposal_prompt


def generate_proposal(
    db: Session,
    company_name: str,
    industry: str,
    budget: float,
    requirements: str,
    preferences: list[str],
) -> dict:
    prompt = build_proposal_prompt(company_name, industry, budget, requirements, preferences)

    try:
        result = call_gemini(prompt, system_instruction=SYSTEM_PROMPT)

        log_ai_call(db, "proposal", prompt, json.dumps(result))

        proposal = Proposal(
            company_name=company_name,
            industry=industry,
            budget=budget,
            generated_proposal=json.dumps(result),
        )
        db.add(proposal)
        db.commit()
        db.refresh(proposal)

        result["stored_id"] = proposal.id
        return result
    except Exception as e:
        log_ai_call(db, "proposal", prompt, "", success=False, error_message=str(e))
        raise
