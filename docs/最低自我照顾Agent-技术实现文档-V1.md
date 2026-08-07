# 最低自我照顾 Agent · 技术实现文档 V1（可直接交给 Claude Code 执行）

> 目标：做一个**能跑通全流程的第一版**。不追求医疗约束的完备性，追求：能回答、回答有依据（引用参考手册）、有记忆（记得我填过什么、传过什么）、有反馈闭环、能在 2 分钟演示里模拟多天。
>
> 本文档是实现指令。按「十、分步实现计划」的顺序做，每步做完能跑再做下一步。

---

## 一、第一版范围（做什么 / 不做什么）

**做：**

1. 介绍页（含登录/注册入口）→ 登录/注册 → 首次进入填用户信息（onboarding）→ 主界面。
2. 核心闭环：点「下班了」→ Agent 生成今晚建议（吃什么 / 动多久 / 几点停 + 理由行）→ 用户接受或一击纠正 → 记录 → 第二天先收「昨晚做得怎么样」的回执 → 调整今晚的最低线。
3. 自由输入：用户随时可以打一句话（「加了三小时班累死了」「中午吃了黄焖鸡」），Agent 接住并体现在当晚建议里。
4. 食物照片上传：视觉模型识别 → 存为当日饮食记录 → 晚上生成建议时纳入考虑。
5. RAG：内置一批权威参考手册（膳食、身体活动、拉伸、睡眠），Agent 生成建议时检索并**在界面上标注来源**。
6. 模拟时钟：演示用的时间控制条，可以「+1 小时」「跳到第二天」，全系统的"今天/昨天"都基于这个虚拟时间。

**不做（第一版明确砍掉）：**

- 部署、推送通知、语音输入、地理围栏。
- PRD 里的严重疾病劝退清单、慢性病适配（只在系统提示词里留一句兜底：听到「疼/晕/胸口不适」就建议休息就医、不给运动建议）。
- 学习模块（次日调整用简单规则，见 7.4）。
- 精致 UI（队友负责，这版只要结构清晰、按钮能点）。

---

## 二、技术选型

| 项 | 选择 | 说明 |
|---|---|---|
| 后端 | Python 3.10+ / FastAPI | 单进程，`uvicorn` 启动 |
| 数据库 | SQLite（直接用 `sqlite3` 或 SQLAlchemy 均可） | 单文件 `app.db`，够用 |
| 前端 | 静态 HTML + 原生 JS（fetch 调后端 API） | 放 `frontend/` 目录，FastAPI 静态托管；队友后续替换 |
| 大模型 | 阿里百炼，**OpenAI 兼容格式**调用 | `base_url = https://dashscope.aliyuncs.com/compatible-mode/v1` |
| 文本模型 | `qwen-plus`（默认，快且便宜；`qwen-max` 备选） | 配置项，可换 |
| 视觉模型 | `qwen-vl-max` | 食物照片识别 |
| 向量模型 | `text-embedding-v4` | RAG 用 |
| 向量存储 | numpy 数组 + SQLite 存文本块，余弦相似度暴力检索 | **不装向量数据库**，语料就几百个块，暴力算够快 |

所有模型名、API Key、base_url 写在 `.env` / `config.py` 里，统一封装一个 `llm.py`，换模型只改配置。

```
# .env 示例
OPENAI_API_KEY=sk-xxx          # 百炼的 key
OPENAI_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
CHAT_MODEL=qwen-plus
VISION_MODEL=qwen-vl-max
EMBED_MODEL=text-embedding-v4
```

**项目结构：**

