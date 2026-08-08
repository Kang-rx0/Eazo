# 安全边界单元测试（纯 Python，不调模型）。随 S 阶段推进逐步扩充：
#   S0：L1 扫描 / 等级合并只升不降 / enforce 骨架
# 运行：/opt/miniconda3/envs/Eazo/bin/python scripts/test_safety.py
import sys
import unittest
from pathlib import Path

# 让脚本能 import backend 包
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.safety import enforce, l1_scan, merge_levels  # noqa: E402


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


if __name__ == "__main__":
    unittest.main(verbosity=2)
