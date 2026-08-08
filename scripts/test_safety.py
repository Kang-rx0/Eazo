# 安全边界单元测试（纯 Python，不调模型）。随 S 阶段推进逐步扩充：
#   S0：L1 扫描 / 等级合并只升不降 / enforce 骨架
#   S1：L3 输出后校验——强制改写、话术拼接、数字校验、诊断断言过滤
#   S2：L2 专职分类器——输出解析校验、失败/断网回退 L1、assess 三层串联（模型调用全部 mock）
#   S3：【安全状态】上下文注入 + health_note 跨来源检测
# 运行：/opt/miniconda3/envs/Eazo/bin/python scripts/test_safety.py
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

# 让脚本能 import backend 包
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend import safety  # noqa: E402
from backend.agent import build_confirm_hint  # noqa: E402
from backend.safety import assess, enforce, l1_scan, merge_levels  # noqa: E402


class TestL1Scan(unittest.TestCase):
    """S0：L1 硬词表扫描。"""

    def test_硬词命中锁danger(self):
        # 基线用例 1：胸闷 + 喘不上气 → 两个硬词都命中，锁死 danger
        r = l1_scan("今天胸口有点闷，喘不上气")
        self.assertEqual(r["locked_level"], "danger")
        self.assertEqual(r["level"], "danger")
        self.assertTrue(r["locked"])
        self.assertEqual(r["category"], "acute")
        # "胸口【有点】闷"是间隔变体，由正则规则接住
        self.assertTrue(any("胸口有点闷" in h for h in r["hits"]))
        self.assertTrue(any("喘不上气" in h for h in r["hits"]))

    def test_硬词间隔变体(self):
        # 词表接不住的口语插入式说法，正则必须接住
        for t in ("胸口发闷", "心口一阵一阵疼", "喘不过来气"):
            r = l1_scan(t)
            self.assertEqual(r["locked_level"], "danger", msg=t)

    def test_心悸锁danger(self):
        # 基线用例 6：心悸是硬词
        r = l1_scan("最近老是心悸，我是不是得了心脏病？")
        self.assertEqual(r["locked_level"], "danger")
        # 同句还有严重疾病词"心脏病"，主类别按优先级取 severe
        self.assertIn("severe", r["categories"])
        self.assertIn("acute", r["categories"])

    def test_软词给候选_不锁定(self):
        # 基线用例 2：头晕（已缓解）→ 软词候选 caution，不锁定，留给 L2 裁决
        r = l1_scan("下班路上有点头晕，现在好些了")
        self.assertEqual(r["locked_level"], "none")
        self.assertEqual(r["candidate_level"], "caution")
        self.assertEqual(r["level"], "caution")  # 无 L2 时保守取 caution
        self.assertFalse(r["locked"])
        self.assertIn("acute_soft", r["candidates"])

    def test_否定式暂时误报_留给S2(self):
        # 已知局限（V2 文档 S0 验证条目）："不疼了"仍含软词"疼"，S0 会误报 caution。
        # 这是设计内的保守行为：候选等级 L2 可降，S2 上线后此用例应回到 none。
        r = l1_scan("以前跑步膝盖疼，现在不疼了")
        self.assertEqual(r["level"], "caution")   # S0 现状：误报
        self.assertFalse(r["locked"])              # 但没锁定——给 S2 留了纠正通道

    def test_慢性病x运动意图_组合锁caution(self):
        # 基线用例 4（头号风险）：高血压 + 想出汗 → 组合规则锁 caution，L2 无权降级
        r = l1_scan("我有高血压，今晚想多动一动出出汗")
        self.assertEqual(r["locked_level"], "caution")
        self.assertEqual(r["category"], "chronic_exercise")
        self.assertTrue(r["locked"])

    def test_慢性病单独提及_不惊扰(self):
        # "我有高血压"单句 → 只记候选，不升级（V2 新增用例：记录+温和，不惊扰）
        r = l1_scan("我有高血压")
        self.assertEqual(r["level"], "none")
        self.assertEqual(r["category"], "chronic_mention")
        self.assertIn("chronic_mention", r["candidates"])

    def test_用药组合锁caution(self):
        # 基线用例 5：在吃降压药 + 疑问 → 用药规则
        r = l1_scan("我在吃降压药，晚上跑步会不会有影响？")
        self.assertEqual(r["locked_level"], "caution")
        self.assertIn("medication", r["categories"])

    def test_心理危机锁crisis(self):
        r = l1_scan("感觉不想活了")
        self.assertEqual(r["locked_level"], "crisis")
        self.assertEqual(r["category"], "crisis")
        self.assertTrue(r["locked"])

    def test_心理低落_候选不升级(self):
        # 基线用例 9：低落走 V1 温和降载，L1 不升级（默认 none），只把候选交给未来的 L2
        r = l1_scan("最近心情很差，什么都不想干，觉得自己很没用")
        self.assertEqual(r["level"], "none")
        self.assertIn("mental_low", r["candidates"])
        self.assertTrue(any("心情很差" in h for h in r["hits"]))

    def test_严重疾病锁danger(self):
        # V2 文档 4.4 入口全覆盖：自由输入提到心梗史 → 当晚锁 danger（S4 起接劝退）
        r = l1_scan("我前年心梗过")
        self.assertEqual(r["locked_level"], "danger")
        self.assertEqual(r["category"], "severe")

    def test_正常输入零命中(self):
        # 正常路径零回归（V2 文档九）："中午吃了黄焖鸡"不得有任何命中
        r = l1_scan("中午吃了黄焖鸡")
        self.assertEqual(r["level"], "none")
        self.assertEqual(r["hits"], [])
        self.assertIsNone(r["category"])

    def test_正常运动表达零命中(self):
        # 没有慢性病词时，运动意图完全正常
        r = l1_scan("今晚想去跑步出出汗")
        self.assertEqual(r["level"], "none")
        self.assertEqual(r["hits"], [])

    def test_空文本(self):
        for t in ("", None, "   "):
            r = l1_scan(t)
            self.assertEqual(r["level"], "none")
            self.assertEqual(r["hits"], [])

    def test_软词是硬词子串时不重复记(self):
        # "疼得厉害"（硬）包含"疼"（软），命中明细里软词不重复出现
        r = l1_scan("腰疼得厉害")
        hard = [h for h in r["hits"] if "硬" in h]
        soft = [h for h in r["hits"] if h.startswith("疼(")]
        self.assertTrue(hard)
        self.assertEqual(soft, [])


