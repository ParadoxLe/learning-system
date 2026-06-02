"""REST API for iFlytek digital human control."""
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.services.digital_human_service import get_dh_service

router = APIRouter(prefix="/api/digital-human", tags=["digital-human"])


class SpeakRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=500)


class StreamResponse(BaseModel):
    stream_url: str
    stream_extend: Optional[dict] = None
    sid: Optional[str] = None
    server: Optional[str] = None
    room_id: Optional[str] = None
    ready: bool = True


@router.post("/start", response_model=StreamResponse)
def start_session():
    """Start a digital human session and return the video stream URL."""
    try:
        svc = get_dh_service()
        result = svc.start()
        return StreamResponse(
            stream_url=result["stream_url"],
            stream_extend=result.get("stream_extend"),
            sid=result.get("sid"),
            server=result.get("server"),
            room_id=result.get("room_id"),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"数字人启动失败：{e}")


@router.post("/speak")
def speak(req: SpeakRequest):
    """Make the digital human speak the given text."""
    svc = get_dh_service()
    if not svc.ready:
        raise HTTPException(status_code=400, detail="数字人尚未就绪，请先调用 /start。")
    try:
        svc.send_text(req.text)
        return {"ok": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"发送文本失败：{e}")


@router.post("/stop")
def stop_session():
    """Stop the digital human session."""
    get_dh_service().stop()
    return {"ok": True}
