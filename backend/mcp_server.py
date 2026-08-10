"""赛事自建 MCP（Streamable HTTP）——挂在主应用 /mcp 路径上（见 main.py 尾部路由）。

为什么手写协议层而不引官方 SDK：仓里没有 lockfile，requirements 每次 Railway 部署都重新
解依赖，决赛期间引新包若解出不兼容版本，是整个 app 一起挂；MCP 的 Streamable HTTP 本质
就是 JSON-RPC over POST，手写百来行零依赖，坏不了主应用。协议按 2025-03-26/2025-06-18
两版实现共同子集：initialize 版本协商、notifications 回 202、tools/list、tools/call、ping；
GET/DELETE /mcp 由 FastAPI 自动 405（未注册即拒），符合"服务端可不支持"条款。

评测语义：平台验证 = initialize 成功 + tools/list 15s 内返回 ≥1 个工具 + 核心工具调用非错误；
之后评测 agent 会拿这些工具体验产品（动态分）。所以工具面 = 产品核心循环本身：
了解产品 → 生成今晚建议 → 看状态 → 补充一句（含安全边界展示）→ 回执。
评测走专用账号 mcp_judge（首次调用自动建，随机密码不可登录，不污染演示账号），
不提供拨钟工具（app_clock 是全局的，动了会搅乱正在给评委演示的虚拟时间）。
"""
from __future__ import annotations

import json
import logging
import secrets
import sqlite3
import threading

from . import agent, clock, db, safety

logger = logging.getLogger(__name__)

SUPPORTED_VERSIONS = ("2025-06-18", "2025-03-26", "2024-11-05")
SERVER_INFO = {"name": "lite-me", "title": "Lite Me（人类省电模式）", "version": "1.0.0"}
INSTRUCTIONS = (
    "Lite Me（人类省电模式）：给下班后只剩一点力气的人，把「今天照顾自己」缩成不可再缩小的"
    "三件事（吃一口正经的 / 动一下 / 停一次），目标是长期不归零而不是单日最优。"
    "建议体验顺序：about_lite_me 了解产品 → start_night 生成今晚建议（真实 Agent 生成，约 10-20 秒）"
    "→ get_tonight_state 查看今晚判断与建议 → add_note 补充一句身体状况"
    "（试试『有点胸闷』，会看到三层安全边界当场接管、撤掉运动建议）→ submit_feedback 回执，"
    "回执会影响次日建议档位。所有工具作用于评测专用账号，可反复调用。"
)

# 带模型调用的工具每日上限（保护 LLM 配额；tools/list、状态读取不计）
_GEN_CAP = 40
_gen_lock = threading.Lock()
_gen_state = {"vday": "", "used": 0}

FEEDBACK_OPTIONS = ("完成了", "只完成一部分", "完全没完成", "建议仍然太难", "跳过")
OFFWORK_STATES = ("今晚更累", "时间更少", "不太舒服", "今天还行")