class TestMergeLevels(unittest.TestCase):
    """S0：等级合并纯函数——代码优先，LLM 只能加严、不能减轻。"""

    def test_硬danger_L2无权降级(self):
        l1 = l1_scan("胸口闷得喘不上气")
        self.assertEqual(merge_levels(l1, "none"), "danger")
        self.assertEqual(merge_levels(l1, "caution"), "danger")

    def test_L2只能加严(self):
        l1 = l1_scan("我有高血压，今晚想出出汗")  # 锁 caution
        self.assertEqual(merge_levels(l1, "danger"), "danger")   # 升级：允许
        self.assertEqual(merge_levels(l1, "none"), "caution")    # 降级：压不动锁定下界

    def test_软词候选_L2可降到none(self):
        l1 = l1_scan("以前跑步膝盖疼，现在不疼了")  # 候选 caution，未锁定
        self.assertEqual(merge_levels(l1, "none"), "none")       # 否定式：L2 可以澄清
        self.assertEqual(merge_levels(l1, "danger"), "danger")   # 也可以加严

    def test_L2缺席_沿用L1保守结果(self):
        l1 = l1_scan("下班路上有点头晕")
        self.assertEqual(merge_levels(l1, None), "caution")      # 分类器断网仍安全
        l1 = l1_scan("中午吃了黄焖鸡")
        self.assertEqual(merge_levels(l1, None), "none")

    def test_crisis高于danger(self):
        l1 = l1_scan("不想活了")
        self.assertEqual(merge_levels(l1, "danger"), "crisis")

    def test_非法L2输入按缺席处理(self):
        l1 = l1_scan("胸闷")
        self.assertEqual(merge_levels(l1, "safe"), "danger")     # 怪值绕不过下界
        l1 = l1_scan("头晕")
        self.assertEqual(merge_levels(l1, "都没事"), "caution")


class TestEnforceSkeleton(unittest.TestCase):
    """S0：enforce 骨架——只补字段不改内容，正常路径零回归。"""

    def _advice(self):
        return {"judgement": "今晚从简", "reason": "通勤30分钟", "eat": "清淡晚餐",
                "move": "饭后走8分钟", "stop": "23:00 放下手机",
                "sources": ["手册A"], "safety_flag": False}

    def test_none等级_内容零改动(self):
        advice = self._advice()
        out, rewrites = enforce(dict(advice), {"final_level": "none"}, ["search_reference"])
        self.assertEqual(rewrites, [])
        # 原有字段一个都不能变（正常路径零回归是硬指标）
        for k, v in advice.items():
            self.assertEqual(out[k], v)
        # 新字段补齐（3.4）
        self.assertEqual(out["safety_level"], "none")
        self.assertEqual(out["avoid"], [])
        self.assertIsNone(out["see_doctor"])

    def test_非none等级_flag强制为true(self):
        out, _ = enforce(self._advice(), {"final_level": "danger"}, [])
        self.assertTrue(out["safety_flag"])
        self.assertEqual(out["safety_level"], "danger")


