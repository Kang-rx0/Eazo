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
                "candidates": []}

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
              "hits": hits, "locked": locked_level != "none", "candidates": candidates}
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


def enforce(advice: dict, safety_state: dict, tools_called: list[str]) -> tuple[dict, list[str]]:
    """L3 输出后校验（V2 文档 3.3）。按最终安全等级对主 Agent 的输出 JSON 做强制改写。

    S0 骨架：只补齐输出结构的新字段（3.4），不做任何改写；返回 (advice, rewrites)，
    rewrites 是改写记录（字符串列表），记入 trace 和日志。
    S1 填充：danger/caution 强制改写、就医话术拼接、数字校验、诊断断言过滤。
    """
    rewrites: list[str] = []
    level = safety_state.get("final_level", "none")

    # 输出 JSON 新增字段（3.4）：safety_level / avoid / see_doctor；safety_flag 保留兼容
    advice.setdefault("avoid", [])
    advice.setdefault("see_doctor", None)
    advice["safety_level"] = level
    if level != "none":
        advice["safety_flag"] = True

    # ---- 以下 S1 实现 ----
    # danger：move/eat 置 null + avoid 清单 + 固定就医话术 + judgement 改休息表述
    # caution/chronic_exercise：move 置 null + "先咨询医生"
    # caution/medication：附固定转介话术 + 删药理解释句
    # crisis：整卡替换为求助文案（占位 {{CRISIS_HOTLINE}}）
    # 数字校验（所有等级）：无 calc_body_metrics 却出现 kcal/克/mmHg/mmol → 删数字短语
    # 诊断断言过滤（所有等级）：'是/可能是/得了+疾病名' → 删除或替换

    if rewrites:
        logger.warning("安全L3改写 level=%s 改写=%s", level, rewrites)
    return advice, rewrites
