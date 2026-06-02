import os
from dotenv import load_dotenv

load_dotenv()

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/learning_system.db")
MODEL_NAME = "deepseek-chat"
SEEDANCE_API_KEY = os.getenv("SEEDANCE_API_KEY", "")
SEEDANCE_BASE_URL = os.getenv("SEEDANCE_BASE_URL", "https://ark.cn-beijing.volces.com/api/v3")
SEEDANCE_MODEL = os.getenv("SEEDANCE_MODEL", "doubao-seedance-1.0-pro-fast")

IFLYTEK_APP_ID = os.getenv("IFLYTEK_APP_ID", "")
IFLYTEK_APP_KEY = os.getenv("IFLYTEK_APP_KEY", "")
IFLYTEK_APP_SECRET = os.getenv("IFLYTEK_APP_SECRET", "")
IFLYTEK_AVATAR_ID = os.getenv("IFLYTEK_AVATAR_ID", "")
IFLYTEK_VCN = os.getenv("IFLYTEK_VCN", "")
IFLYTEK_SPEED = int(os.getenv("IFLYTEK_SPEED", "50"))
IFLYTEK_WS_URL = "wss://avatar.cn-huadong-1.xf-yun.com/v1/interact"

DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY", "")

JWT_SECRET = os.getenv("JWT_SECRET", "learning-system-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_DAYS = 7