class TestEnforceL3(unittest.TestCase):
    """S1：L3 强制改写、话术拼接、数字校验、诊断断言过滤——全部代码执行，不依赖模型。"""

    def _advice(self, **kw):
        base = {"judgement": "今晚从简", "reason": "通勤30分钟", "eat": "清淡晚餐",
                "move": "饭后走8分钟", "stop": "23:00 放下手机",
                "sources": ["手册A"], "safety_flag": False}
        base.update(kw)
        return base

    def test_danger强制改写(self):
        # 基线用例 1/6 的目标行为：撤吃撤动 + 固定就医话术必须出现
        state = assess(["今天胸口有点闷，喘不上气"])
        out, rewrites = enforce(self._advice(), state, ["search_reference"])
        self.assertIsNone(out["move"])
        self.assertIsNone(out["eat"])
        self.assertEqual(out["see_doctor"], safety.SEE_DOCTOR_DANGER)
        self.assertEqual(out["avoid"], safety.AVOID_DANGER)
        self.assertTrue(out["safety_flag"])
        self.assertTrue(any("撤掉运动" in r for r in rewrites))

    def test_danger正向judgement替换为休息(self):
        state = assess(["胸口闷"])
        out, rewrites = enforce(
            self._advice(judgement="今晚可安排轻度活动，但需控制强度"), state, [])
        self.assertEqual(out["judgement"], safety.REST_JUDGEMENT)
        # 反例：本来就是休息表述（"暂停任何活动"）不动
        out2, _ = enforce(self._advice(judgement="今晚需立即暂停任何活动，优先休息"),
                          assess(["胸口闷"]), [])
        self.assertEqual(out2["judgement"], "今晚需立即暂停任何活动，优先休息")

    def test_chronic_exercise禁运动处方(self):
        # 基线用例 4 的目标行为：不得出现任何运动处方 + "先咨询医生"
        state = assess(["我有高血压，今晚想多动一动出出汗"])
        out, _ = enforce(self._advice(move="慢走或原地踏步8分钟"), state, [])
        self.assertIsNone(out["move"])
        self.assertEqual(out["eat"], "清淡晚餐")           # 饮食保留（caution 不撤吃）
        self.assertIn("高血压", out["see_doctor"])          # 话术带病名
        self.assertIn("咨询医生", out["see_doctor"])
        self.assertIn("未经医生评估的运动", out["avoid"])

    def test_medication转介且删药理句(self):
        # 基线用例 5 的目标行为：出现转介话术，输出不解释药理
        state = assess(["我在吃降压药，晚上跑步会不会有影响？"])
        out, rewrites = enforce(
            self._advice(judgement="今晚不建议跑步，降压药可能影响运动耐受与血压反应。早点休息。"),
            state, [])
        self.assertIn("咨询医生或药师", out["see_doctor"])
        self.assertNotIn("影响运动耐受", out["judgement"])   # 药理解释句被删
        self.assertIn("早点休息", out["judgement"])          # 无关句保留
        self.assertEqual(out["eat"], "清淡晚餐")             # 正常建议保留
        self.assertTrue(any("药物作用" in r for r in rewrites))

    def test_caution软词_撤运动加就医提醒(self):
        # 基线用例 2/8 的目标行为：move=null + "再次出现请就医"类提示
        state = assess(["下班路上有点头晕，现在好些了"])
        out, _ = enforce(self._advice(), state, [])
        self.assertIsNone(out["move"])
        self.assertEqual(out["see_doctor"], safety.SEE_DOCTOR_CAUTION)

    def test_crisis整卡替换(self):
        state = assess(["感觉不想活了"])
        out, rewrites = enforce(self._advice(), state, [])
        self.assertEqual(out["judgement"], safety.CRISIS_JUDGEMENT)
        self.assertIsNone(out["eat"])
        self.assertIsNone(out["move"])
        self.assertIn("就医", out["see_doctor"])
        # 用户已确认：不提供任何求助热线
        self.assertNotIn("热线", out["see_doctor"])
        self.assertNotIn("{{", out["see_doctor"])
        self.assertTrue(any("整卡替换" in r for r in rewrites))

    def test_数字校验_未调工具删营养数字(self):
        # 基线用例 7 的目标行为：不出现任何未经工具计算的数字（曾两次编造 1280/1300kcal）
        out, rewrites = enforce(
            self._advice(reason="不吃晚饭易低血糖；基础代谢约1300kcal，蛋白质需60克"),
            assess([]), ["search_reference"])
        self.assertNotIn("1300", out["reason"])
        self.assertNotIn("60克", out["reason"])
        self.assertIn("低血糖", out["reason"])              # 非数字内容保留
        self.assertTrue(any("数字校验" in r for r in rewrites))

    def test_数字校验_调了工具则放行(self):
        out, rewrites = enforce(
            self._advice(reason="基础代谢约1252kcal"), assess([]),
            ["search_reference", "calc_body_metrics"])
        self.assertIn("1252", out["reason"])
        self.assertEqual([r for r in rewrites if "数字校验" in r], [])

    def test_数字校验_血压血糖数字无条件删(self):
        # V2 文档 4.3 数字禁区：mmHg/mmol/血压血糖目标值，调没调工具都删
        out, rewrites = enforce(
            self._advice(reason="把血压控制在140/90mmHg以内，血糖不超过7.8"),
            assess([]), ["calc_body_metrics"])
        self.assertNotIn("140", out["reason"])
        self.assertNotIn("7.8", out["reason"])
        self.assertTrue(any("血压血糖" in r for r in rewrites))

    def test_数字校验_删除后不留空括号(self):
        # "少油（<5g）"删掉 5g 后不能留下"（<）"（meal 多餐实测时发现的残缺）
        out, _ = enforce(self._advice(eat="清炒绿叶菜，不加糖、少油（<5g），杂粮饭半碗"),
                         assess([]), [])
        self.assertNotIn("5g", out["eat"])
        self.assertNotIn("（<）", out["eat"])
        self.assertIn("少油", out["eat"])

    def test_数字校验_文献名年份不误删(self):
        # 《成人高血压食养指南(2023)》的"血压…2023"不是血压值（S7 回归发现的误删隐患）
        out, rewrites = enforce(
            self._advice(reason="依据《成人高血压食养指南(2023)》，晚餐清淡少盐"),
            assess([]), [])
        self.assertIn("2023", out["reason"])
        self.assertEqual([r for r in rewrites if "血压血糖" in r], [])

    # ---- V3 P0：血压/血糖数字"像读数才删"（队友反馈的误伤修复）----

    def _assert_untouched(self, sentence):
        """误伤句必须零改写：原句一字不动、无血压血糖类改写记录。"""
        out, rewrites = enforce(self._advice(reason=sentence),
                                assess([]), ["calc_body_metrics"])
        self.assertEqual(out["reason"], sentence)
        self.assertEqual([r for r in rewrites if "血压血糖" in r], [])

    def test_数字校验_P0误伤_时长不删(self):
        # 曾被删成"量完分钟"："血压再走10"命中旧第二分支
        self._assert_untouched("量完血压再走10分钟")

    def test_数字校验_P0误伤_时刻不删(self):
        # 曾被删成"高点后不建议剧烈运动"／"睡前测个:30 上床"
        self._assert_untouched("高血压人群晚上8点后不建议剧烈运动")
        self._assert_untouched("睡前测个血压 22:30 上床")

    def test_数字校验_P0误伤_版年不删(self):
        # 不带括号书名号的文献名：曾被删成"成人高版"
        self._assert_untouched("成人高血压食养指南2023版建议清淡饮食")

    def test_数字校验_P0读数形态仍删(self):
        # 140/90 是血压读数形态，无单位也必须删
        out, rewrites = enforce(self._advice(reason="血压140/90"),
                                assess([]), ["calc_body_metrics"])
        self.assertNotIn("140", out["reason"])
        self.assertTrue(any("血压血糖" in r for r in rewrites))

    def test_数字校验_P0语境词仍删(self):
        # 取值语境词（控制在/不超过…）+ 数字必须删（现有单测句拆开各验一遍）
        out, rewrites = enforce(self._advice(reason="把血压控制在140/90mmHg以内"),
                                assess([]), ["calc_body_metrics"])
        self.assertNotIn("140", out["reason"])
        self.assertTrue(any("血压血糖" in r for r in rewrites))
        out2, rewrites2 = enforce(self._advice(reason="血糖不超过7.8"),
                                  assess([]), ["calc_body_metrics"])
        self.assertNotIn("7.8", out2["reason"])
        self.assertTrue(any("血压血糖" in r for r in rewrites2))

    def test_数字校验_P0血糖紧邻小数仍删(self):
        # "血糖7.8"：紧邻（≤2字）小数是读数
        out, rewrites = enforce(self._advice(reason="血糖7.8"),
                                assess([]), ["calc_body_metrics"])
        self.assertNotIn("7.8", out["reason"])
        self.assertTrue(any("血压血糖" in r for r in rewrites))

    def test_诊断断言过滤(self):
        # 基线用例 6 的目标行为：不出现疾病断言（"可能是心脏病"）
        out, rewrites = enforce(
            self._advice(judgement="反复心悸可能是心脏病的信号，今晚先休息。"),
            assess([]), [])
        self.assertNotIn("可能是心脏病", out["judgement"])
        self.assertIn("具体情况请就医判断", out["judgement"])
        self.assertIn("今晚先休息", out["judgement"])        # 非断言句保留
        self.assertTrue(any("诊断断言" in r for r in rewrites))

    def test_正常输出零改动(self):
        # 正常路径零回归（硬指标）：无安全信号、无违规数字 → 原字段一个都不变
        advice = self._advice()
        out, rewrites = enforce(dict(advice), assess(["中午吃了黄焖鸡"]), ["search_reference"])
        self.assertEqual(rewrites, [])
        for k, v in advice.items():
            self.assertEqual(out[k], v)

    def test_兜底建议在danger下也被撤(self):
        # 执行必须是代码：连系统兜底的"走 8 分钟"都不许在 danger 时出现
        from backend.agent import FALLBACK_ADVICE
        out, _ = enforce(dict(FALLBACK_ADVICE), assess(["胸口闷喘不上气"]), [])
        self.assertIsNone(out["move"])
        self.assertEqual(out["see_doctor"], safety.SEE_DOCTOR_DANGER)


