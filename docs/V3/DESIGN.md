---
version: alpha
name: 值夜 · Nightwatch
description: 深夜低精力时刻使用的最低自我照顾 Agent。深底、单一琥珀强调、系统字体、零网络依赖；视觉能量来自排版对比与色块，不来自饱和度或动效密度。
colors:
  # 表面：四层，相邻层只差一档明度，靠边框而非明度对比划分区域
  surface: "#14121A"
  surface-container: "#1E1B25"
  surface-container-high: "#2A2633"
  on-surface: "#E9E4DC"
  on-surface-variant: "#A9A2B4"
  # 边框：两档，decorative 不承载信息（见 Colors）
  outline: "#6B6478"
  outline-decorative: "#3A3545"
  # 强调：全局唯一
  primary: "#FFB020"
  on-primary: "#14121A"
  # 第二色，只用于 Agent 说话那一句
  secondary: "#6EE7B7"
  # 印章硬阴影，比 surface 更深，不参与文字配色
  shadow: "#0C0A12"
  # 弹窗遮罩底色，与 shadow 同值但语义独立（见 Colors）；透明度写在 modal 组件里
  scrim: "#0C0A12"
  # 舞台底色，只在移除设备外壳前的评审夹具上出现
  stage: "#0A0910"
  # 安全模式覆写：同名变量整套换成中性灰阶，色相全部抽掉
  sober-surface: "#17171A"
  sober-surface-container: "#212126"
  sober-surface-container-high: "#2B2B31"
  sober-on-surface: "#EDEDEF"
  sober-on-surface-variant: "#B3B3BA"
  sober-outline: "#6E6E77"
  sober-outline-decorative: "#3A3A41"
  sober-primary: "#DADAE0"
  sober-on-primary: "#17171A"
  sober-secondary: "#B3B3BA"
typography:
  # fontWeight 已按本机实测封顶：含 CJK 的行不超过 600（见 Typography）
  display:
    fontFamily: system-ui
    fontSize: 33px
    fontWeight: 600
    lineHeight: 1.16
    letterSpacing: -0.02em
  display-compact:
    fontFamily: system-ui
    fontSize: 28px
    fontWeight: 600
    lineHeight: 1.16
    letterSpacing: -0.02em
  display-stamp:
    fontFamily: system-ui
    fontSize: 30px
    fontWeight: 600
    lineHeight: 1.1
    letterSpacing: -0.01em
  display-stamp-compact:
    fontFamily: system-ui
    fontSize: 25px
    fontWeight: 600
    lineHeight: 1.1
    letterSpacing: -0.01em
  title:
    fontFamily: system-ui
    fontSize: 17px
    fontWeight: 600
    lineHeight: 1.2
  body-lg:
    fontFamily: system-ui
    fontSize: 16px
    fontWeight: 600
    lineHeight: 1.4
  body:
    fontFamily: system-ui
    fontSize: 15px
    fontWeight: 400
    lineHeight: 1.55
  body-voice:
    fontFamily: system-ui
    fontSize: 15px
    fontWeight: 600
    lineHeight: 1.5
  body-ghost:
    fontFamily: system-ui
    fontSize: 15.5px
    fontWeight: 600
    lineHeight: 1.2
  body-strong:
    fontFamily: system-ui
    fontSize: 15px
    fontWeight: 600
    lineHeight: 1.4
  body-md:
    fontFamily: system-ui
    fontSize: 14.5px
    fontWeight: 600
    lineHeight: 1.5
  body-name:
    fontFamily: system-ui
    fontSize: 14px
    fontWeight: 600
    lineHeight: 1.2
    letterSpacing: 0.14em
  body-link:
    fontFamily: system-ui
    fontSize: 14px
    fontWeight: 600
    lineHeight: 1.2
  body-sm:
    fontFamily: system-ui
    fontSize: 13.5px
    fontWeight: 400
    lineHeight: 1.6
  body-sm-strong:
    fontFamily: system-ui
    fontSize: 13.5px
    fontWeight: 600
    lineHeight: 1.6
  body-xs:
    fontFamily: system-ui
    fontSize: 13px
    fontWeight: 400
    lineHeight: 1.25
  caption:
    fontFamily: system-ui
    fontSize: 12.5px
    fontWeight: 600
    lineHeight: 1.2
    letterSpacing: 0.04em
  caption-quiet:
    fontFamily: system-ui
    fontSize: 12.5px
    fontWeight: 400
    lineHeight: 1.6
  label-mono:
    fontFamily: Menlo
    fontSize: 10px
    fontWeight: 400
    lineHeight: 1
    letterSpacing: 0.08em
  label-mono-strong:
    fontFamily: Menlo
    fontSize: 10px
    fontWeight: 600
    lineHeight: 1
    letterSpacing: 0.08em
  label-mono-tight:
    fontFamily: Menlo
    fontSize: 10px
    fontWeight: 600
    lineHeight: 1
    letterSpacing: 0.06em
  label-mono-role:
    fontFamily: Menlo
    fontSize: 10px
    fontWeight: 400
    lineHeight: 1
    letterSpacing: 0.1em
  label-mono-stamp:
    fontFamily: Menlo
    fontSize: 10.5px
    fontWeight: 400
    lineHeight: 1
    letterSpacing: 0.16em
  label-mono-wide:
    fontFamily: Menlo
    fontSize: 11px
    fontWeight: 400
    lineHeight: 1
    letterSpacing: 0.12em
  label-mono-index:
    fontFamily: Menlo
    fontSize: 11px
    fontWeight: 600
    lineHeight: 1
  glyph-mono:
    fontFamily: Menlo
    fontSize: 12px
    fontWeight: 600
    lineHeight: 1
    letterSpacing: 0.04em
  glyph-mono-lg:
    fontFamily: Menlo
    fontSize: 15px
    fontWeight: 600
    lineHeight: 1
rounded:
  xs: 3px             # 行内小字形前缀（voice 竖线、safety 方块）；见 Shapes
  sm: 6px
  md: 12px
  lg: 14px
  xl: 18px
  full: 999px
  identity: 11px      # 唯一例外，只给 Agent 人像；见 Shapes
spacing:
  block: 16px         # 块间默认垂直 margin-top（清单、选项列、芯片组、注脚）
  block-lg: 18px      # 强调块上方（印章、折叠组、判断行组）
  gutter: 20px        # 屏幕左右安全边（主体、页脚）
  card-x: 15px        # 卡片行、选项、阈值容器的水平内边距
  card-y: 13px        # 卡片行、选项、判断行的垂直内边距
  row-gap: 12px       # 判断行的标签列到值列
  inline-lg: 11px     # 形状标记到文字（选项圆圈、清单编号）
  inline-md: 10px     # 阈值标签到内容
  stack: 9px          # 相邻可点块（页脚按钮、选项列、人像到名字组、安全出口字形、Onboarding 次级 editgroup 之间）
  inline: 8px         # 横排等权元素（芯片之间、次级按钮之间、折叠头字形到文字）
  inline-sm: 7px      # 药丸字形前缀、判断行的估算标记左侧
  inline-tight: 6px   # 小字形与文字（芯片方块、估算标记内边距）
  tight: 3px          # 折叠列表行间、印章标签的垂直内边距
