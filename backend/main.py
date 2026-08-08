# FastAPI 入口 + 路由。
# 启动：uvicorn backend.main:app --reload
import hashlib
import json
import logging
import secrets
import sqlite3
import threading
import time

import re

from fastapi import FastAPI, Request, UploadFile
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from . import agent, clock, config, db, llm, safety
from .logging_setup import setup_logging

setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI(title="最低自我照顾 Agent")


@app.on_event("startup")
def _startup() -> None:
    db.init_db()
    logger.info("服务启动，虚拟时间=%s", clock.now().isoformat())


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """记录每次 API 请求：路径、耗时（文档 11.1）。静态资源不记，避免刷屏。"""
    start = time.perf_counter()
    response = await call_next(request)
    if request.url.path.startswith("/api/"):
        cost = time.perf_counter() - start
        logger.info(
            "api %s %s status=%s 耗时=%.3fs",
            request.method, request.url.path, response.status_code, cost,
        )
    return response


# ---------- 账号与登录态（M1；文档要求：密码 hash 即可，不做复杂安全） ----------

def _hash_password(password: str, salt: str) -> str:
    return hashlib.sha256((salt + password).encode("utf-8")).hexdigest()


def _current_user_id(request: Request):
    """从 Authorization: Bearer <token> 解析当前用户，未登录返回 None。"""
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return None
    return db.get_user_id_by_token(auth.removeprefix("Bearer ").strip())


def _issue_token(user_id: int) -> str:
    token = secrets.token_hex(16)
    db.create_session(token, user_id, clock.now().isoformat())
    return token


@app.post("/api/register")
async def api_register(payload: dict):
    """注册：{username, password}。成功后直接发 token（省一次登录）。"""
    username = str(payload.get("username", "")).strip()
    password = str(payload.get("password", ""))
    if not username or not password:
        return JSONResponse(status_code=400, content={"error": "用户名和密码不能为空"})
    salt = secrets.token_hex(8)
    try:
        user_id = db.create_user(
            username, f"{salt}${_hash_password(password, salt)}", clock.now().isoformat()
        )
    except sqlite3.IntegrityError:
        return JSONResponse(status_code=400, content={"error": "用户名已存在"})
    logger.info("user=%s event=register 注册成功 user_id=%s", username, user_id)
    return {"token": _issue_token(user_id)}


@app.post("/api/login")
async def api_login(payload: dict):
    """登录：{username, password} → {token}。其后请求带 Authorization: Bearer <token>。"""
    username = str(payload.get("username", "")).strip()
    password = str(payload.get("password", ""))
    user = db.get_user_by_username(username)
    if user is None:
        return JSONResponse(status_code=401, content={"error": "用户不存在"})
    salt, stored_hash = user["password_hash"].split("$", 1)
    if _hash_password(password, salt) != stored_hash:
        logger.info("user=%s event=login 密码错误", username)
        return JSONResponse(status_code=401, content={"error": "密码错误"})
    logger.info("user=%s event=login 登录成功", username)
    return {"token": _issue_token(user["id"])}


@app.get("/api/profile")
async def api_profile(request: Request):
    """取当前用户档案（个人资料页预填用）。"""
    user_id = _current_user_id(request)
    if user_id is None:
        return JSONResponse(status_code=401, content={"error": "未登录"})
    p = db.get_profile(user_id)
    if p is None:
        return {"profile": None}
    return {"profile": {k: p[k] for k in db.PROFILE_FIELDS}}


@app.post("/api/onboarding")
async def api_onboarding(payload: dict, request: Request):
    """填信息只保存档案，不自动生成建议——首夜建议由用户自己点「下班了」触发。
    档案已存在时是「修改资料」：同样只保存。
    """
    user_id = _current_user_id(request)
    if user_id is None:
        return JSONResponse(status_code=401, content={"error": "未登录"})
    is_update = db.get_profile(user_id) is not None
    db.upsert_profile(user_id, payload)
    username = db.get_username(user_id)
    if is_update:
        logger.info("user=%s event=profile_update 资料已修改", username)
        return {"ok": True, "updated": True}
    logger.info("user=%s event=onboarding 档案已保存", username)
    return {"ok": True}