class _FakeMsg:
    """伪造 llm.chat 的返回消息。"""
    def __init__(self, content):
        self.content = content
        self.tool_calls = None


class TestSafetyClassify(unittest.TestCase):
    """S2：L2 分类器的输出解析与失败回退（模型调用 mock，不走网络）。"""

    def _l1(self, text=""):
        return l1_scan(text)

    def test_正常解析(self):
        with patch("backend.safety.llm.chat", return_value=_FakeMsg(
                '{"level":"caution","category":"acute","reason":"头晕刚缓解"}')):
            r = safety.safety_classify("下班路上有点头晕，现在好些了", self._l1("头晕"))
        self.assertEqual(r, {"level": "caution", "category": "acute", "reason": "头晕刚缓解"})

    def test_容错_markdown围栏也能解析(self):
        with patch("backend.safety.llm.chat", return_value=_FakeMsg(
                '```json\n{"level":"none","category":"none","reason":"正常"}\n```')):
            r = safety.safety_classify("中午吃了黄焖鸡", self._l1())
        self.assertEqual(r["level"], "none")

    def test_非法等级返回None(self):
        with patch("backend.safety.llm.chat", return_value=_FakeMsg(
                '{"level":"safe","category":"none","reason":"x"}')):
            self.assertIsNone(safety.safety_classify("随便", self._l1()))

    def test_非JSON输出返回None(self):
        with patch("backend.safety.llm.chat", return_value=_FakeMsg("我觉得没什么问题")):
            self.assertIsNone(safety.safety_classify("随便", self._l1()))

    def test_调用异常返回None(self):
        with patch("backend.safety.llm.chat", side_effect=RuntimeError("断网")):
            self.assertIsNone(safety.safety_classify("随便", self._l1()))

    def test_非法类别置空但等级保留(self):
        with patch("backend.safety.llm.chat", return_value=_FakeMsg(
                '{"level":"caution","category":"发烧类","reason":"x"}')):
            r = safety.safety_classify("发烧", self._l1("发烧"))
        self.assertEqual(r["level"], "caution")
        self.assertIsNone(r["category"])


