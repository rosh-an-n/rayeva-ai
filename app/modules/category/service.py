import json
from sqlalchemy.orm import Session
from app.core.ai_client import call_gemini
from app.core.logger import log_ai_call
from app.models import Product
from app.modules.category.prompts import SYSTEM_PROMPT, build_category_prompt


def generate_category(db: Session, product_name: str, product_description: str) -> dict:
    prompt = build_category_prompt(product_name, product_description)

    try:
        result = call_gemini(prompt, system_instruction=SYSTEM_PROMPT)

        log_ai_call(db, "category", prompt, json.dumps(result))

        product = Product(
            name=product_name,
            description=product_description,
            category=result.get("primary_category"),
            sub_category=result.get("sub_category"),
            seo_tags=json.dumps(result.get("seo_tags", [])),
            sustainability_filters=json.dumps(result.get("sustainability_filters", [])),
            confidence_score=result.get("confidence_score", 0.0),
        )
        db.add(product)
        db.commit()
        db.refresh(product)

        return {
            "product_name": product_name,
            "primary_category": result.get("primary_category"),
            "sub_category": result.get("sub_category"),
            "seo_tags": result.get("seo_tags", []),
            "sustainability_filters": result.get("sustainability_filters", []),
            "confidence_score": result.get("confidence_score", 0.0),
            "stored_id": product.id,
        }
    except Exception as e:
        log_ai_call(db, "category", prompt, "", success=False, error_message=str(e))
        raise
