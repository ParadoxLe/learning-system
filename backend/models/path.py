import datetime
from sqlalchemy import String, Integer, DateTime, ForeignKey, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.database import Base


class LearningPath(Base):
    __tablename__ = "learning_paths"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"))
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    nodes_json: Mapped[str] = mapped_column(Text, default="[]")
    # nodes_json: [{"order": 1, "title": "...", "resource_ids": [1,2], "duration_min": 30, "status": "pending"}]
    status: Mapped[str] = mapped_column(String(20), default="active")
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, server_default=func.now()
    )

    student = relationship("Student", back_populates="paths")