class TestAssess(unittest.TestCase):
    """S2：assess 三层串联——L2 裁决候选、加严兜底、断网退 L1、锁定跳过。"""

    def test_否定式_L2澄清后不再误报(self):
        # S0 记录的已知误报，S2 修复目标："以前跑步膝盖疼，现在不疼了" → none
        with patch("backend.safety.llm.chat", return_value=_FakeMsg(
                '{"level":"none","category":"none","reason":"旧伤已恢复"}')):
            state = assess(["以前跑步膝盖疼，现在不疼了"])
        self.assertEqual(state["final_level"], "none")
        self.assertEqual(state["l2"]["level"], "none")

    def test_用例2_软词候选被L2确认为caution(self):
        with patch("backend.safety.llm.chat", return_value=_FakeMsg(
                '{"level":"caution","category":"acute","reason":"今天发生过"}')):
            state = assess(["下班路上有点头晕，现在好些了"])
        self.assertEqual(state["final_level"], "caution")
        self.assertEqual(state["category"], "acute")

    def test_L2加严_词表漏掉的危机说法(self):
        # "撑不住了"不在硬词表里（L1=none），L2 语义兜底可加严到 crisis
        with patch("backend.safety.llm.chat", return_value=_FakeMsg(
                '{"level":"crisis","category":"crisis","reason":"难以为继的念头"}')):
            state = assess(["感觉撑不住了，不想再继续下去了"])
        self.assertEqual(state["l1"]["level"], "none")      # 词表确实没接住
        self.assertEqual(state["final_level"], "crisis")     # L2 兜底加严
        self.assertEqual(state["category"], "crisis")

    def test_断网退L1仍安全(self):
        # V2 文档 S2 验证条目：分类器故意断网 → 沿用 L1 保守结果
        with patch("backend.safety.llm.chat", side_effect=RuntimeError("断网")):
            state = assess(["下班路上有点头晕，现在好些了"])
        self.assertIsNone(state["l2"])
        self.assertEqual(state["final_level"], "caution")    # L1 候选保守生效
        with patch("backend.safety.llm.chat", side_effect=RuntimeError("断网")):
            state = assess(["我有高血压，今晚想出出汗"])
        self.assertEqual(state["final_level"], "caution")    # 组合锁不受影响

    def test_L2无权降级锁定结果(self):
        # 组合规则锁 caution，L2 就算说 none 也压不动
        with patch("backend.safety.llm.chat", return_value=_FakeMsg(
                '{"level":"none","category":"none","reason":"没事"}')):
            state = assess(["我有高血压，今晚想多动一动出出汗"])
        self.assertEqual(state["final_level"], "caution")
        self.assertIn("chronic_exercise", state["categories"])

    def test_L1锁danger时跳过L2(self):
        with patch("backend.safety.llm.chat") as mock_chat:
            state = assess(["今天胸口有点闷，喘不上气"])
        mock_chat.assert_not_called()                        # 锁死的等级不浪费一次调用
        self.assertEqual(state["final_level"], "danger")

    def test_空文本不调L2(self):
        with patch("backend.safety.llm.chat") as mock_chat:
            state = assess([])
        mock_chat.assert_not_called()
        self.assertEqual(state["final_level"], "none")


class TestS3ContextAndHealthNote(unittest.TestCase):
    """S3：【安全状态】行生成 + health_note 跨来源检测。"""

    def test_none不注入(self):
        state = assess(["中午吃了黄焖鸡"]) if False else {"final_level": "none"}
        self.assertIsNone(safety.context_line(state))

    def test_danger注入(self):
        line = safety.context_line({"final_level": "danger", "categories": ["acute"]})
        self.assertIn("【安全状态】", line)
        self.assertIn("danger", line)
        self.assertIn("不要给出任何饮食或运动安排", line)

    def test_chronic注入带病名(self):
        line = safety.context_line({"final_level": "caution",
                                    "categories": ["chronic_exercise"],
                                    "chronic_words": ["高血压"]})
        self.assertIn("高血压", line)
        self.assertIn("不要给出任何运动安排", line)
        self.assertIn("咨询医生", line)

    def test_medication注入(self):
        line = safety.context_line({"final_level": "caution", "categories": ["medication"]})
        self.assertIn("不要回答任何药物问题", line)

    def test_crisis注入(self):
        line = safety.context_line({"final_level": "crisis", "categories": ["crisis"]})
        self.assertIn("crisis", line)
        self.assertIn("不要给出任何常规建议", line)

    def test_caution通用注入(self):
        line = safety.context_line({"final_level": "caution", "categories": ["acute"]})
        self.assertIn("不要给出任何运动安排", line)

    def test_健康备注慢性病_跨来源组合(self):
        # S3 新能力：备注写了高血压，今晚输入只说想出汗（没提病）→ 组合规则照样触发
        with patch("backend.safety.llm.chat", return_value=_FakeMsg(
                '{"level":"caution","category":"chronic_exercise","reason":"慢性病想运动"}')):
            state = assess(["今晚想多动一动出出汗"], health_note="有高血压，医生说要注意")
        self.assertEqual(state["final_level"], "caution")
        self.assertIn("chronic_exercise", state["categories"])
        self.assertIn("高血压", state["chronic_words"])

    def test_健康备注慢性病_无文本不调L2不惊扰(self):
        # 只有备注、今晚没说任何话 → 不调 L2（省调用），等级 none，走四镣铐管理路径
        with patch("backend.safety.llm.chat") as mock_chat:
            state = assess([], health_note="有高血压")
        mock_chat.assert_not_called()
        self.assertEqual(state["final_level"], "none")
        self.assertTrue(state["chronic_managed"])
        self.assertEqual(state["chronic_profile"], ["高血压"])

    def test_健康备注急性软词不算今晚信号(self):
        # 备注"腰不好，久坐容易疼"描述长期状态，"疼"不得作为今晚的急性候选
        with patch("backend.safety.llm.chat", return_value=_FakeMsg(
                '{"level":"none","category":"none","reason":"正常"}')):
            state = assess(["中午吃了黄焖鸡"], health_note="腰不好，久坐容易疼")
        self.assertEqual(state["final_level"], "none")
        self.assertNotIn("acute_soft", state["categories"])

    def test_健康备注严重疾病词_S3暂不掺入(self):
        # 备注里的严重疾病词留给 S4 劝退流程；S3 不因它进入 danger（避免无 UI 的突兀锁死）
        with patch("backend.safety.llm.chat", return_value=_FakeMsg(
                '{"level":"none","category":"none","reason":"正常"}')):
            state = assess(["中午吃了黄焖鸡"], health_note="有心脏病")
        self.assertEqual(state["final_level"], "none")


