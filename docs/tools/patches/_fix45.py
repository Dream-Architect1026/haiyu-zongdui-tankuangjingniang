# -*- coding: utf-8 -*-
# fix45: 0.4.5 -> 0.4.6
#   A) 标签取消全部位移，只留发光；标签行独占层叠层（不再越界压到上方元素）
#   B) 页面/标签切换渐隐渐入；题目卡·日志·配置卡·教程卡入场动效；空闲鲸娘轻浮动
#   C) 最小化：几何尺寸与常态完全一致（52px），只叠一层柔光 + 高度平滑过渡，消除生硬跳变
#   D) 最小化态标题栏左前加状态灯：绿=运行中 / 黄=答题中 / 红=终止
# 用法: python _fix45.py [--dry]
import re
import sys

SRC = r"C:\Users\D_A\DoubaoWork\chats\2026-10-05\new-chat-4\海底小纵队·探矿鲸娘.user.js"
BAK = r"C:\Users\D_A\WorkBuddy\2026-10-05-13-53-42\_bak_045.user.js"
LOG = r"C:\Users\D_A\WorkBuddy\2026-10-05-13-53-42\_f45out.txt"
DRY = "--dry" in sys.argv

OLD_VER = "0.4.5"
NEW_VER = "0.4.6"
log = []


def w(s):
    log.append(s)


# ────────────────────────── 纯 CSS（行内禁止双引号） ──────────────────────────
CSS_TEXT = """
/* ==== v0.4.6 : 标签只发光不上浮 + 全局渐隐渐入 + 最小化不跳变 + 状态灯 ==== */

/* --- A. 标签取消全部位移，只留发光；光晕向下偏置，避开卡片上边缘裁切 --- */
.main-page .demo-tabs .el-tabs__item:hover,
.main-page .demo-tabs .el-tabs__item.is-active,
.main-page .demo-tabs .el-tabs__item:active{transform:none!important}
.main-page .demo-tabs .el-tabs__item{will-change:box-shadow,background-color,border-color}
.main-page .demo-tabs .el-tabs__item:hover{border-color:rgba(56,226,255,.40)!important;box-shadow:0 3px 14px rgba(56,226,255,.32),inset 0 1px 0 rgba(255,255,255,.26)!important}

/* --- B. 标签行独占层叠层：发光不被遮住，也永不越界压到上方元素 --- */
.main-page .demo-tabs>.el-tabs__header{position:relative;z-index:2;isolation:isolate}
.main-page .demo-tabs .el-tabs__nav-wrap,
.main-page .demo-tabs .el-tabs__nav-scroll,
.main-page .demo-tabs .el-tabs__nav{position:relative;z-index:1}

/* --- C. 页面（标签页）切换：渐隐渐入 --- */
.main-page .demo-tabs .el-tabs__content{position:relative}
.main-page .demo-tabs .el-tab-pane{animation:hxPaneIn .34s cubic-bezier(.22,1,.36,1) backwards}
@keyframes hxPaneIn{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:translateY(0)}}

/* --- D. 内容入场动效：题目卡逐条浮现 / 日志滑入 / 配置与教程卡浮现 --- */
.main-page .question-card{animation:hxCardIn .34s cubic-bezier(.22,1,.36,1) backwards}
.main-page .question-card:nth-child(2){animation-delay:.05s}
.main-page .question-card:nth-child(3){animation-delay:.1s}
.main-page .question-card:nth-child(4){animation-delay:.15s}
.main-page .question-card:nth-child(n+5){animation-delay:.2s}
.main-page .el-timeline-item{animation:hxLogIn .3s ease backwards}
.main-page .setting>div,.main-page .guide-card{animation:hxCardIn .32s cubic-bezier(.22,1,.36,1) backwards}
@keyframes hxCardIn{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:none}}
@keyframes hxLogIn{from{opacity:0;transform:translateX(-6px)}to{opacity:1;transform:none}}

/* --- E. 空闲态鲸娘轻浮动，给静止画面一点呼吸感 --- */
.main-page .whale-hero.is-idle .whale-hero__avatar{animation:hxIdleFloat 4.6s ease-in-out infinite}
@keyframes hxIdleFloat{0%,100%{transform:translateY(0)}50%{transform:translateY(-5px)}}

/* --- F. 最小化：几何尺寸与常态完全一致，只叠一层柔光（去掉脉冲，避免生硬） --- */
.main-page .el-card:has(.card_content[style*='display: none']) .el-card__header{padding:9px 9px 3px!important;background:linear-gradient(180deg,rgba(56,226,255,.07),rgba(155,107,255,.03) 58%,transparent)!important;border-bottom:none!important}
.main-page .el-card:has(.card_content[style*='display: none']) .card-header{padding:8px 11px!important;border:1px solid rgba(56,226,255,.30)!important;background:linear-gradient(120deg,rgba(56,226,255,.20),rgba(74,140,255,.10) 48%,rgba(155,107,255,.20))!important;box-shadow:0 8px 22px rgba(2,8,24,.34),0 0 14px rgba(56,226,255,.20),inset 0 1px 0 rgba(255,255,255,.22);animation:none!important}
.main-page .el-card:has(.card_content[style*='display: none']) .card-header .title{flex:0 1 auto;justify-content:flex-start}
.main-page .el-card:has(.card_content[style*='display: none']) .card-header .title span{font-size:14px;letter-spacing:.4px}
.main-page .el-card:has(.card_content[style*='display: none']) .card-header__logo{width:24px;height:24px}
.main-page .minus{display:none!important}

/* --- G. 最小化状态灯：绿=运行中 / 黄=答题中 / 红=终止（发光浮动） --- */
.main-page .hx-status-dot{display:none;flex:0 0 auto;width:7px;height:7px;border-radius:50%;position:relative;background:currentColor;color:#4ade80}
.main-page .el-card:has(.card_content[style*='display: none']) .hx-status-dot{display:block;animation:hxDotPulse 1.8s ease-in-out infinite}
.main-page .hx-status-dot[data-hx-status='run']{color:#4ade80;box-shadow:0 0 9px 1px rgba(74,222,128,.85)}
.main-page .hx-status-dot[data-hx-status='busy']{color:#ffc857;box-shadow:0 0 9px 1px rgba(255,200,87,.90)}
.main-page .hx-status-dot[data-hx-status='stop']{color:#ff6b6b;box-shadow:0 0 9px 1px rgba(255,107,107,.90)}
.main-page .hx-status-dot::after{content:'';position:absolute;inset:-3px;border-radius:50%;background:currentColor;opacity:0;animation:hxDotHalo 1.8s ease-out infinite}
@keyframes hxDotPulse{0%,100%{transform:scale(1);opacity:1}50%{transform:scale(1.22);opacity:.78}}
@keyframes hxDotHalo{0%{transform:scale(.6);opacity:.34}70%{transform:scale(1.7);opacity:0}100%{transform:scale(1.7);opacity:0}}

/* --- H. 偏好无动效时全部关闭 --- */
@media (prefers-reduced-motion:reduce){.main-page .demo-tabs .el-tab-pane,.main-page .question-card,.main-page .el-timeline-item,.main-page .setting>div,.main-page .guide-card,.main-page .whale-hero.is-idle .whale-hero__avatar,.main-page .hx-status-dot,.main-page .hx-status-dot::after{animation:none!important}}
"""