TOOLS = [
    {
        "name": "about_lite_me",
        "description": "介绍 Lite Me 是什么、解决什么问题、有哪些核心机制（最小三件事/档位/安全边界/回执闭环），以及用这些工具体验产品的建议顺序。无参数，立即返回。",
        "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False},
    },
    {
        "name": "start_night",
        "description": "「下班了」——为评测账号生成今晚的最小自我照顾建议（吃/动/停三行）。走真实 Agent 生成链路（RAG+工具循环+安全边界），约 10-20 秒。当晚已有建议时默认直接返回已有建议；replan=true 则按最新补充重新生成。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "work_state": {
                    "type": "string",
                    "enum": list(OFFWORK_STATES),
                    "description": "下班时的状态自述，影响今晚建议的松紧，可不填",
                },
                "replan": {
                    "type": "boolean",
                    "description": "当晚已有建议时是否重新生成（会把 add_note 补充的内容纳入考虑），默认 false",
                },
            },
            "additionalProperties": False,
        },
    },
    {
        "name": "get_tonight_state",
        "description": "查看评测账号今晚的完整状态：虚拟时间、今晚判断三行（剩余时间/精力/身体）、已生成的建议（吃/动/停/安全等级）、回执状态、今天补充过的话。只读，立即返回。",
        "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False},
    },
    {
        "name": "add_note",
        "description": "补充一句今晚的情况（如『加班到九点』『刚吃了火锅』『有点胸闷』）。句子会进入今晚建议的生成上下文；若包含危险健康信号（胸闷/胸痛等），三层安全边界会当场接管：撤掉运动建议、只留就医指引。这是产品的安全底线展示入口。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "minLength": 1, "maxLength": 200,
                          "description": "一句话，中文，200 字以内"},
            },
            "required": ["text"],
            "additionalProperties": False,
        },
    },
    {
        "name": "submit_feedback",
        "description": "对最近一晚建议的回执（完成了/只完成一部分/完全没完成/建议仍然太难/跳过）。回执驱动次日档位调整——连续完成会略升、没完成会降回更小的一步，这是「长期不归零」的核心闭环。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "feedback": {"type": "string", "enum": list(FEEDBACK_OPTIONS),
                              "description": "回执档位"},
            },
            "required": ["feedback"],
            "additionalProperties": False,
        },
    },
]

_JUDGE_PROFILE = {
    "off_work_start": "19:00", "off_work_end": "20:00", "overtime_freq": "经常",
    "commute_min": 40, "work_body_state": "久坐", "cooking": "几乎不做",
    "diet_restrictions": "", "health_note": "", "wake_time": "07:30",
    "exercise_base": "几乎不动", "gender": "男", "age": 28,
    "chronic_condition": "", "doctor_advice": "", "favorite_foods": "面食",
    "sleep_time": "00:00",
}


def _judge_user_id() -> int:
    """评测专用账号：不存在则建（随机密码，不可网页登录），档案固定预设。"""
    row = db.get_user_by_username("mcp_judge")
    if row is not None:
        return row["id"]
    from . import main as m  # 延迟导入避免循环（main 顶部 import 本模块）
    salt = secrets.token_hex(8)
    pwd = secrets.token_hex(16)
    try:
        user_id = db.create_user("mcp_judge", f"{salt}${m._hash_password(pwd, salt)}",
                                 clock.now().isoformat())
    except sqlite3.IntegrityError:   # 并发首建撞车：另一个线程刚建好
        user_id = db.get_user_by_username("mcp_judge")["id"]
    db.upsert_profile(user_id, _JUDGE_PROFILE)
    logger.info("mcp: 评测账号 mcp_judge 已创建 user_id=%s", user_id)
    return user_id


def _gen_budget_ok() -> bool:
    """带模型调用的工具每日计数；超限拒绝（评测不至于打满，防的是被扫着白嫖 key）。"""
    with _gen_lock:
        today = clock.today()
        if _gen_state["vday"] != today:
            _gen_state.update(vday=today, used=0)
        if _gen_state["used"] >= _GEN_CAP:
            return False
        _gen_state["used"] += 1
        return True


def _fmt_advice(advice: dict) -> str:
    lines = [f"判断：{advice.get('judgment', '')}"]
    for k in ("eat", "move", "stop"):
        v = advice.get(k)
        if isinstance(v, dict):
            lines.append(f"{ {'eat': '吃', 'move': '动', 'stop': '停'}[k] }：{v.get('内容') or v.get('content') or json.dumps(v, ensure_ascii=False)}")
        elif v:
            lines.append(f"{ {'eat': '吃', 'move': '动', 'stop': '停'}[k] }：{v}")
    if advice.get("safety_level") and advice["safety_level"] != "none":
        lines.append(f"⚠ 安全等级：{advice['safety_level']}（运动类建议已按安全边界撤除/降级）")
    return "\n".join(lines)


# ---------- 工具实现（都返回给评测 agent 读的纯文本） ----------

