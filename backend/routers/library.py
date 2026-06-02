from typing import Optional
from fastapi import APIRouter, Depends, UploadFile, File, Form, Header, HTTPException, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from backend.database import get_db
from backend.services.library_service import LibraryService
from backend.services.auth_service import decode_token, AuthService

router = APIRouter(prefix="/api", tags=["library"])
service = LibraryService()
auth_service = AuthService()


def _check_auth(
    authorization: Optional[str] = Header(None),
    token: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """Auth from Header (API calls) or query param (iframe src)."""
    raw = authorization or (f"Bearer {token}" if token else None)
    if not raw:
        raise HTTPException(status_code=401, detail="请先登录")
    tok = raw.removeprefix("Bearer ").strip()
    payload = decode_token(tok)
    if not payload:
        raise HTTPException(status_code=401, detail="登录已过期，请重新登录")
    user = auth_service.get_user(db, payload["user_id"])
    if not user:
        raise HTTPException(status_code=401, detail="用户不存在")
    return {"user_id": user.id, "username": user.username}


class ExplainRequest(BaseModel):
    student_id: int
    file_id: int
    selected_text: str


@router.post("/library/upload")
async def upload_pdf(
    file: UploadFile = File(...),
    student_id: int = Form(...),
    db: Session = Depends(get_db),
    _auth: dict = Depends(_check_auth),
):
    """Upload a PDF file, extract text, save to library."""
    content = await file.read()
    result = service.upload_pdf(db, student_id, file.filename, content)
    return result


@router.get("/library/")
def list_files(
    student_id: int,
    db: Session = Depends(get_db),
    _auth: dict = Depends(_check_auth),
):
    """List all uploaded files for a student."""
    return {"files": service.list_files(db, student_id)}


@router.get("/library/{file_id}")
def get_file(
    file_id: int,
    student_id: int,
    db: Session = Depends(get_db),
    _auth: dict = Depends(_check_auth),
):
    """Get file info including extracted text."""
    result = service.get_file(db, student_id, file_id)
    if not result:
        return {"error": "文件不存在"}
    return result


@router.delete("/library/{file_id}")
def delete_file(
    file_id: int,
    student_id: int,
    db: Session = Depends(get_db),
    _auth: dict = Depends(_check_auth),
):
    """Delete an uploaded file."""
    ok = service.delete_file(db, student_id, file_id)
    return {"ok": ok}


@router.post("/library/explain")
def explain_text(
    req: ExplainRequest,
    db: Session = Depends(get_db),
    _auth: dict = Depends(_check_auth),
):
    """AI explain selected text from a PDF."""
    file_info = service.get_file(db, req.student_id, req.file_id)
    context = file_info.get("content_text", "") if file_info else ""
    explanation = service.explain_text(req.selected_text, context)
    return {"explanation": explanation}


@router.get("/library/{file_id}/pdf")
def serve_pdf(
    file_id: int,
    student_id: int,
    db: Session = Depends(get_db),
    _auth: dict = Depends(_check_auth),
):
    """Serve the original PDF file for in-browser viewing."""
    result = service.get_file(db, student_id, file_id)
    if not result:
        return {"error": "文件不存在"}
    return FileResponse(result["file_path"], media_type="application/pdf")