# ---------- 每日触点闭环（M4：文档 3.2 / 7.2 / 7.4 / 第九节） ----------

FEEDBACK_OPTIONS = ("完成了", "只完成一部分", "完全没完成", "建议仍然太难", "跳过")
CORRECT_TYPES = ("今晚更累", "时间更少", "不太舒服", "今天还行", "其实我做了",
                 "难度再低一点", "难度再高一点")   # 后两个是建议卡上的难度微调
# 「下班了」时的状态自述选项（生成前先问一句，语义与一击纠正一致）
OFFWORK_STATES = ("今晚更累", "时间更少", "不太舒服", "今天还行")

# 每用户一把锁：防止双击「下班了」并发生成两条当日记录（B9）
_offwork_locks: dict[int, threading.Lock] = {}
_locks_guard = threading.Lock()


def _user_lock(user_id: int) -> threading.Lock:
    with _locks_guard:
        return _offwork_locks.setdefault(user_id, threading.Lock())


def _compute_today_baseline(user_id: int) -> int:
    """按 7.4 档位规则从昨天（最近一条历史记录）推今天的档位。
    完成了 → +0（连续两天完成 → +1，封顶4）；只完成一部分/跳过 → 不变；
    完全没完成/未响应/建议仍然太难 → −1（地板0）。无历史 → 首夜起点 3。
    """
    last2 = db.get_last_records_before(user_id, clock.today(), limit=2)
    if not last2:
        return 3
    last = last2[0]
    level = last["baseline_level"] if last["baseline_level"] is not None else 3
    fb = last["feedback"]
    if fb == "完成了":
        if len(last2) > 1 and last2[1]["feedback"] == "完成了":
            level += 1  # 连续两天完成
    elif fb in ("完全没完成", "未响应", "建议仍然太难"):
        level -= 1
    # 只完成一部分 / 跳过 / 无反馈 → 不变
    return max(0, min(4, level))


