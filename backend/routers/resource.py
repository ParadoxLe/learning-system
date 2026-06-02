from typing import Optional
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.schemas.resource import (
    ResourceGenerateRequest,
    ResourceGenerateResponse,
    ResourceItem,
    ResourceListResponse,
)
from backend.services.resource_service import ResourceService

router = APIRouter(prefix="/api/resources", tags=["resources"])
service = ResourceService()


class CompleteResourceRequest(BaseModel):
    student_id: int
    resource_id: int


@router.post("/generate", response_model=ResourceGenerateResponse)
def generate_resources(req: ResourceGenerateRequest, db: Session = Depends(get_db)):
    """触发资源生成 — 调用多个智能体协作生成个性化学习资源。"""
    results = service.generate_resources(
        db=db,
        student_id=req.student_id,
        resource_types=req.resource_types,
        course_topic=req.course_topic,
        tech_stack=req.tech_stack,
        difficulty=req.difficulty,
    )
    return ResourceGenerateResponse(
        student_id=req.student_id,
        resources=[ResourceItem(**r) for r in results],
    )


@router.get("/{student_id}", response_model=ResourceListResponse)
def list_resources(student_id: int, resource_type: Optional[str] = None, db: Session = Depends(get_db)):
    """获取学生的所有资源列表，可按类型筛选。"""
    results = service.get_resources(db, student_id, resource_type)
    return ResourceListResponse(
        student_id=student_id,
        resources=[ResourceItem(**r) for r in results],
    )


@router.delete("/{resource_id}")
def delete_resource(resource_id: int, student_id: int, db: Session = Depends(get_db)):
    """删除指定资源。"""
    ok = service.delete_resource(db, student_id, resource_id)
    return {"ok": ok}


@router.post("/complete")
def complete_resource(req: CompleteResourceRequest, db: Session = Depends(get_db)):
    """标记资源为已完成，更新用户画像。"""
    result = service.complete_resource(db, req.student_id, req.resource_id)
    return result