def _tool_about(_args: dict) -> str:
    return (
        "Lite Me（人类省电模式）。\n"
        "解决的问题：下班后只剩零碎时间和精力的人，自我照顾计划总在「归零」——"
        "定得越完美断得越快。Lite Me 把每天缩成不可再缩小的三件事：吃一口正经的、"
        "动一下、停一次，目标是长期不归零。\n"
        "核心机制：\n"
        "1. 一天一触点：「下班了」一击生成今晚建议，先断言后纠正，不问一堆问题；\n"
        "2. 档位系统：回执（完成/没完成）驱动次日建议的大小，永远给出你今晚做得到的那一档；\n"
        "3. 三层安全边界：确诊重症劝退 + 危险信号词表 + LLM 分类兜底，"
        "『胸闷』这类信号出现时当场撤掉运动建议、只留就医指引；\n"
        "4. 建议由真实 Agent 生成：RAG 检索膳食/运动指南 + 工具循环 + 安全强制项。\n"
        "建议体验顺序：start_night → get_tonight_state → add_note（试试『有点胸闷』）→ submit_feedback。"
    )


def _tool_start_night(args: dict) -> str:
    from . import main as m
    user_id = _judge_user_id()
    username = "mcp_judge"
    today = clock.today()
    state = args.get("work_state")
    state = state if state in OFFWORK_STATES else None
    replan = bool(args.get("replan"))

    with m._user_lock(user_id):
        existing = db.get_daily_record(user_id, today)
        has_advice = bool(existing and existing["advice_json"])
        if has_advice and not replan:
            advice = json.loads(existing["advice_json"])
            return "今晚已有建议（要按最新补充重出就传 replan=true）：\n" + _fmt_advice(advice)
        if not _gen_budget_ok():
            return "今日评测生成次数已达上限（保护配额），请用 get_tonight_state 查看已有建议。"
        advice = m._run_and_save_today(
            user_id, username,
            record=existing if (has_advice and replan) else None,
            offwork_state=state,
        )
    return "今晚建议已生成：\n" + _fmt_advice(advice)


def _tool_get_state(_args: dict) -> str:
    user_id = _judge_user_id()
    p = db.get_profile(user_id)
    today = clock.today()
    lines = [f"虚拟时间：{clock.now_display()}（评测账号 mcp_judge）"]

    last = db.get_last_records_before(user_id, today, limit=1)
    last_fb = last[0]["feedback"] if last else None
    record = db.get_daily_record(user_id, today)
    level = (record["baseline_level"] if record and record["baseline_level"] is not None
             else None)
    hint = agent.build_confirm_hint(p, clock.now(), last_fb, level if level is not None else 2)
    if hint:
        lines.append(f"今晚判断：剩余约 {hint.get('remaining_min')} 分钟（{hint.get('time_basis')}）；"
                     f"精力：{hint.get('energy_guess')}；身体：{hint.get('body')}")

    if record and record["advice_json"]:
        lines.append("今晚建议：\n" + _fmt_advice(json.loads(record["advice_json"])))
        lines.append(f"回执状态：{record['feedback'] or '未回执'}")
    else:
        lines.append("今晚还没生成建议（调用 start_night）。")

    notes = db.get_free_inputs(user_id, today)
    if notes:
        lines.append("今天补充过：" + "；".join(notes[-5:]))
    return "\n".join(lines)