def _run_and_save_today(user_id: int, username: str, record=None,
                        extra_conditions: list[str] | None = None,
                        offwork_state: str | None = None) -> dict:
    """跑 Agent 并写库。record 为 None 时新建当日记录，否则更新（纠正/自由输入重跑）。
    offwork_state：「下班了」时的状态自述（今晚更累/时间更少/不太舒服/今天还行），
    存进 conditions 后当天所有重生成都会带着它（上下文注入 + 安全扫描）。"""
    if record is None:
        level = _compute_today_baseline(user_id)
        conditions = {"来源": "offwork", "档位": level, "纠正": []}
        if offwork_state:
            conditions["下班状态"] = offwork_state
    else:
        level = record["baseline_level"] if record["baseline_level"] is not None else 3
        conditions = json.loads(record["conditions_json"] or "{}")
    state_line = (f"用户下班时自述状态：{conditions['下班状态']}"
                  if conditions.get("下班状态") else None)
    if state_line:
        extra_conditions = [state_line] + (extra_conditions or [])

    # 输入侧安全检测（V2 三层架构入口）：当天全部自由输入 + 纠正项 + 档案（健康备注/结构化病况）。
    # 当天说过的危险信号对当晚整晚有效——之后不管因为什么重新生成建议，都带着这个等级。
    texts = db.get_free_inputs(user_id, clock.today()) + list(conditions.get("纠正", []))
    if conditions.get("下班状态"):
        texts.append(conditions["下班状态"])   # "不太舒服"这类状态自述也要过安全检测
    profile = db.get_profile(user_id)
    safety_state = safety.assess(
        texts,
        health_note=profile["health_note"] if profile else None,
        chronic_condition=profile["chronic_condition"] if profile else None,
    )
    if safety_state["final_level"] != "none" or safety_state["hits"]:
        conditions["安全"] = {"level": safety_state["final_level"],
                              "命中": safety_state["hits"], "L2": safety_state["l2"]}

    # 慢性病档位封顶（V2 文档 4.3 镣铐二）：baseline 上限 3（正常人 4）
    if safety_state["chronic_managed"] and level > 3:
        logger.info("user=%s 慢性病档位封顶：%s→3", username, level)
        level = 3
        conditions["档位"] = 3

    advice, _trace = agent.run_agent(user_id, username, baseline_level=level,
                                     extra_conditions=extra_conditions,
                                     safety_state=safety_state)
    conditions["agent_notes"] = advice.get("agent_notes", [])

    # 严重疾病劝退入口之二（V2 文档 4.4）：自由输入/纠正里【自述】严重疾病 →
    # 当晚已按 danger 出安全模式建议，这里写入档案（后续 /api/state 转 rejected 视图）。
    # 问句（"我是不是得了心脏病？"）只触发当晚安全模式，不写档案——劝退是持久动作。
    if "severe" in safety_state["categories"] and profile is not None:
        severe_words = [h.split("(")[0] for h in safety_state["hits"] if "严重疾病" in h]
        if safety.is_severe_self_report("\n".join(texts), severe_words):
            db.mark_severe(user_id, f"用户自述（{'、'.join(severe_words)}）")
            advice["severe_notice"] = safety.SEVERE_NOTICE
            logger.warning("user=%s 自述严重疾病 %s，已标记劝退", username, severe_words)
        else:
            logger.info("user=%s 疑问语境提及严重疾病词 %s，仅当晚安全模式、不写档案",
                        username, severe_words)
    if record is None:
        db.insert_daily_record(
            user_id, clock.today(),
            conditions_json=json.dumps(conditions, ensure_ascii=False),
            advice_json=json.dumps(advice, ensure_ascii=False),
            baseline_level=level,
        )
    else:
        db.update_record_advice(
            record["id"],
            advice_json=json.dumps(advice, ensure_ascii=False),
            conditions_json=json.dumps(conditions, ensure_ascii=False),
        )
    return advice


@app.post("/api/offwork")
async def api_offwork(request: Request, payload: dict | None = None):
    """「下班了」：先查昨日待回执（7.2），有则让前端先收回执；否则生成今晚建议。
    payload 可带 {"state": "今晚更累"}——生成前前端先问一句今晚状态，作为初始条件注入。"""
    user_id = _current_user_id(request)
    if user_id is None:
        return JSONResponse(status_code=401, content={"error": "未登录"})
    profile = db.get_profile(user_id)
    if profile is None:
        return JSONResponse(status_code=400, content={"error": "请先完成 onboarding"})
    if profile["severe_flag"]:
        # 严重疾病劝退（V2 文档 4.4）：所有建议生成接口拒绝执行
        return {"rejected": True, "message": safety.SEVERE_NOTICE}
    username = db.get_username(user_id)
    today = clock.today()

    # 双击/并发防护：同一用户的「下班了」串行执行（B9）
    with _user_lock(user_id):
        # 当天已有建议 → 直接返回（界面回到建议卡片；双击的第二次会走到这）
        existing = db.get_daily_record(user_id, today)
        if existing and existing["advice_json"]:
            return {"advice": json.loads(existing["advice_json"]), "already_generated": True}

        # 昨日及更早的未回执：只对最近一天弹回执，更早的标「未响应」（沉默也是数据）
        pending = db.get_pending_records_before(user_id, today)
        if pending:
            latest = pending[-1]
            for old in pending[:-1]:
                db.set_feedback(old["id"], "未响应")
                logger.info("user=%s record=%s vday=%s 标记为未响应", username, old["id"], old["vday"])
            return {
                "need_feedback": True,
                "record": {
                    "record_id": latest["id"],
                    "vday": latest["vday"],
                    "advice": json.loads(latest["advice_json"]) if latest["advice_json"] else None,
                },
            }

        state = (payload or {}).get("state")
        state = state if state in OFFWORK_STATES else None
        logger.info("user=%s event=offwork 触发建议生成 状态自述=%s", username, state)
        advice = _run_and_save_today(user_id, username, offwork_state=state)
        return {"advice": advice}


