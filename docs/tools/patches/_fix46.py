# -*- coding: utf-8 -*-
# fix46: 0.4.6 -> 0.4.7
#   A) 背景板：由上而下的低频脉动光带（background-position 扫掠，永不越界）
#   B) 鲸娘图：浮动 + 双色随相光晕（whale-hero 双伪元素光团 + 头像 filter 光晕）
#   C) 「小鲸娘正在吃白饭」多条随机播放、随机间隔刷新
#   D) 文案改名：仅作答 -> 仅仅作答 ；弹题自动作答 -> 弹题作答（含旧名迁移，避免丢配置）
# 用法: python _fix46.py [--dry]
import re
import sys

SRC = r"C:\Users\D_A\DoubaoWork\chats\2026-10-05\new-chat-4\海底小纵队·探矿鲸娘.user.js"
BAK = r"C:\Users\D_A\WorkBuddy\2026-10-05-13-53-42\_bak_046.user.js"
LOG = r"C:\Users\D_A\WorkBuddy\2026-10-05-13-53-42\_f46out.txt"
DRY = "--dry" in sys.argv

OLD_VER = "0.4.6"
NEW_VER = "0.4.7"
log = []


def w(s):
    log.append(s)


# ────────────────────────── 纯 CSS（行内禁止双引号） ──────────────────────────
CSS_TEXT = """
/* ==== v0.4.7 : 背景脉动光 + 鲸娘浮动与光晕 + 空闲文案随机 ==== */

/* --- A. 背景板：自上而下的低频脉动光带（置于全部内容之下，不吃点击、不越界） --- */
.main-page{isolation:isolate}
.main-page::before{content:'';position:absolute;inset:0;z-index:-1;pointer-events:none;background-image:linear-gradient(180deg,rgba(56,226,255,0) 0%,rgba(56,226,255,.22) 15%,rgba(155,107,255,.20) 26%,rgba(56,226,255,0) 40%);background-size:100% 240%;background-repeat:no-repeat;background-position:50% 50%;animation:hxBgSweep 9.6s cubic-bezier(.45,0,.55,1) infinite}
@keyframes hxBgSweep{0%{background-position:50% 50%;opacity:0}12%{opacity:.85}45%{opacity:.95}100%{background-position:50% -50%;opacity:0}}
.main-page::after{content:'';position:absolute;inset:0;z-index:-1;pointer-events:none;background:radial-gradient(130% 62% at 50% -8%,rgba(56,226,255,.17),rgba(56,226,255,0) 62%);opacity:.4;animation:hxBgBreathe 13s ease-in-out infinite}
@keyframes hxBgBreathe{0%,100%{opacity:.30}50%{opacity:.72}}

/* --- B. 鲸娘区：双色随相光团（一青一紫，错相呼吸），只在鲸娘周围变化 --- */
.main-page .whale-hero{isolation:isolate}
.main-page .whale-hero::before{content:'';position:absolute;left:50%;top:50%;width:212px;height:212px;margin:-106px 0 0 -106px;border-radius:50%;z-index:-1;pointer-events:none;background:radial-gradient(circle,rgba(56,226,255,.30),rgba(56,226,255,.10) 44%,rgba(56,226,255,0) 72%);animation:hxHeroGlowA 7.6s ease-in-out infinite}
.main-page .whale-hero::after{content:'';position:absolute;left:50%;top:50%;width:252px;height:252px;margin:-126px 0 0 -126px;border-radius:50%;z-index:-1;pointer-events:none;background:radial-gradient(circle,rgba(155,107,255,.34),rgba(155,107,255,.12) 46%,rgba(155,107,255,0) 74%);opacity:0;animation:hxHeroGlowB 9.4s ease-in-out infinite}
@keyframes hxHeroGlowA{0%,100%{opacity:.30;transform:scale(.90)}50%{opacity:.95;transform:scale(1.06)}}
@keyframes hxHeroGlowB{0%,100%{opacity:0;transform:scale(.84)}48%{opacity:.88;transform:scale(1.04)}}

/* --- C. 鲸娘图：浮动 + 随相变色光晕（filter 光晕不受 box-shadow !important 影响） --- */
.main-page .whale-hero__avatar{will-change:transform,filter}
.main-page .whale-hero.is-idle .whale-hero__avatar{animation:hxIdleFloat 5.2s ease-in-out infinite,hxWhaleAura 4.4s ease-in-out infinite}
.main-page .whale-hero.is-busy .whale-hero__avatar{animation:hxWhaleBreath 2.4s ease-in-out infinite,hxWhaleAura 4.4s ease-in-out infinite}
@keyframes hxWhaleAura{0%,100%{filter:drop-shadow(0 3px 9px rgba(56,226,255,.45))}50%{filter:drop-shadow(0 7px 18px rgba(155,107,255,.70))}}

/* --- D. 空闲文案轮换时的入场（渐显 + 轻抬） --- */
.main-page .whale-hero__text.hx-line-in{animation:hxLineIn .52s cubic-bezier(.22,1,.36,1)}
@keyframes hxLineIn{from{opacity:0;transform:translateY(6px)}to{opacity:1;transform:none}}

/* --- E. 偏好无动效时全部关闭 --- */
@media (prefers-reduced-motion:reduce){.main-page::before,.main-page::after,.main-page .whale-hero::before,.main-page .whale-hero::after,.main-page .whale-hero__avatar,.main-page .whale-hero__text{animation:none!important}}
"""

