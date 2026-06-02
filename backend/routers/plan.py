from typing import Optional
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.services.plan_service import PlanService

router = APIRouter(prefix="/api/plans", tags=["study-plans"])
service = PlanService()


class AddPlanRequest(BaseModel):
    student_id: int
    plan_date: str
    title: str
    description: str = ""


class UpdatePlanRequest(BaseModel):
    student_id: int
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None


@router.get("/{student_id}")
def list_plans(student_id: int, year: int, month: int, db: Session = Depends(get_db)):
    """Get all plans for a student in a month."""
    plans = service.get_plans(db, student_id, year, month)
    dates = service.get_plan_dates(db, student_id, year, month)
    return {"plans": plans, "dates_with_plans": dates}


@router.post("/")
def add_plan(req: AddPlanRequest, db: Session = Depends(get_db)):
    """Add a new study plan."""
    return service.add_plan(db, req.student_id, req.plan_date, req.title, req.description)


@router.put("/{plan_id}")
def update_plan(plan_id: int, req: UpdatePlanRequest, db: Session = Depends(get_db)):
    """Update or toggle a study plan."""
    return service.update_plan(db, req.student_id, plan_id, req.title, req.description, req.completed)


@router.delete("/{plan_id}")
def delete_plan(plan_id: int, student_id: int, db: Session = Depends(get_db)):
    """Delete a study plan."""
    ok = service.delete_plan(db, student_id, plan_id)
    return {"ok": ok}
