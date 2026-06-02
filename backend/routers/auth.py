from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.schemas.auth import RegisterRequest, LoginRequest, AuthResponse, UserInfo, CaptchaResponse, UpdatePasswordRequest, UpdateAvatarRequest
from backend.services.auth_service import AuthService, decode_token

router = APIRouter(prefix="/api/auth", tags=["auth"])
service = AuthService()


def get_current_user(authorization: str = Header(None), db: Session = Depends(get_db)) -> dict:
    """FastAPI dependency: extract and validate JWT token, return current user."""
    if not authorization:
        raise HTTPException(status_code=401, detail="请先登录")
    token = authorization.removeprefix("Bearer ").strip()
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="登录已过期，请重新登录")
    user = service.get_user(db, payload["user_id"])
    if not user:
        raise HTTPException(status_code=401, detail="用户不存在")
    return {"user_id": user.id, "username": user.username}


@router.get("/captcha", response_model=CaptchaResponse)
def get_captcha():
    """获取图形验证码（4位随机字母数字）。"""
    return service.generate_captcha()


@router.post("/register", response_model=AuthResponse)
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    try:
        return service.register(db, req.username, req.password, req.captcha_id, req.captcha_code)
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.post("/login", response_model=AuthResponse)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    try:
        return service.login(db, req.username, req.password, req.captcha_id, req.captcha_code)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))


@router.get("/me", response_model=UserInfo)
def me(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    info = service.get_user_info(db, current_user["user_id"])
    return info if info else current_user


@router.put("/password")
def update_password(
    req: UpdatePasswordRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        service.update_password(db, current_user["user_id"], req.old_password, req.new_password)
        return {"ok": True}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/avatar")
def update_avatar(
    req: UpdateAvatarRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        service.update_avatar(db, current_user["user_id"], req.avatar)
        return {"ok": True}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