# ───────────── 需要 JS 常量插值的 CSS（最小化高度平滑过渡） ─────────────
JS_CSS_EXTRA = """    + "\\n/* --- I. 最小化高度平滑过渡（用实测标题栏高度，尺寸与常态严丝合缝） --- */"
    + "\\n.main-page .el-card{transition:height .32s cubic-bezier(.22,1,.36,1)}"
    + "\\n.main-page .el-card:has(.card_content[style*='display: none']){height:var(--hx-min-h,52px);overflow:hidden}"
    + "\\n.main-page .el-card:has(.card_content[style*='display:none']){height:var(--hx-min-h,52px);overflow:hidden}"
"""

JS_CONST = ""

JS_TIMER = "\n  let hxStatusTimer = null;"

JS_BLOCK = """
  /* ── 最小化状态灯：绿=运行中 / 黄=答题中 / 红=终止 ───────────── */
  const HX_STATUS_TEXT = { run: "运行中", busy: "答题中", stop: "已终止" };
  /* 判定优先级：正在答题(黄) > 最近出现失败/已到末尾(红) > 其余(绿) */
  const readPanelStatus = () => {
    let busy = false;
    try {
      const questionStore = useQuestionStore();
      const list = questionStore && questionStore.questionList;
      busy = Array.isArray(list) && list.length > 0;
    } catch (error) { /* 忽略 */ }
    if (busy)
      return "busy";
    let dead = false;
    try {
      const logStore2 = useLogStore();
      const logs = logStore2 && Array.isArray(logStore2.logList) ? logStore2.logList : [];
      dead = logs.slice(-6).some((item) => item && (item.type === "danger" || item.type === "error"));
      const last = logs[logs.length - 1];
      if (last && last.type === "success" && /完成|最后一章|最后一题|已到最后一/.test(String(last.message || "")))
        dead = true;
    } catch (error) { /* 忽略 */ }
    return dead ? "stop" : "run";
  };
  let hxStatusDot = null;
  const syncStatusDot = () => {
    const root = hxShadow;
    if (!root)
      return false;
    const title = root.querySelector(".card-header .title");
    if (!title)
      return false;
    if (!hxStatusDot || !hxStatusDot.isConnected || hxStatusDot.parentNode !== title) {
      hxStatusDot = title.querySelector(".hx-status-dot");
      if (!hxStatusDot) {
        hxStatusDot = document.createElement("i");
        hxStatusDot.className = "hx-status-dot";
      }
      title.insertBefore(hxStatusDot, title.firstChild);
    }
    try {
      const headEl = root.querySelector(".el-card__header");
      if (headEl) {
        const measuredH = Math.round(headEl.getBoundingClientRect().height);
        if (measuredH > 30)
          root.host.style.setProperty("--hx-min-h", measuredH + 3 + "px");
      }
    } catch (error) { /* 忽略 */ }
    const state = readPanelStatus();
    if (hxStatusDot.getAttribute("data-hx-status") !== state) {
      hxStatusDot.setAttribute("data-hx-status", state);
      hxStatusDot.setAttribute("title", HX_STATUS_TEXT[state] || state);
    }
    return true;
  };
  const bindStatusDot = () => {
    try { syncStatusDot(); } catch (error) { /* 忽略 */ }
    if (hxStatusTimer === null)
      hxStatusTimer = setInterval(() => {
        try { syncStatusDot(); } catch (error) { /* 忽略 */ }
      }, 800);
    return true;
  };
"""