```
project/
├── backend/
│   ├── main.py            # FastAPI 入口 + 路由
│   ├── config.py          # 读 .env
│   ├── db.py              # 建表 + 数据库操作
│   ├── llm.py             # 模型调用封装（chat / vision / embed）
│   ├── agent.py           # 核心 Agent 循环（本文档第五节）
│   ├── rag.py             # 检索（第六节）
│   ├── clock.py           # 虚拟时钟（第八节）
│   └── tools.py           # Agent 可调用的工具函数
├── scripts/
│   ├── crawl_corpus.py    # 爬取参考手册页面/PDF + 清洗（见 6.2）
│   └── build_corpus.py    # 语料切块 + 向量化，一次性脚本
├── data/
│   ├── corpus_raw/        # 爬虫抓下来的原始 HTML/PDF
│   ├── corpus/            # 清洗后的参考手册正文（markdown）
│   └── corpus.npz         # 生成的向量
├── frontend/
│   ├── index.html         # 介绍页（登录/注册入口）
│   ├── auth.html          # 登录/注册
│   ├── onboarding.html    # 首次填信息
│   └── app.html           # 主界面（核心）
├── logs/                  # 运行日志与 Agent 轨迹（见 十一）
└── app.db
```

---

## 三、架构决策（为什么这么设计，写给团队也写给 Claude Code）

### 3.1 单 Agent + 工具调用，不做多 Agent

**结论：一个主 Agent，带工具调用（function calling）的循环。不做多 Agent，不做 router，不引入任何 Agent 框架（LangChain/LangGraph 等都不用）。**

理由：

- 这个产品只有一个决策时刻（下班触点），输入类型有限。多 Agent 的收益是"不同职责并行/隔离"，这里没有这种需求，只会多出失败点和延迟。
- 评审的技术分（10%）看的是"Agent 能力是否实际参与核心体验、能否稳定跑通、结果是否完整可靠"——**不是数 Agent 个数**。一个会调工具、有记忆、有依据的单 Agent，演示出来的"Agent 味"已经足够：它会自己决定要不要查手册、查哪本、查几次。
- 视觉识别**不是一个 Agent**，只是一次独立的模型调用（见 7.3），代码上是一个普通函数。

### 3.2 不需要模型做 router，用代码分流

进入系统的事件只有这几类，用 `if/else` 分流即可，不需要让模型判断"用户想干什么"：

| 事件 | 来源 | 处理 |
|---|---|---|
| 点「下班了」 | 按钮 | 走 Agent 主循环，生成今晚建议 |
| 一击纠正（今晚更累/时间更少/不太舒服/今天还行/其实我做了） | 按钮 | 把纠正项作为新条件，重跑 Agent 主循环 |
| 自由输入一句话 | 文本框 | 存入记录，然后重跑（或首次跑）Agent 主循环 |
| 上传食物照片 | 上传控件 | 先调视觉模型转成结构化记录存库，再返回一句简短确认（不触发完整建议） |
| 昨晚回执四档 | 按钮 | 只写库 + 更新最低线，不调模型 |

### 3.3 循环怎么转、怎么退出

Agent 主循环就是一个 `while` 循环（自己写，30 行以内）：

```
组装上下文（用户档案 + 近几天记录 + 今天已知信息 + 当前虚拟时间）
循环（最多 6 轮）:
    调 chat 模型（带工具定义）
    如果模型返回工具调用 → 执行工具 → 把结果塞回对话 → 继续下一轮
    如果模型返回最终 JSON → 校验格式 → 退出循环
超过 6 轮还没结束 → 强制让模型"基于已有信息直接给结论"（去掉工具，再调一次）
```

- **退出条件**：模型不再调工具、输出了符合格式的最终 JSON。这是 OpenAI 格式工具调用的标准做法（`finish_reason` 不是 `tool_calls` 时结束）。
- **多轮思考**：不做显式的"思考链编排"。模型每轮可以决定"先查一下拉伸手册""再查一下睡眠建议"，这个工具调用序列本身就是多轮思考，演示时把每轮调了什么工具显示在界面侧边（加分项，见 9.4）。
- **兜底**：任何一步模型调用失败或 JSON 解析失败，重试 1 次；再失败则返回一套写死的默认建议（"饭后走 8 分钟 / 23:00 放下手机"），保证演示不死。

### 3.4 Agent 的工具清单（第一版 4 个）

用 OpenAI 格式的 `tools` 参数声明：