JS_BLOCK = """
  /* ── 空闲态文案：多条随机播放 + 随机间隔刷新 ──────────────── */
  const HX_IDLE_LINES = ["小鲸娘正在吃白饭", "小鲸娘在等主人投喂", "小鲸娘在啃数据海草", "小鲸娘在数小金库", "小鲸娘在磨鲸须", "小鲸娘偷偷打了个哈欠"];
  let hxIdleLineIdx = Math.floor(Math.random() * HX_IDLE_LINES.length);
  let hxIdleLine = HX_IDLE_LINES[hxIdleLineIdx];
  let hxLineTimer = null;
  const paintIdleLine = (animate) => {
    const root = hxShadow;
    if (!root)
      return false;
    const hero = root.querySelector(".whale-hero");
    const text = root.querySelector(".whale-hero__text");
    if (!hero || !text)
      return false;
    if (!hero.classList.contains("is-idle"))
      return false;
    if (!animate && text.textContent === hxIdleLine)
      return true;
    text.textContent = hxIdleLine;
    if (animate) {
      text.classList.remove("hx-line-in");
      void text.offsetWidth;
      text.classList.add("hx-line-in");
    }
    return true;
  };
  const rollIdleLine = () => {
    if (HX_IDLE_LINES.length > 1) {
      let next = hxIdleLineIdx;
      while (next === hxIdleLineIdx)
        next = Math.floor(Math.random() * HX_IDLE_LINES.length);
      hxIdleLineIdx = next;
    }
    hxIdleLine = HX_IDLE_LINES[hxIdleLineIdx];
    try { paintIdleLine(true); } catch (error) { /* 忽略 */ }
    return true;
  };
  const scheduleIdleRoll = () => {
    hxLineTimer = setTimeout(() => {
      rollIdleLine();
      scheduleIdleRoll();
    }, 4200 + Math.floor(Math.random() * 3600));
  };
  const bindIdleLines = () => {
    try { paintIdleLine(false); } catch (error) { /* 忽略 */ }
    if (hxLineTimer === null)
      scheduleIdleRoll();
    return true;
  };
"""

TICK_PATCH = "\n        try { paintIdleLine(false); } catch (error) { /* \u5ffd\u7565 */ }"
MOUNT_PATCH = "\n      try { bindIdleLines(); } catch (error2) { /* \u5ffd\u7565 */ }"
DIAG_PATCH = "\n      w.__HX_LINE__ = () => hxIdleLine;"

# 文案改名（先全局替换旧名，再补迁移条目，顺序不可颠倒）
RENAMES = [
    ('"\u4ec5\u4f5c\u7b54"', '"\u4ec5\u4ec5\u4f5c\u7b54"'),          # "仅作答"      -> "仅仅作答"
    ('"\u5f39\u9898\u81ea\u52a8\u4f5c\u7b54"', '"\u5f39\u9898\u4f5c\u7b54"'),  # "弹题自动作答" -> "弹题作答"
]
MIGRATION_ANCHOR = "  const CONFIG_NAME_MIGRATIONS = {"
MIGRATION_ADD = ('\n    "\u4ec5\u4f5c\u7b54": "\u4ec5\u4ec5\u4f5c\u7b54",'
                 '\n    "\u5f39\u9898\u81ea\u52a8\u4f5c\u7b54": "\u5f39\u9898\u4f5c\u7b54",')

