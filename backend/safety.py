# 安全边界核心逻辑（V2 文档三）。本文件只做三件事：
#   l1_scan       —— L1 硬词表扫描（纯代码，毫秒级）
#   merge_levels  —— 等级合并纯函数（代码优先，LLM 只能加严不能减轻）
#   enforce       —— L3 输出后校验（S0 只搭骨架，S1 填充强制改写/数字校验/诊断过滤）
# L2 专职分类器 safety_classify 在 S2 阶段加入本文件。
import logging
import re

from . import safety_rules as rules

logger = logging.getLogger(__name__)

# 类别 → 展示名（写日志/trace 用，让"硬防线拦了什么"一眼可读）
CATEGORY_DESC = {
    "acute": "急性危险信号",
    "crisis": "心理危机",
    "severe": "严重疾病",
    "chronic_exercise": "慢性病×运动意图",
    "medication": "用药咨询",
    "chronic_mention": "慢性病提及",
    "mental_low": "心理低落",
}

# 主类别的优先级：一段话同时命中多类时，取处理动作覆盖面最大的那个当主类别
_CATEGORY_PRIORITY = ["crisis", "severe", "acute", "chronic_exercise", "medication",
                      "chronic_mention", "mental_low"]


def _max_level(a: str, b: str) -> str:
    """两个等级取高（none < caution < danger < crisis）。"""
    return a if rules.LEVEL_ORDER[a] >= rules.LEVEL_ORDER[b] else b


def _contains_any(text: str, words: list[str]) -> list[str]:
    """返回 text 中出现的所有词（子串匹配，V2 文档 3.1：不上分词库）。"""
    return [w for w in words if w in text]


def l1_scan(text: str) -> dict:
    """L1 硬词表扫描。输入一段用户文本，输出结构化扫描结果：

    {
      "locked_level":    锁定下界——硬词/组合规则给出，任何模型无权降级（危险方向的地板）
      "candidate_level": 候选等级——软词给出，L2 可以结合上下文降到 none（否定式"不疼了"）
      "level":           max(locked, candidate) = 没有 L2 时的 L1 最终结果（保守，宁可误报）
      "category":        主类别（见 _CATEGORY_PRIORITY）
      "categories":      命中的全部类别
      "hits":            命中明细，如 "胸闷(急性红词/硬)"，直接进日志和 trace
      "locked":          locked_level 是否高于 none（True 表示 L2 只能加严）
      "candidates":      候选类别列表（S2 起交给 L2 裁决的部分）
    }
    """
    text = (text or "").strip()
    locked_level, candidate_level = "none", "none"
    categories: list[str] = []
    hits: list[str] = []
    candidates: list[str] = []

    if not text:
        return {"locked_level": "none", "candidate_level": "none", "level": "none",
                "category": None, "categories": [], "hits": [], "locked": False,
                "candidates": [], "chronic_words": []}

    # 1. 心理危机（硬）→ 锁 crisis
    for w in _contains_any(text, rules.CRISIS_HARD_WORDS):
        locked_level = _max_level(locked_level, "crisis")
        categories.append("crisis")
        hits.append(f"{w}(心理危机/硬)")

    # 2. 严重疾病 → 锁 danger（S4 起走劝退流程，S0 先保证当晚安全模式）
    for w in _contains_any(text, rules.SEVERE_DISEASE_WORDS):
        locked_level = _max_level(locked_level, "danger")
        categories.append("severe")
        hits.append(f"{w}(严重疾病/硬)")

    # 3. 急性红词（硬）→ 锁 danger；词表 + 间隔变体正则（"胸口有点闷"）
    for w in _contains_any(text, rules.ACUTE_HARD_WORDS):
        locked_level = _max_level(locked_level, "danger")
        categories.append("acute")
        hits.append(f"{w}(急性红词/硬)")
    for pattern, desc in rules.ACUTE_HARD_PATTERNS:
        m = re.search(pattern, text)
        if m and not any(m.group(0) in h for h in hits):  # 词表已命中同一片段就不重复记
            locked_level = _max_level(locked_level, "danger")
            categories.append("acute")
            hits.append(f"{m.group(0)}(急性红词/硬-{desc})")

    # 4. 组合规则：慢性病 × 运动意图 → 锁 caution（禁运动处方，基线用例 4 的头号风险）
    #    这是代码级确定性规则，不交 L2 裁决——L2 只能在此之上加严。
    chronic_hits = _contains_any(text, rules.CHRONIC_WORDS)
    if chronic_hits:
        exercise_hits = _contains_any(text, rules.EXERCISE_INTENT_WORDS)
        if exercise_hits:
            locked_level = _max_level(locked_level, "caution")
            categories.append("chronic_exercise")
            hits.append(f"{'+'.join(chronic_hits)}×{'+'.join(exercise_hits)}(慢性病×运动意图/组合)")
        else:
            # 慢性病单独提及：不惊扰（V2 用例"我有高血压"单句→记录+温和），只记候选给 L2
            categories.append("chronic_mention")
            candidates.append("chronic_mention")
            hits.append(f"{'+'.join(chronic_hits)}(慢性病提及/候选)")

    # 5. 组合规则：用药 → 锁 caution（不答药物问题，转介医生/药师，基线用例 5）
    med_hits = _contains_any(text, rules.MED_WORDS)
    if med_hits and (_contains_any(text, rules.MED_TAKE_VERBS)
                     or _contains_any(text, rules.QUESTION_HINTS)):
        locked_level = _max_level(locked_level, "caution")
        categories.append("medication")
        hits.append(f"{'+'.join(med_hits)}(用药/组合)")

    # 6. 急性软词（候选）→ candidate caution，S2 起由 L2 结合上下文裁决（可降到 none）
    #    只在没有更高的硬命中时才有记录意义，但明细照记（trace 里能看到全部命中）
    soft_hits = _contains_any(text, rules.ACUTE_SOFT_WORDS)
    # 去重：软词是硬词的子串时（如"胸口疼"含"疼"）不重复记——硬命中已覆盖
    soft_hits = [w for w in soft_hits
                 if not any(w in h.split("(")[0] and w != h.split("(")[0] for h in hits)]
    if soft_hits:
        candidate_level = _max_level(candidate_level, "caution")
        categories.append("acute_soft")
        candidates.append("acute_soft")
        hits.extend(f"{w}(急性软词/候选)" for w in soft_hits)

    # 7. 心理低落（候选）→ candidate none：保持 V1 温和降载行为，不惊扰；L2 上线后可升级
    low_hits = _contains_any(text, rules.MENTAL_LOW_WORDS)
    if low_hits:
        categories.append("mental_low")
        candidates.append("mental_low")
        hits.extend(f"{w}(心理低落/候选)" for w in low_hits)

    level = _max_level(locked_level, candidate_level)
    category = next((c for c in _CATEGORY_PRIORITY if c in categories), None)
    if category is None and "acute_soft" in categories:
        category = "acute"

    result = {"locked_level": locked_level, "candidate_level": candidate_level,
              "level": level, "category": category, "categories": categories,
              "hits": hits, "locked": locked_level != "none", "candidates": candidates,
              "chronic_words": chronic_hits}  # 命中的慢性病名，L3 拼话术用
    if hits:
        logger.info("安全L1命中 level=%s locked=%s 命中=%s 文本=%s",
                    level, locked_level, hits, text[:50])
    return result


