# 数据库：SQLite 建表 + 基础操作（文档第四节）。
import logging
import sqlite3
from datetime import datetime

from . import config

logger = logging.getLogger(__name__)

# 建表 SQL（字段含义见技术文档第四节）
_SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    username      TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at    TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS profiles (
    user_id           INTEGER PRIMARY KEY,
    off_work_start    TEXT,    -- 下班时间范围起
    off_work_end      TEXT,    -- 下班时间范围止
    overtime_freq     TEXT,    -- 加班频率
    commute_min       INTEGER, -- 通勤分钟
    work_body_state   TEXT,    -- 久坐 / 站着走动 / 体力消耗
    cooking           TEXT,    -- 只能外卖 / 能简单做 / 能正经做
    diet_restrictions TEXT,    -- 饮食禁忌，逗号分隔，可空
    health_note       TEXT,    -- 健康问题一行，可空
    wake_time         TEXT,    -- 平时起床时间，"几点停"倒推睡眠时长用
    exercise_base     TEXT DEFAULT '无/偶尔',  -- 运动基础
    gender            TEXT,    -- 计算参数，全部可跳过
    age               INTEGER,
    height_cm         REAL,
    weight_kg         REAL
);

CREATE TABLE IF NOT EXISTS daily_records (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id         INTEGER NOT NULL,
    vday            TEXT NOT NULL,     -- 虚拟日期 "2026-08-07"
    conditions_json TEXT,              -- 当天条件快照
    advice_json     TEXT,              -- Agent 给出的建议（含理由行、来源）
    status          TEXT,              -- pending_feedback / done
    feedback        TEXT,              -- 四档回执，可空
    baseline_level  INTEGER            -- 当天最低线档位（0-4）
);

CREATE TABLE IF NOT EXISTS meal_records (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id    INTEGER NOT NULL,
    vday       TEXT NOT NULL,
    vtime      TEXT NOT NULL,
    source     TEXT NOT NULL,   -- photo / text
    food_json  TEXT,            -- {名称, 估计分量, 类别, 备注}
    image_path TEXT
);

CREATE TABLE IF NOT EXISTS free_inputs (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id        INTEGER NOT NULL,
    vday           TEXT NOT NULL,
    vtime          TEXT NOT NULL,
    text           TEXT NOT NULL,     -- 用户原话
    extracted_json TEXT               -- Agent 提取的条件
);

CREATE TABLE IF NOT EXISTS corpus_chunks (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    doc_name   TEXT NOT NULL,
    category   TEXT NOT NULL,   -- diet / exercise / stretch / sleep
    chunk_text TEXT NOT NULL    -- 向量存 data/corpus.npz，行号对应 id
);

CREATE TABLE IF NOT EXISTS user_notes (
    id      INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    vday    TEXT NOT NULL,      -- 记下这条备注的虚拟日期
    note    TEXT NOT NULL       -- 长期习惯/偏好，如"睡前喜欢喝一杯热牛奶"
);

CREATE TABLE IF NOT EXISTS app_clock (
    id          INTEGER PRIMARY KEY CHECK (id = 1),  -- 全局唯一一行
    virtual_now TEXT NOT NULL                        -- ISO 字符串
);