A_JOIN = 'const layoutCss = LAYOUT_CSS_PARTS.join("");'
A_ADOPTS = "  const CAN_USE_ADOPTED_SHEETS = (() => {"
A_TICK = "        try { syncStatusDot(); } catch (error) { /* \u5ffd\u7565 */ }"
A_MOUNT = "      try { bindStatusDot(); } catch (error2) { /* \u5ffd\u7565 */ }"
A_DIAG = "      w.__HX_STATUS__ = () => readPanelStatus();"


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

for nm, a in [("join", A_JOIN), ("adoptedSheets", A_ADOPTS), ("tick", A_TICK),
              ("mount", A_MOUNT), ("diag", A_DIAG), ("migration", MIGRATION_ANCHOR)]:
    c = s.count(a)
    w("anchor " + nm + " count=" + str(c))
    if c != 1:
        fail("锚点数量异常: " + nm)

for old, new in RENAMES:
    c = s.count(old)
    w("rename " + old + " -> " + new + " 命中 " + str(c))
    if c < 1:
        fail("改名锚点缺失: " + old)

# ---- 版本号审计 ----
w("")
w("---- " + OLD_VER + " occurrences: " + str(s.count(OLD_VER)) + " ----")
ALLOW = re.compile(r"(HX_BUILD|@version|v" + re.escape(OLD_VER) + r"|\u9762\u677f|MIT License|liquid glass|Liquid Glass|\u4e0a\u4e00\u8f6e)")
bad = [m for m in re.finditer(re.escape(OLD_VER), s) if not ALLOW.search(s[max(0, m.start() - 60): m.end() + 60])]
if bad:
    w("!! 可疑的 " + OLD_VER + " 位置: " + str(len(bad)))
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
if any("[style*=" in ln for ln in lines):
    fail("CSS 行内含 [style*= 选择器")

for ln in JS_BLOCK.strip("\n").split("\n"):
    if ln.count('"') % 2 == 1:
        fail("JS 行内双引号数量为奇数（可能截断字符串）: " + ln[:70])
for nm, blk in [("TICK_PATCH", TICK_PATCH), ("MOUNT_PATCH", MOUNT_PATCH), ("DIAG_PATCH", DIAG_PATCH), ("MIGRATION_ADD", MIGRATION_ADD)]:
    for ln in blk.split("\n"):
        if ln.count('"') % 2 == 1:
            fail(nm + " 行内双引号数量为奇数: " + ln[:70])

css_js = ("  // ---- v" + NEW_VER + " ----\n"
          "  LAYOUT_CSS_PARTS.push(\n"
          '    "' + '"\n    + "'.join("\\n" + ln for ln in lines) + '"\n'
          + "  );\n\n")

