# 配置：读 .env，集中管理路径与模型名。换模型只改这里 / .env。
import os
from pathlib import Path

from dotenv import load_dotenv

# 项目根目录（backend/ 的上一层）
BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")

# ---- 大模型（阿里百炼，OpenAI 兼容格式）----
# .env 只用一套变量名：LLM_API_KEY / LLM_BASE_URL
LLM_API_KEY = os.getenv("LLM_API_KEY", "")
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "")
CHAT_MODEL = os.getenv("CHAT_MODEL", "qwen-plus")
VISION_MODEL = os.getenv("VISION_MODEL", "qwen-vl-max")
EMBED_MODEL = os.getenv("EMBED_MODEL", "text-embedding-v4")

# ---- 路径 ----
DB_PATH = BASE_DIR / "app.db"
LOG_DIR = BASE_DIR / "logs"
TRACE_DIR = LOG_DIR / "trace"
FRONTEND_DIR = BASE_DIR / "frontend"
DATA_DIR = BASE_DIR / "data"