components:
  button-primary:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.on-primary}"
    typography: "{typography.title}"
    rounded: "{rounded.lg}"
    height: 52px
    padding: 14px 16px
  button-primary-disabled:
    backgroundColor: transparent
    textColor: "{colors.on-surface-variant}"
    borderColor: "{colors.outline}"
  button-ghost:
    backgroundColor: transparent
    textColor: "{colors.on-surface}"
    borderColor: "{colors.outline}"
    typography: "{typography.body-ghost}"
    rounded: "{rounded.lg}"
    height: 48px
    padding: 14px 16px
  button-minor:
    backgroundColor: transparent
    textColor: "{colors.on-surface-variant}"
    borderColor: "{colors.outline-decorative}"
    typography: "{typography.body-md}"
    rounded: "{rounded.lg}"
    height: 46px
    padding: 11px 4px
  button-safety:
    backgroundColor: transparent
    textColor: "{colors.on-surface}"
    borderColor: "{colors.outline}"
    typography: "{typography.body-md}"
    rounded: "{rounded.full}"
    height: 46px
    padding: 11px 14px
  button-text:
    backgroundColor: transparent
    textColor: "{colors.on-surface-variant}"
    typography: "{typography.body-link}"
    height: 44px
    padding: 10px 14px
  chip:
    backgroundColor: "{colors.surface-container}"
    textColor: "{colors.on-surface}"
    borderColor: "{colors.outline}"
    typography: "{typography.body-md}"
    rounded: "{rounded.md}"
    height: 46px
    padding: 8px 10px
  chip-selected:
    backgroundColor: "{colors.surface-container-high}"
    textColor: "#FFFFFF"
    borderColor: "{colors.primary}"
  option:
    backgroundColor: "{colors.surface-container}"
    textColor: "{colors.on-surface}"
    borderColor: "{colors.outline}"
    typography: "{typography.body-lg}"
    rounded: "{rounded.lg}"
    height: 58px
    padding: 13px 15px
  option-selected:
    backgroundColor: "{colors.surface-container-high}"
    textColor: "#FFFFFF"
    borderColor: "{colors.primary}"
    borderWidth: 2.5px
  option-detailed:
    backgroundColor: "{colors.surface-container}"
    borderColor: "{colors.outline}"
    rounded: "{rounded.lg}"
    padding: "{spacing.card-y} {spacing.card-x}"
    gap: "{spacing.inline-lg}"
    labelColor: "{colors.on-surface}"
    labelTypography: "{typography.body-strong}"
    subColor: "{colors.on-surface-variant}"
    subTypography: "{typography.body-sm}"
    subMarginTop: "{spacing.tight}"
  option-detailed-selected:
    backgroundColor: "{colors.surface-container-high}"
    labelColor: "#FFFFFF"
    subColor: "{colors.on-surface}"
    borderColor: "{colors.primary}"
    borderWidth: 2.5px
  pill:
    backgroundColor: transparent
    textColor: "{colors.primary}"
    borderColor: "{colors.primary}"
    typography: "{typography.caption}"
    rounded: "{rounded.full}"
    padding: 6px 12px 6px 10px
  card:
    backgroundColor: "{colors.surface-container}"
    borderColor: "{colors.outline-decorative}"
    borderWidth: 1.5px
    rounded: "{rounded.xl}"
    padding: 0
  card-row:
    textColor: "{colors.on-surface}"
    typography: "{typography.body-lg}"
    padding: 13px 15px
  card-index:
    backgroundColor: "{colors.surface-container-high}"
    textColor: "{colors.primary}"
    typography: "{typography.label-mono-index}"
    rounded: "{rounded.sm}"
    size: 21px
  card-index-key:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.on-primary}"
  marker-key:
    backgroundColor: transparent
    textColor: "{colors.primary}"
    borderColor: "{colors.primary}"
    typography: "{typography.label-mono-strong}"
    rounded: 5px
    padding: 2px 5px
  stamp:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.on-primary}"
    borderColor: "{colors.on-primary}"
    borderWidth: 2.5px
    typography: "{typography.display-stamp}"
    rounded: "{rounded.xl}"
    padding: 20px 18px
  stamp-label:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.on-primary}"
    borderColor: "{colors.on-primary}"
    borderWidth: 1.5px
    typography: "{typography.label-mono-stamp}"
    rounded: "{rounded.sm}"
    padding: 3px 7px
  stamp-body:
    textColor: "{colors.on-primary}"
    typography: "{typography.body-md}"
  accordion-head:
    backgroundColor: transparent
    textColor: "{colors.on-surface-variant}"
    borderColor: "{colors.outline}"
    borderWidth: 1px
    typography: "{typography.body-sm-strong}"
    rounded: "{rounded.md}"
    height: 46px
    padding: 11px 12px
  accordion-panel:
    backgroundColor: "{colors.surface-container}"
    textColor: "{colors.on-surface-variant}"
    borderColor: "{colors.outline}"
    typography: "{typography.body-sm}"
    rounded: "{rounded.md}"
    padding: 12px 14px 12px 28px
  source-row-text:
    textColor: "{colors.on-surface-variant}"
    typography: "{typography.body-xs}"
  source-row-head:
    backgroundColor: transparent
    textColor: "{colors.on-surface-variant}"
    textColorExpanded: "{colors.on-surface}"
    typography: "{typography.body-xs}"
    height: 44px
  source-row-divider:
    borderColor: "{colors.outline-decorative}"
    borderWidth: 1px
  source-row-tag:
    backgroundColor: transparent
    textColor: "{colors.on-surface-variant}"
    borderColor: "{colors.outline}"
    typography: "{typography.label-mono-tight}"
    rounded: 5px
    padding: 2px 6px
  source-row-value:
    textColor: "{colors.on-surface-variant}"
    typography: "{typography.body-sm}"
  agent-face:
    backgroundColor: "{colors.surface-container-high}"
    borderColor: "{colors.primary}"
    rounded: "{rounded.identity}"
    size: 34px
  agent-voice:
    textColor: "{colors.secondary}"
    typography: "{typography.body-voice}"
    padding: 0 0 0 13px
  agent-name:
    textColor: "{colors.on-surface}"
    typography: "{typography.body-name}"
  agent-role:
    textColor: "{colors.on-surface-variant}"
    typography: "{typography.label-mono-role}"
  title-mark:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.on-primary}"
    rounded: 5px
    padding: 0 6px
  tag:
    textColor: "{colors.primary}"
    typography: "{typography.label-mono-wide}"
  row:
    borderColor: "{colors.outline-decorative}"
    borderWidth: 1px
    padding: 13px 0
  row-label:
    textColor: "{colors.on-surface-variant}"
    typography: "{typography.body-xs}"
    width: 78px
  row-value:
    textColor: "{colors.on-surface}"
    typography: "{typography.title}"
  row-est:
    backgroundColor: transparent
    textColor: "{colors.on-surface-variant}"
    borderColor: "{colors.outline}"
    typography: "{typography.label-mono-tight}"
    rounded: 5px
    padding: 2px 6px
  row-reason:
    textColor: "{colors.on-surface-variant}"
    typography: "{typography.body-sm}"
    marginTop: "{spacing.stack}"
    indent: 90px
    paddingBottom: "{spacing.card-y}"
    borderColor: "{colors.outline-decorative}"
    borderWidth: 1px
    linkElement: "{components.button-text}"
    linkGlyph: "改一下"
    linkPaddingX: "{spacing.inline}"
    linkWrap: nowrap
    linkShrink: 0
  threshold:
    backgroundColor: "{colors.surface-container}"
    borderColor: "{colors.outline-decorative}"
    borderWidth: 1.5px
    rounded: "{rounded.xl}"
    padding: 14px 15px
  threshold-label:
    textColor: "{colors.on-surface-variant}"
    typography: "{typography.label-mono}"
    width: 46px
  note:
    textColor: "{colors.on-surface-variant}"
    borderColor: "{colors.outline-decorative}"
    borderWidth: 1px
    typography: "{typography.caption-quiet}"
  wheel-picker:
    backgroundColor: "{colors.surface-container}"
    textColor: "{colors.on-surface-variant}"
    borderColor: "{colors.outline}"
    borderWidth: 1.5px
    rounded: "{rounded.md}"
    rowHeight: 40px
    containerHeight: 76px
    edgePeek: 18px
    visibleRows: 1
    selectedTextColor: "{colors.primary}"
    selectedTypography: "{typography.title}"
    itemTypography: "{typography.body-sm}"
    fadeHeight: 18px
    compactContainerHeight: 60px
    compactEdgePeek: 10px
  card-carousel:
    backgroundColor: "{colors.surface-container}"
    rounded: "{rounded.xl}"
    gap: "{spacing.inline}"
    dotSize: 5px
    dotGap: "{spacing.inline}"
    dotColor: "{colors.outline-decorative}"
    dotActiveColor: "{colors.primary}"
  welcome-tour:
    backgroundColor: "{colors.surface}"
    posterPaddingX: 20px
    dotSize: 5px
    dotGap: "{spacing.inline}"
    dotColor: "{colors.outline-decorative}"
    dotActiveColor: "{colors.primary}"
  time-band:
    height: 8px
    rounded: "{rounded.sm}"
    spentColor: "{colors.surface-container-high}"
    freeColor: "{colors.primary}"
    hatchColor: "{colors.outline}"
    hatchAngle: 45deg
    hatchLineWidth: 1px
    hatchGap: 3px
    minSegmentWidth: 24px
    tickTypography: "{typography.label-mono-tight}"
  photo-thumb:
    backgroundColor: "{colors.surface-container-high}"
    borderColor: "{colors.outline-decorative}"
    borderWidth: 1px
    rounded: "{rounded.md}"
    size: 56px
    removeSize: 20px
    removeBackgroundColor: "{colors.surface-container-high}"
    removeTextColor: "{colors.on-surface-variant}"
  icon-entry-list:
    backgroundColor: "{colors.surface-container}"
    borderColor: "{colors.outline-decorative}"
    borderWidth: 1.5px
    rounded: "{rounded.xl}"
  icon-entry-row:
    backgroundColor: transparent
    textColor: "{colors.on-surface-variant}"
    textColorActive: "{colors.on-surface}"
    dividerColor: "{colors.outline-decorative}"
    dividerWidth: 1px
    typography: "{typography.body-md}"
    height: 52px
    padding: "13px 15px"
    gap: "{spacing.inline}"
    iconSize: 30px
    iconRounded: "{rounded.md}"
    iconBackgroundColor: "{colors.surface-container-high}"
    iconColor: "{colors.on-surface-variant}"
    iconColorActive: "{colors.on-surface}"
    indicatorGlyphCollapsed: "＋"
    indicatorGlyphExpanded: "－"
    indicatorTypography: "{typography.label-mono}"
  icon-entry-grid:
    display: flex-row
    bubbleBackgroundColor: "{colors.surface-container}"
    bubbleBorderColor: "{colors.outline}"
    bubbleBorderWidth: 1.5px
    bubbleRounded: "{rounded.xl}"
    bubblePadding: "{spacing.stack} {spacing.card-x}"
    bubbleTailWidth: 18px
    bubbleTailHeight: 12px
    compactInputMinHeight: 52px
  icon-entry-cell:
    layout: icon-over-label
    iconSize: 20px
    iconColor: "{colors.on-surface-variant}"
    iconColorActive: "{colors.on-surface}"
    textColor: "{colors.on-surface-variant}"
    textColorActive: "{colors.on-surface}"
    typography: "{typography.body-md}"
    gap: "{spacing.inline}"
    padding: "{spacing.card-y} {spacing.inline-tight}"
  nav-icon:
    backgroundColor: transparent
    iconColor: "{colors.on-surface-variant}"
    iconColorActive: "{colors.on-surface}"
    size: 44px
    iconSize: 20px
  settings-group:
    textColor: "{colors.on-surface-variant}"
    typography: "{typography.label-mono-strong}"
    marginTop: "{spacing.gutter}"
    marginTopFirst: "{spacing.inline-tight}"
  settings-list:
    backgroundColor: "{colors.surface-container}"
    borderColor: "{colors.outline}"
    borderWidth: 1.5px
    rounded: "{rounded.xl}"
    marginTop: "{spacing.block}"
  settings-row:
    backgroundColor: transparent
    backgroundColorActive: "{colors.surface-container-high}"
    labelColor: "{colors.on-surface}"
    labelTypography: "{typography.body-strong}"
    subColor: "{colors.on-surface-variant}"
    subTypography: "{typography.body-sm}"
    subMarginTop: "{spacing.tight}"
    valueColor: "{colors.on-surface-variant}"
    valueTypography: "{typography.body-sm}"
    valueMaxWidth: 46%
    dividerColor: "{colors.outline-decorative}"
    dividerWidth: 1px
    minHeight: 52px
    padding: "13px 15px"
    gap: "{spacing.row-gap}"
    chevronGlyph: "›"
    chevronTypography: "{typography.glyph-mono-lg}"
    chevronColor: "{colors.on-surface-variant}"
    dangerLabelColor: "{colors.on-surface-variant}"
  switch:
    width: 44px
    height: 26px
    rounded: "{rounded.full}"
    trackColor: "{colors.surface-container-high}"
    trackColorOn: "{colors.primary}"
    borderColor: "{colors.outline}"
    borderColorOn: "{colors.primary}"
    borderWidth: 1.5px
    knobSize: 19px
    knobColor: "{colors.on-surface-variant}"
    knobColorOn: "{colors.on-primary}"
    knobInset: 2px
    knobTravel: 18px
  modal:
    overlayColor: "{colors.scrim}"
    overlayOpacity: 0.72
    backgroundColor: "{colors.surface-container}"
    borderColor: "{colors.outline}"
    borderWidth: 1.5px
    rounded: "{rounded.xl}"
    padding: "{spacing.gutter}"
    wrapPadding: "{spacing.gutter}"
    titleTypography: "{typography.display-stamp-compact}"
    titleColor: "{colors.on-surface}"
    bodyTypography: "{typography.body}"
    bodyColor: "{colors.on-surface-variant}"
    bodyMarginTop: "{spacing.inline-md}"
    actionsMarginTop: "{spacing.block-lg}"
    actionsGap: "{spacing.stack}"
  free-text-field:
    element: "input|textarea"
    backgroundColor: "{colors.surface-container}"
    textColor: "{colors.on-surface}"
    borderColor: "{colors.outline-decorative}"
    borderWidth: 1.5px
    rounded: "{rounded.lg}"
    minHeight: 52px
    minHeightTextarea: 78px
    padding: "14px 15px"
    typography: "{typography.body-lg}"
    placeholderColor: "{colors.on-surface-variant}"
    placeholderTypography: "{typography.body-sm}"
    placeholderWeight: 400
    micSize: 22px
    micBorderColor: "{colors.outline-decorative}"
    rowGap: "{spacing.inline}"
  calibration-sheet:
    overlayColor: "{colors.scrim}"
    overlayOpacity: 0.72
    backgroundColor: "{colors.surface-container}"
    borderColor: "{colors.outline}"
    borderWidth: 1.5px
    roundedTop: "{rounded.xl}"
    padding: "{spacing.gutter}"
    titleTypography: "{typography.display-stamp-compact}"
    bodyTypography: "{typography.body}"
    groupGap: "{spacing.block-lg}"
  note-sheet:
    shell: "{components.calibration-sheet}"
    freeTextElement: "{components.free-text-field}"
    optionGap: "{spacing.inline-md}"
    actionsElement: "{components.button-minor}"
    actionsGap: "{spacing.inline}"
  adjust-sheet:
    shell: "{components.calibration-sheet}"
    timeElement: "{components.wheel-picker}"
    choiceElement: "{components.chip}"
    saveElement: "{components.button-primary}"
  echo:
    element: button
    backgroundColor: "{colors.surface-container}"
    backgroundColorActive: "{colors.surface-container-high}"
    textColor: "{colors.on-surface-variant}"
    highlightColor: "{colors.on-surface}"
    typography: "{typography.body-sm}"
    highlightTypography: "{typography.body-sm-strong}"
    rounded: "{rounded.md}"
    padding: "13px 15px"
    marginTop: "{spacing.block}"
    separator: "　·　"
    maxItems: 3
    chevronGlyph: "›"
    chevronTypography: "{typography.glyph-mono-lg}"
    chevronColor: "{colors.on-surface-variant}"
---

# 值夜 · 设计规范