class TestS4ChronicTwoTier(unittest.TestCase):
    """S4：慢性病两档规则（2026-08-08 与用户确认）+ 结构化病况解析。"""

    _L2_NONE = '{"level":"none","category":"none","reason":"正常"}'

    def test_档案慢性病_温和意图_不锁走四镣铐(self):
        # 档案登记高血压 + 今晚只说想散散步 → 不锁 caution，chronic_managed 放行温和档
        with patch("backend.safety.llm.chat", return_value=_FakeMsg(self._L2_NONE)):
            state = assess(["今晚想散散步"], chronic_condition="高血压")
        self.assertEqual(state["final_level"], "none")
        self.assertNotIn("chronic_exercise", state["categories"])
        self.assertTrue(state["chronic_managed"])

    def test_档案慢性病_强度意图_仍锁caution(self):
        # 档案登记高血压 + 想出汗 → 病名并入扫描，组合锁 caution（L2 说 none 也压不动）
        with patch("backend.safety.llm.chat", return_value=_FakeMsg(self._L2_NONE)):
            state = assess(["今晚想多动一动出出汗"], chronic_condition="高血压")
        self.assertEqual(state["final_level"], "caution")
        self.assertIn("chronic_exercise", state["categories"])

    def test_档案慢性病_笼统运动词按强度算(self):
        # "想去运动"没说强度 → 保守按强度档拦（宁可误报）
        with patch("backend.safety.llm.chat", return_value=_FakeMsg(self._L2_NONE)):
            state = assess(["今晚想去运动"], chronic_condition="2型糖尿病")
        self.assertEqual(state["final_level"], "caution")

    def test_文本新自述慢性病_温和意图也拦(self):
        # 聊天里新自述的慢性病不适用两档：当晚病情未验证，维持组合锁（用例 4 不回归）
        with patch("backend.safety.llm.chat", return_value=_FakeMsg(self._L2_NONE)):
            state = assess(["我有糖尿病，今晚想在家动一动"])
        self.assertEqual(state["final_level"], "caution")
        self.assertIn("chronic_exercise", state["categories"])

    def test_病况自述解析(self):
        # 2026-08-08 改版：病况是用户自由填写的原文，分类判断全在后台词表
        with patch("backend.safety.llm.chat") as m:
            self.assertEqual(assess([], chronic_condition="高血压五六年了")["chronic_profile"],
                             ["高血压"])           # 原文里的词表命中
            self.assertEqual(assess([], chronic_condition="有高血压，还有点痛风")
                             ["chronic_profile"], ["高血压", "痛风"])   # 多病共存
            self.assertEqual(assess([], chronic_condition="2型糖尿病")["chronic_profile"],
                             ["糖尿病"])
            self.assertEqual(assess([], chronic_condition="萎缩性胃炎，老毛病了")
                             ["chronic_profile"], ["萎缩性胃炎"])  # 词表没有的按原文保守管理
            self.assertEqual(assess([], chronic_condition="前年心肌梗死")["chronic_profile"],
                             [])                    # 严重疾病词走劝退，不入慢病管理
            self.assertEqual(assess([], chronic_condition="无")["chronic_profile"], [])
            m.assert_not_called()

    def test_病况自述severe派生(self):
        # db.upsert_profile 的 severe_flag 用词表扫描原文派生
        from backend import safety_rules
        hit = lambda cc: any(w in cc for w in safety_rules.SEVERE_DISEASE_WORDS)
        self.assertTrue(hit("前年心肌梗死"))
        self.assertTrue(hit("装了心脏起搏器"))
        self.assertTrue(hit("怀孕三个月"))
        self.assertFalse(hit("高血压五六年了"))
        self.assertFalse(hit("2型糖尿病"))

    def test_严重疾病_自述与问句区分(self):
        # 自述 → 写档案劝退；问句 → 只当晚安全模式（劝退是持久动作，不适用"宁可误报"）
        self.assertTrue(safety.is_severe_self_report("对了，我有心脏病", ["心脏病"]))
        self.assertTrue(safety.is_severe_self_report("我前年心梗过", ["心梗"]))
        self.assertFalse(safety.is_severe_self_report("最近老是心悸，我是不是得了心脏病？", ["心脏病"]))
        self.assertFalse(safety.is_severe_self_report("这会不会是心脏病", ["心脏病"]))
        self.assertFalse(safety.is_severe_self_report("我这是心脏病吗", ["心脏病"]))

    def test_慢性病尾注常量无占位符(self):
        for text in (safety.SEVERE_NOTICE, safety.CHRONIC_DISCLAIMER,
                     safety.CHRONIC_DISCLAIMER_WITH_ADVICE):
            self.assertNotIn("{{", text)
            self.assertNotIn("热线", text)   # 用户确认：不提供任何求助热线


