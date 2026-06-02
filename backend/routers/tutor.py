import json
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from backend.database import get_db
from backend.services.tutor_service import TutorService

router = APIRouter(prefix="/api", tags=["tutor-assessment"])
service = TutorService()


class TutorAskRequest(BaseModel):
    student_id: int
    question: str
    context: str = ""


from typing import Optional


class TutorAskRequest(BaseModel):
    student_id: int
    question: str
    context: str = ""


class AssessmentRequest(BaseModel):
    student_id: int
    learning_data: Optional[dict] = None


class AssessmentResponse(BaseModel):
    student_id: int
    assessment: dict


@router.post("/tutor/ask")
def ask_tutor(req: TutorAskRequest, db: Session = Depends(get_db)):
    """智能辅导 — 学生提问，获取多模态解答。"""
    answer = service.answer_question(db, req.student_id, req.question, req.context)
    return {"student_id": req.student_id, "answer": answer}


@router.post("/tutor/ask/stream")
def ask_tutor_stream(req: TutorAskRequest, db: Session = Depends(get_db)):
    """智能辅导 — 流式输出解答。"""
    def generate():
        for token in service.answer_question_stream(db, req.student_id, req.question, req.context):
            yield f"data: {json.dumps(token)}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")


@router.post("/assessment/evaluate", response_model=AssessmentResponse)
def evaluate_learning(req: AssessmentRequest, db: Session = Depends(get_db)):
    """学习评估 — 基于学生画像生成多维度评估报告（学习数据可选）。"""
    result = service.evaluate(db, req.student_id, req.learning_data or {})
    return AssessmentResponse(student_id=req.student_id, assessment=result)
