import datetime
from sqlalchemy import String, DateTime, func, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.database import Base


class Student(Base):
    __tablename__ = "students"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    major: Mapped[str] = mapped_column(String(200), default="")
    grade: Mapped[str] = mapped_column(String(50), default="")
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, server_default=func.now()
    )

    user = relationship("User", back_populates="students")
    profile = relationship("LearningProfile", back_populates="student", uselist=False)
    resources = relationship("LearningResource", back_populates="student")
    paths = relationship("LearningPath", back_populates="student")
    plans = relationship("StudyPlan", back_populates="student")