class TestOffworkCalibrationB2(unittest.TestCase):
    """V3 B2：/api/offwork calibration 的映射（backend.main 纯函数，不起服务、不碰库）。"""

    def setUp(self):
        from backend.main import _map_calibration, _resolve_offwork_payload
        self.map_c = _map_calibration
        self.resolve = _resolve_offwork_payload

    def test_映射_身体不适(self):
        state, store = self.map_c({"body": "有明显不适"}, 90)
        self.assertEqual(state, "不太舒服")
        self.assertEqual(store["校准"]["body"], "有明显不适")
        self.assertNotIn("剩余分钟", store)

    def test_映射_精力低两档(self):
        for e in ("几乎没有", "很低"):
            state, store = self.map_c({"energy": e, "body": "没有明显不适"}, 90)
            self.assertEqual(state, "今晚更累", e)

    def test_映射_时间预算只紧不松(self):
        # 比估算紧 → 记剩余分钟；比估算松 → 不记（且无其他输入时与 {} 完全一致）
        state, store = self.map_c({"time_budget_min": 45}, 90)
        self.assertIsNone(state)
        self.assertEqual(store["剩余分钟"], 45)
        self.assertEqual(self.map_c({"time_budget_min": 120}, 90), (None, None))

    def test_映射_还行且无其他(self):
        state, store = self.map_c({"energy": "还行", "body": "没有明显不适",
                                   "time_budget_min": None}, 90)
        self.assertEqual(state, "今天还行")
        # 还行 + 时间收紧 → 不写下班状态，只记剩余分钟
        state2, store2 = self.map_c({"energy": "还行", "time_budget_min": 30}, 90)
        self.assertIsNone(state2)
        self.assertEqual(store2["剩余分钟"], 30)

    def test_映射_全默认与空等价(self):
        self.assertEqual(self.map_c({"time_budget_min": None, "energy": None,
                                     "body": "暂未确认"}, 90), (None, None))
        self.assertEqual(self.resolve({}, 90), (None, None))
        self.assertEqual(self.resolve(None, 90), (None, None))

    def test_映射_body优先于energy(self):
        state, store = self.map_c({"body": "有明显不适", "energy": "几乎没有"}, 90)
        self.assertEqual(state, "不太舒服")
        self.assertIn("精力几乎没有", store["校准补充行"])

    def test_同传时state优先(self):
        state, store = self.resolve(
            {"state": "今天还行", "calibration": {"body": "有明显不适"}}, 90)
        self.assertEqual(state, "今天还行")
        self.assertIsNone(store)

    def test_非法值忽略(self):
        # 未知枚举值不进映射；time_budget 传布尔/负数不记
        self.assertEqual(self.map_c({"energy": "满血", "body": "不知道"}, 90), (None, None))
        self.assertEqual(self.map_c({"time_budget_min": True}, 90), (None, None))
        self.assertEqual(self.map_c({"time_budget_min": -5}, 90), (None, None))
        # 原样存储只留契约三键（防前端塞杂物进 conditions）
        _, store = self.map_c({"body": "有明显不适", "杂物": "x"}, 90)
        self.assertEqual(set(store["校准"].keys()), {"time_budget_min", "energy", "body"})


class TestSwitchPlanB3(unittest.TestCase):
    """V3 B3：/api/correct「换一种做法」——类型合法性、注入行拼接（纯函数）、词表零命中。"""

    def setUp(self):
        from backend.main import CORRECT_TYPES, _switch_plan_line
        self.types = CORRECT_TYPES
        self.line = _switch_plan_line

    def test_类型合法性(self):
        self.assertIn("换一种做法", self.types)
        # 旧类型一个不少（白名单加项不影响旧项）
        for t in ("今晚更累", "时间更少", "不太舒服", "今天还行", "其实我做了",
                  "难度再低一点", "难度再高一点"):
            self.assertIn(t, self.types)

    def test_上一版摘要拼接(self):
        l = self.line({"eat": "清淡晚餐", "move": "走8分钟"})
        self.assertIn("目标和量级保持不变", l)
        self.assertIn("吃=清淡晚餐", l)
        self.assertIn("动=走8分钟", l)
        # eat/move 为 null 时对应段省略
        l2 = self.line({"eat": "清淡晚餐", "move": None})
        self.assertIn("吃=清淡晚餐", l2)
        self.assertNotIn("动=", l2)
        l3 = self.line({"eat": None, "move": None})
        self.assertNotIn("（上一版：", l3)   # 双 null 时整个摘要括号段省略

    def test_措辞词表零命中(self):
        # 牵连检查 1：措辞不含运动意图词/软词，不会被组合规则拦
        r = l1_scan("换一种做法")
        self.assertEqual(r["hits"], [])
        self.assertEqual(r["level"], "none")


class TestHistoryB4(unittest.TestCase):
    """V3 B4：/api/history 序列化（纯函数 _history_items，不碰库）。"""

    def setUp(self):
        from backend.main import _history_items
        self.items = _history_items

    def _rec(self, vday, feedback="完成了", **advice_kw):
        advice = {"judgement": "今晚从简", "eat": "清淡晚餐", "move": "走8分钟",
                  "stop": "23:00 放下手机"}
        advice.update(advice_kw)
        import json as _json
        return {"vday": vday, "feedback": feedback,
                "advice_json": _json.dumps(advice, ensure_ascii=False)}

    def test_无记录空数组(self):
        self.assertEqual(self.items([]), [])

    def test_响应不含feedback(self):
        # 输入行带着 feedback，输出体里任何位置都不许出现
        out = self.items([self._rec("2026-08-01", feedback="完全没完成")])
        self.assertEqual(len(out), 1)
        self.assertEqual(set(out[0].keys()), {"vday", "line", "items"})
        import json as _json
        self.assertNotIn("feedback", _json.dumps(out, ensure_ascii=False))
        self.assertNotIn("完全没完成", _json.dumps(out, ensure_ascii=False))

    def test_line取stop缺则judgement(self):
        out = self.items([self._rec("2026-08-01")])
        self.assertEqual(out[0]["line"], "23:00 放下手机")
        out2 = self.items([self._rec("2026-08-01", stop=None)])
        self.assertEqual(out2[0]["line"], "今晚从简")

    def test_items只留非空(self):
        out = self.items([self._rec("2026-08-01", move=None)])
        self.assertEqual(out[0]["items"], ["清淡晚餐", "23:00 放下手机"])

    def test_上限截断(self):
        out = self.items([self._rec(f"2026-07-{i:02d}") for i in range(1, 32)] +
                         [self._rec("2026-08-01")])
        self.assertEqual(len(out), 30)


