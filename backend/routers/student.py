from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from backend.database import get_db
from backend.models.student import Student
from backend.routers.auth import get_current_user

router = APIRouter(prefix="/api/students", tags=["students"])


class StudentCreate(BaseModel):
    name: str
    major: str = ""
    grade: str = ""


class StudentResponse(BaseModel):
    id: int
    name: str
    major: str
    grade: str


@router.get("/", response_model=list[StudentResponse])
def list_students(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    students = (
        db.query(Student)
        .filter(Student.user_id == current_user["user_id"])
        .order_by(Student.id)
        .all()
    )
    return [StudentResponse(id=s.id, name=s.name, major=s.major, grade=s.grade) for s in students]


@router.post("/", response_model=StudentResponse)
def create_student(
    req: StudentCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    student = Student(
        name=req.name, major=req.major, grade=req.grade,
        user_id=current_user["user_id"],
    )
    db.add(student)
    db.commit()
    db.refresh(student)
    return StudentResponse(id=student.id, name=student.name, major=student.major, grade=student.grade)