1. `search_reference(query, category)` — 检索参考手册。`category` 可选：`diet` / `exercise` / `stretch` / `sleep` / `any`。返回 top-3 文本块，每块带来源名称。
2. `get_user_history(days)` — 取最近 N 天的记录（建议、完成情况、饮食记录、自由输入）。
3. `log_note(text)` — Agent 把它从自由输入里提取到的关键条件记一笔（比如从"加了三小时班"提取出"今晚到家晚、精力低"）。
4. `calc_body_metrics()` — **确定性计算工具**（见 3.5），返回该用户的基础代谢、每日估算消耗、蛋白质参考区间等。参数从档案读，模型不传数字，杜绝模型自己心算。

用户档案和当天已知信息**直接放进系统提示词**，不做成工具——减少无意义的调用轮次。

### 3.5 统一公式：做成工具函数，不做成 skills

膳食热量、蛋白质需求这类**有统一公式的计算，一律写成 Python 函数**（`tools.py` 里的普通代码），注册为工具让 Agent 调用。理由：

- 公式是确定性的，让大模型自己算数学是最不稳的做法（算术经常错）；写进代码则永远算对，这才是"稳妥"。
- "skills" 是开发工具（Claude Code）里给开发过程用的提示词包，不是产品运行时的机制，运行时对应物就是工具调用。

`calc_body_metrics` 内部实现（写死在代码里，带注释注明公式名）：

```python
# 基础代谢 BMR，Mifflin-St Jeor 公式
# 男：10*体重kg + 6.25*身高cm - 5*年龄 + 5
# 女：10*体重kg + 6.25*身高cm - 5*年龄 - 161
# 每日估算消耗 TDEE = BMR * 活动系数（久坐1.2 / 站着走动1.4 / 体力消耗1.6）
# 蛋白质参考：一般成人 0.8–1.0 g/kg；有轻度训练 1.2–1.6 g/kg
# 缺身高/体重/年龄任一项 → 返回 {"available": false}，Agent 就不引用数字
```

返回示例（普通 JSON，字段带中文说明）：

```json
{
  "available": true,
  "bmr_kcal": 1580,
  "tdee_kcal": 1900,
  "protein_g_range": [78, 104],
  "note": "估算值，仅作参考量级，不用于精确配餐"
}
```

使用纪律（写进系统提示词）：这些数字只用来**定量级和方向**（"晚餐别超过大概600千卡这个量级""今天蛋白质明显不够，晚上补一个蛋"），不做精确配比、不逐克计算——既满足你们第一版想要的计算能力，也不至于滑成卡路里计算器。

---

## 四、数据库设计

```sql
users(id, username, password_hash, created_at)

profiles(user_id, off_work_start, off_work_end, overtime_freq,  -- 下班时间范围+加班频率
         commute_min,                                            -- 通勤分钟
         work_body_state,       -- 久坐 / 站着走动 / 体力消耗
         cooking,               -- 只能外卖 / 能简单做 / 能正经做
         diet_restrictions,     -- 饮食禁忌，逗号分隔，可空
         health_note,           -- 健康问题一行，可空
         exercise_base,         -- 运动基础，默认 "无/偶尔"
         gender, age, height_cm, weight_kg)  -- 计算参数，放表单最后、全部可跳过；缺任一项则 calc_body_metrics 不可用

daily_records(id, user_id, vday,          -- vday = 虚拟日期 "2026-08-07"
              conditions_json,            -- 当天条件快照：到家时间/精力/剩余时间/纠正项…
              advice_json,                -- Agent 给出的建议（含理由行、来源）
              status,                     -- pending_feedback / done
              feedback,                   -- 完成了 / 只完成一部分 / 完全没完成 / 建议仍然太难 / null
              baseline_level)             -- 当天最低线档位（见 7.4），整数

meal_records(id, user_id, vday, vtime, source,   -- source: photo / text
             food_json,                          -- {名称, 估计分量, 类别, 备注}
             image_path)

free_inputs(id, user_id, vday, vtime, text, extracted_json)  -- 原话 + Agent 提取的条件

corpus_chunks(id, doc_name, category, chunk_text)   -- 向量存 data/corpus.npz，行号对应 id

app_clock(id=1, virtual_now)   -- 全局虚拟时间，ISO 字符串

sessions(token, user_id, created_at)   -- 登录态，最简单的 token 表
```