def merge_levels(l1: dict, l2_level: str | None) -> str:
    """裁决合并纯函数（V2 文档 3.2）：代码优先，LLM 只能加严、不能减轻。

    - 硬命中（locked_level）是不可变下界：final 永远 >= locked_level。
    - L2 在场时：final = max(locked, L2)。L2 可以把软词候选降到 none（否定式"不疼了"），
      也可以把任何结果升级，但压不动锁定下界。
    - L2 缺席/失败时（l2_level=None）：final = max(locked, candidate)，即沿用 L1 的
      保守结果——分类器断网系统仍安全（宁可误报）。
    """
    if l2_level is None:
        return _max_level(l1["locked_level"], l1["candidate_level"])
    if l2_level not in rules.LEVEL_ORDER:
        # 非法输入按缺席处理，谁也别想用怪值绕过下界
        logger.warning("merge_levels 收到非法 L2 等级 %r，按 L2 缺席处理", l2_level)
        return _max_level(l1["locked_level"], l1["candidate_level"])
    return _max_level(l1["locked_level"], l2_level)


def assess(texts: list[str]) -> dict:
    """输入侧检测总入口：把一批用户文本（当天自由输入、纠正项等）合并扫描，产出 safety_state。

    S1 阶段只有 L1（L2 在此之后无条件缺席，merge 取保守结果）；S2 在这里接入 safety_classify。
    safety_state 是贯穿主流程的安全上下文，enforce/trace/日志都吃它。
    """
    joined = "\n".join(t for t in texts if t and t.strip())
    l1 = l1_scan(joined)
    final = merge_levels(l1, None)  # S2 起：L2 裁决候选后再合并
    return {"final_level": final, "category": l1["category"],
            "categories": l1["categories"], "hits": l1["hits"],
            "chronic_words": l1["chronic_words"], "l1": l1, "l2": None}


# ---- L3 固定话术（V2 文档五；后端拼接，永不指望模型写）----
# 危机文案：用户 2026-08-08 确认——不提供任何求助热线，只建议就医/咨询专业医生
CRISIS_JUDGEMENT = "听起来你现在很难受。今晚不用做任何事，好好休息。"
CRISIS_SEE_DOCTOR = ("如果这种感觉持续存在，或者你有伤害自己的念头，"
                     "请一定告诉信任的人，并尽快就医、咨询专业医生。")