def fail(msg):
    w("FAIL: " + msg)
    open(LOG, "w", encoding="utf-8").write("\n".join(log))
    raise SystemExit(1)


raw = open(SRC, "rb").read().decode("utf-8")
w("orig_bytes=" + str(len(raw.encode("utf-8"))))
w("orig_crlf=" + str(raw.count("\r\n")))
w("orig_bareLF=" + str(len(re.findall(r"(?<!\r)\n", raw))))

s = raw.replace("\r\n", "\n")
if s.count("\n") != raw.count("\r\n"):
    fail("CRLF 归一化异常: LF=" + str(s.count("\n")) + " CRLF=" + str(raw.count("\r\n")))
w("normalized_LF=" + str(s.count("\n")))
w("")

# ---- 锚点校验 ----
A_JOIN = 'const layoutCss = LAYOUT_CSS_PARTS.join("");'
A_TIMER = "  let balanceTimer = null;"
A_ADOPTS = "  const CAN_USE_ADOPTED_SHEETS = (() => {"
A_DIAG = "      w.__HX_BALANCE__ = () => fetchBalance();"
A_MOUNT = "      try { bindLiquidGlass(); } catch (error2) { /* \u5ffd\u7565 */ }"
for nm, a in [("join", A_JOIN), ("balanceTimer", A_TIMER), ("adoptedSheets", A_ADOPTS), ("diagBalance", A_DIAG), ("mountHook", A_MOUNT)]:
    c = s.count(a)
    w("anchor " + nm + " count=" + str(c))
    if c != 1:
        fail("锚点数量异常: " + nm)

REQUIRED = [
    'const HX_BUILD = "0.4.5";',
    "const useQuestionStore = pinia.defineStore(\"questionStore\", {",
    "const useLogStore = pinia.defineStore(\"logStore\", {",
    'const _hoisted_3 = { class: "minus" };',
    "class: \"card_content\"",
    "const PANEL_HEIGHT =",
    # 4 条待覆盖的旧位移规则
    "background:rgba(255,255,255,.07)!important;transform:translateY(-1px);",
    "border-color:rgba(56,226,255,.32)!important;transform:translateY(-1px);",
    "rgba(8,18,38,.30))!important;transform:translateY(-2px);",
    "rgba(155,107,255,.22))!important;transform:translateY(-2px);",
]
for r in REQUIRED:
    c = s.count(r)
    w("needle[" + str(c) + "] " + r[:74])
    if c != 1:
        fail("锚点缺失或重复: " + r[:74])

