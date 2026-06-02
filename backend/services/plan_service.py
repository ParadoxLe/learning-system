import datetime
from sqlalchemy.orm import Session
from backend.models.plan import StudyPlan


class PlanService:
    def get_plans(self, db: Session, student_id: int, year: int, month: int) -> list[dict]:
        """Get all plans for a student in a given month."""
        plans = (
            db.query(StudyPlan)
            .filter(
                StudyPlan.student_id == student_id,
                StudyPlan.plan_date >= datetime.date(year, month, 1),
                StudyPlan.plan_date < datetime.date(year, month + 1, 1) if month < 12
                else datetime.date(year + 1, 1, 1),
            )
            .order_by(StudyPlan.plan_date.asc(), StudyPlan.created_at.asc())
            .all()
        )
        return [self._to_dict(p) for p in plans]

    def get_plan_dates(self, db: Session, student_id: int, year: int, month: int) -> list[str]:
        """Get dates that have plans in a month (for calendar highlights)."""
        plans = (
            db.query(StudyPlan.plan_date)
            .filter(
                StudyPlan.student_id == student_id,
                StudyPlan.plan_date >= datetime.date(year, month, 1),
                StudyPlan.plan_date < datetime.date(year, month + 1, 1) if month < 12
                else datetime.date(year + 1, 1, 1),
            )
            .distinct()
            .all()
        )
        return [str(p[0]) for p in plans]

    def add_plan(self, db: Session, student_id: int, plan_date: str, title: str,
                 description: str = "") -> dict:
        """Add a new study plan."""
        plan = StudyPlan(
            student_id=student_id,
            plan_date=datetime.date.fromisoformat(plan_date),
            title=title,
            description=description,
        )
        db.add(plan)
        db.commit()
        db.refresh(plan)
        return self._to_dict(plan)

    def update_plan(self, db: Session, student_id: int, plan_id: int,
                    title: str = None, description: str = None, completed: bool = None) -> dict:
        """Update a study plan."""
        plan = (
            db.query(StudyPlan)
            .filter(StudyPlan.id == plan_id, StudyPlan.student_id == student_id)
            .first()
        )
        if not plan:
            return {"ok": False, "message": "计划不存在"}

        if title is not None:
            plan.title = title
        if description is not None:
            plan.description = description
        if completed is not None:
            plan.completed = completed

        db.commit()
        db.refresh(plan)
        return {"ok": True, "plan": self._to_dict(plan)}

    def delete_plan(self, db: Session, student_id: int, plan_id: int) -> bool:
        """Delete a study plan."""
        plan = (
            db.query(StudyPlan)
            .filter(StudyPlan.id == plan_id, StudyPlan.student_id == student_id)
            .first()
        )
        if not plan:
            return False
        db.delete(plan)
        db.commit()
        return True

    @staticmethod
    def _to_dict(plan: StudyPlan) -> dict:
        return {
            "id": plan.id,
            "student_id": plan.student_id,
            "plan_date": str(plan.plan_date),
            "title": plan.title,
            "description": plan.description,
            "completed": plan.completed,
            "created_at": str(plan.created_at),
        }