@app.post("/api/feedback")
async def api_feedback(payload: dict, request: Request):
    """昨晚回执四档 + 跳过。允许当天内改回执（点错了后悔）：
    若今天的建议已生成且新回执导致档位变化，按新档位重跑 Agent 并返回新建议。
    """
    user_id = _current_user_id(request)
    if user_id is None:
        return JSONResponse(status_code=401, content={"error": "未登录"})
    feedback = payload.get("feedback")
    record = db.get_record_by_id(payload.get("record_id") or -1)
    if record is None or record["user_id"] != user_id:
        return JSONResponse(status_code=400, content={"error": "记录不存在"})
    if feedback not in FEEDBACK_OPTIONS:
        return JSONResponse(status_code=400, content={"error": f"feedback 需为 {FEEDBACK_OPTIONS} 之一"})
    db.set_feedback(record["id"], feedback)
    username = db.get_username(user_id)
    logger.info("user=%s event=feedback record=%s vday=%s 反馈=%s",
                username, record["id"], record["vday"], feedback)

    # 改回执的连锁：今天建议已生成 + 新回执算出的档位不同 → 重算档位并重出今晚建议
    today_rec = db.get_daily_record(user_id, clock.today())
    if today_rec and today_rec["advice_json"] and record["vday"] < clock.today():
        new_level = _compute_today_baseline(user_id)
        if new_level != today_rec["baseline_level"]:
            logger.info("user=%s 回执修改导致档位 %s→%s，重出今晚建议",
                        username, today_rec["baseline_level"], new_level)
            conditions = json.loads(today_rec["conditions_json"] or "{}")
            conditions["档位"] = new_level
            rec = dict(today_rec) | {
                "conditions_json": json.dumps(conditions, ensure_ascii=False),
                "baseline_level": new_level,
            }
            db_conn = db.get_conn()
            try:
                db_conn.execute("UPDATE daily_records SET baseline_level = ? WHERE id = ?",
                                (new_level, today_rec["id"]))
                db_conn.commit()
            finally:
                db_conn.close()
            extra = [f"用户一击纠正：{c}" for c in conditions.get("纠正", [])]
            extra.append("用户刚修改了昨晚的回执，今晚档位已按新回执重算")
            advice = _run_and_save_today(user_id, username, record=rec, extra_conditions=extra)
            return {"ok": True, "feedback": feedback, "advice": advice, "new_level": new_level}
    return {"ok": True, "feedback": feedback}