old_shift = len(re.findall(r"\.main-page \.demo-tabs \.el-tabs__item[^{]*\{[^}]*translateY", s))
w("")
w("旧 translateY 标签规则数 = " + str(old_shift))
if old_shift < 4:
    fail("旧位移规则少于预期（4）")

# ---- 版本号审计 ----
w("")
w("---- " + OLD_VER + " occurrences: " + str(s.count(OLD_VER)) + " ----")
for m in re.finditer(re.escape(OLD_VER), s):
    w("  ..." + s[max(0, m.start() - 55): m.end() + 55].replace("\n", "\\n") + "...")
ALLOW = re.compile(r"(HX_BUILD|@version|v" + re.escape(OLD_VER) + r"|\u9762\u677f|MIT License|liquid glass|Liquid Glass)")
bad = [m for m in re.finditer(re.escape(OLD_VER), s) if not ALLOW.search(s[max(0, m.start() - 60): m.end() + 60])]
if bad:
    w("!! 可疑的 " + OLD_VER + " 出现位置: " + str(len(bad)))
    for m in bad:
        w("   @" + str(m.start()) + " ..." + s[max(0, m.start() - 70): m.end() + 40].replace("\n", "\\n"))
    if not DRY:
        fail("存在可疑版本号位置，已中止")
else:
    w("全部 " + OLD_VER + " 均为版本字面量，可安全全局替换")

# ---- 生成 CSS 插入块 ----
lines = [ln.strip() for ln in CSS_TEXT.strip().split("\n")]
lines = [ln for ln in lines if ln]
if not lines:
    fail("CSS_TEXT 为空")
w("")
w("new_css_lines=" + str(len(lines)))
if any('"' in ln for ln in lines):
    fail("CSS 行内含双引号，会破坏 JS 字符串")
for ln in JS_CSS_EXTRA.split("\n"):
    if ln.strip() and ln.count('"') % 2 == 1:
        fail("JS_CSS_EXTRA 行内双引号数量为奇数（会截断字符串）: " + ln[:80])
    if '[style*="' in ln:
        fail("JS_CSS_EXTRA 使用了双引号属性选择器（会破坏 JS 字符串）")

css_js = ("  // ---- v" + NEW_VER + " ----\n"
          "  LAYOUT_CSS_PARTS.push(\n"
          '    "' + '"\n    + "'.join("\\n" + ln for ln in lines) + '"\n'
          + JS_CSS_EXTRA
          + "  );\n\n")

# JS_BLOCK 的每行双引号必须成对（否则会截断后续代码）
for ln in JS_BLOCK.strip("\n").split("\n"):
    if ln.count('"') % 2 == 1:
        fail("JS 行内双引号数量为奇数（可能截断字符串）: " + ln[:70])