def _tool_add_note(args: dict) -> str:
    from . import main as m
    text = str(args.get("text", "")).strip()
    if not text:
        return "内容不能为空。"
    user_id = _judge_user_id()
    p = db.get_profile(user_id)
    db.insert_free_input(user_id, clock.today(), clock.now().strftime("%H:%M"), text)

    # 与 /api/free_input 同一道即时安全闸门：当天全部自由输入重扫，命中 danger/crisis
    # 当场把建议重算成安全模式（详见 main.api_free_input 的注释）
    gate = safety.assess(
        db.get_free_inputs(user_id, clock.today()),
        health_note=p["health_note"] if p is not None else None,
        chronic_condition=p["chronic_condition"] if p is not None else None,
    ) if p is not None else {"final_level": "none", "hits": []}
    if gate["final_level"] in ("danger", "crisis"):
        if not _gen_budget_ok():
            return "已记下，并检测到危险健康信号；今日评测生成次数已达上限，未重出建议。"
        with m._user_lock(user_id):
            existing = db.get_daily_record(user_id, clock.today())
            ex_advice = (json.loads(existing["advice_json"])
                         if existing and existing["advice_json"] else None)
            if ex_advice and ex_advice.get("safety_level") in ("danger", "crisis"):
                advice = ex_advice
            else:
                advice = m._run_and_save_today(user_id, "mcp_judge",
                                               record=existing if ex_advice else None,
                                               safety_state=gate)
        return ("⚠ 检测到危险健康信号，安全边界已接管（这就是产品的安全底线）：\n"
                + _fmt_advice(advice))
    return "记下了。这句话会进入今晚建议的生成上下文（已生成过建议时可用 start_night 的 replan=true 重出）。"


def _tool_feedback(args: dict) -> str:
    fb = args.get("feedback")
    if fb not in FEEDBACK_OPTIONS:
        return f"feedback 需为 {FEEDBACK_OPTIONS} 之一。"
    user_id = _judge_user_id()
    record = db.get_daily_record(user_id, clock.today())
    if record is None or not record["advice_json"]:
        return "还没有可回执的建议，先调用 start_night。"
    db.set_feedback(record["id"], fb)
    return (f"回执已记录：{fb}。它会驱动次日建议档位——连续完成略升一档、"
            f"没完成降回更小的一步（长期不归零的核心闭环）。")


_TOOL_IMPL = {
    "about_lite_me": _tool_about,
    "start_night": _tool_start_night,
    "get_tonight_state": _tool_get_state,
    "add_note": _tool_add_note,
    "submit_feedback": _tool_feedback,
}


# ---------- JSON-RPC 分发 ----------

def _result(msg_id, result: dict) -> dict:
    return {"jsonrpc": "2.0", "id": msg_id, "result": result}


def _error(msg_id, code: int, message: str) -> dict:
    return {"jsonrpc": "2.0", "id": msg_id, "error": {"code": code, "message": message}}


def handle_message(msg: dict) -> dict | None:
    """处理单条 JSON-RPC 消息。返回 None 表示这是通知（notification），无响应体。"""
    if not isinstance(msg, dict) or msg.get("jsonrpc") != "2.0" or "method" not in msg:
        return _error(msg.get("id") if isinstance(msg, dict) else None,
                      -32600, "Invalid Request")
    method = msg["method"]
    msg_id = msg.get("id")
    is_notification = "id" not in msg

    if method.startswith("notifications/"):
        return None
    if is_notification:   # 其它无 id 的请求也按通知处理（宽容）
        return None

    if method == "initialize":
        params = msg.get("params") or {}
        want = params.get("protocolVersion")
        # 版本协商：客户端要的版本我们支持就回它；不认识就按规范回我们支持的最新版
        version = want if want in SUPPORTED_VERSIONS else SUPPORTED_VERSIONS[0]
        return _result(msg_id, {
            "protocolVersion": version,
            "capabilities": {"tools": {"listChanged": False}},
            "serverInfo": SERVER_INFO,
            "instructions": INSTRUCTIONS,
        })
    if method == "ping":
        return _result(msg_id, {})
    if method == "tools/list":
        return _result(msg_id, {"tools": TOOLS})
    if method == "tools/call":
        params = msg.get("params") or {}
        name = params.get("name")
        impl = _TOOL_IMPL.get(name)
        if impl is None:
            return _error(msg_id, -32602, f"Unknown tool: {name}")
        try:
            text = impl(params.get("arguments") or {})
            return _result(msg_id, {"content": [{"type": "text", "text": text}],
                                    "isError": False})
        except Exception:
            logger.exception("mcp: 工具 %s 执行异常", name)
            return _result(msg_id, {"content": [{"type": "text",
                                                 "text": "工具执行出错，请稍后重试。"}],
                                    "isError": True})
    return _error(msg_id, -32601, f"Method not found: {method}")