@app.post("/api/correct")
async def api_correct(payload: dict, request: Request):
    """一击纠正：把纠正项作为新条件，重跑 Agent 主循环（文档 3.2）。"""
    user_id = _current_user_id(request)
    if user_id is None:
        return JSONResponse(status_code=401, content={"error": "未登录"})
    ctype = payload.get("type")
    if ctype not in CORRECT_TYPES:
        return JSONResponse(status_code=400, content={"error": f"type 需为 {CORRECT_TYPES} 之一"})
    p = db.get_profile(user_id)
    if p is not None and p["severe_flag"]:
        return {"rejected": True, "message": safety.SEVERE_NOTICE}
    record = db.get_daily_record(user_id, clock.today())
    if record is None or not record["advice_json"]:
        return JSONResponse(status_code=400, content={"error": "今天还没有建议，先点「下班了」"})
    username = db.get_username(user_id)
    logger.info("user=%s event=correct type=%s 重跑建议", username, ctype)

    # 难度微调（V2 追加）：只动今晚档位。措辞不进安全检测文本（"难度再高一点"不是
    # 风险信号，不会被组合规则拦截）；上限受档位表约束——正常 4、慢性病 3（四镣铐）。
    if ctype in ("难度再低一点", "难度再高一点"):
        old_level = record["baseline_level"] if record["baseline_level"] is not None else 3
        cap = 3 if safety.assess([], health_note=p["health_note"] if p else None,
                                 chronic_condition=p["chronic_condition"] if p else None
                                 )["chronic_managed"] else 4
        new_level = max(0, min(cap, old_level + (1 if ctype == "难度再高一点" else -1)))
        if new_level == old_level:
            msg = ("今晚已经是最低档了——再低就只剩好好吃饭、早点睡了" if ctype == "难度再低一点"
                   else "结合你的情况，今晚这个量已经是合适的上限了，先按这个来")
            return {"ok": True, "message": msg, "advice": json.loads(record["advice_json"])}
        record = dict(record)
        conditions = json.loads(record["conditions_json"] or "{}")
        conditions["档位"] = new_level
        record["baseline_level"] = new_level
        record["conditions_json"] = json.dumps(conditions, ensure_ascii=False)
        conn = db.get_conn()
        try:
            conn.execute("UPDATE daily_records SET baseline_level = ? WHERE id = ?",
                         (new_level, record["id"]))
            conn.commit()
        finally:
            conn.close()
        direction = "低" if ctype == "难度再低一点" else "高"
        extra = [f"用户一击纠正：{c}" for c in conditions.get("纠正", [])]
        extra.append(f"用户希望今晚建议的难度再{direction}一点（档位已从 {old_level} 调整为 {new_level}）")
        advice = _run_and_save_today(user_id, username, record=record, extra_conditions=extra)
        return {"advice": advice, "new_level": new_level}

    # 「其实我做了」＝昨晚的回执报错了：把昨天记录改成「完成了」，档位跟着重算（B7）
    yesterday_updated = False
    record = dict(record)
    if ctype == "其实我做了":
        last = db.get_last_records_before(user_id, clock.today(), limit=1)
        if last and last[0]["feedback"] != "完成了":
            db.set_feedback(last[0]["id"], "完成了")
            yesterday_updated = True
            logger.info("user=%s 「其实我做了」：昨日(%s)回执改为完成了", username, last[0]["vday"])
            new_level = _compute_today_baseline(user_id)
            if new_level != record["baseline_level"]:
                conn = db.get_conn()
                try:
                    conn.execute("UPDATE daily_records SET baseline_level = ? WHERE id = ?",
                                 (new_level, record["id"]))
                    conn.commit()
                finally:
                    conn.close()
                record["baseline_level"] = new_level

    conditions = json.loads(record["conditions_json"] or "{}")
    corrections = conditions.get("纠正", [])
    corrections.append(ctype)
    conditions["纠正"] = corrections
    conditions["档位"] = record["baseline_level"]
    record["conditions_json"] = json.dumps(conditions, ensure_ascii=False)
    extra = [f"用户一击纠正：{c}" for c in corrections]
    advice = _run_and_save_today(user_id, username, record=record, extra_conditions=extra)
    return {"advice": advice, "yesterday_updated": yesterday_updated}


