# 虚拟时钟（文档第八节）：全局 virtual_now 存在 app_clock 表。
# 全后端业务逻辑禁止直接用系统时间，一律用本模块的 now()。
import logging
from datetime import datetime, timedelta

from . import db

logger = logging.getLogger(__name__)

_WEEKDAY_CN = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]


def now() -> datetime:
    """当前虚拟时间。"""
    conn = db.get_conn()
    try:
        row = conn.execute("SELECT virtual_now FROM app_clock WHERE id = 1").fetchone()
        return datetime.fromisoformat(row["virtual_now"])
    finally:
        conn.close()


def today() -> str:
    """当前虚拟日期，即 vday，如 "2026-08-07"。"""
    return now().date().isoformat()


def now_display() -> str:
    """人类可读格式，如 "2026-08-07 19:20 （周五）"，注入提示词 / 前端展示用。"""
    t = now()
    return f"{t.strftime('%Y-%m-%d %H:%M')} （{_WEEKDAY_CN[t.weekday()]}）"


def _write(t: datetime) -> datetime:
    t = t.replace(microsecond=0)
    conn = db.get_conn()
    try:
        conn.execute("UPDATE app_clock SET virtual_now = ? WHERE id = 1", (t.isoformat(),))
        conn.commit()
    finally:
        conn.close()
    logger.info("clock 虚拟时钟变更 -> %s", t.isoformat())
    return t


def advance_hours(hours: float) -> datetime:
    """前进 N 小时。"""
    return _write(now() + timedelta(hours=hours))


def advance_days(days: int) -> datetime:
    """跳到 N 天后的 19:00（演示按钮「下一天」）。"""
    target = now() + timedelta(days=days)
    return _write(target.replace(hour=19, minute=0, second=0))


def set_time(iso_str: str) -> datetime:
    """直接设置虚拟时间，参数为 ISO 字符串。格式非法会抛 ValueError。"""
    return _write(datetime.fromisoformat(iso_str))


def reset() -> datetime:
    """重置为真实当前时间（仅演示控制条用，不属于业务逻辑）。"""
    return _write(datetime.now())
