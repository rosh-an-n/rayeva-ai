from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.database import get_db
from app.modules.category.service import generate_category

router = APIRouter(prefix="/api/v1/category", tags=["category"])


class CategoryRequest(BaseModel):
    product_name: str
    product_description: str


@router.post("/generate")
def generate(req: CategoryRequest, db: Session = Depends(get_db)):
    try:
        return generate_category(db, req.product_name, req.product_description)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