CRISIS_STOP = "今晚只需要休息，能早点睡就早点睡"
SEE_DOCTOR_DANGER = "如果不适持续或加重，请尽快就医。"
SEE_DOCTOR_CAUTION = "如果不适再次出现或持续，请及时就医。"
SEE_DOCTOR_CHRONIC = "涉及{disease}的运动安排，请先咨询医生，今晚先以休息为主。"
SEE_DOCTOR_CHRONIC_GENERIC = "运动方案请先咨询医生，今晚先以休息为主。"
MEDICATION_NOTE = "用药相关的问题，请咨询医生或药师。"
REST_JUDGEMENT = "今晚先照顾好自己，好好休息。"

AVOID_DANGER = ["任何运动或体力活动", "熬夜硬撑"]
AVOID_CHRONIC = ["未经医生评估的运动"]
AVOID_CAUTION = ["剧烈或长时间的活动"]

# 会被数字校验删除的文本字段（advice 里模型写的自然语言字段）
_TEXT_FIELDS = ("judgement", "reason", "eat", "move", "stop")

# 营养数字（kcal/千卡/大卡/克/g）：本轮没调 calc_body_metrics 就一律删（基线用例 7 两次编造）
_NUTRI_NUM_RE = re.compile(r"[约大概≈~]*\d+(?:\.\d+)?\s*(?:kcal|千卡|大卡|克|g)(?![a-zA-Z0-9])")
# 医疗数字（mmHg/mmol/血压/血糖目标值）：无论模型怎么来的都删（V2 文档 4.3 数字禁区）
_MED_NUM_RE = re.compile(
    r"[约大概≈~]*\d+(?:\.\d+)?(?:\s*/\s*\d+(?:\.\d+)?)?\s*(?:mmHg|毫米汞柱|mmol/?L?)"
    r"|(?:血压|血糖)[^，。；！？]{0,6}?\d+(?:[./]\d+(?:\.\d+)?)*"
)
# 诊断断言（'是/可能是/得了 + 疾病名'句式）：疾病名表与 L1 共用（V2 文档 3.3）
_DIAG_RE = re.compile(
    r"(?:是|可能是|应该是|得了|患了|患上)[^，。；！？]{0,6}?(?:"
    + "|".join(map(re.escape, rules.CHRONIC_WORDS + rules.SEVERE_DISEASE_WORDS))
    + r")"
)
# 药物作用解释句：句子同时含"药"和作用类词就删（用药场景不解释药理，基线用例 5）
_DRUG_ACTION_WORDS = ("影响", "作用", "副作用", "耐受", "反应", "药效", "代谢", "吸收")
# danger 时 judgement 若仍是正向活动安排（"可安排轻度活动"）→ 替换为休息表述；
# 前置否定（"不可安排"）不算正向
_POSITIVE_ACT_RE = re.compile(r"(?<![不别没无])(?:可|能|适合|建议)[^，。；]{0,4}(?:安排|运动|锻炼|活动|走|拉伸)")


def _split_sentences(text: str) -> list[str]:
    """按中文句读切分（含逗号级），保留分隔符（删句时用）。
    切到逗号粒度是为了少删无辜内容："…可能是心脏病的信号，今晚先休息"只该删前半句。"""
    parts = re.split(r"(?<=[。；！？!?，,])", text)
    return [p for p in parts if p]


def _drop_sentences(text: str, should_drop, keep_placeholder: str | None = None) -> tuple[str, list[str]]:
    """删掉满足条件的句子，返回 (新文本, 被删句子)。keep_placeholder 非空时用它替换被删句。"""
    kept, dropped = [], []
    for s in _split_sentences(text):
        if should_drop(s):
            dropped.append(s)
            if keep_placeholder and keep_placeholder not in kept:
                kept.append(keep_placeholder)
        else:
            kept.append(s)
    return "".join(kept).strip("，；"), dropped


def _strip_field_numbers(advice: dict, regex: re.Pattern, why: str, rewrites: list[str]) -> None:
    """从所有文本字段里删掉 regex 命中的数字短语，记入 rewrites。"""
    for field in _TEXT_FIELDS:
        val = advice.get(field)
        if not isinstance(val, str):
            continue
        matches = regex.findall(val)
        if matches:
            advice[field] = regex.sub("", val).strip("，、 ")
            rewrites.append(f"{why}：{field} 删除数字短语 {matches}")


