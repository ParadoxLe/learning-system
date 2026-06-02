from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.services.rag_service import rag_service

router = APIRouter(prefix="/api/rag", tags=["rag"])


@router.post("/build-index")
def build_index(
    student_id: int = Query(...),
    db: Session = Depends(get_db),
):
    """为指定学生构建/重建向量索引（包含所有资源和上传文件）。"""
    result = rag_service.build_index(db, student_id)
    return {
        "student_id": student_id,
        "resources_chunks": result["resources_chunks"],
        "files_chunks": result["files_chunks"],
        "total_chunks": result["resources_chunks"] + result["files_chunks"],
    }


@router.get("/search")
def search_knowledge(
    student_id: int = Query(...),
    q: str = Query(..., min_length=1),
    n: int = Query(3, ge=1, le=10),
    db: Session = Depends(get_db),
):
    """搜索学生知识库中最相关的内容片段。"""
    results = rag_service.search(student_id, q, n)
    return {"student_id": student_id, "query": q, "results": results, "count": len(results)}


@router.delete("/index")
def delete_index(
    student_id: int = Query(...),
):
    """删除学生的向量索引。"""
    rag_service.delete_student_index(student_id)
    return {"student_id": student_id, "message": "索引已删除"}
