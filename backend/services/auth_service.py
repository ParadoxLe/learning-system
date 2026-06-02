import hashlib
import os
import random
import string
import datetime
import time
import uuid
import jwt
import logging
from sqlalchemy.orm import Session
from backend.models.user import User
from backend.models.student import Student
from backend.models.profile import LearningProfile
from backend.config import JWT_SECRET, JWT_ALGORITHM, JWT_EXPIRE_DAYS

logger = logging.getLogger(__name__)

# In-memory captcha store: {captcha_id: (code, expiry_timestamp)}
_captcha_store: dict[str, tuple[str, float]] = {}

CAPTCHA_EXPIRE_SECONDS = 300  # 5 minutes


def _hash_password(password: str) -> str:
    salt = os.urandom(32)
    key = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 100000)
    return salt.hex() + ":" + key.hex()


def _verify_password(password: str, stored: str) -> bool:
    salt_hex, key_hex = stored.split(":")
    salt = bytes.fromhex(salt_hex)
    key = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 100000)
    return key.hex() == key_hex


def create_token(user_id: int, username: str) -> str:
    payload = {
        "user_id": user_id,
        "username": username,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(days=JWT_EXPIRE_DAYS),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_token(token: str):  # -> dict | None (Python 3.10+)
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.PyJWTError:
        return None


class AuthService:
    def generate_captcha(self) -> dict:
        """Generate a 4-char alphanumeric captcha, store in memory, return id + text."""
        captcha_id = uuid.uuid4().hex[:16]
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
        _captcha_store[captcha_id] = (code, time.time() + CAPTCHA_EXPIRE_SECONDS)
        return {"captcha_id": captcha_id, "captcha_text": code}

    def register(self, db: Session, username: str, password: str, captcha_id: str, captcha_code: str) -> dict:
        # Validate captcha
        entry = _captcha_store.get(captcha_id)
        if not entry:
            raise ValueError("验证码已失效，请刷新重试")
        stored_code, expiry = entry
        if time.time() > expiry:
            del _captcha_store[captcha_id]
            raise ValueError("验证码已过期，请刷新重试")
        if captcha_code.upper().strip() != stored_code.upper().strip():
            raise ValueError("验证码错误")
        # One-time use
        del _captcha_store[captcha_id]

        existing = db.query(User).filter(User.username == username).first()
        if existing:
            raise ValueError("用户名已存在")

        user = User(username=username, password_hash=_hash_password(password))
        db.add(user)
        db.flush()

        # Auto-create a student record for this user
        student = Student(name=username, user_id=user.id)
        db.add(student)
        db.commit()
        db.refresh(user)

        token = create_token(user.id, user.username)
        return {"user_id": user.id, "username": user.username, "token": token,
                "student_id": student.id}

    def login(self, db: Session, username: str, password: str, captcha_id: str, captcha_code: str) -> dict:
        # Validate captcha
        entry = _captcha_store.get(captcha_id)
        if not entry:
            raise ValueError("验证码已失效，请刷新重试")
        stored_code, expiry = entry
        if time.time() > expiry:
            del _captcha_store[captcha_id]
            raise ValueError("验证码已过期，请刷新重试")
        if captcha_code.upper().strip() != stored_code.upper().strip():
            raise ValueError("验证码错误")
        del _captcha_store[captcha_id]

        user = db.query(User).filter(User.username == username).first()
        if not user:
            raise ValueError("该用户未注册")
        if not _verify_password(password, user.password_hash):
            raise ValueError("密码错误")

        # Get or create student
        student = db.query(Student).filter(Student.user_id == user.id).first()
        token = create_token(user.id, user.username)
        return {"user_id": user.id, "username": user.username, "token": token,
                "student_id": student.id if student else None}

    def get_user(self, db: Session, user_id: int):  # -> User | None (Python 3.10+)
        return db.query(User).filter(User.id == user_id).first()

    def get_user_info(self, db: Session, user_id: int) -> dict:
        user = self.get_user(db, user_id)
        if not user:
            return None
        student = db.query(Student).filter(Student.user_id == user_id).first()
        has_profile = False
        if student:
            profile = db.query(LearningProfile).filter(
                LearningProfile.student_id == student.id
            ).first()
            has_profile = profile is not None
        return {
            "id": user.id,
            "username": user.username,
            "avatar": user.avatar or "",
            "created_at": user.created_at.strftime("%Y-%m-%d") if user.created_at else "",
            "student_id": student.id if student else None,
            "has_profile": has_profile,
        }

    def update_password(self, db: Session, user_id: int, old_password: str, new_password: str):
        user = self.get_user(db, user_id)
        if not user:
            raise ValueError("用户不存在")
        if not _verify_password(old_password, user.password_hash):
            raise ValueError("原密码错误")
        user.password_hash = _hash_password(new_password)
        db.commit()

    def update_avatar(self, db: Session, user_id: int, avatar_data: str):
        user = self.get_user(db, user_id)
        if not user:
            raise ValueError("用户不存在")
        user.avatar = avatar_data
        db.commit()