@app.post("/api/free_input")
async def api_free_input(payload: dict, request: Request):
    """自由输入一句话：先存库；当天已有建议则重跑，否则轻确认（文档 3.2 / 第九节）。"""
    user_id = _current_user_id(request)
    if user_id is None:
        return JSONResponse(status_code=401, content={"error": "未登录"})
    text = str(payload.get("text", "")).strip()
    if not text:
        return JSONResponse(status_code=400, content={"error": "内容不能为空"})
    p = db.get_profile(user_id)
    if p is not None and p["severe_flag"]:
        return {"rejected": True, "message": safety.SEVERE_NOTICE}
    username = db.get_username(user_id)
    fid = db.insert_free_input(user_id, clock.today(), clock.now().strftime("%H:%M"), text)
    logger.info("user=%s event=free_input text=%s", username, text[:50])

    record = db.get_daily_record(user_id, clock.today())
    if record is None or not record["advice_json"]:
        return {"ok": True, "message": "记下了。晚上生成建议时会考虑进去。"}

    conditions = json.loads(record["conditions_json"] or "{}")
    extra = [f"用户一击纠正：{c}" for c in conditions.get("纠正", [])]
    extra.append("用户刚补充了一句话（见【今天已知】的自由输入），请把它纳入考虑")
    advice = _run_and_save_today(user_id, username, record=record, extra_conditions=extra)
    if advice.get("agent_notes"):
        db.set_free_input_extracted(
            fid, json.dumps(advice["agent_notes"], ensure_ascii=False))
    return {"advice": advice}


# ---------- Agent 轨迹（M6：文档 9.4 / 11.2，演示侧栏用） ----------

def _trace_step_label(r: dict) -> str | None:
    """把一轮 trace 变成人话，如「检索了《膳食指南2022》」。"""
    tool = r.get("tool")
    if tool == "search_reference":
        args = r.get("args", {})
        return f"检索手册（{args.get('category', 'any')}）：{args.get('query', '')}"
    if tool == "calc_body_metrics":
        return "计算身体指标（基础代谢/消耗/蛋白质量级）"
    if tool == "get_user_history":
        return "查看最近几天的记录"
    if tool == "log_note":
        return f"记下条件：{r.get('args', {}).get('text', '')}"
    if "output" in r:
        return "给出结论"
    if "error" in r:
        return "模型调用失败，使用兜底建议"
    return None


@app.get("/api/agent_trace")
async def api_agent_trace(request: Request):
    """最近一次 Agent 循环的轨迹：直接读 logs/trace/ 里该用户最新的文件。"""
    user_id = _current_user_id(request)
    if user_id is None:
        return JSONResponse(status_code=401, content={"error": "未登录"})
    username = db.get_username(user_id)
    # 严格匹配 "日期_用户名_时分秒.json"，避免用户名互为前缀时（a 和 a_b）串轨迹。
    # 按文件真实修改时间取最新——文件名里是虚拟时间，演示中时钟往回拨会让名字排序失真。
    pattern = re.compile(rf"^\d{{4}}-\d{{2}}-\d{{2}}_{re.escape(username)}_\d{{4,6}}\.json$")
    files = sorted(
        (f for f in config.TRACE_DIR.glob("*.json") if pattern.match(f.name)),
        key=lambda f: f.stat().st_mtime,
    )
    if not files:
        return {"trace": None}
    data = json.loads(files[-1].read_text(encoding="utf-8"))
    steps = [s for s in (_trace_step_label(r) for r in data.get("rounds", [])) if s]

    # 安全层动作追加进 steps（V2 3.4：侧栏能展示"硬防线拦了什么"；none 且无命中时不加行）
    sf = data.get("safety") or {}
    if sf.get("L1命中"):
        steps.append("安全层：词表命中 " + "、".join(sf["L1命中"]))
    if sf.get("L2"):
        steps.append(f"安全层：分类器判定 {sf['L2']['level']}（{sf['L2'].get('reason', '')}）")
    if sf.get("等级") and sf["等级"] != "none":
        steps.append(f"安全层：最终等级 {sf['等级']}，输出按安全模式强制执行")
    for rw in sf.get("L3改写") or []:
        steps.append(f"安全层：{rw}")

    return {
        "trace": {
            "virtual_time": data.get("virtual_time"),
            "steps": steps,
            "duration_s": data.get("duration_s"),
            "sources": (data.get("final") or {}).get("sources", []),
            "safety": sf or None,
        }
    }


# ---------- 食物照片（M5：文档 7.3） ----------