**设计要点**：条件和结果绑在同一条 `daily_records` 里（这是 PRD 数据一节的核心要求，将来才能分析"这人在什么条件下会崩"）。用户自报（照片、文字）和系统推断分字段存，第一版至少用 `source` 字段区分。

---

## 五、Agent 设计

### 5.1 系统提示词骨架（agent.py 里写死，中文）

```
你是一个「最低自我照顾」助手，服务对象是下班后精力所剩无几的上班族。

你的任务：根据用户档案、今天的已知信息和参考手册，给出今晚的最低行动建议。

规则：
1. 输出永远是固定形状：今晚判断+理由 / 吃什么 / 动多久 / 几点停。任一行没有该说的就省略，不硬凑。
2. 只说"多少、到什么程度"，不给训练计划、不算卡路里、不做疾病判断。
3. 建议必须小：默认 10 分钟以内的轻活动。用户状态越差，要求越小，直到只剩"早点睡"。
4. 理由行必须回显用户的具体条件（如"按你久坐+通勤40分钟…"），让用户看到你是算过的。
5. 给建议前，用 search_reference 查参考手册，最终输出中给出所依据的来源名。
6. 不评判用户已经吃的东西，只往前看。饮食禁忌是硬约束，绝不突破。
7. 如果用户提到 疼/晕/胸口不适/喘不上气，不给任何活动建议，建议休息、必要时就医。
8. 最终输出必须是 JSON（格式见下），不要输出其他内容。
```

### 5.2 最终输出 JSON 格式

```json
{
  "judgement": "今晚只剩约20分钟，不安排训练",
  "reason": "按你久坐 + 通勤40分钟 + 自述加班3小时计算，到家约21:40，精力低",
  "eat": "太晚了别吃正经饭，垫一口热的，别空腹睡",      // 可为 null
  "move": "饭后在楼下走8分钟",                          // 可为 null
  "stop": "23:00 放下手机",
  "sources": ["中国居民膳食指南(2022)", "WHO 2020 身体活动指南"],
  "safety_flag": false        // true 时前端只显示休息/就医提示
}
```

后端校验：必须能 `json.loads`，`judgement` 和 `stop` 至少存在。前端按行渲染，null 的行不显示；`sources` 渲染成小字"参考依据"。

### 5.3 每次调用时注入的上下文

系统提示词后面拼接：

```
【用户档案】<profiles 表内容，格式化成短句>
【当前虚拟时间】2026-08-07 19:20 （周五）
【今天已知】到家时间估计 / 已记录的三餐（含照片识别结果）/ 自由输入原话 / 一击纠正项
【最近3天】<daily_records 摘要：建议了什么、反馈是什么>
【当前最低线档位】3（档位含义见下）
```

这就是"记忆"：不需要向量记忆库，把结构化记录直接注入就有很强的演示效果（"它记得我中午拍的黄焖鸡"）。

---

## 六、RAG：参考手册

### 6.1 语料清单（人工下载/整理，不要让脚本去爬）

目标：把以下内容整理成 markdown 文件放进 `data/corpus/`，每个文件开头标注 `<!-- doc_name: xxx, category: diet, source_url: xxx -->`。获取方式：优先用 6.2 的爬虫脚本自动抓取+清洗；抓不下来的（如需要跳转/反爬的页面）人工复制正文补齐。每个文档几千字的核心建议部分就够，不必全书收录。

