# 反馈修改 批次 E 验证记录：结论屏关键词琥珀高亮

> 日期：2026-08-09 ｜ 分支：ui-integration ｜ 执行依据：`docs/V3/反馈修改计划.md` 第 5 条
> 改动文件：`backend/agent.py`（输出 JSON schema 加一行）、`backend/safety.py`（enforce 出口加 focus 一致性）、`frontend/app.html`（`renderJudgement`）、`scripts/test_safety.py`（+7 个用例）、`docs/交接文档.md`（契约）

## 一、落地清单

### 契约：advice 新增**可选**字段 `focus`

```json
"focus": "judgement 里最关键的 2~6 个字，必须是 judgement 的原文片段；挑不出就用 null"
```

- 只加在提示词的输出 schema 里，**`_parse_advice` 的必填校验一行没动**（仍只要求 judgement/stop）——模型不给 focus 不算解析失败，老行为零破坏。
- `focus` 为 null / 缺字段 / 对不上原文，界面都只是"整句平铺"，不影响任何既有功能。

### 后端出口保证一致性（`safety.enforce` 第 5 步，新增）

L3 的任何一条改写都可能动 judgement（crisis 整卡替换、danger 正向活动改写、诊断断言过滤、内部术语清除……）。在 enforce 末尾统一收口：

```
focus 不是字符串 / 是空白 / 不是最终 judgement 的子串  →  focus = None
```

一条规则覆盖所有改写路径，不用在每个分支里各写一遍。**绝不让一个对不上原文的片段流到前端**。

### 前端渲染（`renderJudgement`）

- 只有 `focus` 确实是 `judgement` 的子串才高亮，否则整句平铺（与后端同一条校验，双保险）；
- **DOM 拆分**：`createTextNode(前) + <em>focus</em> + createTextNode(后)`，用 `replaceChildren` 装配。
  **严禁 `innerHTML` 直插模型文本**——模型输出永远只作为文本节点存在，不可能变成标签；
- 样式复用 `nightwatch.css` 现成的 `h1 em`（v0.2 同款琥珀底），无新增 CSS。

## 二、验证

### 真实生成（demo1，走完整路径）

| | 值 |
|---|---|
| judgement | `今晚到家时间正常，精力尚可，安排最低档轻活动` |
| focus | `最低档轻活动` |
| 渲染出的 DOM | `今晚到家时间正常，精力尚可，安排<em>最低档轻活动</em>` |

✅ 琥珀底高亮块正确出现在大字里（截图为证），模型能稳定挑出关键词。

### 渲染分支穷举（直接喂 `renderJudgement`，含注入用例）

| 输入 | 结果 |
|---|---|
| judgement 含 `<img src=x onerror=alert(1)>` | ✅ 转义成 `&lt;img …&gt;` 文本，**未创建任何元素**（`querySelector('img')` 为 null） |
| focus = `<script>x</script>` | ✅ 不是子串 → 整句平铺，**未创建 script** |
| focus 不是子串（`跑步`） | ✅ 整句平铺，em 数 = 0 |
| focus = null | ✅ 整句平铺 |
| 无 focus 字段 | ✅ 整句平铺 |
| focus 在句首 | ✅ `<em>从简</em>就好，别硬撑` |
| focus 等于整句 | ✅ 整句被包 em |

### 安全路径

- **danger**（真实生成）：judgement `今晚必须休息，停止一切活动`、focus `必须休息` → 高亮正常，`data-sober=true` 下 `--amber` 是灰阶，高亮块渲染成**灰底黑字，不刺眼、不像警报**，符合"语气温和不是红色警报"。计划判断正确，无需特判。
- **crisis**：judgement 被整卡替换为定稿关怀语，enforce 第 5 步把 focus 清成 None → 无高亮。由单测覆盖（见下）。

### 单测（新增 7 个，`TestFocusHighlight`）

| 用例 | 断言 |
|---|---|
| 是子串则原样保留 | focus 不变 |
| 不是子串则置空 | focus → None |
| crisis 整卡替换后 focus 作废 | focus → None 且 judgement 已换成关怀语 |
| danger 改写 judgement 后 focus 作废 | focus → None |
| danger 未改写 judgement 则 focus 保留 | 反向用例，防止规则写得过宽 |
| 非字符串/空白一律置空 | `123 / "" / "   " / []` 全部 → None |
| 缺字段不报错也不新增 | 不抛异常，`get("focus")` 为 None |

**`scripts/test_safety.py`：113/113 全绿**（106 → 113）。

### 回归

`scripts/safety_regression.py`：**18/18 全绿**（动了提示词 schema，按计划强制全量重跑）。

## 三、问题与潜在问题

1. **写这批用例时先写错了一个断言**：以为 `今晚去楼下走走` 会触发 danger 的正向活动改写，实际 `_POSITIVE_ACT_RE` 要求前面有「可/能/适合/建议」这类词才命中，所以 judgement 没被改、focus 也就该保留。改成 `今晚可以去楼下走走` 后通过，并补了一条"未改写则保留"的反向用例。**这条正则比看上去窄**，以后写相关用例要先确认它到底匹配什么。
2. **focus 由模型自由挑选，长度不受代码约束**。提示词写了 2~6 字，但没有代码兜底——模型给一个很长的片段（甚至整句）时，只要是子串就会整段高亮。实测模型给的是 `最低档轻活动`（6 字）、`必须休息`（4 字），表现稳定；要硬约束可以在 enforce 里加长度上限，本批按计划"只做可选字段"没加。
3. **高亮块折行时观感一般**：`最低档轻活动` 跨两行时，第二行的琥珀块顶到左边缘、圆角被切开。这是 `h1 em` 的既有样式（v0.2 同款），不是本批引入的；嫌难看可以给 `em` 加 `box-decoration-break: clone`。
4. **每晚只高亮一处**。schema 只允许一个 focus，模型若想强调两处只能二选一。原型也是单处高亮，未扩展。
5. **focus 不参与任何决策**，纯展示。它不进安全检测文本、不进历史、不影响档位——出问题最多是不高亮，不会影响建议内容。
6. **老记录没有 focus**：数据库里之前生成的 advice_json 都不含这个字段，回看历史或刷新旧建议时一律整句平铺，属预期。