# 视觉模型提示词：不确定就写最可能的，不要拒答
VISION_PROMPT = """识别图中食物，输出 JSON（不要输出其他内容）：
{"名称": "整份食物的概括名称", "估计分量": "大概分量", "类别": "粉面/炸物/米饭/火锅/烧烤/甜品饮料/轻食/家常 之一", "备注": "包含的主要食材，逗号分隔"}
不确定就写最可能的，不要拒答。"""


@app.post("/api/meal/photo")
async def api_meal_photo(file: UploadFile, request: Request):
    """上传食物照片 → 视觉模型转结构化记录存库 → 一句轻确认（不触发完整建议）。"""
    user_id = _current_user_id(request)
    if user_id is None:
        return JSONResponse(status_code=401, content={"error": "未登录"})
    username = db.get_username(user_id)
    image_bytes = await file.read()
    if not image_bytes:
        return JSONResponse(status_code=400, content={"error": "文件为空"})

    # 原图落盘（meal_records.image_path）
    uploads = config.DATA_DIR / "uploads"
    uploads.mkdir(parents=True, exist_ok=True)
    t = clock.now()
    image_path = uploads / f"{t.strftime('%Y-%m-%d_%H%M%S')}_{username}.jpg"
    image_path.write_bytes(image_bytes)

    try:
        raw = llm.vision(image_bytes, VISION_PROMPT, mime=file.content_type or "image/jpeg")
        m = re.search(r"\{.*\}", raw or "", re.S)
        food = json.loads(m.group(0)) if m else None
    except Exception:
        food = None
    if not food or not food.get("名称"):
        # 兜底：识别失败也不报错、不阻塞（文档：演示中途不允许白屏或报错）
        logger.error("user=%s vision识别失败，走兜底", username)
        food = {"名称": "一餐饭", "估计分量": "未知", "类别": "家常", "备注": "识别失败，仅记录用餐"}

    db_conn = db.get_conn()
    try:
        cur = db_conn.execute(
            "INSERT INTO meal_records (user_id, vday, vtime, source, food_json, image_path) "
            "VALUES (?, ?, ?, 'photo', ?, ?)",
            (user_id, clock.today(), t.strftime("%H:%M"),
             json.dumps(food, ensure_ascii=False), str(image_path)),
        )
        meal_id = cur.lastrowid
        db_conn.commit()
    finally:
        db_conn.close()
    logger.info("user=%s event=meal_photo 识别=%s", username, food.get("名称"))
    # 轻确认，不评判、不展开（文档 7.3）；带 meal_id 供「记错了？删除」
    return {"ok": True, "meal_id": meal_id, "food": food,
            "message": f"记下了：{food['名称']}。晚上给你参考。"}


@app.post("/api/meal/delete")
async def api_meal_delete(payload: dict, request: Request):
    """删除一条饮食记录（识别错了/传错图时的回退）。"""
    user_id = _current_user_id(request)
    if user_id is None:
        return JSONResponse(status_code=401, content={"error": "未登录"})
    meal_id = payload.get("meal_id") or -1
    db_conn = db.get_conn()
    try:
        row = db_conn.execute(
            "SELECT * FROM meal_records WHERE id = ? AND user_id = ?", (meal_id, user_id)
        ).fetchone()
        if row is None:
            return JSONResponse(status_code=400, content={"error": "记录不存在"})
        db_conn.execute("DELETE FROM meal_records WHERE id = ?", (meal_id,))
        db_conn.commit()
    finally:
        db_conn.close()
    if row["image_path"]:
        from pathlib import Path
        p = Path(row["image_path"])
        try:
            # 只删 uploads 目录下的文件，防止 image_path 被构造成其他路径
            if p.is_file() and p.parent == config.DATA_DIR / "uploads":
                p.unlink()
        except OSError:
            logger.warning("删除图片文件失败：%s", row["image_path"])
    logger.info("user_id=%s event=meal_delete meal_id=%s", user_id, meal_id)
    return {"ok": True, "message": "已删除这条饮食记录"}


# ---------- 虚拟时钟（文档第八节） ----------

