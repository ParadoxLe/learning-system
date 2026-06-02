import json
import logging
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.schemas.profile import ProfileChatRequest, ProfileChatResponse, ProfileResponse
from backend.services.profile_service import ProfileService

router = APIRouter(prefix="/api/profile", tags=["profile"])
service = ProfileService()
logger = logging.getLogger(__name__)


@router.post("/chat", response_model=ProfileChatResponse)
def profile_chat(req: ProfileChatRequest, db: Session = Depends(get_db)):
    """对话式画像构建 — 发送消息，获取追问或完整画像。"""
    try:
        result = service.chat(db, req.student_id, req.message)
        return ProfileChatResponse(
            status=result["status"],
            message=result.get("message", ""),
            profile=result.get("profile"),
        )
    except Exception as e:
        logger.exception(f"Profile chat failed for student {req.student_id}")
        raise HTTPException(status_code=500, detail=f"画像构建失败：{str(e)}")


@router.post("/chat/stream")
def profile_chat_stream(req: ProfileChatRequest, db: Session = Depends(get_db)):
    """对话式画像构建（流式）— SSE 逐 token 返回，最后推送完整画像。"""
    def generate():
        try:
            for item in service.chat_stream(db, req.student_id, req.message):
                if isinstance(item, dict):
                    yield f"data: {json.dumps(item, ensure_ascii=False)}\n\n"
                else:
                    yield f"data: {json.dumps({'token': item}, ensure_ascii=False)}\n\n"
        except Exception as e:
            logger.exception(f"Profile chat stream failed for student {req.student_id}")
            yield f"data: {json.dumps({'error': str(e)}, ensure_ascii=False)}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")


@router.get("/{student_id}", response_model=ProfileResponse)
def get_profile(student_id: int, db: Session = Depends(get_db)):
    """获取学生的最新学习画像。"""
    result = service.get_profile(db, student_id)
    if result:
        return ProfileResponse(**result)
    return ProfileResponse(student_id=student_id, profile={}, version=0)


@router.post("/{student_id}/update")
def update_profile(student_id: int, new_info: dict, db: Session = Depends(get_db)):
    """用新信息更新已有画像（随学随新）。"""
    return service.update_profile(db, student_id, new_info.get("message", ""))