if not DRY:
    s = s.replace(A_JOIN, css_js + A_JOIN, 1)
    s = s.replace(A_TIMER, A_TIMER + JS_CONST + JS_TIMER, 1)
    s = s.replace(A_ADOPTS, JS_BLOCK + "\n" + A_ADOPTS, 1)
    s = s.replace(A_DIAG, A_DIAG + "\n      w.__HX_STATUS__ = () => readPanelStatus();", 1)
    s = s.replace(A_MOUNT, A_MOUNT + "\n      try { bindStatusDot(); } catch (error2) { /* \u5ffd\u7565 */ }", 1)
    s = s.replace(OLD_VER, NEW_VER)

    exp_use_q = raw.count("const questionStore = useQuestionStore();") + 1
    exp_ver = raw.count(OLD_VER) + 2  # 全局替换 + CSS 注释(v0.4.6) + css_js 分节注释
    exp_dot_cls = CSS_TEXT.count("hx-status-dot") + JS_BLOCK.count("hx-status-dot")
    exp_dot_keys = CSS_TEXT.count("[data-hx-status='")
    exp_kf = CSS_TEXT.count("@keyframes hxDot")
    w("")
    w("computed: useQuestionStore=" + str(exp_use_q) + " ver=" + str(exp_ver)
      + " dotClass=" + str(exp_dot_cls) + " dotKeys=" + str(exp_dot_keys)
      + " keyframes=" + str(exp_kf))

    checks = [
        ("HX_BUILD " + NEW_VER, s.count('const HX_BUILD = "' + NEW_VER + '";'), 1),
        (OLD_VER + " 残留", s.count(OLD_VER), 0),
        (NEW_VER + " 出现", s.count(NEW_VER), exp_ver),
        ("push 次数", s.count("LAYOUT_CSS_PARTS.push("), 6),
        ("hxStatusTimer 声明", s.count("let hxStatusTimer = null;"), 1),
        ("HX_MINIMIZED_HEIGHT 已移除", s.count("HX_MINIMIZED_HEIGHT"), 0),
        ("最小化高度用实测变量", s.count("height:var(--hx-min-h,52px)"), 2),
        ("实测写入 --hx-min-h", s.count('setProperty("--hx-min-h"'), 1),
        ("readPanelStatus 定义", s.count("const readPanelStatus = () => {"), 1),
        ("readPanelStatus 引用", s.count("readPanelStatus"), 3),
        ("syncStatusDot 定义", s.count("const syncStatusDot = () => {"), 1),
        ("syncStatusDot 引用", s.count("syncStatusDot"), 3),
        ("bindStatusDot 定义", s.count("const bindStatusDot = () => {"), 1),
        ("bindStatusDot 调用", s.count("bindStatusDot();"), 1),
        ("__HX_STATUS__ 探针", s.count("w.__HX_STATUS__ = "), 1),
        ("useQuestionStore 调用", s.count("const questionStore = useQuestionStore();"), exp_use_q),
        ("状态灯类名", s.count("hx-status-dot"), exp_dot_cls),
        ("取消位移规则", s.count(".main-page .demo-tabs .el-tabs__item:active{transform:none!important}"), 1),
        ("标签行叠层", s.count(".main-page .demo-tabs>.el-tabs__header{position:relative;z-index:2;isolation:isolate}"), 1),
        ("最小化只留标题栏", s.count(".main-page .minus{display:none!important}"), 1),
        ("最小化取消脉冲", s.count(";animation:none!important}"), 1),
        ("最小化高度过渡", s.count(".main-page .el-card{transition:height .32s cubic-bezier(.22,1,.36,1)}"), 1),
        ("页面切换动效", s.count("@keyframes hxPaneIn{"), 1),
        ("卡片入场动效", s.count("@keyframes hxCardIn{"), 1),
        ("日志入场动效", s.count("@keyframes hxLogIn{"), 1),
        ("空闲浮动动效", s.count("@keyframes hxIdleFloat{"), 1),
        ("一次性动效用 backwards", s.count("cubic-bezier(.22,1,.36,1) backwards"), 3),
        ("状态灯 3 色", s.count(".hx-status-dot[data-hx-status='"), exp_dot_keys),
        ("灯关键帧", s.count("@keyframes hxDotPulse{") + s.count("@keyframes hxDotHalo{"), exp_kf),
        ("旧位移仍在(被覆盖)", len(re.findall(r"\.main-page \.demo-tabs \.el-tabs__item[^{]*\{[^}]*translateY", s)), old_shift),
        ("未用 important 压掉呼吸动画", s.count(".is-active{box-shadow:0 0 20px"), 0),
        ("join 保留", s.count("const layoutCss = LAYOUT_CSS_PARTS.join"), 1),
    ]
    ok = True
    for name, got, exp in checks:
        mark = "OK" if got == exp else "BAD"
        if got != exp:
            ok = False
        w("  [" + mark + "] " + name + " = " + str(got) + " (expect " + str(exp) + ")")
    if not ok:
        fail("结构断言未通过")

    out = s.replace("\r\n", "\n").replace("\n", "\r\n")
    if re.search(r"(?<!\r)\n", out):
        fail("输出存在裸 LF")
    open(BAK, "wb").write(raw.encode("utf-8"))
    open(SRC, "wb").write(out.encode("utf-8"))
    w("")
    w("--- written ---")
    w("backup=" + BAK)
    w("backup_bytes=" + str(len(raw.encode("utf-8"))))
    w("new_bytes=" + str(len(out.encode("utf-8"))))
    w("new_crlf=" + str(out.count("\r\n")))
    w("new_bareLF=" + str(len(re.findall(r"(?<!\r)\n", out))))
    w("new_lines=" + str(out.count("\r\n") + 1))
else:
    w("")
    w("DRY RUN - 未写入")

w("")
w("RESULT=" + ("DRY" if DRY else "PASS"))
open(LOG, "w", encoding="utf-8").write("\n".join(log))
print("EXIT_OK" if not DRY else "DRY_OK")
