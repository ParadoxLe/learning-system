"""Quiz router — generates and grades practice quizzes for weak-point reinforcement."""

import json
import logging
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.agents.quiz_agent import QuizAgent
from backend.services.profile_service import ProfileService

router = APIRouter(prefix="/api/quiz", tags=["quiz"])
profile_service = ProfileService()
quiz_agent = QuizAgent()
logger = logging.getLogger(__name__)


class GenerateRequest(BaseModel):
    student_id: int
    count: int = 5


class SubmitRequest(BaseModel):
    student_id: int
    answers: dict  # {"1": "A", "2": "B", ...}
    questions: list  # the full questions array from the generate response


@router.post("/generate")
def generate_quiz(req: GenerateRequest, db: Session = Depends(get_db)):
    """Generate a quiz targeting the student's weak points."""
    result = profile_service.get_profile(db, req.student_id)
    if not result or not result.get("profile"):
        raise HTTPException(status_code=404, detail="请先完成学习画像构建")

    profile = result["profile"]
    if isinstance(profile, str):
        try:
            profile = json.loads(profile)
        except json.JSONDecodeError:
            profile = {}

    try:
        quiz = quiz_agent.generate(profile, req.count)
        return {"quiz": quiz, "student_id": req.student_id}
    except Exception as e:
        logger.exception(f"Quiz generation failed for student {req.student_id}")
        raise HTTPException(status_code=500, detail=f"题目生成失败：{str(e)}")


@router.post("/submit")
def submit_quiz(req: SubmitRequest):
    """Grade a submitted quiz and return score + feedback."""
    questions = req.questions
    answers = req.answers

    total = len(questions)
    correct_count = 0
    results = []

    for q in questions:
        qid = str(q.get("id", ""))
        user_ans = answers.get(qid, "")
        correct_ans = q.get("correct", "")
        is_correct = user_ans.upper() == correct_ans.upper()

        if is_correct:
            correct_count += 1

        results.append({
            "id": q.get("id"),
            "question": q.get("question"),
            "topic": q.get("topic", ""),
            "user_answer": user_ans,
            "correct_answer": correct_ans,
            "is_correct": is_correct,
            "explanation": q.get("explanation", ""),
        })

    score_pct = round(correct_count / total * 100) if total > 0 else 0

    return {
        "score": correct_count,
        "total": total,
        "score_pct": score_pct,
        "results": results,
    }
