# Agent 可调用的工具函数（文档 3.4 / 3.5）。
# 统一公式一律写成确定性 Python 代码，不让大模型心算。
import json
import logging
from datetime import date, timedelta

from . import clock, db, rag

logger = logging.getLogger(__name__)


def search_reference(query: str, category: str = "any") -> list[dict]:
    """检索参考手册，返回 top-3 文本块，每块带来源名称。"""
    if category not in ("diet", "exercise", "stretch", "sleep", "any"):
        category = "any"
    results = rag.search(query, category, top_k=3)
    return [{"来源": r["doc_name"], "内容": r["chunk_text"]} for r in results]


def get_user_history(user_id: int, days: int = 3) -> dict:
    """取最近 N 天的记录：建议与反馈、饮食记录、自由输入。"""
    days = max(1, min(int(days), 14))
    since = (date.fromisoformat(clock.today()) - timedelta(days=days)).isoformat()
    conn = db.get_conn()
    try:
        records = conn.execute(
            "SELECT vday, advice_json, status, feedback, baseline_level FROM daily_records "
            "WHERE user_id = ? AND vday >= ? ORDER BY vday",
            (user_id, since),
        ).fetchall()
        meals = conn.execute(
            "SELECT vday, vtime, source, food_json FROM meal_records "
            "WHERE user_id = ? AND vday >= ? ORDER BY vday, vtime",
            (user_id, since),
        ).fetchall()
        inputs = conn.execute(
            "SELECT vday, vtime, text FROM free_inputs "
            "WHERE user_id = ? AND vday >= ? ORDER BY vday, vtime",
            (user_id, since),
        ).fetchall()
    finally:
        conn.close()

    def _advice_brief(advice_json):
        if not advice_json:
            return None
        try:
            a = json.loads(advice_json)
            return {k: a.get(k) for k in ("judgement", "eat", "move", "stop")}
        except (json.JSONDecodeError, TypeError):
            return None

    return {
        "每日建议与反馈": [
            {"日期": r["vday"], "建议": _advice_brief(r["advice_json"]),
             "反馈": r["feedback"] or "（未回执）", "档位": r["baseline_level"]}
            for r in records
        ],
        "饮食记录": [
            {"日期": m["vday"], "时间": m["vtime"], "来源": m["source"],
             "内容": json.loads(m["food_json"]) if m["food_json"] else None}
            for m in meals
        ],
        "用户自由输入": [
            {"日期": i["vday"], "时间": i["vtime"], "原话": i["text"]} for i in inputs
        ],
    }


# 活动系数（TDEE = BMR * 系数）
_ACTIVITY_FACTOR = {"久坐": 1.2, "站着走动": 1.4, "体力消耗": 1.6}


def calc_body_metrics(user_id: int) -> dict:
    """确定性计算工具（文档 3.5）。
    基础代谢 BMR，Mifflin-St Jeor 公式：
      男：10*体重kg + 6.25*身高cm - 5*年龄 + 5
      女：10*体重kg + 6.25*身高cm - 5*年龄 - 161
    每日估算消耗 TDEE = BMR * 活动系数（久坐1.2 / 站着走动1.4 / 体力消耗1.6）
    蛋白质参考：一般成人 0.8–1.0 g/kg；有轻度训练 1.2–1.6 g/kg
    缺身高/体重/年龄/性别任一项 → {"available": false}，Agent 就不引用数字。
    """
    p = db.get_profile(user_id)
    if p is None or not all([p["gender"], p["age"], p["height_cm"], p["weight_kg"]]):
        return {"available": False, "note": "缺少性别/年龄/身高/体重，无法估算"}
    w, h, a = p["weight_kg"], p["height_cm"], p["age"]
    bmr = 10 * w + 6.25 * h - 5 * a + (5 if p["gender"] == "男" else -161)
    tdee = bmr * _ACTIVITY_FACTOR.get(p["work_body_state"], 1.2)
    if p["exercise_base"] and p["exercise_base"] != "无/偶尔":
        protein = [round(w * 1.2), round(w * 1.6)]
    else:
        protein = [round(w * 0.8), round(w * 1.0)]
    return {
        "available": True,
        "bmr_kcal": round(bmr),
        "tdee_kcal": round(tdee),
        "protein_g_range": protein,
        "note": "估算值，仅作参考量级，不用于精确配餐",
    }


# OpenAI 格式的工具声明（文档 3.4，第一版 4 个）
TOOL_DEFS = [
    {
        "type": "function",
        "function": {
            "name": "search_reference",
            "description": "检索权威参考手册（膳食/运动/拉伸/睡眠），返回最相关的3个文本块，每块带来源名称。给建议前必须先查。",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "检索问题，用自然语言"},
                    "category": {
                        "type": "string",
                        "enum": ["diet", "exercise", "stretch", "sleep", "any"],
                        "description": "手册类别：diet饮食/exercise运动/stretch拉伸/sleep睡眠/any不限",
                    },
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_user_history",
            "description": "取该用户最近N天的记录（建议与反馈、饮食记录、自由输入原话）。",
            "parameters": {
                "type": "object",
                "properties": {
                    "days": {"type": "integer", "description": "取最近几天，默认3"},
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "log_note",
            "description": "把你从用户自由输入里提取到的关键条件记一笔（如从「加了三小时班」提取出「今晚到家晚、精力低」）。",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "提取出的关键条件，一句话"},
                },
                "required": ["text"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "calc_body_metrics",
            "description": "确定性计算该用户的基础代谢、每日估算消耗、蛋白质参考区间（参数自动从档案读取，你不需要传数字）。数字只用来定量级和方向，不做精确配比。",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
]
