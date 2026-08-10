# 判断页自由输入 → 「时间 / 精力 / 身体」三项校准的抽取（V3 判断页暂存台）。
#
# 为什么需要它：s-confirm 改成暂存台之后，用户在这一屏说的每一句话都只落在
# 「你补充的」列表里，三行判断纹丝不动——但用户说「胃不舒服」时，屏上「身体状况」
# 还写着"暂未确认"就是在说假话（那句话其实已经注入生成上下文了，只是没显示出来）。
# 本模块负责把明确说到的项写回判断行，让"我说的话被收到了"看得见。
#
# 两层，词表优先：
#   L1 规则层——纯代码、零成本、离线可用（没有 .env 也照常工作），命中即返回；
#   L2 模型层——只在规则层什么都没抽到时才跑一次。任何失败（无 key / 超时 / 输出
#              不合法）一律返回空字典，退化成"只记进补充列表"，绝不乱写。
#
# 硬约束：只抽"这句话明确说到的项"。没说到的项**不出现在返回值里**——判断行那边靠
# "键存不存在"决定要不要摘掉「估」徽标，凭空补一个键就等于替用户下了判断。
import json
import logging
import re

from . import llm, safety

logger = logging.getLogger(__name__)

# 三项的合法取值：必须与 s-confirm「改一下」抽屉里的芯片 data-val 完全一致，
# 否则写回判断行后再打开抽屉会选不中，也过不了后端 _map_calibration 的映射表。
ENERGY_VALUES = ("几乎没有", "很低", "还行")
BODY_VALUES = ("有明显不适", "没有明显不适")

# ---- 规则层：精力 ----
# 只收"说的是自己现在没劲了"的表达。不收「不累」「还行」这类否定/正向说法——
# 把"我不累"读成"精力还行"是推断而不是转述，交给 L2 更稳妥。
_ENERGY_NONE_WORDS = [   # 到"几乎没有"这一档：说的是已经动不了了
    "精疲力尽", "筋疲力尽", "一点力气都没有", "一点劲都没有", "没有一点力气",
    "累瘫", "累趴", "累垮", "动不了", "撑不住了", "废了", "透支",
]
_ENERGY_LOW_WORDS = [    # 到"很低"这一档：明确说累/困，但没到动不了
    "累死", "累惨", "好累", "太累", "很累", "特别累", "巨累", "累得",
    "疲惫", "疲乏", "疲劳", "没力气", "没劲", "乏力",
    "困死", "困得", "好困", "太困", "很困", "眼皮打架",
]

# ---- 规则层：时间 ----
_CN_DIGITS = {"零": 0, "一": 1, "两": 2, "二": 2, "三": 3, "四": 4, "五": 5,
              "六": 6, "七": 7, "八": 8, "九": 9, "十": 10}
_NUM = r"\d{1,3}|[零一两二三四五六七八九十]{1,3}"
# A 式：直接说预算——「今晚只有一个小时」「大概还有 40 分钟」「就剩半小时」。
#      必须带"还有/只有/只剩"这类前缀，否则「昨天睡了八小时」也会被当成今晚的预算。
_TIME_BUDGET_RE = re.compile(
    rf"(?:还有|只有|只剩|剩下|不到|就剩)\s*(?:大概|大约)?\s*({_NUM})\s*(?:个)?\s*(小时|钟头|分钟)")
_TIME_HALF_RE = re.compile(r"(?:还有|只有|只剩|剩下|不到|就剩)\s*(?:大概|大约)?\s*半\s*(?:个)?\s*(?:小时|钟头)")
# B 式：说到几点结束。折成分钟要靠睡点和通勤，见 _minutes_until_sleep。
#      两种说法的落点不一样，必须分开：说"到几点下班/走"是**离开公司**的时间，还要加通勤；
#      说"几点到家/回家"人已经在家了，再加一次通勤等于凭空吃掉半小时。
_TIME_LEAVE_RE = re.compile(
    rf"(?:加班|忙|开会|工作|干|弄)\s*到\s*({_NUM})\s*[点:：]\s*(半|\d{{2}})?")