> 日期：2026-08-06（Asia/Shanghai）
> 格式：遵循 [design.md](https://github.com/google-labs-code/design.md) 规范（version alpha）
> 提炼来源：选型阶段原型 F「性格声音优先」（选型过程产物，未随仓库分发）
> 修订：2026-08-07 全量核对 F，补齐 15 个 token 与 18 个组件条目，修正 9 处与 F 不符的值
> 修订：2026-08-07 新增 4 个组件（wheel-picker / card-carousel / time-band / photo-thumb），组件数 34 → 38；不改动现有 22 色 / 27 字体级别 / 7 档圆角 / 13 间距的任何数值
> 修订：2026-08-08 收紧 wheel-picker 为静止单行 + 边缘提示（原可视 5 行 + 大范围渐隐遮罩），新增 containerHeight/edgePeek 字段；同时把 rowHeight 由此前与原型不一致的 36px 修正为实际的 40px。首版 edgePeek/fadeHeight 定为 10px，实测发现 10px 落在格内天然留白范围内、露不出邻格文字边缘，随后改为 18px（containerHeight 随之为 76px），fadeHeight 同步为 18px。组件数不变（38）
> 修订：2026-08-08 新增 1 个组件（welcome-tour，首次整屏引导卡），组件数 38 → 39；分页点沿用 card-carousel 的 dotSize/dotGap/dotColor/dotActiveColor 数值，不新增独立色值或档位
> 修订：2026-08-08 补写 Source Row（理由行）组件小节——该组件早已用于 s-plan/s-alt/s-shrink，但此前未进本文，是文档缺口的回填；同时新增首夜（s-firstnight）专用的可折叠变体：常驻规则从「结论屏理由行一律不可折叠」收窄为「除首夜外常驻」，因为 PRD 认定首夜理由行是唯一一次建信任的机会，改回可折叠但默认展开；折叠头是新 token（source-row-head，44px 高、⌄/⌃ 箭头），不套用 accordion-head 的虚线方框。新增 source-row-text/head/divider/tag/value 共 5 个 token，组件数 39 → 44
> 修订：2026-08-08 Pill（状态药丸）组件下线，5 个结论屏（s-firstnight/s-plan/s-alt/s-shrink/s-chronic）同步移除顶部药丸标签；`.plan li b` 由分类字（判/吃/动/停）改为 CSS counter 自动编号，修正此前与 Card Index 小节既有规范的偏差。组件数 44 → 43
> 修订：2026-08-08 新增 1 个组件（icon-entry，Home 页图标功能入口），组件数 43 → 44；同时修正 Home 页「补充今天」「传张三餐」两个按钮此前误借用 button-minor 装饰边（outline-decorative，对比度 1.57）的问题——两档边框分工是硬性规则，独立可点入口必须用可见档（outline，对比度 3.29），button-minor 的装饰边只适用于已有边框容器内的次级选项（如 `.recall` 三个反馈按钮），不适用于页面背景上的独立功能入口，这是对既有硬规则的订正而非新增判断。新组件复用 Accordion 已有的虚线↔实线 + ＋/－ 指示字符机制，新增图标色只用 on-surface-variant/on-surface，不占用琥珀或薄荷这两个已锁定的强调色
> 修订：2026-08-08 新增 1 个颜色 token（scrim，弹窗遮罩底色），色数 22 → 23；字体级别 27 / 圆角 7 档 / 间距 13 档不变。取值与 shadow 相同但不复用，理由沿用本文既有的 on-primary ↔ surface 同值不合并原则；不设 sober-scrim（安全模式抽的是色相，该值已接近无色相黑），透明度作为 modal 组件自身的 overlayOpacity，不进全局 token。此条为「先改本文再落下游」规则的正常执行：产品外壳补齐（返回栈、设置中心、弹窗）需要遮罩色，这是其中唯一一个现有 token 拼不出来的值
> 修订：2026-08-08 修正 icon-entry 组件两处问题，组件数不变（44）。① `height` 由 64px 改为 52px；② 去掉中段文字的主/副两行堆叠，改为单行（超长省略号截断）。用户反馈图标+文字组合下文案偏多；核对后发现该组件原本就该照 Accordion 已定的单行折叠头规范做（46px、单行、无副标题），64px 双行是上一条记录里引入时未对齐这条既有惯例。副标题原本承担的「为什么/怎么用」说明没有删掉，而是按「只说一次」原则挪进展开后的面板文案里只出现一次：Home 页「传张三餐」按钮的面板提示语由「拍一张就行，不拍也没关系」改为「拍一张就行，不拍也没关系——传了会让今晚的饮食建议更准」，把原副标题「照片给饮食做参考」的意思带出来；「补充今天」按钮的展开态文本框本身已说明用法，未改动。顺带把按钮文字的 font-size/line-height 从 14px/1.35 订正为与组件声明的 typography.body-md 完全一致的 14.5px/1.5
> 修订：2026-08-08 icon-entry 拆分为 icon-entry-list（外层卡片容器）+ icon-entry-row（卡片内的行），组件数 44 → 45（下线 1、新增 2，净增 1）。起因是用户反馈 Home 页树洞/食记两个入口「感觉很怪」：旧版每个入口各自一个虚线描边按钮、左右并列悬浮在页面背景上。复核发现两处根因——①虚线在本设计里只用来表示 Accordion「还没展开的折叠内容」，借给两个随时可用的真实功能入口，读出来的意思正好相反（虚线在通用 UI 语言里更接近「空状态/待办占位」）；②两个按钮左右并列构成一个两列网格，偏离 Layout 一节「单栏、无卡片网格」的通用原则。改法：两行合并进同一张卡片（icon-entry-list，与 Card 组件同规格：18px 圆角、1.5px outline-decorative 边框、surface-container 底），行与行之间只用 1px 装饰档分隔线（icon-entry-row 的 dividerColor），这是 Card Row 已经确立的写法，不是新造的容器语义。**这条修订同时收窄了上一条「边框必须是可见档」的硬规则**：该规则成立的前提是入口直接立在页面背景上、没有父级边框兜底；现在入口已经在 icon-entry-list 的实体边框内部，和 `button-minor` 在 `.recall` 内部使用装饰档的既有豁免（见 Do's and Don'ts 及 `.recall .minor .btn`）是同一件事，不是新开一个例外。展开面板不再有自己的圆角/左侧强调条，改为紧跟触发行、只用一条顶部装饰分隔线延续同一张卡片。单行标签、图标只用中性色两条硬规则不变
> 修订：2026-08-08 产品外壳（返回栈、设置中心、确认弹窗、历史回声）落地，新增 7 个组件——nav-icon、settings-group、settings-list、settings-row、switch、modal、echo——组件数 45 → 52（frontmatter 实际条目 53，差的一条是保留供历史追溯的已弃用 `pill`，见 Pill 小节；本文的组件数一直按这个口径记）。**23 色 / 27 字体级别 / 7 档圆角 / 13 间距全部不变**：这一轮没有新增任何全局 token，所有组件只引用已有档位，组件自身尺寸（44px 命中区、52px 行高、44×26 开关、19px 圆钮）按 wheel-picker / photo-thumb / icon-entry 的既有做法留在组件内部。落地时反查出下游 5 处越界值并就地订正，全部是先照本文改原型、不是反过来改本文：① `.modal h2` 20px 在字体标度上不存在（25px 与 17px 之间是空的），改用 display-stamp-compact（25px）；② `.setrow .chev` 17px 无衬线借用了 title 的字号却不是它的字重，改用 glyph-mono-lg（15px mono），与 Accordion / Icon Entry 的 ＋/－ 指示字符归为同一档；③ `.setgroup` 字距 .1em + 字重 600 的组合不存在，收到 label-mono-strong（.08em）；④ `.setgroup` 上边距 24px 不在间距标度上，收到 gutter（20px）；⑤ `.setrow .lab s` 上边距 2px 小于标度最小档，收到 tight（3px）。同批新增三条 Do's and Don'ts：破坏性确认的主按钮给「不执行」那一侧（没有红色可用，也不为一个弹窗新造危险色，改用主次分工表达）、开关状态必须同时由滑块位置表达、历史回声不显示完成情况与连续天数。Echo 的三条硬规则（不显示做没做到 / 不显示连续天数 / 不做成可浏览页面）是 PRD 设计原则五「一切文案写成避免归零」在视觉层的直接落点，不是本文自行引入的产品判断
> 修订：2026-08-08 推翻同日早些时候定的 Echo 第三条硬规则「不做成可浏览的历史页面，不可导出」，组件数不变（52，仍是 frontmatter 53 减已弃用 pill 的口径）。起因：用户从产品外壳落地那天起就一直把这行回声理解成「点开应该能看完整历史」的入口，明确要求推翻这一条；另外两条硬规则（不显示做没做到、不显示连续天数）不在推翻范围——它们的来源是 PRD 设计原则五「一切文案写成避免归零」，用户的诉求也只是「能翻到更早的记录」，不是要一份带完成度的成绩单，没有理由跟着一起松动。改法零新增视觉 token：新增的只读列表屏 `s-history` 完全复用已有的 `settings-list`/`settings-row` 渲染每一行（标签放事项、值放日期、`disabled`），和「设置 · 关于」屏「版本」那一行是同一种写法；入口就是 Home 页那一行回声本身——`echo` 组件 frontmatter 补上 `element: button`、`backgroundColorActive`（复用 `surface-container-high`，与 `settings-row` 的 hover/active 同值）、`chevronGlyph`/`chevronTypography`/`chevronColor`（复用 `settings-row` 的 chevron 三项），原来的纯文本 `<p>` 改为可点按钮，行尾追加 `›`。同步改写 Echo 组件小节与 Do's and Don'ts 里对应这条规则的措辞，避免文档自相矛盾
> 修订：2026-08-08 当晚校准的「今晚还剩多久」由四枚预设 chip 收为一只纵向滚轮，复用既有 `wheel-picker`，不新增 token 或组件。滚轮默认停在 Agent 估出的余量，用户不动即接受；需要改时可直接上下滚动，避免低精力时还要在多颗候选按钮之间比较。取值范围 20–180 分钟、10 分钟一档属于该校准场景的产品实现，不写进全局组件规格。同步修正抽屉开场：先完成内部滚动定位、强制浏览器确认初始离屏位，再在下一帧开启位移动画；不在 transition 同一帧执行 `scrollIntoView`，避免浏览器重算滚动容器而出现抽屉跳动。动效仅在 `prefers-reduced-motion: no-preference` 下声明，`reduce` 下即时呈现，符合 Motion 的双向声明
> 修订：2026-08-08 继续收轻当晚校准：剩余时间滚轮采用 `wheel-picker` 的紧凑变体（60px 高、上下各 10px 边缘提示），不再沿用 Onboarding 的 76px 大滚轮。移除它自身的圆角容器与实体外框，只保留两条 1px 装饰档选择线；已选文本为 15px 琥珀色，邻项仅作极轻提示。这样滚轮读作一条可调整的时间带，而不是校准抽屉中又一枚大按钮；精力和身体状况维持既有明确的 chip 选择，避免三项都变成不同的输入语言。新增的仅是既有组件的紧凑尺寸字段，组件数及全局色/字体/圆角/间距档位不变
> 修订：2026-08-08 把视觉重心让给「昨日反馈」卡片与主 CTA「开始今晚」：① 新增 `option-detailed`/`option-detailed-selected`，把 `.recall` 的两组反馈按钮（正常夜「做到了吗」、安全夜「现在感觉怎么样」）从等宽纯文字按钮改成标题+描述的两行选项列表，复用 `option` 的圆圈/边框/已选标签语言；选中态背景升到 `surface-container-high` 后描述文字须用 `on-surface`，沿用未选中态的 `on-surface-variant` 会落进对比度表已标记的禁止组合（5.98，见「对比度」一节），这是套用既有硬规则，不是新判断。② `icon-entry-row`（卡片内纵向堆叠行）弃用，新增 `icon-entry-grid`/`icon-entry-cell`：树洞、食记、历史三个入口改为卡片内横排三等分的图标+文字方块，历史格随之从独立的 `echo` 一行改为其中一格，`echo` 组件同步弃用（预览摘要、去重、`maxItems`、分隔符等字段不再被渲染，`s-history` 完整列表不受影响，仍完全复用 `settings-list`/`settings-row`）。这是对 2026-08-08 早些时候「历史设为可点入口」那条决定的**样式层收窄**：历史仍可点进 `s-history`，只是不再单独占一整行、不再显示预览文字，不是推翻。

**顺带订正一处历史计数缺口，不静默沿用旧数字。** 逐条核对 frontmatter 实际条目发现改动前是 54 条（活跃 53、弃用 1 即 `pill`），比上一条修订记录写的「52」多 1；差的 1 条是 `calibration-sheet`（当晚校准抽屉容器），它在「当晚校准」功能落地时进了 frontmatter，但当时的修订记录（见上方 2026-08-08 剩余时间滚轮相关两条）只描述了滚轮改紧凑变体，没有一条显式登记新增这个容器组件、也没有同步改计数——这是文档自身的记录缺口，不是本轮改动引入的。本轮在此基础上新增 4（`option-detailed`/`option-detailed-selected`/`icon-entry-grid`/`icon-entry-cell`）、新增弃用 2（`icon-entry-row`/`echo`），frontmatter 实际条目 54 → 58，弃用条目 1 → 3（`pill`/`icon-entry-row`/`echo`，均保留供追溯不计入组件数），**组件数应订正为 53 → 55**。23 色 / 27 字体级别 / 7 档圆角 / 13 间距全部不变，新组件只引用已有档位

> 修订：2026-08-08 6 个结论屏（`s-firstnight`/`s-confirm`/`s-plan`/`s-alt`/`s-shrink`/`s-chronic`）的 footer 统一收为「主按钮 / 调整一下 / 身体不舒服」三行，此前分散在各屏的改法（`s-confirm` 三个「改一下」文本链接、`s-plan` 独立的「补充一句」折叠区、每屏各异的换一换/再轻一点/今天不做等快捷按钮行）全部并入同一张 `calibration-sheet`：抽屉内新增常驻置顶的「补充一句」（自由输入 + 加班/早会/不方便三个即点芯片，原地挪自 `s-plan`，行为不变）和按当前屏动态给出的「换个做法」快捷跳转区（复用 `button-minor`），原有的时间/精力/身体结构化校准三项收进一个按屏隐藏的分组，只在 `s-confirm`/`s-plan` 显示。新增 1 个组件 `free-text-field`，回填 `.field`/`.mic`/`.inline-row` 这套早已在 Onboarding 与 Home「树洞」使用、但此前从未进 frontmatter 的自由输入字段规格；`calibration-sheet` 补充 `actionsElement`/`actionsGap` 两个字段描述新增的快捷跳转区，未引入新颜色/字体/圆角/间距值。同步改写 Calibration Sheet 小节的说明文字，并订正其中一处沿用自 Modal 小节的复制粘贴错误（此前该小节误把「清空全部数据」确认弹窗的「主按钮给不执行那一侧」硬规则原样复制成了自己的硬规则，与校准抽屉的实际交互无关，予以移除并替换为校准抽屉自己的硬规则）；顺带订正 Edit Group 小节「当前六份原型未实装」的过时表述——该字段本身早已实装，未定的只有麦克风代表的语音输入。frontmatter 实际条目 58 → 59，弃用条目仍为 3（`pill`/`icon-entry-row`/`echo`），**组件数 55 → 56**。23 色 / 27 字体级别 / 7 档圆角 / 13 间距全部不变

> 修订：2026-08-08 `option-detailed`/`option-detailed-selected` 弃用，从原型移除，组件数 56 → 54。用户反馈 `.recall` 两组反馈按钮（正常夜「做到了吗」、安全夜「现在感觉怎么样」）连同下方树洞/食记/历史三格「反馈信息收集做得太重」，且点击树洞/食记后看不到任何展开内容。诊断确认后者不止是视觉偏重，是真实布局缺陷：`.homelist{overflow:hidden}` 处在 `#s-home .body{display:flex; flex-direction:column}` 之内，按 flexbox 规范只有 `overflow:visible` 的项享有自动最小尺寸保护，`.homelist` 的自动最小尺寸因此是 0，在 `.body` 无滚动余量时被当作「最弱项」优先压缩，导致展开的树洞/食记面板被裁到几像素高、内容不可见。两处一并处理，用户在两轮确认中都选择推荐方案：① 展开面板就地修复，给 `.homelist` 补 `flex-shrink:0`，交还给 `.body` 已有的 `overflow-y:auto` 正常滚动展开，不改用抽屉/半屏等新交互模式；② 顺带把两组反馈按钮一起改轻，`option-detailed` 回退为纯单行 `option`，描述文案（如「都做完了，很不容易」）不再单独出现在按钮上——它们本来就与选中后的确认提示（`recallDoneText()`）内容重复，回退不丢信息。frontmatter 的 `option-detailed`/`option-detailed-selected` 条目保留供历史追溯，弃用条目 3 → 5（`pill`/`icon-entry-row`/`echo`/`option-detailed`/`option-detailed-selected`）。frontmatter 实际条目仍为 59，23 色 / 27 字体级别 / 7 档圆角 / 13 间距全部不变，未新增或修改任何全局 token

> 修订：2026-08-08 用户反馈单一的「调整一下」抽屉语义不清，拆分为「我要补充」（Note Sheet）与「改一下」（Adjust Sheet）两个独立入口。`calibration-sheet` 保留原 key 名但收窄为两张抽屉共用的外壳（遮罩、背景、边框、圆角、内边距、标题/正文字体），不再自带内容分段。**我要补充**（`note-sheet`，新 key）挂在全部 6 个结论屏的 footer，内容为「补充一句」+ 按屏动态给的「换个做法」快捷跳转，是往前走的定性修正，与原逻辑一致地不做数值重算。**改一下**（`adjust-sheet`，新 key）改回历史布局——只在 `s-confirm` 的 3 条 Row Reason（剩余时间/当前精力/身体状况）依据文字末尾各挂一个「改一下」文本链接，点开是同一张只装「时间/精力/身体」三项结构化校准 + 保存按钮的抽屉；`s-plan` 及其余屏不再出现这个入口——那三项是 `s-confirm` 阶段对「今晚状况」的初始判断，进入后续屏后要改的是行动本身，走「我要补充」即可，不重新暴露数值输入。同时补写此前从未进本文的 **Row Reason（判断依据行）** 小节（新 key `row-reason`）：`.rowsrc` 左侧 90px 对齐判断值列、`body-sm` 次要色、装饰档分隔线收尾，常驻不折叠；并收紧 Judgment Row 的硬规则一句，把「改判断走 Row Reason 的『改一下』，不直接把行变成输入框」写明确，不是新判断。三个新 key 净增 3、无新增弃用，frontmatter 实际条目 59 → 62，弃用条目仍为 5（`pill`/`icon-entry-row`/`echo`/`option-detailed`/`option-detailed-selected`），**组件数 54 → 57**。23 色 / 27 字体级别 / 7 档圆角 / 13 间距全部不变，新组件只引用已有档位，零新增全局 token

> 修订：2026-08-08 无头浏览器截图核对拆分后的 `s-confirm` 发现一处真实视觉缺陷：「剩余时间」「当前精力」两条 Row Reason 的依据文字较长，`.textlink` 沿用默认 14px 横向内边距时被 `.rowsrc` 的横向空间挤压，「改一下」三个字换行断成「改一」/「下」两行，「身体状况」一行因依据文字更短未复现。给 `row-reason` 新增 `linkPaddingX: "{spacing.inline}"`（8px）、`linkWrap: nowrap`、`linkShrink: 0` 三个字段，落地为 `.rowsrc .textlink` 这个更具体的选择器，`.textlink` 组件本身不改，其余 5 处既有用法不受影响。frontmatter 条目数与组件数不变（62 / 57），未新增全局 token，只是给已有 key 补充此前遗漏的字段

> 修订：2026-08-10 用户定调 `s-confirm` 从「中转站」改为「**暂存台**」：这一屏上所有跟补充信息、修正判断有关的操作，结果都必须先显示在这一屏上，页脚的琥珀主按钮是唯一能推进到建议页的出口。此前 Adjust Sheet 保存后直接重算并跳屏、Note Sheet 在判断页也走「提交并重新安排」，等于两个隐藏出口绕过了主按钮，用户改一项就被送走、没机会核对改对没有。改动全在行为与文案层，**零新增 token、零新增/弃用组件**（frontmatter 仍 62 条、组件数仍 57，23 色 / 27 字体级别 / 7 档圆角 / 13 间距不变），涉及四处文档：① **Judgment Row** 补写「值也可以来自用户改过的那一版」——改过的行换成用户给的值并**摘掉估算标记**（已经不是估的了，留着就是错误信息），Row Reason 同步改口「你刚改的，按这个算」，让「我刚才那一下生效了」在屏上看得见，而不是靠跳屏来证明。② 新增 **Supplement Log（判断页「你补充的」）** 小节：判断行组下方一段只读列表，标签复用判断行标签列的 13px / 400 / 次要色、列表复用 Home 已在用的「HH:MM 你说：XX」同一份数据与同一套样式，`spacing.block-lg` + `spacing.stack` 两个既有档位定位，无补充时整段隐藏。③ **Note Sheet** 的引导语与主按钮按屏分两种并列表写明（判断页「先记下」→ 留在本屏只留痕迹；其余 5 屏「提交并重新安排」→ 抽条件重算并进计划页），配一条硬规则：文案必须和提交后真正发生的事一致，否则不是语气差异而是骗点击。④ **Adjust Sheet** 主按钮由「按这个重新算」改为「按这个记下」，补写「打开时预填当前判断行上显示的值、原样保存等于没改」与「保存后留在判断页、只写回三行，不重算不落库不跳屏」，并删去原文「保存后正确回写 `state.today` 并按原逻辑重算,包括『有明显不适』触发安全分支」——「有明显不适」现在只写回身体那一行，与其余两项一起等主按钮交出去。同时把 Row Reason 硬规则里「必须真的能打开一处会重新计算这条判断的地方」改为「会改写这条判断的地方——改写发生在判断行上、当场可见」。主按钮文案定为**固定**的「就按这个安排」而不随改动状态浮动：唯一出口只能有一副面孔，文案一变用户就得重新判断按下去会发生什么。**注意本轮只收窄前端呈现，不放松安全**：判断页的补充虽然不再即时重算，后端在「当天还没建议」这条分支上补了一道即时安全闸门，命中 danger/crisis 立刻按下推进键等效处理并硬退出到安全结束页——安全永远赢过「停在当前屏」这条既有规则不受暂存台影响

> 修订：2026-08-10（二）用户指出暂存台的一处自相矛盾：在判断页说了「胃不舒服」，句子进了下面的「你补充的」，上面「身体状况」那行却还写着「暂未确认」——而同一句话从 Home 的「身体不舒服」进来时那一行**会**变，两个入口行为不一致。更要命的是这句话其实已经被带进今晚的生成上下文了，屏上那句「暂未确认」不是克制，是说假话。据此**推翻**上一条修订留下的「判断页的补充不即时改写三行判断」这条硬规则，改为：补充里**明确说到**三行中某一项时，那一行当场改成这句话的意思、摘掉估算标记、Row Reason 回显**用户原话**「你说：胃不舒服」；没说到的行一律不动，估算和「估」照旧。判断页仍然是暂存台——写回只发生在这一屏上，主按钮仍是唯一推进出口，这一条没有松动。改动全在行为与文案层，**零新增 token、零新增/弃用组件**（frontmatter 仍 62 条、组件数仍 57，23 色 / 27 字体级别 / 7 档圆角 / 13 间距不变），涉及三处文档：① **Judgment Row** 把「改过的行」的来源从「只有 Adjust Sheet」扩到「Adjust Sheet 或一句补充」，并把 Row Reason 拆成两种写法——手选写「你刚改的，按这个算」、抽出来的写「你说：<原话>」，因为用户必须能分辨这个值是自己定的还是系统替他理解的（后者才需要核对）。回显原话而不是复述结论（不写「你说：身体有明显不适」），把结论复述一遍等于把判断藏起来。② **Supplement Log** 的硬规则由「只有留下痕迹一种反馈」改写为「两种反馈，都当场发生在这一屏上，都不推进」，并写明句子与判断行两处并存、不是二选一，以及抽不出来时退化成只留列表（也就是原来的样子）、抽错了按「改一下」当场覆盖、手选永远压过推断。③ **Note Sheet** 表格里 `s-confirm` 那一行的「提交后」补上写回判断行，「不重算、不跳屏」保持不变

本文只管**视觉识别怎么复现**。产品做什么、Agent 怎么判断、有哪些流程和状态，全部以 PRD 为准；两者冲突时 PRD 优先。

本文的 YAML token 是数值的唯一真相。下游不得引入本文没有的档位；需要新档位时先改本文。

**本文与源原型 F 不同的五处，全部是刻意的**：

1. **字重全部封顶 600。** F 里声明了 650 / 700 / 800 / 850，但 `PingFang SC` 在 600 以上塌平（实测比值 1.0000），声明更高档只让同一行的数字变粗、汉字不变。本文所有 token 只用 400 / 600，渲染结果与 F 在纯 CJK 行上一致，在混排行上比 F 更整齐。详见 Typography 规则三。
2. **单行控件的行高写成实测比值。** F 在按钮、芯片、选项上不写 `line-height`，走浏览器 `normal`；本文按实测结果写成 1.2 / 1.25 等具体值。数值与 F 的声明方式不同，渲染一致。详见 Typography 行高节。
3. **结论屏的理由行常驻，不进折叠框——首夜例外。** F 把它折起来了，本设计改为常驻（build-notes 第 5 节 D5）。折叠组件只留给有真实补充内容的次要说明。首夜（`s-firstnight`）的理由行保留可折叠变体，但也**默认收起**，让用户先看到今晚的行动；需要了解依据时可自行展开。其余结论屏（`s-plan`/`s-alt`/`s-shrink`）不受影响，继续常驻不可折叠。折叠头不套用 Accordion 组件的虚线方框样式，是更轻的按钮+箭头变体，见 Source Row 组件。
4. **不把「全大写」当识别特征。** F 在 mono 标记上写了 `text-transform:uppercase`，但内容是汉字、没有可见效果。本文不收这条规则，换成 Latin 内容时也不必套用。
5. **顶栏内边距 `14px 18px 10px` 保持不标准化。** 它不走 20px gutter，作为标定项保留——人像 + 文字组合需要视觉居中而不是数值居中。

**F 做对、必须原样保留的六处**（F 会作为 CSS 参照一起交付，这六处不要在「整理规范」的名义下改掉）：

1. **单一强调色。** 全局只有琥珀，没有第二个彩色。改成「琥珀=行动、绿=完成、红=警告」就退回需要图例的仪表盘。详见 Colors。
2. **印章的硬阴影 + 倾斜。** `6px 6px 0 0` 零模糊、`-1.2deg`，只用在一处。这是全流程唯一的能量峰值，用柔和阴影替代等于没有。详见 Elevation & Depth。
3. **两档边框的分工。** `outline-decorative`（1.57）只做装饰分隔，可点边界一律 `outline`（3.29）。统一成一个「好看的灰」会让按钮边界在低亮度下消失。详见 Colors。
4. **状态同时由形状表达。** 字形前缀、方块、圆圈、`已选` 标签，每个状态都有非颜色的第二载体。详见 Do's and Don'ts。
5. **安全模式是整套变量覆写。** 一个根节点属性覆写全部同名变量，不是逐组件改色。详见 Colors。
6. **只用系统字体。** 断网时版面不变，这是比赛硬要求「可直接访问和实际体验」的一部分。详见 Typography。


## Overview

值夜是一个上夜班的同事：话少，替你把今晚的事挡掉。

界面性格由此推出三条基调：

**深底不是深色模式，是使用时刻的物理条件。** 核心使用时刻在深夜、用户已经很累、多数人会把屏幕亮度调低。亮底屏幕本身就是负担，所以 `surface` 是 `#14121A`——偏紫的深底，与系统深色模式的中性黑有可辨差别。正文色 `#E9E4DC` 偏暖不是纯白：深底上的纯白在低亮度屏幕上会发光晕。

**能量来自排版对比和色块，不来自饱和度或动效密度。** 全局只有一个强调色。33px 标题压在 15px 说明上方、琥珀实心块压在深底上、印章带 6px 硬阴影且微微倾斜——这些提供视觉活力，而不需要第二个彩色或连续动画。这条区分「界面有活力」和「界面向用户索取活力」：后者会要求一个已经耗尽的人再兴奋起来。

**留白偏紧，不偏空旷。** 屏幕内容少（每屏最多四行结论 + 一句话），但不铺开成杂志版式。用户要的是「一眼看完」，块间垂直间距默认 16px、强调块 18px，视线不需要长距离移动。

**空间与密度**：单栏，393pt 宽视口，无侧边栏、无标签栏、无卡片网格。每屏一个主按钮。

**不做的事**：不用渐变作为组件底色、不用玻璃拟态、不用图标字体或图片资源（人像与图标全部纯 CSS 或内联 SVG）、不加载 webfont。

**本文的覆盖边界**：只覆盖 393pt 屏幕内的产品界面。手机外壳、侧键、iOS 状态栏、home 指示条、舞台背景和右侧说明面板都是评审夹具，不受本文约束（它们各自带渐变和阴影，与上一段规则无关），交付时应全部移除。

## Colors

调色板是四层深表面 + 一个琥珀强调 + 一个薄荷第二色。除此之外界面上没有第三个彩色。

- **Surface（`#14121A`）**：屏幕底色与固定页脚底色。偏紫的深底。
- **Surface Container（`#1E1B25`）**：卡片、内容容器、未选中的可点区域。与底色只差一档明度，区域靠边框划分而非明度对比。
- **Surface Container High（`#2A2633`）**：卡片里再嵌一层——人像底、行内编号方块、选中态的芯片与选项。
- **On Surface（`#E9E4DC`）**：结论内容、标题、按钮文字。暖白，非纯白。
- **On Surface Variant（`#A9A2B4`）**：维度名、理由、说明、次级按钮文字。
- **Outline（`#6B6478`）**：需要被看见的边界。
- **Outline Decorative（`#3A3545`）**：装饰性分隔。
- **Primary（`#FFB020`）**：全局唯一强调色。
- **Secondary（`#6EE7B7`）**：只用于 Agent 说话那一句。
- **On Primary（`#14121A`）**：琥珀底上的文字。与 `surface` 同值但语义不同，不要合并——琥珀底的对侧色和画布底色恰好相同是巧合，将来改任一个都不该带动另一个。
- **Scrim（`#0C0A12`）**：弹窗遮罩。与 `shadow` 同值，同样不合并，理由与上一条一致。

### Scrim 不是第三个彩色

`scrim`、`shadow`、`stage` 三个都比 `surface` 更深，都不参与文字配色，也都不承载语义——它们是「比底还底」的一档，与「全局只有一个强调色」那条规则不冲突。判据是：**能不能有文字压在上面**。能的才算进配色，`scrim` 上面永远只有弹窗本体，不直接放文字。

它与 `shadow` 取同一个值，但**不复用 `shadow`**。理由同 `on-primary` 与 `surface`：现在相等是巧合，印章阴影和弹窗遮罩将来任一个要调，都不该带动另一个。

**不设 `sober-scrim`。** 安全模式抽掉的是色相，而 `#0C0A12` 已经接近无色相的黑，没有可抽的东西；遮罩的功能（压暗背景、把注意力收进弹窗）在两种模式下完全一致。这是 `sober-*` 覆写组的一个有意缺项，不是遗漏。

透明度不进 token，写在 modal 组件的 `overlayOpacity` 里——和 `wheel-picker`、`photo-thumb` 把自身尺寸留在组件内的做法一致。遮罩浓度是那一个组件的事，不是全局档位。

### Primary 锁死在一个颜色

主按钮、印章底、状态药丸、Agent 说话的竖线、核心标记，全部走同一个琥珀。

产品要表达的判断只有一个层级：「今晚只保住这一件事」。多一个彩色就多一个语义层级，用户在低精力状态下要先分辨颜色代表什么，才能读内容。单色强调让「有琥珀色的地方就是今晚要看的地方」成为不需要学习的规则。

拿掉这条会退化成：琥珀表示行动、绿色表示完成、红色表示警告的常规仪表盘，颜色重新变成需要图例的编码系统。

### 两档边框的分工是硬性的

`outline-decorative` 对 `surface` 的对比度是 **1.57**。这个值不足以让边界在深夜低亮度屏幕上可靠可见。

所以：**分隔线可以用 `outline-decorative`（丢了不影响理解），任何需要被识别为「一个可点区域的边界」的一律用 `outline`（3.29）。** 卡片内部的行分隔用装饰档是对的，芯片外框用可见档是对的。

拿掉这条区分会退化成：所有边框统一取一个好看的灰度，然后在真实亮度下，按钮的可点边界消失，用户只能靠猜。

### Secondary 是身份，不是配色

薄荷色在整个界面里只出现一处：Agent 说话的那一句。它与琥珀竖线组成一个固定形态，形态本身就是「这是 Agent 在说话」的标识。

**不让第二处用它**：性格靠位置和形状被认出来，不靠字数。一旦薄荷色出现在第二个地方，「薄荷色 = Agent 的声音」这条等式失效，性格必须回到靠文案长度表现，而这与「每屏最多一句」直接冲突。

### 安全模式是整套变量覆写

`sober-*` 那组值不是一个配色变体，是一个机制：一个属性挂在设备根节点上，覆写同名变量，整套灰阶生效——色相全部抽掉，人像退成方块，Agent 说话那一句在 CSS 里不渲染。

```css
.device[data-sober]{
  --ink:#17171A; --ink-2:#212126; --ink-3:#2B2B31;
  --line:#3A3A41; --line-2:#6E6E77;
  --text:#EDEDEF; --muted:#B3B3BA;
  --amber:#DADAE0; --mint:#B3B3BA; --on-amber:#17171A;
}
```

覆写同一批变量名，所以**所有组件不需要各自写安全态样式**——这是它复用价值高的原因。琥珀变成浅灰 `#DADAE0`，主强调仍然存在、只是不再有情绪。薄荷虽然也被覆写，但那一句已经不渲染，覆写值只是防止将来有第二处用到它时漏掉。

两条实现规则：

1. **只由安全信号触发**，不做深色/浅色主题开关、不给用户手动切换。它变成偏好设置，就不再读作「它自己停下来了」。
2. **退场必须整套发生。** 只换颜色不去掉那句话，等于让一个中性灰的界面继续开玩笑，比不退场更糟。

安全模式下对比度不降级——`sober-on-surface` 对新底色是 15.30，比常态还高。可读性不能因为气氛变严肃而变差。

> 触发条件、何时进入这个模式、以及慢病场景下的半退场，属于产品定义，见 PRD 安全闸门一节。

### 对比度

全部实测值（WCAG 2.1 相对亮度公式复算，非估值）：

| 前景 | 对 `surface` | 对 `surface-container` | 对 `surface-container-high` |
|---|---|---|---|
| `on-surface` | 14.67 | 13.40 | 11.66 |
| `on-surface-variant` | 7.53 | 6.87 | 5.98 ✗ |
| `primary` | 10.15 | 9.27 | 8.07 |
| `secondary` | 12.18 | 11.12 | 9.68 |
| `outline` | 3.29 | 3.00 | 2.61 ✗ |
| `outline-decorative` | 1.57 | 1.43 | 1.25 |

`on-primary` 对 `primary` 是 10.15。安全模式下 `on-surface` 15.30、`on-surface-variant` 8.58、`primary` 12.85，全部高于常态。

**标 ✗ 的两格是禁止组合，不是缺陷。** `surface-container-high` 上只允许 `on-surface`、`primary` 和 `#FFFFFF`。

新增任何颜色或新的前景/背景组合前先复算，低于以下值不得使用：

- 正文与结论内容：**≥ 7**
- 次要文字：**≥ 6.5**
- 非文字边界：**≥ 3**
- 装饰性分隔：无下限，但不得承载信息

**为什么定得比 WCAG AA（4.5）高**：使用时刻是深夜、用户已经很累、多数人会把屏幕亮度调低。AA 是正常条件下的最低可读，这里的条件不正常。

> 完整 WCAG 合规需要人工用辅助技术实测并由无障碍专家复核，本节只覆盖对比度这一项。

## Typography

只用系统字体栈，无 webfont。断网时版面与对比度不变——这不是妥协，是可靠性要求：作品要能在现场直接打开体验。

```css
--sans: -apple-system, BlinkMacSystemFont, "PingFang SC", "Hiragino Sans GB",
        "Microsoft YaHei", "Noto Sans CJK SC", "Source Han Sans SC", sans-serif;
--mono: ui-monospace, SFMono-Regular, Menlo, Consolas, "PingFang SC", monospace;
```

本机实测解析结果：**CJK 走 `PingFang SC`，Latin 与数字走 `system-ui`，mono 走 `Menlo`**。

**27 个字体级别，落在 17 档字号上**。源原型产品侧实际有 17 档字号，文档按「字号 + 字重 + 行高 + 字距」的组合拆成 27 个命名级别：display 四个、title 一个、body 十一个、caption 两个、label-mono 七个、glyph-mono 两个。同一字号出现多个级别是因为字重、行高或字距不同：15px 有四个（`body` / `body-voice` / `body-strong` / `glyph-mono-lg`，前三个差行高与字重、第四个换字体族），10px 有四个 mono 级别只差字距（0.06 / 0.08 / 0.1em），13.5px 和 12.5px 各两个只差字重。半像素档（14.5 / 13.5 / 12.5 / 10.5）保留是因为在源原型里使用次数多，取使用多的一侧能少改地方——这是实现成本的考虑，不是视觉判断。0.5px 在 393pt 宽的视口上不产生可感知的层级差。

**矮屏（`max-height:740px`）降档**。标题 33→28、30→25，card-row 16→15、内边距 13/15→11/14。正文不降——空间不够时先牺牲标题气势，不牺牲可读性。

- **Body Large（16px）**：结论行内容与反馈选项——比说明大一档，因为这是用户唯一必须读懂的东西。
- **Label Mono（10-11px）**：mono 字体，大字距。用于行标、`核心`、`已选`、`估` 这类元数据标记。mono 与内容形成质感区分，用户不必阅读就知道那是标记而非内容。源原型在这些元素上声明了 `text-transform:uppercase`，但内容是汉字，没有可见效果——**不要把全大写当成本设计的识别特征**，换成 Latin 内容时也不必套用。

### 字重：CJK 三档，混排必须封顶

**实测结论**（无头 Chrome 渲染后统计 canvas 墨量，CJK 等宽、宽度测不出粗细）：

| 侧 | 可分辨档位 | 实测 |
|---|---|---|
| CJK（`PingFang SC`） | **三档：400 / 500 / 600** | 400→500 墨量 +24%，500→600 +8%，600→850 完全塌平（比值 1.0000）。13 / 16 / 33px 三个字号结论一致 |
| Latin 与数字（`system-ui`） | **九档全部生效** | 400→850 每档递增 4-6% 墨量，字宽也逐档变宽 |
| mono（`Menlo`） | **两档：400 / 600+** | 500 与 400 完全相同，600 往上塌平 |

**规则一：CJK 侧只用 400 / 600。** 400 给长说明、折叠内容、行标签和小字说明，600 给结论内容、标题、按钮、印章、Agent 说话那一句。

500 档实测可分辨，但**源原型产品侧出现 0 次**，本文也没有任何 token 用它。它作为「需要第三档时唯一允许的值」保留，不作为现有层级的一部分——想用它之前先确认规则二不够用。

**规则二：层次差不够时用字号和颜色补，不用字重。** 真正拉开层级的是 `on-surface` 与 `on-surface-variant` 的明度差和字号差。

**规则三：含 CJK 的行一律封顶 600。** 声明更高档时，同一行里数字和 Latin 真的走到那一档，而汉字被封顶在 600——`23:30 上床` 里数字会比汉字明显粗一档。纯数字、纯 Latin 的独立元素（状态栏时间、行内编号、mono 标记）可以走更高档，因为它们不与汉字同行。

拿掉规则三会退化成：标题里的时间点看起来像被加粗强调过，而那不是任何人的设计意图——用户会以为数字被特意突出了。

### 行高：只在会折行的地方成立

会折行的元素（标题、说明、`.voice`、结论行、折叠内容、印章说明、阈值行）必须按 token 的行高走。

**单行控件（按钮、芯片、选项、折叠头、药丸）的高度由 `height` + `padding` 决定，行高不参与。** 源原型在这些元素上没写 `line-height`，走浏览器的 `normal`；`normal` 不是单一比值，它按字体度量取整到整数 px，实测在 12.5–17px 区间落在 1.125 到 1.231 之间。本文给这些 token 写的是实测比值（如 `title` 的 1.2 ≈ 17px 走 normal 得到的 20px），数值与源原型的声明方式不同，渲染结果一致。

不要给单行控件按行高重算高度：`option` 是 58px、`chip` 46px，这些是 `height` 的值，与 `body-lg` / `body-md` 的行高无关。

### 字距

CJK 正文不加字距。调整只有三类：

- **标题收紧**：`-0.02em`（33px）、`-0.01em`（30 / 25px 印章）。大字号下默认字距显得松散。
- **mono 标记放开**：产品侧共五档，`0.06em`（估算标记）、`0.08em`（`核心` / 阈值标签）、`0.1em`（角色标签）、`0.12em`（Tag）、`0.16em`（印章标签）。小字号 mono 不加字距会糊成一团；这五档按「标记有多需要被当成一个整体读」排，估算标记最贴内容所以最紧，印章标签最像印刷标识所以最松。
- **两处 CJK 例外**：Agent 名字 `0.14em`（`body-name`）、状态药丸 `0.04em`（`caption`）。这两处是刻意的：名字要读作一个标识而不是一个词，药丸要读作一个状态标签。除这两处外，CJK 元素不加字距——源原型的主按钮带 `0.01em`，在 17px 上折算 0.17px，不可感知，已合并掉。

## Layout

单栏，垂直堆叠，无网格。视口按 393pt 宽设计。

### 三层结构

```
┌─────────────────┐
│ topbar  固定    │  Agent 人像 + 名字 + 角色标签
├─────────────────┤
│ body    可滚    │  内容，overflow-y:auto
├─────────────────┤
│ foot    固定    │  主按钮 + 次级动作 + 安全出口，带上边框
└─────────────────┘
```

**为什么页脚固定**：用户在低精力状态下，主按钮的位置必须可预测。内容长度随分支变化，如果按钮跟着内容走，每次都要先找按钮在哪。上边框（装饰档，1px）让页脚在滚动时与内容有明确分界。

### 间距

**块间垂直（`margin-top`）**：正常块 **16px**（清单、选项列、芯片组、注脚），强调块 **18px**（印章、折叠组、判断行组）。

**同组元素之间（`gap`）**，按「里面装的东西有多大」分五档：

| 档 | 用在哪 | 依据 |
|---|---|---|
| **12px** | 判断行的标签列↔值列 | 两列是并列关系，要读作「同一行的两部分」而不是两个块，需要比 11px 再放开一点 |
| **11px** | 清单编号↔文字、选项圆圈↔文字 | 形状标记比文字矮，靠 11px 让它读作行首标记而不是紧贴的装饰 |
| **10px** | 阈值标签↔内容 | 46px 定宽标签列，10px 已足够分开 |
| **9px** | 页脚按钮之间、选项列之间、人像↔名字组、安全出口的方块↔文字、Onboarding 同屏内相邻的次级 editgroup 之间、同一 editgroup 内 chips↔紧跟的补充输入框 | 相邻的可点块，间距要小到读作一组、大到不误触 |
| **8px** | 芯片↔芯片、次级按钮↔次级按钮、折叠头的字形↔文字 | 横排等权元素，比 9px 再收一档，强调「这些是同一批备选」 |

**字形标记↔文字**：**6px**（芯片方块、估算标记内边距）。**7px**（药丸字形前缀、判断行的估算标记左 margin）。

**收紧**：折叠列表的行间 **3px**、印章标签内边距的垂直向 **3px**。

**8px 是一个真实档位**，不要因为它「看起来像默认值」而回避——它承担横排等权元素的间距，与 9px 的「一组可点块」是两个不同判断。

**三层内边距**：
- **顶栏**：`14px 18px 10px`（上 / 左右 / 下），针对人像图形、名字和角色标签优化，不走 20px gutter。
- **主体**：`6px 20px 14px`（上 / 左右 / 下）。左右 20px 是屏幕安全边，上方 6px 拉近内容与顶栏，下方 14px 避免最后一块元素贴页脚边框。
- **页脚**：`12px 20px calc(16px + env(safe-area-inset-bottom))`（上 / 左右 / 下）。上方 12px 让主按钮与边框保持合适距离，下方动态适配全面屏手势区。

**为什么顶栏不走 20px**：人像 + 文字组合不同于文字块，14/18/10 的不对称内边距让这组元素视觉居中而不是数值居中。这是一个标定项，不需要标准化。

**为什么统一块间到 16px 而不是分层**：内容块之间没有需要用间距表达的层级差——四行结论和一句话之间不存在「更相关」和「更不相关」。一个值让实现时不必判断。

### 每屏一个主按钮

次级动作横排进一行（`button-minor`，46px 高，装饰档边框，次要文字色）。安全出口在所有给出建议的屏幕上常驻，形态永远相同。

**为什么次级动作横排而不是纵向堆叠**：纵向堆叠会让每个选项看起来同等重要，用户要逐个读。横排一行读作「这些都是备选」，主按钮的唯一性保持完整。

### 触控目标

最小 **44px**，实际取值：主按钮 52px、幽灵按钮 48px、次级与安全出口 46px、芯片 46px、反馈选项 58px。

反馈选项最大是刻意的：那一屏用户要在三到四个选项里选一个，且是当晚最后一次交互，精力最低。

## Elevation & Depth

**默认没有高度。** 层次靠表面明度和边框，不靠阴影。四层表面（`surface` → `surface-container` → `surface-container-high`）各差一档明度，加上两档边框，足够表达嵌套关系。

深底上的柔和阴影几乎不可见——在 `#14121A` 上投一层半透明黑，得到的还是 `#14121A`。用阴影表达高度在深色界面里是无效的手法。

**唯一的例外是印章的硬阴影**：`6px 6px 0 0 #0C0A12`，零模糊、零扩散、纯位移。这不是模拟光照，是平面设计里的偏移印刷效果——它让印章读作「一个盖上去的实体」而不是「一个更亮的卡片」。配合 2.5px 深色描边和 `-1.2deg` 旋转，构成全流程唯一的能量峰值。

这个手法只允许用在印章一处。第二处出现就变成一种通用装饰，峰值随之消失。

## Shapes

圆角六档：`3 / 6 / 12 / 14 / 18 / 999`。

| 档 | 用在哪 | 依据 |
|---|---|---|
| `3` | 行内高亮标记（`em` 包裹 `[keyword]`） | 标题或正文里高亮一个词时的小色块底，足以脱离锐角但不突出 |
| `6` | mono 状态索引、聚焦环 | 贴着文字的小方块，圆角再大就变成胶囊，读起来像标签而非编号 |
| `12` | 中等可点区域（芯片、折叠头） | 一次点击的目标，够软但不显得可拖动 |
| `14` | 主要可点区域（按钮、反馈选项） | 比 12 大一档，让主按钮不靠颜色也能被认出层级 |
| `18` | 内容容器（卡片、印章） | 容器包着若干行，圆角需要大到能读成「一块」 |
| `999` | 胶囊（状态药丸、安全出口） | 全圆角表示「这不是内容块，是一个状态或一个出口」 |

**唯一例外：Agent 人像的 `11px`。** 保留是因为它要同时不像圆头像、不像方图标——34×34 上 11px 正好落在「一个有身份的方块」这个印象上，换成 12 会开始像普通图标容器。例外只允许这一处，且必须写在这里，否则下一个人会照抄出第二个例外。

`50%` 保留给真正的圆形（人像的眼睛、单选圈），它是形状不是圆角档位。

**形状标记（≤13px 的纯 CSS 小图形）不走这个阶梯**，各自按视觉需要单独定：芯片方块 13px / `4px`、安全出口方块 11px / `3px`、人像的嘴 2px 高 / `2px`、说话竖线 3px 宽 / `3px`（等于全圆）。这些值不 token 化——它们是图形本身的一部分，与容器圆角不是同一类判断，一旦进阶梯就会有人拿去给组件用。

**为什么砍到六档**：源原型 F 产品侧有十一个圆角值，其中 `2 / 3 / 4 / 5` 四档在真实屏幕上肉眼无法区分。多出来的档位不产生视觉信息，只产生「下次该用哪个」的犹豫。本设计保留 `3px` 只给行内高亮标记（`h1 em`），日常组件从 6 起步。

拿掉这条会退化成：每个组件按手感单独定圆角，界面看起来仍然「还行」，但没有一处能说清为什么，改版时全靠重新试。

**折叠头↔折叠内容的映射**：折叠头本身 `12px`，展开后内容容器 `18px`（与卡片同档）；头仍可见，用 1px 虚线描边表示「这里还有内容展开了」，与常规边框的「这是一个边界」区分。

### 边框宽度

五档：

| 档 | 用在哪 | 依据 |
|---|---|---|
| **1px** | 装饰分隔（判断行、卡片行、页脚上边框、注脚上边框）、折叠头虚线、小标记描边（`核心` / `已选` / 估算） | 只表达「这里有一条界线」，不表达可点 |
| **1.5px** | 常态组件边框（人像、芯片、选项、卡片、阈值容器、印章标签） | 可点区域和内容容器的默认档 |
| **2px** | 形状标记轮廓（选项的 18px 圆圈、安全出口的 11px 方块） | 小图形要在 1.5px 的容器边框旁边仍然可辨，得比容器粗一档 |
| **2.5px** | 选项（`.opt`）选中态、印章描边 | 全流程只有两处需要「这一处比别处重」，两处共用同一档 |
| **3px** | 折叠内容的左边框、Agent 说话的琥珀竖线 | 竖线是身份标记不是边界，要粗到能当色块读 |

**芯片选中态不加粗，只换颜色**（1.5px 不变，边框转琥珀 + 底色升一档 + 内嵌方块填充）。芯片是横排多选的粗颗粒纠正，逐个加粗会让整排跳动。

**选项选中态加粗到 2.5px** 是因为它是纵向单选：同一时刻只有一个是 2.5px，跳动不会累积，而单选需要更强的「就是这一个」。

## Components

组件的数值在 YAML `components` 里。这里写状态集合和硬规则。

### Agent Face（人像）

34×34、11px 圆角的方块，纯 CSS 画两眼一嘴，无图片资源。三态：

| 态 | 形态 | 时机 |
|---|---|---|
| 常态 | 两点一横 | 默认 |
| 无奈 | 右眼变横线，嘴略偏 | Agent 承认自己判断偏高时 |
| 安全模式 | 五官消失，换中性方块，边框变灰 | 安全模式生效时 |

**硬规则：表情只反映 Agent 对自己判断的态度，永不反映对用户状态的评价。** 表情一旦与用户的完成情况挂钩，就变成一个会失望的脸——那与产品目标相反。

### Agent Voice（说话）

左侧 3px 琥珀竖线（`::before` 绝对定位，上下各内缩 3px，3px 圆角即全圆）+ 薄荷色文字（15px / 1.5 / 600），13px 左内边距。**每屏最多一句。** 安全模式下 `display:none`，不是变灰。

形态固定、位置固定、长度固定（一句）。这三个固定让性格可识别而不占篇幅。

### Pill（已弃用，2026-08-08 从原型移除）

原为全圆角胶囊状态标签，1.5px 琥珀描边、透明底、琥珀文字，出现在 `s-firstnight`/`s-plan`/`s-alt`/`s-shrink`/`s-chronic` 五个结论屏顶部。用户反馈首夜屏信息量太大、阅读压力高，逐屏核对后发现药丸文案与同屏其他内容重复：要么和 H1 语义重复（如 `s-shrink` 药丸「这版更小」× 标题「那就再小一点」），要么原因已经写在下面的理由行里（如 `s-firstnight` 药丸「今晚先给条低的」× 理由行「第一晚：还没有你的完成记录，先给条低的试」）——顶部同时出现药丸和 H1 会争夺视觉焦点，去掉药丸不丢信息。

frontmatter 保留 `pill` 条目供历史追溯，不再有组件引用它。

### Card（内容容器）

18px 圆角，1.5px 装饰档边框，`surface-container` 底，`overflow:hidden`。

**容器本身内边距为 0，内边距在行上（`card-row`：13px 15px）。** 这不是省事，是为了让行分隔线通到容器两侧边缘——如果容器带内边距，分隔线会在两端各留一段空白，卡片就读成「几条并列的短线」而不是「一张被切分的表」。

内部行用 1px 装饰档下边框分隔，最后一行不带分隔线。行内可挂 `核心` 标记（`marker-key`：琥珀描边 mono 小标签，右对齐）。

区别于阈值容器（`threshold`）：同样 18px 圆角、1.5px 边框、同一底色，但它内边距在容器上（14px 15px），因为里面是两行不需要分隔线的对比内容。

### Stamp（印章）

琥珀实底 + 2.5px 深色描边 + `6px 6px 0` 硬阴影 + `-1.2deg` 旋转。内含一个 mono 小标签、一行大标题、一行说明。

**只在一处出现：用户接受建议的那一刻。** 它是全流程唯一的能量峰值，第二处出现峰值就消失。

### Chip / Option（选择控件）

芯片是粗颗粒纠正用的横排按钮组，46px 高，最小宽度 86px，`aria-pressed` 表达选中。选项是纵向单选列表，58px 高。

两者都**带形状标记**：芯片带 13px 方块（4px 圆角，1.5px 描边），选项带 18px 圆圈（`50%`，2px 描边）。选中时填充琥珀并留一圈内阴影做出「实心圆点」效果——芯片 `inset 0 0 0 2px`，选项 `inset 0 0 0 3.5px`，两者都用 `surface-container-high` 作内圈色，按图形尺寸取值。

**Home 昨晚回顾紧凑变体。** 三个反馈选项（正常夜和安全夜各一组）横向等分同一行，避免回顾卡把紧接着的树洞 / 食记入口挤出首屏。它沿用 Option 的 18px 圆圈和选中填充，但容器改用 `button-minor` 的 46px 高、11px 4px 内边距、`body-md` 字号和 8px 间距；为保住三等分宽度，选中态不追加行尾「已选」标签，圆点和 `aria-pressed` 是状态载体。点选完成后只保留一句确认，**水平居中并收为 `caption`**（12.5px），让它读作轻反馈而不是新的内容段落。这个变体只用于一次性回顾，不改变普通选项仍为纵向 58px 列表的规则。

**选中态的三处差异**：芯片只换颜色（边框保持 1.5px 转琥珀，底色升一档，文字转 `#fff`）；选项另外把边框加粗到 2.5px，并在行尾追加 mono `已选` 标签（琥珀描边，5px 圆角）。

**硬规则同上：状态不靠颜色单独表意。**

**两行变体（`option-detailed`，已弃用，2026-08-08 从原型移除）。** 曾专用于 `.recall` 的两组反馈按钮（正常夜「做到了吗」、安全夜「现在感觉怎么样」），把单行标题换成标题+一行描述，让选项本身携带一句共情文案。用户反馈这组按钮连同其下方的树洞/食记/历史三格「反馈信息收集做得太重」；排查同时发现一处真实布局缺陷——`.recall` 与树洞/食记所在的 `.homelist` 同处 `#s-home .body{display:flex; flex-direction:column}` 之内，`.homelist{overflow:hidden}` 按 flexbox 规范的自动最小尺寸为 0（只有 `overflow:visible` 的项才受最小内容尺寸保护），而 `.body` 在没有滚动余量时会优先压缩这个「最弱项」，导致展开树洞/食记面板时内容被裁到只剩几像素、看不出任何交互反馈，不只是视觉偏重的主观感受。两处一并处理：`option-detailed` 回退为纯单行 `option`，描述文案已在选中后的确认提示（`recallDoneText()`）里保留，不丢信息；`.homelist` 补 `flex-shrink:0`，交还给 `.body` 已有的 `overflow-y:auto` 正常滚动展开，不再被压缩。frontmatter 的 `option-detailed`/`option-detailed-selected` 条目保留供历史追溯，不再有组件引用它们。

### Button（五态）

全部共用 14px 圆角 + 1.5px 边框 + `width:100%`，只有次级按钮横排时不占满。

| 态 | 底 / 边框 / 文字 | 高 | 字号 | 内边距 |
|---|---|---|---|---|
| 主按钮 | 琥珀实底 / 琥珀 / `on-primary` | 52px | 17px | 14px 16px |
| 幽灵 | 透明 / 可见档 / 正文色 | 48px | 15.5px | 14px 16px |
| 次级 | 透明 / 装饰档 / 次要色 | 46px | 14.5px | 11px 4px |
| 安全出口 | 透明 / 可见档 / 正文色，全圆角 | 46px | 14.5px | 11px 14px |
| 禁用 | 透明 / 可见档 / 次要色 | 52px | 17px | 14px 16px |

**禁用态字重降一档**（源原型 800 → 650；本设计 CJK 封顶后是 600 → 500 意图，实际渲染同为 600，字重差在汉字上不可见）。**禁用的可辨识性靠底色与文字色，不靠字重**——琥珀实底消失、文字转次要色，这两处足够。

次级按钮的水平内边距只有 **4px**：它横排在一行里，宽度由 flex 分，内边距大了文字会先折行。

主按钮按下用 `filter:brightness(.92)`——琥珀实底上改边框色不可见。其他三态按下改边框色为琥珀。

文本链接（`button-text`）不算按钮态：无边框、无底、带下划线，44px 最小高度，用于「今晚先不用」这类退出动作。

### Safety Exit（安全出口）

全圆角胶囊，46px 高，1.5px 可见档边框，正文色文字（14.5px），带 11px 方块字形前缀（纯 CSS `::before`，2px 描边、3px 圆角，与文字间隔 9px），内容居中。**形态在所有屏幕上完全相同**——位置、尺寸、文案、字形都不变。

方块用描边而不是填充：填充会让它读作一个状态指示（「已启用」），描边读作一个出口标记。

用户在身体不适时不应该需要寻找这个出口。任何屏幕上它都长一个样、在同一个位置。

### Accordion（折叠）

折叠头：46px 高，12px 圆角，**1px 虚线**可见档边框，次要文字色，13.5px。展开后只改两处——边框转实线、文字转正文色。右侧 `::after` 用 mono 15px 的 `＋` / `－` 表达状态（`margin-left:auto` 推到行尾）。

展开内容：`surface-container` 底、12px 圆角、**3px 可见档左边框**、`padding:12px 14px 12px 28px`（左侧 28px 给圆点列表让位）、13.5px / 1.6 行高次要色文字、行间 3px。

**虚线↔实线是这个组件唯一的结构信号**：虚线读作「这里还有内容没展开」，实线读作「这是一个边界」。关掉动效后这个信号仍然成立。

> **本设计与源原型 F 的偏离**：F 把结论屏的理由行放在这个折叠框里，本设计改为常驻（build-notes 第 5 节 D5）。折叠组件只用于有真实补充内容、需要按需展开的次要说明。首夜例外见 Source Row 组件——理由行改回可折叠，但用的是更轻的按钮+箭头变体，不是本组件的虚线方框。

### Source Row（理由行）

结论屏「为什么是这条线」的专用组件，语义是「这是依据，不是结论」——所以字号比最低线本身轻一档，也不套用 Accordion 的虚线方框。引导语是 `<button>`（`source-row-head`：13px / 400 / 次要色 / 44px 高，满足触控目标），右侧 `::after` 用 mono 12px 的 `⌄` / `⌃` 表达折叠/展开。展开后头部文字色由次要色转正文色；不改变整体结构，也不额外制造卡片。

行动建议屏（`s-plan` / `s-alt` / `s-shrink`）默认收起：用户先看到今晚做什么，想知道依据时再展开查看 `dt`/`dd` 行。首夜 `s-firstnight` 同样默认收起（`aria-expanded="false"`），避免理由行抢占首次行动建议的注意力；用户可按需查看。演示重置会还原各屏的默认状态。

两种变体共用同一套行结构：`dt`/`dd` 行顶部加一条分隔线（`source-row-divider`：1px / `outline-decorative`），每行下方再加一条，行内 `padding:11px 0`。`dt` 复用 `row-est` 的视觉语言（`source-row-tag`：mono 10px / 0.06em / 600 / 次要色 / `outline` 描边 / 5px 圆角 / `padding:2px 6px`），标的是信息来源（「你刚填」「第一晚」「接下来」），不是数值本身。`dd`（`source-row-value`：13.5px / 400 / 1.6 行高 / 次要色）承载实际理由文字。

**硬规则：这个组件永远只服务「为什么」，不重复结论屏已经说过的「是什么」。** 一旦某一行开始复述最低线本身，说明它该被删除或并入结论文案，而不是留在这里凑数。

### Threshold Compare（阈值前后对比）

容器与卡片同规格（18px 圆角、1.5px 装饰档边框、`surface-container` 底），但内边距在容器上（14px 15px）。

两行，各 `padding:6px 0`，标签列定宽 46px（mono 10px / 0.08em / 次要色），与内容间隔 10px：

- **上一次**：14.5px / 600，次要文字色，`text-decoration:line-through`。
- **下一次**：同字号，正文色，`::before` 加琥珀 `→ ` 前缀（700 字重）。上方 1px 装饰档分隔线，`margin-top:4px` + `padding-top:11px`。

两行相同时收掉上一行，箭头换成中点。

**硬规则：只表达相对关系，不给总量、不做进度条。** 这个组件的存在是为了让「Agent 学到了什么」可见，而进度条会把它变成一个可以追求达成的指标。

### Tag（标签）

琥珀色 mono 行内标签（`label-mono-wide`：11px / 0.12em），带方括号标记。上下 margin 让它与前后段落拉开距离。

**硬规则：只标记已确定的状态或事实，不用于模糊预测或鼓励性提示。**

### Title Mark（标题内高亮）

`h1 em` 实现的行内关键词高亮：琥珀实底、深色文字、**5px** 圆角、6px 左右内边距，`em` 只作为语义标记不应用斜体。

**只在需要从一行标题里突出一个词时使用，不泛化成通用装饰。**

### Agent Name & Role（人物信息）

人像旁的 Agent 名字用 `agent-name`（`body-name`：14px / 600 / 0.14em），角色标签用 `agent-role`（`label-mono-role`：mono 10px / 0.1em / 次要色）。两者只出现在顶栏，与人像一起构成固定身份信息。

名字的 0.14em 字距是 CJK 上的刻意例外（正文汉字不加字距）——两个字的名字需要靠字距撑开才能读作一个标识而不是一个词。

### Judgment Row（判断行）

两列布局：左侧标签列（`dt` / `body-xs`：13px / 次要色 / 78px 宽），右侧值列（`dd` / `title`：17px / 600 字重）。可在值后附 mono 估算标记（`row-est`：10px / 0.06em / 次要色 / 可见档描边 / 5px 圆角）。行与行之间用装饰档分隔线，第一行上方再加一条，构成判断行组（`.rows`）。

**只作为判断清单而不作为可编辑表单输入——这是 Agent 决策的透明化结构，不是用户填写区。需要修正判断时通过 Row Reason 里的「改一下」进入 Adjust Sheet，不直接把行变成输入框。**

**判断行的值不只来自 Agent，也来自用户已经改过的那一版。** 用户在 Adjust Sheet 里改过某项、或在「我要补充」里说的一句话明确说到了某项后，这一行显示的是用户那一版的值，同时**摘掉估算标记**——它已经不是估的了，标记留着就是错误信息。没被改过的行保持原样：值是 Agent 的估算，标记在，依据是 Agent 那句解释。三行各自独立，改一行不影响另外两行的呈现。

下方 Row Reason 同步换掉，两种写法对应两种来源，必须能分辨：手动在 Adjust Sheet 里选的写「你刚改的，按这个算」；从一句话里抽出来的写「你说：<原话>」，回显用户自己的措辞。用户得能看出这个值是自己亲手定的还是系统替他理解的——后者才需要核对，写成一样就把这个区别抹掉了。

### Row Reason（判断依据行）

紧跟在某条判断行下面的一句解释（`.rowsrc`，`body-sm`：13.5px / 次要色 / 1.6 行高），左侧留白 **90px**（= 标签列 78px + 判断行 gap 12px），让依据文字跟判断值对齐,不跟左侧标题对齐；行末 1px 装饰档分隔线收尾。它不是折叠内容,一律常驻显示。

依据文字后追加一个复用 `{components.button-text}` 的「改一下」链接（`row-reason.linkGlyph`），点击打开 Adjust Sheet 并定位到这条判断对应的分组。这个位置的链接收窄横向内边距到 `{spacing.inline}`（8px，`row-reason.linkPaddingX`）、强制不换行（`linkWrap: nowrap`）、不参与 flex 收缩（`linkShrink: 0`）——`.rowsrc` 是横向空间紧张的两栏布局,链接若沿用 `button-text` 默认的 14px 内边距会在依据文字较长的行被挤到只剩单字宽度、把「改一下」拆成两行,`.textlink` 本身的 44px 触控高与其余 5 处既有用法不变,只在 `.rowsrc .textlink` 这个更具体的选择器上收紧。

**硬规则：链接只在这条判断依据对应 Adjust Sheet 里的一项结构化输入时出现。** 判断依据本身只是陈述、不是表单；「改一下」不是随手加的装饰，它必须真的能打开一处会改写这条判断的地方——改写发生在判断行上、当场可见，不是跳到下一屏才兑现。

### Supplement Log（判断页「你补充的」）

`s-confirm` 的判断行组下方、页脚之上的一段只读列表：一行 `body-xs` 次要色标签「你补充的」（与判断行标签列同字号/字重/色，`spacing.block-lg` 上边距），下方 `spacing.stack` 处接 Home 页那套「HH:MM 你说：XX」的补充记录列表，完全复用同一份数据和同一套样式，不新增任何 token。当天还没补充过时整段隐藏，不留空标题。

**硬规则：判断页上的补充有两种反馈，都当场发生在这一屏上，都不推进。** 用户在这一屏「我要补充」说的话，第一去向是出现在这个列表里；如果这句话里**明确说到**了上面三行判断中的某一项（「胃不舒服」→ 身体、「累得不行」→ 精力、「加班到九点」→ 剩余时间），那一行同时改成这句话的意思，摘掉估算标记，Row Reason 改为回显这句原话「你说：胃不舒服」——句子仍然留在列表里，两处并存，不是二选一。**没说到的行一律不动**：估算继续挂着「估」，屏上绝不出现一个用户没说过的数。

回显的是**用户的原话**而不是我们抽出的结论（不是「你说：身体有明显不适」），因为这一行的用途是让用户自己核对我们理解得对不对——把结论复述一遍等于把判断藏起来。抽不出来（这句话没说到三项里的任何一项，或抽取不可用）就退化成只留在列表里，这也是原来的样子；抽错了用户按「改一下」当场覆盖，手选永远压过我们的推断。

这条规则推翻了本节此前写的「不即时改写三行判断」。当时的顾虑是「自由句是定性的，硬翻译成数值就是替用户下判断」，但真正替用户下判断的是**另一种沉默**：用户说了「胃不舒服」，系统其实已经把这句话带进了今晚的生成，屏上身体那行却还写着「暂未确认」——那不是克制，那是说假话。写回并回显原话，用户看得见、改得动；不写回，用户只能猜。

**硬规则（管整个 `s-confirm`）：这一屏是暂存台，页脚的琥珀主按钮是唯一的推进出口。** 屏上所有跟补充信息、修正判断有关的操作——「我要补充」的自由句、「改一下」的三项校准、从 Home 带着一句不适进来——结果都必须先落在这一屏上看得见，谁都不许顺手把人送进建议页。主按钮文案固定为「就按这个安排」，不随改了什么而变：它表达的是「以屏上此刻这一版为准，去安排」，无论用户改了三行、只补了一句话、还是什么都没动，这句话都成立且指向同一件事。文案随状态浮动会让唯一出口看起来像好几个不同的按钮，用户就得每次重新判断按下去会发生什么。

### Card Index（卡片序号与关键标记）

`.plan li b` 实现的列表编号：mono 数字（`label-mono-index`：11px / 600），21×21 方块，6px 圆角，墨色三档底；带 `data-key` 属性时改琥珀底。

关键标记（`.plan li[data-key]::after`）为琥珀描边 `核心` 标签（`label-mono-strong`：10px / 0.08em），5px 圆角，右对齐自动推至行尾。

**硬规则：序号是结构标定，不承载优先级信息。关键标记明确出现条件（见 PRD），不随意打到其他项上。**

### Marker Key（已弃用，内容并入 Card Index）

本小节已废，内容并入上一节。frontmatter 保留 `marker-key` 条目只为对应 `.plan li[data-key]::after` 的琥珀描边「核心」标签。

### Note（注脚）

页脚上方 1px 装饰档分隔线 + 12px 上内边距，`caption-quiet`（12.5px / 1.6），次要文字色。用于补充说明或免责声明，不重复主内容。

### Text Link（文本链接按钮）

无边框、透明底、44px 最小触控高度、下划线（3px offset）、次要文字色、650 字重。形态像链接但技术上是 `<button>`，用于不主要但可点的辅助动作。

### Edit Group（自由输入区）

`editgroup > p` 作为引导文字（13px / 次要色 / 8px 下 margin），后接实际输入框或控件（字段本身的规格见 Free Text Field）。Onboarding 的饮食禁忌、身高体重等结构明确的单项输入均走这个组合，已实装。

**规则位仍未定的只有语音输入：麦克风字形（`.mic`）目前纯装饰，具体要不要接、接了之后的交互形态待用户决定。**

### Wheel Picker（滚轮选择器）

纯 CSS 实现，`scroll-snap-type: y mandatory` + `scroll-snap-align: center`，不引入任何 JS 库。默认变体用于 Onboarding 时间：单格 **40px** 高，数字约 17px 高、垂直居中，容器高 **76px**（上下各 18px），保留 1.5px 可见档描边、12px 圆角与 `surface-container` 底。18px 必须大于格内天然留白（约 11.5px），才能真的露出相邻数值的一点笔画。选中格转琥珀，其余格用 `body-sm`（13.5px）次要色；渐隐遮罩覆盖整段探出区域。

当滚轮是一个已分组校准项中的单一数值（当前为「今晚还剩多久」）时，用紧凑变体：容器高 **60px**、上下各 **10px** 边缘提示；不再自带圆角卡片或实体外框，只保留中心的两条 1px 装饰线。选中值收为 `body-strong`（15px / 600）琥珀色，邻项只露极轻边缘。它应该读作一条可拖动的时间带，不能与其下的 chip 一样读作大按钮。

**硬规则：必须有预置默认值，不动即接受。** 这是滚轮相对于 chip 的唯一优势——覆盖任意时刻的同时不强迫用户操作。若某处滚轮没有合理默认值，说明这里不该用滚轮。

`role="listbox"`，每格 `role="option"`，容器 `aria-activedescendant` 指向选中格；`↑`/`↓` 键改值一格，触发方式与触摸拖拽产生同一个事件路径，不建两套状态同步逻辑。

> 具体用在哪几屏、步长与取值范围属于产品定义，见 PRD。当前原型把它同时用于 Onboarding 上下班时间与当晚校准的剩余时间；后者默认停在 Agent 估值，用户不动即接受。

### Card Carousel（卡片轮播）

横向 `scroll-snap-type: x mandatory`，每张卡片占容器 100% 宽，卡片本身复用 `card` 规格（18px 圆角、1.5px 装饰档边框、`surface-container` 底）。卡片间 `gap` 用 `spacing.inline`（8px）。

分页点直径 **5px**（复用 `marker-key` 的 5px 圆角作为直径基准，视觉上两者都是「贴着内容的小标记」），点间距用 `spacing.inline`（8px），非激活态 `outline-decorative`、激活态 `primary`，无描边、纯色块——分页点是位置指示不是可点边界,不需要 `outline` 那档对比度。

**硬规则：分页点是状态反映,不是导航控件的唯一入口。** 键盘与手势(滑动)必须同样可达,分页点仅做视觉同步,`role="tablist"`/`role="tab"` 语义可选叠加但不是唯一交互路径。

### Welcome Tour（首次整屏引导卡）

与 Card Carousel 同样是横向 `scroll-snap-type: x mandatory`，但不是"屏内嵌一个小轮播"，而是整屏本身就是轮播——每张卡贴满 `.body` 四边：**无描边、无圆角、背景与屏幕底色一致**（`{colors.surface}`），不复用 `card` 的容器规格。卡片内容（tag + 标题 + 说明）左右各留 **20px**（`posterPaddingX`），对齐屏幕内容区已有的水平安全边，保证沉浸感不牺牲文字对齐一致性。

分页点直接沿用 Card Carousel 已定数值（`dotSize` 5px、`dotGap` 8px、非激活 `outline-decorative`、激活 `primary`），因为两者表达的是同一件事——"第几张"。

**与 Card Carousel 硬规则的唯一差异：这里的分页点可以点击跳转。** Card Carousel 的分页点只做视觉同步、不是导航入口；Welcome Tour 只有 3 张、无更深的功能层级，允许分页点兼作跳转控件，但手势滑动仍是主入口，点击是补充路径而非替代。进入下一阶段的按钮从第 1 张起常驻显示、不设单独"跳过"文字链接——不能做成必须看完才能继续。

**硬规则：整屏海报变体只用于首次打开的价值引导，不用于承载表单或需要长期停留的内容。** 一旦某屏需要输入或多次往返查看，就不再适用这个变体的沉浸式无边框写法。

### Time Band（时间关系带）

单条横向进度带,高 **8px**,`rounded.sm`(6px)圆角,总宽随容器。分两类分段:**已占用**(如通勤)用 `outline` 色的斜纹填充——**45° 斜线,线宽 1px,间隔 3px**,不填实色,不用琥珀;**可支配**用 `primary` 实色填充。每个分段最小宽度 **24px**,窄于此宽度时段落仍保持可辨认的最小块,不按比例压缩到消失。

刻度与时间点文字用 `label-mono-tight`(10px / 600 / 0.06em),贴在带的上方或下方,不叠在带内。

**为什么已占用用斜纹而不用实色**:这条带要表达"这段时间不是空的,但也不是被禁止的"——斜纹读作"有内容占着",实色读作"这里不能动"。两类分段都用实色会让带看起来像一个进度条(暗示"已完成/未完成"),而这条带表达的是时间归属,不是完成度。

**硬规则:只表达时间归属的比例关系,不做成进度条,不出现百分比或"已用 X%"文案。**

**安全模式下的斜纹**:斜纹颜色随 `data-sober` 切到 `sober-outline`,不使用任何琥珀系颜色(常态与安全态都不用 `primary`/`sober-primary` 画斜纹,只用 `outline`/`sober-outline`)。这是本设计目前唯一的斜纹图案用法,引入前提是明确它在安全模式下不携带情绪色。

### Photo Thumb（照片缩略图）

用户一次可选多张后，每张是 **56px** 正方形缩略图，`rounded.md`(12px)圆角，1px 装饰档描边，`surface-container-high` 底（图片加载前的占位色），以 `spacing.inline`（8px）间距自动换行。移除操作以「清除照片」文字入口统一清掉本次选择，不逐张制造额外操作。

**硬规则:缩略图只证明"文件已选中",不暗示内容被读取。** 缩略图旁或下方的回执文案不得出现"看到""识别""分析"——界面不得暗示产品理解了用户上传的内容。

### Icon Entry（图标功能入口）

Home 页与 `.recall` 相邻的一组功能入口（树洞、食记）是**无容器的横排两格**（`icon-entry-grid`），取代此前的纵向堆叠行（`icon-entry-row`，已弃用）。它是 Home 的补充输入层；其上方的昨晚反馈仍使用 `surface-container-high` 和 `outline` 外框区分，而「开始今晚」仍是唯一的琥珀主按钮。入口行以 `display:flex` 横排，每个 `icon-entry-cell` 用 `flex:1 1 0` 等分可用宽度，图标在上、文字在下（`layout: icon-over-label`）纵向居中：只有 **20px** 线性图标和下方单行文字（`body-md`，超长省略号截断），不设图标底座、外框或格间分隔线。

**只保留一行标签,不带副标题，这一条不变。** 图标已经承担一次说明，副标题基本是把图标的意思再讲一遍——这条判断在上一版就已确立，横排布局下依然成立。真正需要交代「为什么/怎么用」的场合，仍放进展开后的面板里只说一次（例如传三餐面板的提示语）。

**指示字符（＋/－）随行式布局一并下线，改为直接展开/收起，无独立指示字形。** 横排入口都以图标与文字色从次要色转主文字色（`iconColorActive`/`textColorActive`）作为展开态提示，不再额外画字形。树洞和食记共享一块展开位：点另一格会替换当前面板，不累计两块输入；再次点当前格可以收起。展开面板占满宽度，**在入口行上方以紧凑对话气泡浮出**：`surface-container` 底、1.5px `outline` 描边、`rounded.xl` 圆角、9px×15px 内边距；底部居中于触发入口的一枚 18×12px 同色尾巴把两者关联起来。树洞输入收为 52px 单行高度，麦克风仍是装饰，贴在右侧；食记复用同一气泡外壳，在同一行只放简短提示与「添加照片」操作。这样两个入口的展开交互读作同一类“补充一句”，又不占用下方主操作区。

**硬规则：这组入口不承担分组或状态语义，不加外框、格线或图标底座。** 它们只负责进入补充功能；边界仅在用户展开输入面板时出现，避免与上方的昨晚反馈卡和下方主 CTA 竞争层级。

**硬规则:图标颜色只能用 on-surface-variant / on-surface,不占用琥珀或薄荷。** 两个强调色分别锁死给「主 CTA/印章/核心标记」和「Agent 语音行」两处专用场景（见 Colors）,这里新增的图标必须走中性色阶,否则界面里会出现第三种彩色语义,用户需要多记一条对照表。

### Nav Icon（顶栏返回与设置）

顶栏右侧的两个图标按钮：返回箭头（`‹`，内联 SVG 折线）和更多入口（3 个实心圆点的内联 SVG）。命中区 **44px** 见方，图标 20px，透明底、无边框，只用次要文字色，`:hover`/`:active` 转主文字色。当前更多入口只通向设置，但不让 20px 图标承担解释「设置」的任务：放射状图形会被读成明暗模式，三条滑杆在这个尺度又过于复杂，三点菜单只表达「还有一处次级入口」，由落地页标题补全语义。图标一律内联 SVG，不引图标字体——全文件零外部请求这条约束优先于任何图标库的便利。

**返回箭头只在非根屏出现，更多入口只在 Home 出现。** 这不是布局偏好，是 PRD 设计原则一（使用时刻的交互成本）的直接落点：结论屏（`s-firstnight`/`s-plan`/`s-alt`/`s-shrink`）是当天精力最低的一刻，屏幕上只该有「接受 / 换一个 / 收一收」这几个真实选项，多一个通往设置的入口就是多一次分心。返回箭头在结论屏同样隐藏——用户到这里不该再往回翻，往回翻意味着重新做已经做完的决定。**安全页 `s-safety` 是唯一例外**：仍显示同一枚箭头，但它的无障碍标签是「返回首页」、行为也是直接回首页，绝不退回上一张饮食或运动建议；安全模式的停止决定不被导航撤销。

**负外边距是光学对齐，不是间距档。** `.navicon` 的 `margin-right:-12px`（更多入口 `-10px`）把 44px 命中区的空白部分推出容器边界，让**图标本身**而不是命中框与 20px gutter 对齐。这类光学补偿写在组件内部，不进 spacing 标度——标度管的是元素之间的真实距离。

### Settings List / Row（设置列表）

设置中心的唯一结构。外层 `settings-list` 是一张标准 Card（`rounded.xl`、1.5px 边框、`surface-container` 底），行与行之间 1px `outline-decorative` 分隔线；行高最低 **52px**，与 `icon-entry-row` 同档。行内三列：左侧标签（`body-strong` 主标题 + 可选 `body-sm` 次级说明）、右侧当前值（`body-sm`，最宽 46%，超长省略号截断）、末尾 `›`。

**外框可见档、内部分隔装饰档，是两档边框分工的标准用法。** 容器边框负责「这一整块是可点区域」，内部分隔线只负责「这是两行不是一行」，不承载信息边界——与 `icon-entry-list` / `icon-entry-row` 同一套判据，不是新判断。

**`›` 走 `glyph-mono-lg`，和 Home 那张卡的 ＋/－ 同档。** 它是指示字形而不是正文，用 mono 让它与 Accordion、Icon Entry 的指示字符长在一起；此前它是 17px 无衬线，那个字号在标度上并不存在（17px 只以 `title` 存在，且字重 600），是一处需要订正的越界值。

**当前值那一列写「现在是多少」，次级说明那一行写「这行是什么」。** 两者共用 `body-sm` 一档小字，靠位置区分职责，不靠字号或颜色再分一层。同一行同时出现两者时，说明在左、值在右，视线一次扫过就能读出「推送与停下提示 / 几点找你、要不要提醒睡 / 22:10」。

**硬规则：危险项不引入红色。** 「清空全部数据」这类不可撤销的行只把主标签降到次要文字色，靠**位置**（单独一组、列在最末）区分，不新造危险色。全局仍是琥珀一个强调色（见 Colors），加一个红就等于加第三种彩色语义。

**分组标题走 `label-mono-strong`，紧贴它下面那张卡。** 20px 上边距（首个 6px，因为屏幕标题已经提供了间隔），mono 小字，只做分区，不可点。

### Switch（开关）

只用于二值长期设置（推送开不开、要不要提醒睡）。44×26 轨道，`rounded.full`，19px 圆钮，开启时轨道转琥珀、钮转 `on-primary` 并右移 18px。

**硬规则：状态的第二载体是滑块位置，不只是颜色。** 与 Chip / Option 同一条规则——任何状态都必须同时由形状表达一次，颜色只是加速识别。这条在深夜低亮度、以及安全模式抽掉全部色相之后尤其重要：安全模式下轨道从琥珀变成中性亮灰，位置差是唯一还剩下的信号。

### Modal（确认弹窗）

**只用于不可撤销的操作，当前全局仅一处**（清空全部数据）。结构是遮罩 + 居中卡片：遮罩取 `scrim` 色、0.72 不透明度；卡片 `rounded.xl`、1.5px 可见档边框、`surface-container` 底、20px 内边距；标题 `display-stamp-compact`（25px），正文 `body`，按钮纵向堆叠、9px 间距。

**硬规则：遮罩上不放文字。** `scrim` 是「比底还底」的一档，不参与文字配色（见 Colors）——它上面永远只有弹窗本体。

### Free Text Field（自由输入字段）

`.field` 是全文件唯一的自由输入容器：`surface-container` 底，1.5px `outline-decorative` 边框，`rounded.lg`（14px）圆角，用户已输入的内容走 `body-lg`（16px / 600 / 1.4），最小高度 **52px**（`textarea` 变体 78px）。占位文字是辅助示例，统一走 `body-sm`（13.5px / 400 / 1.6）和次要色，不与用户内容或可执行操作争夺注意力。麦克风字形（`.mic`，22px 圆形描边）纯装饰，标记「以后这里能语音输入」，本轮不接实际录音。横排输入行（`.inline-row`）用 `spacing.inline`（8px）间距，让输入框和麦克风字形贴在一起而不各自占一整行。

**当前两处使用同一套字段：Home 页「树洞」入口的展开面板，以及当晚校准抽屉顶部的「补充一句」。** 两处都不强制填写、不做输入校验，键入内容只作为语气参考，不承担条件判断——真正影响当晚结论的是紧邻的三个即点芯片（加班 / 早会 / 不方便），点击立即生效收起，不需要额外的「保存」步骤。Home 的食记气泡则支持多张照片作为用户主动给出的饮食事实，提示语只说明“拍下今天吃的”会让**晚餐建议**更贴近实际，不把单张照片误写成整天记录。这是对本文长期缺口的回填：`.field`/`.mic`/`.inline-row` 早已在 Onboarding（饮食禁忌、身高体重，走 Edit Group 的 `.editgroup > p` 引导文字 + 该字段组合）、Home「树洞」和这次的校准抽屉里反复使用，但此前从未进 frontmatter，是文档缺口而不是新设计。**Edit Group 小节「规则位已预留，具体交互形态待用户决定」的表述只对麦克风代表的语音输入这一项仍然成立**——文字输入本身的视觉形态（本节）已经在用，待决定的只是要不要真的接语音。

### Calibration Sheet（共用外壳）

`calibration-sheet` 不再是单张抽屉，而是 Note Sheet 与 Adjust Sheet 共用的外壳规格：从底部进入，不创建新页面；遮罩与 Modal 共用 `scrim` 与 0.72 不透明度；抽屉本体 `surface-container` 背景、1.5px 上沿及侧边框、`rounded.xl` 顶角、20px 内边距、标题走 `display-stamp-compact`、正文走 `body`。两张抽屉共用同一个遮罩节点，同一时刻只会有一张打开。

**硬规则：外壳本身不预设内容分段——分几段、每段放什么，由 Note Sheet 和 Adjust Sheet 各自决定。**

### Note Sheet（我要补充抽屉）

全部 6 个结论屏（`s-firstnight`/`s-confirm`/`s-plan`/`s-alt`/`s-shrink`/`s-chronic`）的 footer 统一放一个「我要补充」（`button-ghost`），点开的都是这张抽屉。内容固定两段，从上到下：**补充一句**（Free Text Field + 主按钮）常驻显示，不管从哪个结论屏打开都在；用户输入后只在点击主按钮时才生效。**换个做法**是按当前屏动态给出的快捷跳转（如「换一种做法」「再轻一点」「今天不做」「还是不合适」），复用 `button-minor` 横排等权布局，不同屏给不同的选项，`s-confirm` 没有可跳的选项、这段整体隐藏。补充只写入今晚状态，不写入长期资料。

**这段的引导语与主按钮文案按屏分两种，因为提交后会发生的事本来就是两件事：**

| 打开的屏 | 引导语 | 主按钮 | 提交后 |
|---|---|---|---|
| `s-confirm`（还没出建议） | 说一句，我先记进今晚的判断里。 | **先记下** | 收起抽屉、**留在判断页**：这句话出现在 Supplement Log 里，说到的判断行同时改成它的意思（见 Supplement Log）；不重算、不跳屏 |
| 其余 5 屏（已经有建议） | 说一句，我按今晚的新情况重新安排。 | **提交并重新安排** | 从文本里抽取「加班 / 火锅 / 早会」等今晚条件并重算，随后进入更新后的计划页 |

**硬规则：文案必须和提交后真正发生的事一致。** 在判断页写「提交并重新安排」而实际只是记下，等于骗一次点击；反过来在计划页写「先记下」而实际重算了整晚安排，等于偷偷替用户做了决定。这两句文案不是语气差异，是行为声明。

### Adjust Sheet（改一下抽屉）

仅 `s-confirm` 的 3 条 Row Reason（剩余时间/当前精力/身体状况）可以触发，入口是每条依据文字右侧的「改一下」链接。抽屉的引导语是「这几项不对就改，改完回判断页看一眼。」，内容固定为**时间 / 精力 / 身体**三项结构化校准（现有 Chip，状态仍须有形态和颜色两种载体）加一个主按钮「按这个记下」。三项一起展示、一起提交，不按触发来源单独收窄——因为它们本来就是 `s-confirm` 对「今晚状况」的同一次初始判断,改一项时另外两项仍需要看得见才能判断要不要一起调。抽屉打开时三项**预填当前判断行上显示的值**（用户改过的显示改过的，没改过的显示 Agent 的估算），原样保存等于没改。

保存后收起抽屉、**留在判断页**：改过的项当场写回对应判断行（换值、摘估算标记、依据改口，见 Judgment Row），三行之外什么都不发生——不重算、不落库、不跳屏。「有明显不适」也一样只写回身体那一行，不在这里单独触发安全分支；它连同其余两项一起，等用户按下页脚主按钮时才作为今晚状况交出去。

**硬规则：结构化校准只在最初产生这三项判断的屏（`s-confirm`）可修正；其余屏（含 `s-plan`）的调整走定性的「我要补充」，不重新暴露这三项数值输入。** 摆出改不了当前屏结论的输入项，会让用户以为改了会生效，属于假交互。

### Echo（历史回看，独立行形态已弃用）

历史入口不在 Home 页：回看并不影响今晚结论，和树洞、食记的即时输入放在一起会制造相同交互方式的错觉。它放在设置首页的独立「回看」分组，入口文案为「我收到过的建议」，点击进入只读列表屏 `s-history`。不显示预览摘要、不需要按线去重或 `maxItems` 截断；无记录时入口仍可进，由列表页的空状态说明。

`echo` frontmatter 条目保留供追溯，不再有组件引用它；`element: button`、`chevronGlyph` 等字段描述的是弃用前的行形态，不代表当前渲染。

**硬规则：不显示做没做到。** 反馈（`fb`）会被存下来给次日适配用，但**永远不渲染**。一排「做到 / 没顾上」就是打卡记录，而这个产品对「昨晚没做到」的回应是把线降低，不是把它记在账上（PRD 设计原则五：一切文案写成「避免归零」）。

**硬规则：不显示连续天数。** 连续天数会归零，而整个设计的前提是**没有东西会归零**。一旦屏幕上出现「连续 3 天」，用户就获得了一个可以被打断的东西，那正是这个产品要消除的失败模式。

**规则仍然成立（2026-08-08 二度确认）：点开进入只读列表页 `s-history`。** 这条是同日更早的修订推翻旧规则（「不做成可浏览的历史页面」）后确立的，本轮只改历史入口的位置，不改它可点这件事。`s-history` 本身**完全复用已有的 `settings-list`/`settings-row` 组件渲染，未改动**：每行是一个 `disabled` 的 `settings-row`，标签放事项、值放日期，倒序、不去重。上面两条硬规则（不显示做没做到、不显示连续天数）同样没有松动，来源仍是 PRD 设计原则五。

## Do's and Don'ts

**Do** 每屏只用一个主按钮，让它是屏幕上唯一的琥珀实底块。
**Don't** 引入第三个彩色，或用绿/红表达完成与警告。

**Do** 用 `outline`（3.29）画任何可点区域的边界。
**Don't** 用 `outline-decorative`（1.57）承载信息边界——它在深夜低亮度下不可见。

**Do** 含 CJK 的行把字重封顶在 600。
**Don't** 声明 650 以上再指望汉字变粗——只有数字和 Latin 会变，同行会粗细不齐。

**Do** 靠表面明度和边框表达层次。
**Don't** 在深底上用柔和阴影表达高度——它不可见。硬阴影只留给印章一处。

**Do** 让状态同时由颜色和形状表达（字形前缀、方块、圆圈、`已选` 标签、开关滑块位置）。
**Don't** 让任何状态只由颜色区分。

**Do** 在不可撤销的确认里，把主按钮给「不执行」那一侧，焦点也落在它上面。
**Don't** 为破坏性操作新造一个危险色，或让最亮最大的目标是那个删不回来的动作。

**Do** 把「我给过你什么」放在设置的独立「回看」分组，进一个只读列表（`s-history`）。
**Don't** 显示做没做到、连续天数——那会把「今晚这一件」变成一份成绩单。

**Do** 保持对比度在 7 / 6.5 / 3 三条线以上，新组合先复算。
**Don't** 按 WCAG AA 的 4.5 收——使用条件是深夜加低亮度屏幕，AA 不够。

**Do** 保持安全模式为整套覆写：颜色、人像、说话那一句同时退场。
**Don't** 把它做成主题开关或让用户手动切换。

**Do** 只用系统字体，保证断网时版面不变。
**Don't** 加载 webfont 或图标字体。

**Do** 把动效全部包在 `prefers-reduced-motion: no-preference` 里，另在 `reduce` 下加 `!important` 兜底。
**Don't** 让任何信息只由动效传达——关掉动效后所有内容仍要成立。

**Do** 让活力留在界面里（排版对比、色块、印章）。
**Don't** 用感叹号、连续动画或鼓励式文案向用户索取活力。

### Motion

交互曲线使用 `cubic-bezier(.22, 1, .36, 1)`；页面切换沿用方案 B 的
`cubic-bezier(.22, .61, .36, 1)`。

- **切屏**：整页先以 `.42s` 淡入、`.52s` 从下方 10px 归位，并以 `visibility` 管理不可见页；不以 `display:none` 切断过渡。当前页的直接区块再以 `.62s` 从下方 12px 淡入，依次延迟 `.02s`、`.09s`、`.16s`……进入。
- **印章**：`.34s`，从 `rotate(4deg) scale(.9)` 落到 `rotate(-1.2deg) scale(1)`。这是全流程唯一有弹性的动效。
- **按下**：缩放 `.975`。
- **当晚校准抽屉**：遮罩 `.20s` 淡入；抽屉以 `.26s` 自底部归位，使用同一交互曲线。关闭反向执行。
- **安全模式不用弹性。** 那个时刻界面在退场，弹性动效读作轻快，与之矛盾。

`prefers-reduced-motion` 双向声明：所有位移、缩放、旋转和 transition 都写在 `no-preference` 里，`reduce` 下再加一层 `animation:none !important; transition:none !important` 兜底。关掉动效后，缩小分支和学习结果仍靠文字与形态表达。

### Focus

`3px solid` 薄荷色描边，`2px` 偏移，`6px` 圆角。切屏时焦点落到屏幕容器上以接住键盘位置，但容器本身不画描边（`.screen:focus{outline:none}`）——那是一个不可见的锚点，画出来会让用户以为整屏被选中了。
