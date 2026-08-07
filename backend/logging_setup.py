# 日志初始化（文档 11.1）：标准库 logging，同时输出到控制台和 logs/app.log，按天滚动。
# 必须记的事件：每次 API 请求、每次模型调用、每次兜底触发、虚拟时钟变更。
import logging
from logging.handlers import TimedRotatingFileHandler

from . import config

_FORMAT = "%(asctime)s [%(levelname)s] %(message)s"
_DATEFMT = "%Y-%m-%d %H:%M:%S"

_initialized = False


def setup_logging() -> None:
    """初始化全局日志，幂等：重复调用不重复加 handler。"""
    global _initialized
    if _initialized:
        return

    config.LOG_DIR.mkdir(parents=True, exist_ok=True)
    config.TRACE_DIR.mkdir(parents=True, exist_ok=True)

    formatter = logging.Formatter(_FORMAT, datefmt=_DATEFMT)

    # 文件：按天滚动，保留 14 天
    file_handler = TimedRotatingFileHandler(
        config.LOG_DIR / "app.log", when="midnight", backupCount=14, encoding="utf-8"
    )
    file_handler.setFormatter(formatter)

    # 控制台
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    root = logging.getLogger()
    root.setLevel(logging.INFO)
    root.addHandler(file_handler)
    root.addHandler(console_handler)

    _initialized = True
