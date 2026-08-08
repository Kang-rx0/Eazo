# 核心 Agent 循环（文档第五节 + 3.3）：单 Agent + 工具调用，最多 6 轮，带兜底。
import json
import logging
import re
import time
from datetime import datetime, timedelta

from . import clock, config, db, llm, safety, tools

logger = logging.getLogger(__name__)

MAX_ROUNDS = 6

# 系统提示词骨架（文档 5.1）
SYSTEM_PROMPT = """你是一个「最低自我照顾」助手，服务对象是下班后精力所剩无几的上班族。

你的任务：根据用户档案、今天的已知信息和参考手册，给出今晚的最低行动建议。

规则：
1. 输出永远是固定形状：今晚判断+理由 / 吃什么 / 动多久 / 几点停。任一行没有该说的就省略，不硬凑。
2. 只说"多少、到什么程度"，不给训练计划、不算卡路里、不做疾病判断。
3. 建议必须小：默认 10 分钟以内的轻活动。用户状态越差，要求越小，直到只剩"早点睡"。
   「几点停」要用用户档案里的起床时间倒推，尽量保证约 7 小时以上的睡眠机会（依据睡眠手册）；到家越晚，停得越早。档案没填起床时间就按常规 23:00 左右。
4. 理由行必须回显【用户档案】和【今天已知】里的真实条件（身体状态、通勤分钟数、到家时间等），让用户看到你是算过的。只允许使用上下文中真实出现的数字和条件，严禁编造。
5. 给建议前，用 search_reference 查参考手册，最终输出中给出所依据的来源名。
6. 不评判用户已经吃的东西，只往前看。饮食禁忌是硬约束，绝不突破。
   上下文若出现【口味偏好】：优先顺着用户的爱好给『最轻的改法』（少粉多菜、去皮、清汤多菜），而不是没收爱好换成别的；但优先级最低——医嘱、饮食禁忌、安全要求都压过偏好。
7. 如果用户提到 疼/晕/胸口不适/喘不上气，不给任何活动建议，建议休息、必要时就医。
   如果用户明确表达精疲力尽（如"累死了""累瘫了""一点力气都没有"）或加班到很晚，主动撤掉运动安排（move 置 null），只保留吃什么和几点停——今晚能好好吃饭、按时睡觉就已经达标。
   系统会在你之外做代码级安全检查，你的判断只会被它加严、不会被放宽；上下文若出现【安全状态】行，其中的限制必须无条件遵守。
8. 涉及热量/蛋白质量级时，用 calc_body_metrics 工具取数，不要自己心算；数字只用来定量级和方向。
   本轮没调用该工具，就绝对不要在输出里出现任何 kcal/克数——宁可不提数字。
9. 用户提到长期习惯或偏好（如"我习惯睡前喝杯热牛奶""我不爱吃香菜"），用 log_note 的 durable=true 记下来——它会永久保存，今后每天都会出现在【长期备注】里；今晚才有效的状态（累、加班、时间少）用 durable=false。
10. 最终输出必须是 JSON（格式见下），不要输出其他内容。
11. 上下文若出现【医嘱】行（硬约束，优先级高于一切手册建议）：建议不得与医嘱冲突；医嘱覆盖的方面（如吃什么、能不能动）以医嘱为准，你只做医嘱框架内的最小化安排；医嘱里若有药名/剂量，只说"按医嘱执行"，绝不复述、不解释药理。
    上下文若出现【慢性病档案】行：运动安排最多散步/拉伸级，绝不出现任何血压/血糖数值，饮食从清淡保守安排。

最终输出 JSON 格式：
{
  "judgement": "今晚判断，一句话",
  "reason": "理由，必须回显用户的具体条件",
  "eat": "吃什么的建议，没有就用 null",
  "move": "动多久的建议，没有就用 null",
  "stop": "几点停，如：23:00 放下手机",
  "sources": ["引用的参考手册名"],
  "safety_flag": false
}
（safety_flag 为 true 时表示出现了疼/晕/胸口不适等信号，此时 eat/move 置 null，只保留休息/就医提示。）"""

# 档位含义（文档 7.4），作为上下文告诉 Agent
BASELINE_DESC = {
    4: "15–20 分钟轻活动",
    3: "8–10 分钟",
    2: "5 分钟 / 几个拉伸",
    1: "只有「几点停」，不安排活动",
    0: "只说一句「少玩手机、早点睡」，不提任何要求",
}