| 文件 | 类别 | 来源（权威、公开） |
|---|---|---|
| `膳食指南2022.md` | diet | 《中国居民膳食指南(2022)》核心推荐，中国营养学会官网 [dg.cnsoc.org](http://dg.cnsoc.org/)，核心信息公开版见 [福建省卫健委转载页](https://wjw.fujian.gov.cn/ztzl/jkjy/jkzgxd/202206/t20220615_5930367.htm) |
| `身体活动指南2021.md` | exercise | 《中国人群身体活动指南(2021)》全文 PDF（中国疾控中心牵头编制），[中国公共卫生杂志公开全文](https://www.zgggws.com/cn/article/pdf/preview/10.11847/zgggws1137503.pdf) |
| `WHO身体活动指南2020.md` | exercise | WHO 2020 身体活动与久坐行为指南，[PMC 公开全文](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7719906/)（英文，可直接收录英文，检索没问题） |
| `全民健身指南.md` | exercise | 国家体育总局《全民健身指南》，[官方解读页](https://www.sport.gov.cn/n315/n331/n405/c819327/content.html) |
| `办公族拉伸.md` | stretch | Mayo Clinic 办公桌拉伸系列 [mayoclinic.org](https://www.mayoclinic.org/healthy-lifestyle/adult-health/in-depth/office-stretches/art-20046041) + CCOHS 工位拉伸 [ccohs.ca](https://www.ccohs.ca/oshanswers/ergonomics/office/stretching.html) |
| `睡眠卫生.md` | sleep | CDC 睡眠健康 [cdc.gov/sleep](https://www.cdc.gov/sleep/about/index.html) + NIOSH 改善睡眠建议 [cdc.gov/niosh](https://www.cdc.gov/niosh/bulletin/2020/sleep.html) |

> 版权注意：这些是政府/公共机构的公开健康指导内容，作为检索依据并标注来源，比赛场景没有问题。不要在产品里整篇复现原文。

### 6.2 爬取与清洗脚本 `scripts/crawl_corpus.py`

一次性脚本，依赖 `requests + beautifulsoup4 + pdfplumber`。在脚本顶部维护一个来源列表（url、doc_name、category、类型 html/pdf），对应 6.1 的表。

**抓取：**

1. HTML 页面：`requests.get`（带常见浏览器 User-Agent，超时 30s，失败重试 1 次），原始文件存 `data/corpus_raw/`。
2. PDF（如身体活动指南全文）：下载后用 `pdfplumber` 逐页提取文字。
3. 每个来源之间 `sleep(2)`，只抓列表里的固定几个页面，不递归爬链接。

**清洗规则（按顺序执行）：**

1. HTML 只取正文容器，剔除 `script/style/nav/header/footer/aside` 和导航、版权声明、面包屑。
2. 去掉空行堆叠、页眉页脚重复行（PDF 常见：同一行文字在多页重复出现 → 删）、页码、参考文献编号（`[12]` 这类）。
3. 过滤与主题无关的段落：丢掉长度 < 20 字的碎句；丢掉不含任何领域关键词（吃/食/动/运动/睡/拉伸/活动/训练 等一张小关键词表）且超过 200 字的整段——防止把网页上的新闻列表混进语料。
4. 英文来源（WHO、CDC、Mayo Clinic）保留英文原文即可，检索用向量模型是跨语言的，不需要翻译。
5. 输出为 markdown：一级标题=文档名，段落间空一行，文件头写 `doc_name / category / source_url / 抓取日期` 注释。

**验证：** 跑完后人工翻一遍 `data/corpus/` 里的每个文件（就 6 个），确认没有导航栏残留、没有乱码。清洗质量直接决定 RAG 质量，这一步值得花 10 分钟人眼检查。

**兜底：** 某个来源抓取失败（403/超时），脚本打印警告并跳过，在文件里生成占位说明，由人工复制正文补齐，不阻塞流程。

### 6.3 构建脚本 `scripts/build_corpus.py`

1. 读 `data/corpus/*.md`，按标题/空行切块，每块 300–500 字，块首拼上文档名（提高检索质量）。
2. 批量调 `text-embedding-v4` 得到向量。
3. 文本块写入 `corpus_chunks` 表，向量存 `data/corpus.npz`（顺序与 id 对应）。
4. 幂等：重跑先清空再建。

### 6.4 检索 `rag.py`

`search(query, category="any", top_k=3)`：query 向量化 → 与全部向量算余弦相似度（numpy 一行）→ 按 category 过滤 → 返回 top_k 的 `(doc_name, chunk_text)`。总共就几百块，暴力检索毫秒级。

---

## 七、页面流转、反馈闭环、状态机（你问的"怎么知道回到哪个界面"）

### 7.1 核心思路：后端记状态，前端开屏先问后端

前端 `app.html` 每次加载（以及虚拟时间变化后）先调 `GET /api/state`，后端根据数据库算出**现在该显示哪个视图**，前端照着渲染。软件"知道回到哪个界面"，靠的就是这一个接口，不靠前端自己记。

```
GET /api/state 返回：
{
  "view": "onboarding" | "home" | "advice",
  "pending_feedback": {昨天的建议摘要} | null,   // 有未回执的昨日建议
  "today_advice": {今天已生成的建议} | null,
  "today_meals": [...],                          // 今天已记录的饮食
  "virtual_now": "2026-08-07T19:20"
}
```

判定规则（伪代码）：

```
如果 profiles 里没有该用户 → view = "onboarding"
否则如果 今天(vday) 已有 daily_records 且用户已接受 → view = "advice"（展示今晚建议卡片）
否则 → view = "home"（大按钮「下班了」）
另外：若昨天及更早存在 status = pending_feedback 的记录 → pending_feedback 带上它
```

### 7.2 反馈闭环（采纳你队友的方案，和 PRD 一致）

**回执放在下一天点「下班了」的时刻**——这正好符合 PRD 的"昨晚回执和今晚最低线在同一屏解决"：

1. 第 1 天：用户点「下班了」→ Agent 给建议 → 用户点「就这样」（接受）→ 记录 `status=pending_feedback` → 界面停在建议卡片视图（卡片下方常驻两个小按钮：「其实我做了」「换个更小的」，不强迫点）。
2. 用户关掉/时间推进到第 2 天。
3. 第 2 天：用户点「下班了」→ 后端发现昨天有 `pending_feedback` → **先弹一屏回执**：「昨晚『饭后走8分钟』做得怎么样？」四档按钮（完成了 / 只完成一部分 / 完全没完成 / 建议仍然太难）+ 一个「跳过」→ 点完立即写库、按 7.4 调档 → 紧接着生成今晚建议。
4. 如果用户连续几天没打开：所有未回执记录标为「已送达、未响应」（沉默也是数据），最低线自动下调一档，**只对最近一天弹回执**，不堆积多屏。

这样"接受之后然后呢"的答案是：**界面停在建议卡片（当晚随时可回来一击纠正），反馈动作天然发生在下一次触点的开头。** 不需要额外页面，也不需要等用户主动想起来。

### 7.3 食物照片流程

1. 主界面/建议卡片上有一个小入口「补充一句 / 拍一下」（按 PRD，不做成首屏主角）。
2. 上传图片 → `POST /api/meal/photo` → 后端调 `qwen-vl-max`，提示词：「识别图中食物，输出 JSON：{name, portion(大概分量), category(粉面/炸物/米饭/火锅/烧烤/甜品饮料/轻食/家常), note}。不确定就写最可能的，不要拒答。」
3. 存 `meal_records(source=photo)`，返回一句轻确认：「记下了：黄焖鸡米饭。晚上给你参考。」**不评判、不展开。**
4. 晚上跑 Agent 主循环时，这条记录出现在【今天已知】里，模型自然会在"吃什么"一行里考虑（比如中午吃得重，晚上就建议清淡将就一口）。

### 7.4 次日调整：用最简单的档位规则（不做学习模块）

`baseline_level` 取 0–4 档，写死一张表：

| 档 | 动多久 的量级 | 说明 |
|---|---|---|
| 4 | 15–20 分钟轻活动 | 天花板，不外露 |
| 3 | 8–10 分钟 | 首夜起点（正常模式下沿） |
| 2 | 5 分钟 / 几个拉伸 | |
| 1 | 只有"几点停" | |
| 0 | 一句"少玩手机、早点睡" | 地板，不再缩 |

规则：反馈=完成了 → +0（连续两天完成 → +1，封顶 4）；只完成一部分 → 不变；完全没完成 / 未响应 → −1；建议仍然太难 → −1 且备注。档位作为上下文告诉 Agent（"当前档位 2，建议量级：5 分钟以内"），**具体内容仍由 Agent 结合手册和当天条件生成**——这样既有机制、又不是决策树。

---

## 八、虚拟时钟（演示核心道具）

- `app_clock` 表存一个全局 `virtual_now`。`clock.py` 提供 `now()`，**全后端禁止直接用系统时间**，一律 `clock.now()`。
- 接口：`POST /api/clock` 支持 `{advance_hours: 2}`、`{advance_days: 1}`（跳到次日 19:00）、`{set: "..."}`。
- 前端：页面右下角一个半透明"演示控制条"，显示当前虚拟时间 + 三个按钮：「+1小时」「下一天」「重置」。真实感说明：演示时讲"我们用时间控制模拟多天使用"，评委完全接受，这比拖动滑块简单可靠。
- 「跳到下一天」后前端自动重新调 `/api/state`，界面随之切换——这就自然演出"第二天打开先收回执"的效果。

---

## 九、API 一览

```
POST /api/register            {username, password}
POST /api/login               {username, password} → {token}     # 其后请求带 token
POST /api/onboarding          {profiles 各字段}
GET  /api/state                                                   # 7.1
POST /api/offwork             {}                → 建议 JSON        # "下班了"，含回执逻辑触发前置
POST /api/feedback            {record_id, feedback}               # 四档回执
POST /api/correct             {type: 今晚更累/时间更少/不太舒服/今天还行/其实我做了} → 重出建议
POST /api/free_input          {text}            → 重出建议（当天已有建议时）或轻确认
POST /api/meal/photo          multipart 图片    → 识别结果 + 轻确认
POST /api/clock               {advance_hours | advance_days | set}
GET  /api/agent_trace         最近一次 Agent 循环的工具调用轨迹（给演示侧栏用）
```

`POST /api/offwork` 内部顺序：查昨日 pending → 若有则先返回 `{need_feedback: true, record}`，前端收完回执再调一次 → 跑 Agent 主循环 → 存 `daily_records` → 返回建议。

### 9.4 演示加分项：Agent 过程可视化

Agent 循环里把每轮动作记到内存（`agent_trace`）：「检索了《膳食指南2022》→ 检索了《睡眠卫生》→ 给出结论」。前端在建议卡片旁用小字/折叠面板展示。这 10% 技术分基本就靠这个 + 来源标注 + 记忆演示拿。

---

## 十、分步实现计划（按顺序做，每步可独立验证）

**M0 骨架**：项目结构、config、db 建表、日志初始化（11.1）、虚拟时钟 + `/api/clock`、前端四个空页面能互相跳转。验证：改虚拟时间，`/api/state` 返回值变化，`logs/app.log` 有记录。

**M1 账号与 onboarding**：注册/登录（密码 hash 即可，不用做复杂安全）、onboarding 表单（按 PRD 字段：下班时间范围+加班频率、通勤、身体状态三选一、能否做饭三选一、饮食禁忌多选可跳过、健康问题一行可跳过、性别/年龄/身高/体重放最后可跳过；全部带默认值，点选为主）。提交后进入主界面。验证：新用户被 `/api/state` 导向 onboarding，填完导向 home。

**M2 RAG**：`crawl_corpus.py` 抓取并清洗 6.1 的来源（失败的人工补），人眼检查 `data/corpus/`，再跑 `build_corpus.py`、实现 `rag.search()`。验证：写个临时脚本，`search("久坐一天下班后适合什么活动", "exercise")` 返回相关块，且内容干净无导航残留。

**M3 Agent 主循环 + 首夜建议**：`llm.py`、`tools.py`（含 `calc_body_metrics`）、`agent.py`（5.1–5.3），onboarding 完成后立即调用一次生成首夜建议（首夜固定档位 3，理由行必须回显 onboarding 字段）。验证：不同 onboarding 组合（久坐 vs 体力消耗）给出方向不同的建议，且带来源；填了身高体重的用户，追问饮食时建议里出现量级参考（来自工具计算，非模型心算）；每次运行在 `logs/trace/` 生成缩进 JSON。

**M4 每日触点闭环**：「下班了」按钮、建议卡片、接受、一击纠正五个按钮、自由输入框、`/api/feedback` 回执屏、7.4 档位规则。验证：用虚拟时钟连过 3 天——第 1 天接受、第 2 天开头收到回执、选"完全没完成"、第 3 天建议明显变小。

**M5 食物照片**：上传 → qwen-vl 识别 → 入库 → 轻确认；晚上建议体现中午吃的东西。验证：上传一张外卖照片，晚上"吃什么"一行与之相关。

**M6 演示打磨**：agent_trace 侧栏、来源小字、安全信号测试（输入"胸口不舒服" → 只出休息/就医提示）、失败兜底默认建议、种子演示账号（一条脚本把演示用户和前两天历史灌好）。

**M7 走一遍 2 分钟演示脚本**（验收）：
1. 新用户 60 秒完成 onboarding → 当场拿到首夜建议（理由行回显字段）。
2. 次日中午（时钟+），拍一张黄焖鸡 → 轻确认。
3. 傍晚点「下班了」→ 先回执昨晚 → 自由输入「加了三个小时班累死了」→ Agent 主动撤掉运动，只留吃什么和几点睡（这是 PRD 指定的"最该演的一帧"）。
4. 展示来源依据和 Agent 调用轨迹。

---

## 十一、日志与可读记录

### 11.1 系统日志 `logs/app.log`

用标准库 `logging`（不引额外依赖），同时输出到控制台和文件，按天滚动（`TimedRotatingFileHandler`）。人类可读的单行格式：

```
2026-08-07 19:20:31 [INFO] user=demo1 event=offwork 触发建议生成
2026-08-07 19:20:33 [INFO] user=demo1 llm_call model=qwen-plus round=1 tool=search_reference 耗时=1.2s
2026-08-07 19:20:36 [WARN] user=demo1 json解析失败，重试第1次
2026-08-07 19:20:39 [ERROR] user=demo1 vision调用超时，走兜底
```

必须记的事件：每次 API 请求（路径、用户、耗时）、每次模型调用（模型名、轮次、调了什么工具、耗时、是否重试）、每次兜底触发、虚拟时钟变更。**排查"演示时为什么建议不对"全靠这个文件。**

### 11.2 Agent 轨迹 `logs/trace/`

每次 Agent 主循环结束，把完整过程存成一个**缩进格式的 JSON 文件**（一次运行一个文件，不追加）：

```
logs/trace/2026-08-07_demo1_1920.json
```

内容：注入的上下文摘要、每一轮的模型输出/工具调用/工具返回、最终 JSON、总耗时。写入统一用：

```python
json.dump(data, f, ensure_ascii=False, indent=2)
```

`GET /api/agent_trace` 直接读最新的这个文件返回给前端侧栏。

### 11.3 可读性约定（全项目强制）

- **所有**给人看的 JSON 文件（trace、导出的记录、调试输出）一律 `indent=2, ensure_ascii=False`，中文正常显示、有换行缩进。**禁止 jsonl / 单行压缩 JSON 落盘。**
- 需要给用户/评委看的记录（比如"我的历史"页面、导出），优先渲染成普通文字（"8月7日：建议饭后走8分钟，你反馈完成了"），JSON 只作为开发调试视图。
- 数据库里的 `*_json` 字段存储时也用 `ensure_ascii=False`，方便直接用 SQLite 工具查看。

## 十二、给 Claude Code 的执行约定

- 全程中文注释和界面文案。
- 不引入 LangChain / LlamaIndex / 向量数据库；运行时依赖只要 `fastapi uvicorn openai numpy python-dotenv`；爬虫脚本额外用 `requests beautifulsoup4 pdfplumber`（只在 scripts/ 用，不进运行时）。日志用标准库 `logging`。
- 每完成一个 M 阶段，跑通该阶段的验证再继续。
- 模型调用全部经过 `llm.py`，带 1 次重试和超时（30s）；任何模型失败路径都要有写死的兜底返回，**演示中途不允许白屏或报错**。
- 语料文件如果暂缺，先放占位内容并在 README 里列出 6.1 的待补清单，不阻塞后续阶段。
