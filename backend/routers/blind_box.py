from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.services.blind_box_service import BlindBoxService

router = APIRouter(prefix="/api", tags=["blind-box"])
service = BlindBoxService()


@router.get("/blind-box/daily")
def get_daily_blind_box(
    student_id: int = Query(...),
    db: Session = Depends(get_db),
):
    """返回今日知识盲盒卡片（同一天同一学生返回相同内容）。"""
    return service.get_daily_card(db, student_id)