# 爱吃的食物类别 → 最轻的改法（PRD 原表）。软参考：顺着爱好改，不没收爱好。
FAVORITE_FOOD_STRATEGIES = {
    "粉面类": "少主食多配菜、汤别喝完（比如螺蛳粉就少粉多菜）",
    "炸物快餐": "去皮、别配含糖饮料（比如炸鸡少吃点皮）",
    "盖饭便当": "调整菜和饭的比例",
    "火锅麻辣烫": "选清汤、多涮青菜、蘸料别调太厚",
    "烧烤夜宵": "挪个时机、控住分量",
    "甜品奶茶": "减糖/换无糖，当加餐别当正餐",
    "轻食沙拉": "提醒别只有菜没蛋白",
    "家常菜": "在现有习惯上给最轻的加法",
}

# 兜底默认建议（文档 3.3：任何失败路径演示不死）
FALLBACK_ADVICE = {
    "judgement": "今晚从简，做最小的一件事就够",
    "reason": "系统繁忙，先按通用的最低线来",
    "eat": None,
    "move": "饭后在楼下走 8 分钟",
    "stop": "23:00 放下手机",
    "sources": [],
    "safety_flag": False,
    "fallback": True,
}


def _fmt_profile(p) -> str:
    """把 profiles 行格式化成短句（文档 5.3）。"""
    parts = [
        f"下班时间 {p['off_work_start']}–{p['off_work_end']}，{p['overtime_freq']}",
        f"通勤单程约 {p['commute_min']} 分钟",
        f"上班时{p['work_body_state']}",
        f"晚上{p['cooking']}",
        f"运动基础：{p['exercise_base']}",
    ]
    if p["wake_time"]:
        parts.insert(2, f"平时 {p['wake_time']} 起床")
    if p["diet_restrictions"]:
        parts.append(f"饮食禁忌（硬约束）：{p['diet_restrictions']}")
    if p["health_note"]:
        parts.append(f"健康备注：{p['health_note']}")
    body = [
        f"性别{p['gender']}" if p["gender"] else None,
        f"{p['age']}岁" if p["age"] else None,
        f"{p['height_cm']}cm" if p["height_cm"] else None,
        f"{p['weight_kg']}kg" if p["weight_kg"] else None,
    ]
    body = [b for b in body if b]
    if body:
        parts.append("、".join(body))
    return "；".join(parts)


def _estimate_home_time(p) -> str:
    """按下班时间+通勤估算到家时间。"""
    try:
        end = datetime.strptime(p["off_work_end"], "%H:%M")
        home = end + timedelta(minutes=p["commute_min"] or 0)
        return home.strftime("%H:%M")
    except (ValueError, TypeError):
        return "未知"


def build_context(user_id: int, baseline_level: int, extra_conditions: list[str] | None = None,
                  safety_state: dict | None = None) -> str:
    """组装每次调用注入的上下文（文档 5.3；V2 3.5 追加【安全状态】行）。"""
    p = db.get_profile(user_id)
    history = tools.get_user_history(user_id, days=3)
    today = clock.today()

    today_meals = [m for m in history["饮食记录"] if m["日期"] == today]
    today_inputs = [i for i in history["用户自由输入"] if i["日期"] == today]
    recent = [r for r in history["每日建议与反馈"] if r["日期"] != today]

    user_notes = db.get_user_notes(user_id)
    lines = [
        f"【用户档案】{_fmt_profile(p)}",
        f"【长期备注】{'；'.join(user_notes) if user_notes else '（暂无）'}",
        f"【当前虚拟时间】{clock.now_display()}",
        f"【今天已知】到家时间估计 {_estimate_home_time(p)}"
        + (f"；已记录饮食：{json.dumps(today_meals, ensure_ascii=False)}" if today_meals else "；今天暂无饮食记录")
        + (f"；用户自由输入：{json.dumps(today_inputs, ensure_ascii=False)}" if today_inputs else "")
        + (f"；补充条件：{'；'.join(extra_conditions)}" if extra_conditions else ""),
        f"【最近3天】{json.dumps(recent, ensure_ascii=False) if recent else '无历史记录（首次使用）'}",
        f"【当前最低线档位】{baseline_level}（建议量级：{BASELINE_DESC[baseline_level]}；"
        f"档位表 4={BASELINE_DESC[4]} / 3={BASELINE_DESC[3]} / 2={BASELINE_DESC[2]} / "
        f"1={BASELINE_DESC[1]} / 0={BASELINE_DESC[0]}）",
    ]
    # 【口味偏好】注入（软参考，优先级最低）：带上每类的"最轻的改法"
    fav = (p["favorite_foods"] or "").strip() if "favorite_foods" in p.keys() else ""
    if fav:
        tips = [f"{c}（{FAVORITE_FOOD_STRATEGIES[c]}）" for c in fav.split(",")
                if c in FAVORITE_FOOD_STRATEGIES]
        if tips:
            lines.append("【口味偏好】（软参考，优先级最低：医嘱、饮食禁忌、安全要求都高于它）"
                         "用户爱吃：" + "；".join(tips))

    # 【慢性病档案】/【医嘱】注入（V2 文档 4.2/4.3）：档案登记的慢性病每晚都带着
    cc = (p["chronic_condition"] or "").strip() if "chronic_condition" in p.keys() else ""
    if cc and cc != "无" and not cc.startswith("严重疾病"):
        lines.append(f"【慢性病档案】用户登记有：{cc}。硬要求：运动安排最多散步/拉伸级；"
                     f"绝不出现任何血压/血糖数值；饮食按公开指南的慢病原则清淡保守安排。")
        if p["doctor_advice"]:
            lines.append(f"【医嘱】（硬约束，优先级高于一切手册建议）：{p['doctor_advice']}")

    # 【安全状态】注入（V2 文档 3.5）：让模型第一时间就不朝错误方向写；none 时不加行
    if safety_state:
        safety_line = safety.context_line(safety_state)
        if safety_line:
            lines.append(safety_line)
    return "\n".join(lines)