def enforce(advice: dict, safety_state: dict, tools_called: list[str]) -> tuple[dict, list[str]]:
    """L3 输出后校验（V2 文档 3.3）：按最终安全等级对主 Agent 的输出 JSON 做强制改写。

    检测可以用 LLM，执行必须是代码——这里的每一条改写都不依赖模型自觉。
    返回 (advice, rewrites)；rewrites 记入 trace 和日志。
    """
    rewrites: list[str] = []
    level = safety_state.get("final_level", "none")
    categories = safety_state.get("categories") or []

    # 输出 JSON 新增字段（3.4）：safety_level / avoid / see_doctor；safety_flag 保留兼容
    advice.setdefault("avoid", [])
    advice.setdefault("see_doctor", None)
    advice["safety_level"] = level
    if level != "none":
        advice["safety_flag"] = True

    # ---- 1. 等级驱动的强制改写 ----
    if level == "crisis":
        # 整卡替换为求助文案：不保留任何常规建议，语气温和不评判
        rewrites.append(f"crisis：整卡替换为求助文案（原judgement：{advice.get('judgement')}）")
        advice.update({
            "judgement": CRISIS_JUDGEMENT, "reason": None, "eat": None, "move": None,
            "stop": CRISIS_STOP, "sources": [], "avoid": [],
            "see_doctor": CRISIS_SEE_DOCTOR, "safety_flag": True,
        })
    elif level == "danger":
        # 不建议做什么 + 提醒就医，不给正向处方——连"走8分钟"都不给
        if advice.get("move"):
            rewrites.append(f"danger：撤掉运动安排（原：{advice['move']}）")
            advice["move"] = None
        if advice.get("eat"):
            rewrites.append(f"danger：撤掉饮食安排（原：{advice['eat']}）")
            advice["eat"] = None
        advice["avoid"] = list(AVOID_DANGER)
        advice["see_doctor"] = SEE_DOCTOR_DANGER
        j = advice.get("judgement") or ""
        if _POSITIVE_ACT_RE.search(j):
            rewrites.append(f"danger：judgement 含正向活动安排，替换为休息表述（原：{j}）")
            advice["judgement"] = REST_JUDGEMENT
    elif level == "caution":
        if "chronic_exercise" in categories:
            # 慢性病×运动意图：禁运动处方（基线用例 4 头号风险）
            if advice.get("move"):
                rewrites.append(f"caution/chronic：撤掉运动安排（原：{advice['move']}）")
            advice["move"] = None
            advice["avoid"] = list(dict.fromkeys(advice["avoid"] + AVOID_CHRONIC))
            chronic = safety_state.get("chronic_words") or []
            advice["see_doctor"] = (SEE_DOCTOR_CHRONIC.format(disease="、".join(chronic))
                                    if chronic else SEE_DOCTOR_CHRONIC_GENERIC)
        elif "medication" not in categories:
            # 急性软词等一般 caution（头晕已缓解/崴脚）：撤运动 + 复发就医提醒
            if advice.get("move"):
                rewrites.append(f"caution：撤掉运动安排（原：{advice['move']}）")
                advice["move"] = None
            advice["avoid"] = list(dict.fromkeys(advice["avoid"] + AVOID_CAUTION))
            advice["see_doctor"] = SEE_DOCTOR_CAUTION
        if "medication" in categories:
            # 用药：正常建议保留，但不答药物问题、不解释药理（转介医生/药师）
            for field in _TEXT_FIELDS:
                val = advice.get(field)
                if not isinstance(val, str):
                    continue
                new_val, dropped = _drop_sentences(
                    val, lambda s: "药" in s and any(w in s for w in _DRUG_ACTION_WORDS))
                if dropped:
                    rewrites.append(f"caution/medication：{field} 删除药物作用解释句 {dropped}")
                    advice[field] = new_val or None
            note = MEDICATION_NOTE
            advice["see_doctor"] = f"{advice['see_doctor']} {note}" if advice["see_doctor"] else note

    # ---- 2. 数字校验（所有等级都跑）----
    if "calc_body_metrics" not in tools_called:
        _strip_field_numbers(advice, _NUTRI_NUM_RE, "数字校验(未调calc_body_metrics)", rewrites)
    _strip_field_numbers(advice, _MED_NUM_RE, "数字校验(血压血糖类禁区)", rewrites)

    # ---- 3. 诊断断言过滤（所有等级都跑）----
    for field in _TEXT_FIELDS:
        val = advice.get(field)
        if not isinstance(val, str) or not _DIAG_RE.search(val):
            continue
        new_val, dropped = _drop_sentences(val, lambda s: bool(_DIAG_RE.search(s)),
                                           keep_placeholder="具体情况请就医判断。")
        rewrites.append(f"诊断断言过滤：{field} 替换断言句 {dropped}")
        advice[field] = new_val

    if rewrites:
        logger.warning("安全L3改写 level=%s 改写=%s", level, rewrites)
    return advice, rewrites
