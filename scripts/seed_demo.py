# 种子演示账号（文档 M6）：一条脚本把演示用户和前两天历史灌好。
# 运行：/opt/miniconda3/envs/Eazo/bin/python scripts/seed_demo.py
# 幂等：重跑先删掉旧的 demo1 及其所有数据再灌。
# 灌完后的演示起点：demo1 登录 → 主界面「下班了」→ 先弹昨晚回执 → 生成今晚建议。
import hashlib
import json
import secrets
import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend import clock, db  # noqa: E402
from backend.logging_setup import setup_logging  # noqa: E402

USERNAME, PASSWORD = "demo1", "demo123"


def main() -> None:
    setup_logging()
    db.init_db()
    today = date.fromisoformat(clock.today())
    d1 = (today - timedelta(days=1)).isoformat()   # 昨天：待回执
    d2 = (today - timedelta(days=2)).isoformat()   # 前天：已完成

    conn = db.get_conn()
    try:
        # 清掉旧演示数据（幂等）
        old = conn.execute("SELECT id FROM users WHERE username = ?", (USERNAME,)).fetchone()
        if old:
            uid = old["id"]
            for table in ("daily_records", "meal_records", "free_inputs", "profiles", "sessions"):
                key = "token" if table == "sessions" else "user_id"
                if table == "sessions":
                    conn.execute("DELETE FROM sessions WHERE user_id = ?", (uid,))
                else:
                    conn.execute(f"DELETE FROM {table} WHERE user_id = ?", (uid,))
            conn.execute("DELETE FROM users WHERE id = ?", (uid,))

        # 建用户（密码哈希方式与 main.py 一致：salt$sha256(salt+password)）
        salt = secrets.token_hex(8)
        pw_hash = salt + "$" + hashlib.sha256((salt + PASSWORD).encode()).hexdigest()
        uid = conn.execute(
            "INSERT INTO users (username, password_hash, created_at) VALUES (?, ?, ?)",
            (USERNAME, pw_hash, clock.now().isoformat()),
        ).lastrowid

        # 档案：典型久坐上班族
        conn.execute(
            "INSERT INTO profiles (user_id, off_work_start, off_work_end, overtime_freq, "
            "commute_min, work_body_state, cooking, diet_restrictions, health_note, "
            "wake_time, exercise_base, gender, age, height_cm, weight_kg) "
            "VALUES (?, '18:00', '19:00', '偶尔加班', 40, '久坐', '只能外卖', NULL, NULL, "
            "'07:00', '无/偶尔', '女', 28, 162, 54)",
            (uid,),
        )

        # 前天：完成了（给「连续完成升档」留伏笔）
        advice_d2 = {
            "judgement": "今晚精力尚可，安排最低档的身体唤醒",
            "reason": "按你久坐+通勤40分钟，到家约19:40，精力中等",
            "eat": "外卖选有青菜的套餐，别点炸物",
            "move": "饭后在楼下走 8 分钟",
            "stop": "23:00 放下手机",
            "sources": ["中国人群身体活动指南(2021)", "中国居民膳食指南(2022)"],
            "safety_flag": False,
        }
        conn.execute(
            "INSERT INTO daily_records (user_id, vday, conditions_json, advice_json, "
            "status, feedback, baseline_level) VALUES (?, ?, ?, ?, 'done', '完成了', 3)",
            (uid, d2,
             json.dumps({"来源": "seed演示", "档位": 3}, ensure_ascii=False),
             json.dumps(advice_d2, ensure_ascii=False)),
        )

        # 昨天：待回执（演示第一幕：点「下班了」先收这条回执）
        advice_d1 = {
            "judgement": "今晚到家偏晚，只做几个拉伸就够",
            "reason": "按你久坐+通勤40分钟+自述有点累，到家约20:00",
            "eat": "太晚就垫一口热的，别空腹睡",
            "move": "工位拉伸 3 个动作，共 8 分钟",
            "stop": "23:00 放下手机",
            "sources": ["办公族拉伸指导", "睡眠卫生"],
            "safety_flag": False,
        }
        conn.execute(
            "INSERT INTO daily_records (user_id, vday, conditions_json, advice_json, "
            "status, feedback, baseline_level) VALUES (?, ?, ?, ?, 'pending_feedback', NULL, 3)",
            (uid, d1,
             json.dumps({"来源": "seed演示", "档位": 3}, ensure_ascii=False),
             json.dumps(advice_d1, ensure_ascii=False)),
        )

        # 昨天中午一条饮食记录（演示"它记得我拍过什么"）
        conn.execute(
            "INSERT INTO meal_records (user_id, vday, vtime, source, food_json, image_path) "
            "VALUES (?, ?, '12:30', 'photo', ?, NULL)",
            (uid, d1,
             json.dumps({"名称": "黄焖鸡米饭", "估计分量": "一份", "类别": "米饭",
                         "备注": "鸡肉, 香菇, 米饭"}, ensure_ascii=False)),
        )
        conn.commit()
    finally:
        conn.close()

    print(f"演示账号已就绪：{USERNAME} / {PASSWORD}")
    print(f"  前天({d2})：建议已完成；昨天({d1})：待回执 + 中午黄焖鸡记录")
    print("  演示流程：登录 → 点「下班了」→ 先收昨晚回执 → 生成今晚建议")


if __name__ == "__main__":
    main()