def _parse_advice(content: str):
    """解析最终 JSON：能 loads 且 judgement 和 stop 至少存在。失败返回 None。"""
    if not content:
        return None
    # 容错：剥掉 markdown 代码块围栏
    m = re.search(r"\{.*\}", content, re.S)
    if not m:
        return None
    try:
        advice = json.loads(m.group(0))
    except json.JSONDecodeError:
        return None
    if not isinstance(advice, dict) or not advice.get("judgement") or not advice.get("stop"):
        return None
    advice.setdefault("sources", [])
    advice.setdefault("safety_flag", False)
    return advice


def _exec_tool(name: str, args: dict, user_id: int, notes: list[str]):
    """执行一个工具调用，返回可 JSON 化的结果。
    任何工具抛异常都兜住返回错误信息给模型，绝不让整次请求 500（演示不死）。
    """
    try:
        if name == "search_reference":
            return tools.search_reference(args.get("query", ""), args.get("category", "any"))
        if name == "get_user_history":
            return tools.get_user_history(user_id, args.get("days", 3))
        if name == "log_note":
            note = args.get("text", "")
            durable = bool(args.get("durable", False))
            if note:
                notes.append(note)
                if durable:
                    added = db.add_user_note(user_id, clock.today(), note)
                    logger.info("user_id=%s log_note 长期备注%s：%s",
                                user_id, "新增" if added else "已存在", note)
                    return {"ok": True, "已记录": note, "长期保存": True}
            return {"ok": True, "已记录": note}
        if name == "calc_body_metrics":
            return tools.calc_body_metrics(user_id)
        return {"error": f"未知工具 {name}"}
    except Exception:
        logger.error("工具 %s 执行失败，返回错误给模型继续", name, exc_info=True)
        return {"error": f"工具 {name} 执行出错，请基于已有信息继续"}


def _save_trace(username: str, trace: dict) -> None:
    """轨迹落盘（文档 11.2）：一次运行一个缩进 JSON 文件。"""
    t = clock.now()
    # 文件名带秒，避免同一分钟内多次重跑（一击纠正）互相覆盖
    path = config.TRACE_DIR / f"{t.strftime('%Y-%m-%d')}_{username}_{t.strftime('%H%M%S')}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(trace, f, ensure_ascii=False, indent=2)
    logger.info("trace 已写入 %s", path)