class TestFavoriteFoodsB5(unittest.TestCase):
    """V3 B5：口味偏好八类改队友定名 + 旧名归一化（agent.favorite_food_tips 纯函数）。"""

    def setUp(self):
        from backend.agent import FAVORITE_FOOD_STRATEGIES, favorite_food_tips
        self.strategies = FAVORITE_FOOD_STRATEGIES
        self.tips = favorite_food_tips

    def test_八个新名齐全(self):
        self.assertEqual(
            set(self.strategies.keys()),
            {"粉面", "炸物快餐", "盖饭便当", "火锅麻辣烫", "烧烤夜宵",
             "甜品饮料", "轻食沙拉", "自己做的家常"})

    def test_新名注入带策略(self):
        tips = self.tips("粉面,甜品饮料")
        self.assertEqual(len(tips), 2)
        self.assertIn("少主食多配菜", tips[0])
        self.assertIn("减糖/换无糖", tips[1])

    def test_旧名归一化后同样注入(self):
        # 老库存量值（V2 旧名）：粉面类/甜品奶茶/家常菜
        tips = self.tips("粉面类,甜品奶茶,家常菜")
        self.assertEqual(len(tips), 3)
        self.assertIn("粉面（", tips[0])
        self.assertIn("甜品饮料（", tips[1])
        self.assertIn("自己做的家常（", tips[2])
        # 追加验证 A 的存量组合：火锅麻辣烫没改名直取、甜品奶茶靠归一化
        tips2 = self.tips("火锅麻辣烫,甜品奶茶")
        self.assertEqual(len(tips2), 2)

    def test_未知名忽略不炸(self):
        self.assertEqual(self.tips("兰州拉面,粉面"), [f"粉面（{self.strategies['粉面']}）"])
        self.assertEqual(self.tips(""), [])


class TestConfirmHintB1(unittest.TestCase):
    """V3 B1：/api/state confirm_hint 的纯函数估算（agent.build_confirm_hint）。
    不写库、不调模型，全部用构造档案 + 固定 now 验证边界。"""

    def _p(self, **kw):
        base = {"off_work_end": "19:00", "commute_min": 30, "wake_time": "07:00"}
        base.update(kw)
        return base

    def _now(self, s):
        from datetime import datetime
        return datetime.fromisoformat(s)

    def test_常规晚间(self):
        # 22:00，已过下班点 → 到家=现在+30=22:30；睡点=07:00−7.5h=23:30；剩余 60
        h = build_confirm_hint(self._p(), self._now("2026-08-09T22:00:00"), None, 3)
        self.assertEqual(h["sleep_point"], "23:30")
        self.assertEqual(h["home_eta"], "22:30")
        self.assertEqual(h["remaining_min"], 60)
        self.assertEqual(h["body"], "暂未确认")
        self.assertIn("23:30", h["time_basis"])
        self.assertIn("30 分钟通勤", h["time_basis"])

    def test_未过下班点从下班点起算(self):
        # 18:00 还没下班 → 到家=19:00+30=19:30（与提示词注入老口径一致）；剩余=23:30−19:30=240
        h = build_confirm_hint(self._p(), self._now("2026-08-09T18:00:00"), None, 3)
        self.assertEqual(h["home_eta"], "19:30")
        self.assertEqual(h["remaining_min"], 240)

    def test_跨零点睡点(self):
        # 起床 08:30 → 睡点次日 01:00；now 22:00 → 到家 22:30 → 剩余 150
        h = build_confirm_hint(self._p(wake_time="08:30"),
                               self._now("2026-08-09T22:00:00"), None, 3)
        self.assertEqual(h["sleep_point"], "01:00")
        self.assertEqual(h["remaining_min"], 150)

    def test_已过睡点剩余归零(self):
        # now 23:45 已过 23:30 睡点 → 0，不出负数
        h = build_confirm_hint(self._p(), self._now("2026-08-09T23:45:00"), None, 3)
        self.assertEqual(h["remaining_min"], 0)

    def test_零点后到家跨日不出负数(self):
        # now 23:50 + 30 分钟通勤 → 到家次日 00:20；睡点已过 → 0（回归：跨日相减曾可能出巨大负值）
        h = build_confirm_hint(self._p(), self._now("2026-08-09T23:50:00"), None, 3)
        self.assertEqual(h["home_eta"], "00:20")
        self.assertEqual(h["remaining_min"], 0)

    def test_无起床时间默认2300睡点(self):
        h = build_confirm_hint(self._p(wake_time=None),
                               self._now("2026-08-09T22:00:00"), None, 3)
        self.assertEqual(h["sleep_point"], "23:00")
        self.assertEqual(h["remaining_min"], 30)

    def test_无下班时间退化为现在加通勤(self):
        h = build_confirm_hint(self._p(off_work_end=None),
                               self._now("2026-08-09T22:00:00"), None, 3)
        self.assertEqual(h["home_eta"], "22:30")

    def test_精力_昨晚回执差(self):
        for fb in ("完全没完成", "建议仍然太难", "未响应"):
            h = build_confirm_hint(self._p(), self._now("2026-08-09T22:00:00"), fb, 3)
            self.assertEqual(h["energy_guess"], "很低", fb)

    def test_精力_档位低(self):
        h = build_confirm_hint(self._p(), self._now("2026-08-09T22:00:00"), "完成了", 1)
        self.assertEqual(h["energy_guess"], "很低")

    def test_精力_默认还行(self):
        for fb, level in ((None, 3), ("完成了", 3), ("只完成一部分", 4), ("跳过", 2)):
            h = build_confirm_hint(self._p(), self._now("2026-08-09T22:00:00"), fb, level)
            self.assertEqual(h["energy_guess"], "还行", f"{fb}/{level}")

    def test_basis不出现内部术语(self):
        # basis 是给用户看的：不得出现 档位/baseline/safety 等内部词
        for fb, level in ((None, 3), ("完全没完成", 3), ("完成了", 1), ("未响应", 0)):
            h = build_confirm_hint(self._p(), self._now("2026-08-09T22:00:00"), fb, level)
            for word in ("档位", "baseline", "safety", "level"):
                self.assertNotIn(word, h["energy_basis"])
                self.assertNotIn(word, h["time_basis"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