_TIME_LEAVE2_RE = re.compile(
    rf"({_NUM})\s*[点:：]\s*(半|\d{{2}})?\s*(?:多)?\s*(?:才|才能|才会)?\s*(?:下班|结束|走|出发)")
_TIME_HOME_RE = re.compile(
    rf"({_NUM})\s*[点:：]\s*(半|\d{{2}})?\s*(?:多)?\s*(?:才|才能|才会)?\s*(?:到家|回家|才到)")


def _to_int(s: str) -> int | None:
    """把「40」或「九」「十」「十二」「二十」转成整数；认不出返回 None。"""
    s = s.strip()
    if s.isdigit():
        return int(s)
    if not s or any(c not in _CN_DIGITS for c in s):
        return None
    if len(s) == 1:
        return _CN_DIGITS[s]
    if s[0] == "十":                      # 十、十一、十二
        return 10 + (_CN_DIGITS[s[1]] if len(s) > 1 else 0)
    if len(s) == 2 and s[1] == "十":      # 二十、三十
        return _CN_DIGITS[s[0]] * 10
    if len(s) == 3 and s[1] == "十":      # 二十一
        return _CN_DIGITS[s[0]] * 10 + _CN_DIGITS[s[2]]
    return None


def _minutes_until_sleep(end_total: int, hint: dict, commute: int) -> int | None:
    """「忙到 end_total（当天 00:00 起算的分钟，可越过 1440）」→ 到家后离睡点还剩多少分钟。

    口径与 build_confirm_hint 完全一致：到家 = 结束时间 + 通勤，剩余 = 睡点 − 到家。
    用户说的就是"几点到家"时，调用方传 commute=0（人已经在家了，不能再加一次通勤）。
    跨零点只认两种情形：睡点本身在凌晨（如 01:00，档案里起床很晚的人），以及调用方
    已经把"十二点"折成次日的 end_total。睡点是 23:00 而人 23:30 才到家，那就是
    "今晚没时间了"→ 0，不是"再等 23.5 小时"。算不出返回 None。
    """
    try:
        sh, sm = map(int, hint["sleep_point"].split(":"))
    except (KeyError, ValueError, AttributeError):
        return None
    if not (0 <= end_total <= 36 * 60):
        return None
    home = end_total + max(0, commute)
    sleep = sh * 60 + sm
    if sh < 12:                # 睡点在凌晨 → 属于次日
        sleep += 24 * 60
    remaining = max(0, sleep - home)
    if remaining > 12 * 60:    # 超过 12 小时说明解析歪了，宁可不写
        return None
    return remaining


def _rule_time(text: str, hint: dict, commute: int) -> int | None:
    """规则层的时间抽取：A 式直接给预算，B 式按结束时间倒算。都没中返回 None。"""
    m = _TIME_BUDGET_RE.search(text)
    if m:
        n = _to_int(m.group(1))
        if n is not None:
            mins = n * 60 if m.group(2) in ("小时", "钟头") else n
            return mins if 0 <= mins <= 12 * 60 else None
    if _TIME_HALF_RE.search(text):        # 「就剩半小时」——半不是数字，单独一条
        return 30
    morning = any(w in text for w in ("早", "上午", "中午"))
    # 离开公司的说法要加通勤，到家的说法不加（见 _TIME_HOME_RE 注释）
    for pat, cm in ((_TIME_LEAVE_RE, commute), (_TIME_LEAVE2_RE, commute),
                    (_TIME_HOME_RE, 0)):
        m = pat.search(text)
        if not m:
            continue
        hour = _to_int(m.group(1))
        if hour is None or hour > 24:
            continue
        tail = m.group(2)
        minute = 30 if tail == "半" else (int(tail) if tail and tail.isdigit() else 0)
        # 下班场景说的都是晚上：「九点下班」= 21 点，「十二点」= 次日零点（不是中午）
        if not morning:
            if hour == 12:
                hour = 24
            elif hour < 12:
                hour += 12
        got = _minutes_until_sleep(hour * 60 + minute, hint, cm)
        if got is not None:
            return got
    return None