def run_agent(user_id: int, username: str, baseline_level: int = 3,
              extra_conditions: list[str] | None = None,
              safety_state: dict | None = None) -> tuple[dict, dict]:
    """Agent 主循环（文档 3.3）。返回 (advice, trace)；任何失败路径返回兜底建议。
    safety_state：输入侧安全检测结果（safety.assess），出口处由 L3 强制执行；
    不传则按 none 处理——数字校验和诊断断言过滤仍然全量跑（所有等级都跑的硬防线）。
    """
    start = time.perf_counter()
    notes: list[str] = []
    if safety_state is None:
        safety_state = safety.assess([])
    context = build_context(user_id, baseline_level, extra_conditions, safety_state)
    messages = [{"role": "system", "content": SYSTEM_PROMPT + "\n\n" + context}]
    trace = {"user": username, "virtual_time": clock.now_display(),
             "context": context, "rounds": [], "final": None, "duration_s": None}
    advice = None
    parse_retry_used = False

    round_no = 0
    while round_no < MAX_ROUNDS:
        round_no += 1
        try:
            msg = llm.chat(messages, tools=tools.TOOL_DEFS)
        except Exception:
            advice = dict(FALLBACK_ADVICE)
            trace["rounds"].append({"round": round_no, "error": "模型调用失败，走兜底"})
            logger.error("user=%s agent round=%d 模型调用失败，走兜底", username, round_no)
            break

        if msg.tool_calls:
            # 模型要调工具 → 执行 → 结果塞回对话 → 下一轮
            messages.append({
                "role": "assistant", "content": msg.content or "",
                "tool_calls": [tc.model_dump() for tc in msg.tool_calls],
            })
            for tc in msg.tool_calls:
                try:
                    args = json.loads(tc.function.arguments or "{}")
                except json.JSONDecodeError:
                    args = {}
                result = _exec_tool(tc.function.name, args, user_id, notes)
                messages.append({
                    "role": "tool", "tool_call_id": tc.id,
                    "content": json.dumps(result, ensure_ascii=False),
                })
                trace["rounds"].append({
                    "round": round_no, "tool": tc.function.name, "args": args,
                    "result_brief": str(result)[:200],
                })
                logger.info("user=%s agent round=%d tool=%s args=%s",
                            username, round_no, tc.function.name, args)
            continue

        # 模型给了最终输出 → 校验 JSON
        advice = _parse_advice(msg.content)
        trace["rounds"].append({"round": round_no, "output": msg.content})
        if advice is not None:
            break
        if not parse_retry_used:
            # JSON 解析失败，重试 1 次（文档 3.3）
            parse_retry_used = True
            logger.warning("user=%s json解析失败，重试第1次", username)
            messages.append({"role": "assistant", "content": msg.content or ""})
            messages.append({"role": "user",
                             "content": "你的输出不是合法 JSON 或缺少 judgement/stop 字段。"
                                        "请只输出符合格式的 JSON，不要任何其他内容。"})
            continue
        advice = dict(FALLBACK_ADVICE)
        logger.error("user=%s json解析重试后仍失败，走兜底", username)
        break

    if advice is None:
        # 超过 6 轮还没结束 → 去掉工具，强制基于已有信息给结论（文档 3.3）
        logger.warning("user=%s agent 超过%d轮未结束，强制收敛", username, MAX_ROUNDS)
        messages.append({"role": "user",
                         "content": "不要再调用工具了。基于已有信息，直接输出最终 JSON 结论。"})
        try:
            msg = llm.chat(messages)  # 不带工具
            advice = _parse_advice(msg.content)
            trace["rounds"].append({"round": "force_final", "output": msg.content})
        except Exception:
            advice = None
        if advice is None:
            advice = dict(FALLBACK_ADVICE)
            logger.error("user=%s 强制收敛失败，走兜底", username)

    # L3 输出后校验（V2 安全边界）：按安全等级强制改写，兜底建议也不例外
    # （danger 时连兜底的"走 8 分钟"都必须撤——执行必须是代码，不依赖任何模型自觉）
    tools_called = [r["tool"] for r in trace["rounds"] if r.get("tool")]
    advice, rewrites = safety.enforce(advice, safety_state, tools_called)
    trace["safety"] = {"等级": safety_state["final_level"], "类别": safety_state.get("category"),
                       "L1命中": safety_state.get("hits", []), "L2": safety_state.get("l2"),
                       "L3改写": rewrites}

    # 慢性病固定尾注（V2 文档 4.3 镣铐三：后端拼接，不指望模型）；crisis 整卡替换时不加
    if safety_state.get("chronic_managed") and advice.get("safety_level") != "crisis":
        p = db.get_profile(user_id)
        has_advice = bool(p and "doctor_advice" in p.keys() and p["doctor_advice"])
        advice["disclaimer"] = (safety.CHRONIC_DISCLAIMER_WITH_ADVICE if has_advice
                                else safety.CHRONIC_DISCLAIMER)

    if notes:
        advice["agent_notes"] = notes
    trace["final"] = advice
    trace["duration_s"] = round(time.perf_counter() - start, 1)
    try:
        _save_trace(username, trace)
    except OSError:
        logger.error("trace 写入失败", exc_info=True)
    return advice, trace