@app.post("/api/clock")
async def api_clock(payload: dict):
    """时间控制：{advance_hours: 2} / {advance_days: 1} / {set: "..."} / {reset: true}"""
    try:
        if "advance_hours" in payload:
            t = clock.advance_hours(float(payload["advance_hours"]))
        elif "advance_days" in payload:
            t = clock.advance_days(int(payload["advance_days"]))
        elif "set" in payload:
            t = clock.set_time(str(payload["set"]))
        elif payload.get("reset"):
            t = clock.reset()
        else:
            return JSONResponse(
                status_code=400,
                content={"error": "参数需为 advance_hours / advance_days / set / reset 之一"},
            )
    except (ValueError, TypeError) as e:
        return JSONResponse(status_code=400, content={"error": f"参数不合法：{e}"})
    return {"virtual_now": t.isoformat(), "display": clock.now_display()}


# ---------- 状态（文档 7.1） ----------

@app.get("/api/state")
async def api_state(request: Request):
    """前端开屏先问后端"现在该显示哪个视图"。
    M1 判定：未登录 → 401（前端跳登录页）；无档案 → onboarding；有档案 → home。
    advice 视图与 pending_feedback 的判定在 M4 补全（依赖 daily_records 写入逻辑）。
    """
    user_id = _current_user_id(request)
    if user_id is None:
        return JSONResponse(status_code=401, content={"error": "未登录"})
    pending_feedback = None
    yesterday_feedback = None
    state_profile = db.get_profile(user_id)
    if state_profile is not None and state_profile["severe_flag"]:
        # 严重疾病劝退视图（V2 文档 4.4）：语气抱歉而非拒斥；可去「我的资料」修改（误报纠正通道）
        return {"view": "rejected", "message": safety.SEVERE_NOTICE,
                "virtual_now": clock.now().isoformat(),
                "virtual_now_display": clock.now_display(), "vday": clock.today()}
    if state_profile is None:
        view = "onboarding"
        today_advice = None
    else:
        record = db.get_daily_record(user_id, clock.today())
        today_advice = json.loads(record["advice_json"]) if record and record["advice_json"] else None
        view = "advice" if today_advice else "home"
        pending = db.get_pending_records_before(user_id, clock.today())
        if pending:
            latest = pending[-1]
            pending_feedback = {
                "record_id": latest["id"], "vday": latest["vday"],
                "advice": json.loads(latest["advice_json"]) if latest["advice_json"] else None,
            }
        # 昨晚已回执的记录：供前端显示「昨晚记为：X（点错了？改）」
        last = db.get_last_records_before(user_id, clock.today(), limit=1)
        if last and last[0]["feedback"] and last[0]["feedback"] != "未响应":
            lf = last[0]
            yesterday_feedback = {
                "record_id": lf["id"], "vday": lf["vday"], "feedback": lf["feedback"],
                "advice": json.loads(lf["advice_json"]) if lf["advice_json"] else None,
            }
    conn = db.get_conn()
    try:
        meals = conn.execute(
            "SELECT vtime, source, food_json FROM meal_records "
            "WHERE user_id = ? AND vday = ? ORDER BY vtime",
            (user_id, clock.today()),
        ).fetchall()
    finally:
        conn.close()
    return {
        "view": view,
        "pending_feedback": pending_feedback,
        "yesterday_feedback": yesterday_feedback,
        "today_advice": today_advice,
        "today_meals": [
            {"vtime": m["vtime"], "source": m["source"],
             "food": json.loads(m["food_json"]) if m["food_json"] else None}
            for m in meals
        ],
        "virtual_now": clock.now().isoformat(),
        "virtual_now_display": clock.now_display(),
        "vday": clock.today(),
    }


# 静态托管前端（放在所有 API 路由之后，"/" 直接出 index.html）
app.mount("/", StaticFiles(directory=config.FRONTEND_DIR, html=True), name="frontend")