if not DRY:
    s = s.replace(A_JOIN, css_js + A_JOIN, 1)
    s = s.replace(A_ADOPTS, JS_BLOCK + "\n" + A_ADOPTS, 1)
    s = s.replace(A_TICK, A_TICK + TICK_PATCH, 1)
    s = s.replace(A_MOUNT, A_MOUNT + MOUNT_PATCH, 1)
    s = s.replace(A_DIAG, A_DIAG + DIAG_PATCH, 1)
    # 先改文案名（全局），再补迁移条目（含旧名键），顺序不可颠倒
    for old, new in RENAMES:
        s = s.replace(old, new)
    s = s.replace(MIGRATION_ANCHOR, MIGRATION_ANCHOR + MIGRATION_ADD, 1)
    # 版本号最后替换
    s = s.replace(OLD_VER, NEW_VER)

    exp_ver = raw.count(OLD_VER) + 2
    exp_paint = JS_BLOCK.count("paintIdleLine") + TICK_PATCH.count("paintIdleLine")
    exp_roll = JS_BLOCK.count("rollIdleLine")
    exp_sched = JS_BLOCK.count("scheduleIdleRoll")
    exp_bind = JS_BLOCK.count("bindIdleLines") + MOUNT_PATCH.count("bindIdleLines")
    exp_css_lines = len(lines)
    w("")
    w("computed: ver=" + str(exp_ver) + " paint=" + str(exp_paint) + " roll=" + str(exp_roll)
      + " sched=" + str(exp_sched) + " bind=" + str(exp_bind))

    checks = [
        ("HX_BUILD " + NEW_VER, s.count('const HX_BUILD = "' + NEW_VER + '";'), 1),
        (OLD_VER + " 残留", s.count(OLD_VER), 0),
        (NEW_VER + " 出现", s.count(NEW_VER), exp_ver),
        ("push 次数", s.count("LAYOUT_CSS_PARTS.push("), 7),
        ("join 保留", s.count("const layoutCss = LAYOUT_CSS_PARTS.join"), 1),
        # CSS：背景脉动光
        (".main-page::before 扫掠光", s.count(".main-page::before{content:'';position:absolute;inset:0;z-index:-1"), 1),
        ("@keyframes hxBgSweep", s.count("@keyframes hxBgSweep{"), 1),
        ("@keyframes hxBgBreathe", s.count("@keyframes hxBgBreathe{"), 1),
        ("扫掠用 background-position", s.count("background-size:100% 240%"), 1),
        # CSS：鲸娘光团与浮动
        ("hero 青色光团", s.count(".main-page .whale-hero::before{content:''"), 1),
        ("hero 紫色光团", s.count(".main-page .whale-hero::after{content:''"), 1),
        ("@keyframes hxHeroGlowA", s.count("@keyframes hxHeroGlowA{"), 1),
        ("@keyframes hxHeroGlowB", s.count("@keyframes hxHeroGlowB{"), 1),
        ("@keyframes hxWhaleAura", s.count("@keyframes hxWhaleAura{"), 1),
        ("空闲浮动+光晕双动画", s.count(".main-page .whale-hero.is-idle .whale-hero__avatar{animation:hxIdleFloat 5.2s ease-in-out infinite,hxWhaleAura 4.4s ease-in-out infinite}"), 1),
        ("作答呼吸+光晕双动画", s.count(".main-page .whale-hero.is-busy .whale-hero__avatar{animation:hxWhaleBreath 2.4s ease-in-out infinite,hxWhaleAura 4.4s ease-in-out infinite}"), 1),
        # CSS：空闲文案轮换入场
        ("@keyframes hxLineIn", s.count("@keyframes hxLineIn{"), 1),
        ("文案入场类", s.count(".main-page .whale-hero__text.hx-line-in{animation:hxLineIn"), 1),
        # CSS：静音
        ("新静音块", s.count("@media (prefers-reduced-motion:reduce){.main-page::before,.main-page::after"), 1),
        # JS
        ("HX_IDLE_LINES 定义", s.count("const HX_IDLE_LINES = ["), 1),
        ("paintIdleLine 定义", s.count("const paintIdleLine = (animate) => {"), 1),
        ("paintIdleLine 引用", s.count("paintIdleLine"), exp_paint),
        ("rollIdleLine 定义", s.count("const rollIdleLine = () => {"), 1),
        ("rollIdleLine 引用", s.count("rollIdleLine"), exp_roll),
        ("scheduleIdleRoll 定义", s.count("const scheduleIdleRoll = () => {"), 1),
        ("scheduleIdleRoll 引用", s.count("scheduleIdleRoll"), exp_sched),
        ("bindIdleLines 定义", s.count("const bindIdleLines = () => {"), 1),
        ("bindIdleLines 引用", s.count("bindIdleLines"), exp_bind),
        ("hxLineTimer 声明", s.count("let hxLineTimer = null;"), 1),
        ("随机间隔刷新", s.count("4200 + Math.floor(Math.random() * 3600)"), 1),
        ("__HX_LINE__ 探针", s.count("w.__HX_LINE__ = () => hxIdleLine;"), 1),
        # 文案改名
        ("旧名 仅作答 残留(应仅剩迁移键)", s.count('"\u4ec5\u4f5c\u7b54"'), 1),
        ("新名 仅仅作答 = 参数名+3处映射", s.count('"\u4ec5\u4ec5\u4f5c\u7b54"'), 4),
        ("旧名 弹题自动作答 残留(应仅剩迁移键)", s.count('"\u5f39\u9898\u81ea\u52a8\u4f5c\u7b54"'), 1),
        ("新名 弹题作答 = 常量+2处映射", s.count('"\u5f39\u9898\u4f5c\u7b54"'), 3),
        ("常量 VIDEO_QUIZ_SETTING 已改", s.count('const VIDEO_QUIZ_SETTING = "\u5f39\u9898\u4f5c\u7b54";'), 1),
        ("参数名 已改", s.count('{ name: "\u4ec5\u4ec5\u4f5c\u7b54", value: false, type: "boolean" },'), 1),
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
