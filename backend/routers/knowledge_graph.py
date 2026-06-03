"""Knowledge Graph router — serves graph data built from student profile."""

import logging
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.services.knowledge_graph_service import build_knowledge_graph
from backend.services.profile_service import ProfileService

router = APIRouter(prefix="/api/knowledge-graph", tags=["knowledge-graph"])
profile_service = ProfileService()
logger = logging.getLogger(__name__)


@router.get("/{student_id}")
def get_knowledge_graph(student_id: int, db: Session = Depends(get_db)):
    """Build and return a knowledge graph from the student's learning profile."""
    result = profile_service.get_profile(db, student_id)
    if not result or not result.get("profile"):
        return {"nodes": [], "edges": [], "categories": [], "summary": {}}

    profile = result["profile"]
    if isinstance(profile, str):
        import json
        try:
            profile = json.loads(profile)
        except json.JSONDecodeError:
            profile = {}

    try:
        graph = build_knowledge_graph(profile)
        graph["student_id"] = student_id
        graph["profile_version"] = result.get("version", 0)
        return graph
    except Exception as e:
        logger.exception(f"Failed to build knowledge graph for student {student_id}")
        raise HTTPException(status_code=500, detail=f"知识图谱构建失败：{str(e)}")