CREATE TABLE IF NOT EXISTS sessions (
    token      TEXT PRIMARY KEY,
    user_id    INTEGER NOT NULL,
    created_at TEXT NOT NULL
);
"""


def get_conn() -> sqlite3.Connection:
    """拿一个连接。row_factory 设成 Row，方便按列名取值。"""
    conn = sqlite3.connect(config.DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# profiles 表可写入的字段（onboarding 提交时按此白名单过滤）
PROFILE_FIELDS = [
    "off_work_start", "off_work_end", "overtime_freq", "commute_min",
    "work_body_state", "cooking", "diet_restrictions", "health_note",
    "wake_time", "exercise_base", "gender", "age", "height_cm", "weight_kg",
]


def init_db() -> None:
    """建表（幂等），并给 app_clock 播种初始虚拟时间。"""
    conn = get_conn()
    try:
        conn.executescript(_SCHEMA)
        # 轻量迁移：老库的 profiles 缺 wake_time 列时补上（SQLite 不支持 IF NOT EXISTS 加列）
        cols = [r["name"] for r in conn.execute("PRAGMA table_info(profiles)")]
        if "wake_time" not in cols:
            conn.execute("ALTER TABLE profiles ADD COLUMN wake_time TEXT")
            logger.info("db 迁移：profiles 表补充 wake_time 列")
        # 播种虚拟时钟：仅在首次初始化时用一次系统时间做起点，
        # 之后全后端业务逻辑一律走 clock.now()，禁止直接用系统时间。
        row = conn.execute("SELECT virtual_now FROM app_clock WHERE id = 1").fetchone()
        if row is None:
            initial = datetime.now().replace(microsecond=0).isoformat()
            conn.execute(
                "INSERT INTO app_clock (id, virtual_now) VALUES (1, ?)", (initial,)
            )
            logger.info("db 初始化：app_clock 播种 virtual_now=%s", initial)
        conn.commit()
        logger.info("db 初始化完成：%s", config.DB_PATH)
    finally:
        conn.close()


# ---------- 用户 / 会话 / 档案（M1） ----------

def create_user(username: str, password_hash: str, created_at: str) -> int:
    """建用户，用户名重复抛 sqlite3.IntegrityError。返回新用户 id。"""
    conn = get_conn()
    try:
        cur = conn.execute(
            "INSERT INTO users (username, password_hash, created_at) VALUES (?, ?, ?)",
            (username, password_hash, created_at),
        )
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()


def get_user_by_username(username: str):
    conn = get_conn()
    try:
        return conn.execute(
            "SELECT * FROM users WHERE username = ?", (username,)
        ).fetchone()
    finally:
        conn.close()


def create_session(token: str, user_id: int, created_at: str) -> None:
    conn = get_conn()
    try:
        conn.execute(
            "INSERT INTO sessions (token, user_id, created_at) VALUES (?, ?, ?)",
            (token, user_id, created_at),
        )
        conn.commit()
    finally:
        conn.close()


def get_user_id_by_token(token: str):
    """token 换 user_id，查不到返回 None。"""
    conn = get_conn()
    try:
        row = conn.execute(
            "SELECT user_id FROM sessions WHERE token = ?", (token,)
        ).fetchone()
        return row["user_id"] if row else None
    finally:
        conn.close()


def upsert_profile(user_id: int, fields: dict) -> None:
    """写入/覆盖用户档案。fields 只取 PROFILE_FIELDS 白名单里的键。"""
    data = {k: fields.get(k) for k in PROFILE_FIELDS}
    cols = ", ".join(data.keys())
    marks = ", ".join(["?"] * len(data))
    conn = get_conn()
    try:
        conn.execute("DELETE FROM profiles WHERE user_id = ?", (user_id,))
        conn.execute(
            f"INSERT INTO profiles (user_id, {cols}) VALUES (?, {marks})",
            (user_id, *data.values()),
        )
        conn.commit()
    finally:
        conn.close()


def get_profile(user_id: int):
    conn = get_conn()
    try:
        return conn.execute(
            "SELECT * FROM profiles WHERE user_id = ?", (user_id,)
        ).fetchone()
    finally:
        conn.close()


def get_username(user_id: int):
    conn = get_conn()
    try:
        row = conn.execute("SELECT username FROM users WHERE id = ?", (user_id,)).fetchone()
        return row["username"] if row else None
    finally:
        conn.close()


# ---------- 每日记录（M3：首夜建议入库） ----------

def insert_daily_record(user_id: int, vday: str, conditions_json: str,
                        advice_json: str, baseline_level: int) -> int:
    """存一条当日建议，初始状态 pending_feedback。返回记录 id。"""
    conn = get_conn()
    try:
        cur = conn.execute(
            "INSERT INTO daily_records (user_id, vday, conditions_json, advice_json, "
            "status, feedback, baseline_level) VALUES (?, ?, ?, ?, 'pending_feedback', NULL, ?)",
            (user_id, vday, conditions_json, advice_json, baseline_level),
        )
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()


def get_daily_record(user_id: int, vday: str):
    """取某虚拟日的记录（同日多条时取最新一条）。"""
    conn = get_conn()
    try:
        return conn.execute(
            "SELECT * FROM daily_records WHERE user_id = ? AND vday = ? ORDER BY id DESC",
            (user_id, vday),
        ).fetchone()
    finally:
        conn.close()


# ---------- M4：回执、纠正、自由输入 ----------

def get_record_by_id(record_id: int):
    conn = get_conn()
    try:
        return conn.execute(
            "SELECT * FROM daily_records WHERE id = ?", (record_id,)
        ).fetchone()
    finally:
        conn.close()


def get_pending_records_before(user_id: int, vday: str):
    """今天以前所有未回执的记录，按日期升序。"""
    conn = get_conn()
    try:
        return conn.execute(
            "SELECT * FROM daily_records WHERE user_id = ? AND vday < ? "
            "AND status = 'pending_feedback' ORDER BY vday",
            (user_id, vday),
        ).fetchall()
    finally:
        conn.close()


def get_last_records_before(user_id: int, vday: str, limit: int = 2):
    """今天以前最近的 N 条记录（新在前），用于算次日档位与连续完成。"""
    conn = get_conn()
    try:
        return conn.execute(
            "SELECT * FROM daily_records WHERE user_id = ? AND vday < ? "
            "ORDER BY vday DESC, id DESC LIMIT ?",
            (user_id, vday, limit),
        ).fetchall()
    finally:
        conn.close()


def set_feedback(record_id: int, feedback: str) -> None:
    """写回执并结束该记录（四档或 跳过/未响应）。"""
    conn = get_conn()
    try:
        conn.execute(
            "UPDATE daily_records SET feedback = ?, status = 'done' WHERE id = ?",
            (feedback, record_id),
        )
        conn.commit()
    finally:
        conn.close()


def update_record_advice(record_id: int, advice_json: str, conditions_json: str) -> None:
    """纠正/自由输入后重跑 Agent，更新当日记录的建议与条件快照。"""
    conn = get_conn()
    try:
        conn.execute(
            "UPDATE daily_records SET advice_json = ?, conditions_json = ? WHERE id = ?",
            (advice_json, conditions_json, record_id),
        )
        conn.commit()
    finally:
        conn.close()


def insert_free_input(user_id: int, vday: str, vtime: str, text: str) -> int:
    conn = get_conn()
    try:
        cur = conn.execute(
            "INSERT INTO free_inputs (user_id, vday, vtime, text, extracted_json) "
            "VALUES (?, ?, ?, ?, NULL)",
            (user_id, vday, vtime, text),
        )
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()


def get_free_inputs(user_id: int, vday: str) -> list[str]:
    """取某天的全部自由输入原话（按时间顺序）。安全边界 L1 扫描用：
    当天说过的危险信号（如"胸口闷"）对当晚整晚有效，重新生成建议时都要扫。"""
    conn = get_conn()
    try:
        rows = conn.execute(
            "SELECT text FROM free_inputs WHERE user_id = ? AND vday = ? ORDER BY vtime, id",
            (user_id, vday),
        ).fetchall()
        return [r["text"] for r in rows]
    finally:
        conn.close()


def set_free_input_extracted(free_input_id: int, extracted_json: str) -> None:
    conn = get_conn()
    try:
        conn.execute(
            "UPDATE free_inputs SET extracted_json = ? WHERE id = ?",
            (extracted_json, free_input_id),
        )
        conn.commit()
    finally:
        conn.close()


# ---------- 长期备注（B6：用户的持久习惯/偏好，每次生成建议都注入） ----------

def add_user_note(user_id: int, vday: str, note: str) -> bool:
    """存一条长期备注。完全相同的内容不重复存，返回是否新增。"""
    conn = get_conn()
    try:
        exists = conn.execute(
            "SELECT 1 FROM user_notes WHERE user_id = ? AND note = ?", (user_id, note)
        ).fetchone()
        if exists:
            return False
        conn.execute(
            "INSERT INTO user_notes (user_id, vday, note) VALUES (?, ?, ?)",
            (user_id, vday, note),
        )
        conn.commit()
        return True
    finally:
        conn.close()


def get_user_notes(user_id: int) -> list:
    conn = get_conn()
    try:
        return [r["note"] for r in conn.execute(
            "SELECT note FROM user_notes WHERE user_id = ? ORDER BY id", (user_id,)
        ).fetchall()]
    finally:
        conn.close()