def rule_extract(text: str, hint: dict | None = None, commute: int = 0) -> dict:
    """规则层：纯代码、不调模型。返回只含"明确说到"的键的字典。"""
    out: dict = {}
    # 身体：直接复用安全 L1 的急性词表（硬词 + 软词）。这张表本来就是"这句话在说
    # 身上出事了"的判据，不另起炉灶；命中软词（如"不舒服""疼"）也算说到了身体。
    cats = set(safety.l1_scan(text)["categories"])
    if cats & {"acute", "acute_soft"}:
        out["body"] = "有明显不适"
    # 精力：先看"几乎没有"那档（更重的说法优先），再看"很低"
    if any(w in text for w in _ENERGY_NONE_WORDS):
        out["energy"] = "几乎没有"
    elif any(w in text for w in _ENERGY_LOW_WORDS):
        out["energy"] = "很低"
    # 时间：需要睡点和通勤才能倒算，缺 hint 就只试 A 式
    mins = _rule_time(text, hint or {}, commute)
    if mins is not None:
        out["time_budget_min"] = mins
    return out


_LLM_PROMPT = """你是一个信息抽取器，只做抽取，不做建议、不做判断。

用户刚说了一句话，描述今晚的状况。请判断这句话是否**明确说到**了以下三项，
只输出说到的项，没说到的项一律填 null——宁可漏，不可猜。

1. time_budget_min：今晚睡前还能自由支配多少分钟。只有当用户明确说了时长
   （"只有一小时"）或结束时间（"加班到九点"）时才填。参考：用户的睡点是 {sleep_point}，
   通勤 {commute} 分钟，当前估算剩余 {remaining} 分钟。填整数分钟。
2. energy：只能是 "几乎没有" / "很低" / "还行" 三者之一。用户明确说累/困/没劲才填低档，
   明确说状态不错才填 "还行"。没提到精力就填 null。
3. body：只能是 "有明显不适" / "没有明显不适" 二者之一。用户提到身体任何部位不适、
   疼痛、恶心、发烧等就填 "有明显不适"；明确说身体没问题才填 "没有明显不适"。

只输出 JSON，不要解释：{{"time_budget_min": null, "energy": null, "body": null}}

示例：
输入：胃有点胀 → {{"time_budget_min": null, "energy": null, "body": "有明显不适"}}
输入：今天开了一天会，脑子转不动了 → {{"time_budget_min": null, "energy": "很低", "body": null}}
输入：中午吃的火锅 → {{"time_budget_min": null, "energy": null, "body": null}}"""


def llm_extract(text: str, hint: dict | None = None, commute: int = 0) -> dict:
    """模型层：只在规则层什么都没抽到时调用。任何失败都返回 {}（调用方据此退化）。"""
    hint = hint or {}
    try:
        prompt = _LLM_PROMPT.format(
            sleep_point=hint.get("sleep_point", "未知"),
            commute=commute,
            remaining=hint.get("remaining_min", "未知"),
        )
        msg = llm.chat([{"role": "system", "content": prompt},
                        {"role": "user", "content": f"输入：{text}"}])
        m = re.search(r"\{.*\}", msg.content or "", re.S)
        data = json.loads(m.group(0))
        out: dict = {}
        tb = data.get("time_budget_min")
        if isinstance(tb, (int, float)) and not isinstance(tb, bool) and 0 <= tb <= 12 * 60:
            out["time_budget_min"] = int(tb)
        if data.get("energy") in ENERGY_VALUES:
            out["energy"] = data["energy"]
        if data.get("body") in BODY_VALUES:
            out["body"] = data["body"]
        return out
    except Exception:
        logger.warning("判断页抽取：模型层失败，本句只进补充列表（文本=%s）", text[:50],
                       exc_info=True)
        return {}


def extract(text: str, hint: dict | None = None, commute: int = 0) -> dict:
    """总入口：词表先兜，没兜住再让模型补一次。返回 {} 表示"这句话没说到三项里的任何一项"。"""
    got = rule_extract(text, hint, commute)
    if got:
        logger.info("判断页抽取：规则层命中 %s（文本=%s）", got, text[:50])
        return got
    got = llm_extract(text, hint, commute)
    if got:
        logger.info("判断页抽取：模型层命中 %s（文本=%s）", got, text[:50])
    return got
