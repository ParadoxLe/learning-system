import json
from pydantic import BaseModel
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.schemas.path import PathGenerateRequest, PathGenerateResponse, PathListResponse
from backend.services.path_service import PathService

router = APIRouter(prefix="/api/learning-path", tags=["learning-path"])
service = PathService()


class CompleteNodeRequest(BaseModel):
    student_id: int
    path_id: int
    phase_idx: int
    node_order: int


@router.post("/generate", response_model=PathGenerateResponse)
def generate_path(req: PathGenerateRequest, db: Session = Depends(get_db)):
    """为学生生成个性化学习路径。"""
    result = service.generate_path(db, req.student_id, req.course_goal)
    return PathGenerateResponse(**result)


@router.post("/generate/stream")
def generate_path_stream(req: PathGenerateRequest, db: Session = Depends(get_db)):
    """流式生成学习路径。"""
    def generate():
        for item in service.generate_path_stream(db, req.student_id, req.course_goal):
            yield f"data: {json.dumps(item, ensure_ascii=False)}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")


@router.get("/{student_id}", response_model=PathListResponse)
def list_paths(student_id: int, db: Session = Depends(get_db)):
    """获取学生的所有学习路径。"""
    paths = service.get_paths(db, student_id)
    return PathListResponse(student_id=student_id, paths=paths)


@router.post("/complete-node")
def complete_node(req: CompleteNodeRequest, db: Session = Depends(get_db)):
    """标记学习路径节点为已完成，并自动更新用户画像。"""
    result = service.complete_node(
        db, req.student_id, req.path_id, req.phase_idx, req.node_order
    )
    return result


@router.delete("/{path_id}")
def delete_path(path_id: int, student_id: int, db: Session = Depends(get_db)):
    """删除指定学习路径。"""
    ok = service.delete_path(db, student_id, path_id)
    return {"ok": ok}
