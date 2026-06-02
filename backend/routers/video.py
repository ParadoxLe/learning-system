from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from backend.database import get_db
from backend.services.video_service import VideoService

router = APIRouter(prefix="/api/video", tags=["video"])
service = VideoService()


class GenerateVideoRequest(BaseModel):
    resource_id: int
    duration: int = 5


@router.post("/generate")
def generate_video(req: GenerateVideoRequest, db: Session = Depends(get_db)):
    """Trigger Seedance video generation from a video_script resource."""
    result = service.generate_video(db, req.resource_id)
    return result


@router.get("/status/{resource_id}")
def check_video_status(resource_id: int, db: Session = Depends(get_db)):
    """Check video generation status for a resource."""
    result = service.check_video_status(db, resource_id)
    return result
