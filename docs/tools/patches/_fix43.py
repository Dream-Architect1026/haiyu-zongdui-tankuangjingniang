# -*- coding: utf-8 -*-
# fix43: 0.4.4 -> 0.4.5
#   A) 修复作答态(is-busy)鲸娘图片消失：把 .whale-hero__balance 移出行宽预算
#   B) 标签条：去掉外层 dock，5 个标签各自独立液态玻璃胶囊、等宽均分、激活发光
#   C) 标题栏最小化/最大化两个按钮各自一枚玻璃胶囊
#   D) 最小化态美化
# 用法: python _fix43.py [--dry]
import re
import sys

SRC = r"C:\Users\D_A\DoubaoWork\chats\2026-10-05\new-chat-4\海底小纵队·探矿鲸娘.user.js"
BAK = r"C:\Users\D_A\WorkBuddy\2026-10-05-13-53-42\_bak_044.user.js"
LOG = r"C:\Users\D_A\WorkBuddy\2026-10-05-13-53-42\_f43out.txt"
DRY = "--dry" in sys.argv

log = []


def w(s):
    log.append(s)


CSS_TEXT = """
/* ==== v0.4.5 : hero 作答态修复 + 标签独立胶囊 + 最小化美化 ==== */

/* --- A. 修复作答态(is-busy)：余额块退出 flex 行宽预算，鲸娘图不再被挤出可视区 --- */
.main-page .whale-hero{position:relative}
.main-page .whale-hero__avatar{flex:0 0 auto}
.main-page .whale-hero__bubble{flex:0 1 auto;min-width:0}
.main-page .whale-hero__balance{transition:opacity .28s ease,transform .28s ease,height .28s ease,width .28s ease}
.main-page .whale-hero.is-busy .whale-hero__bubble{flex:0 1 auto;min-width:0}
.main-page .whale-hero.is-busy .whale-hero__balance{flex:0 0 0px;width:0;min-width:0;padding:0;margin:0;height:0;opacity:0;overflow:hidden;pointer-events:none;transform:translateY(-4px)}

/* --- B. 标签：移除外层 dock，每个标签自成液态玻璃胶囊，等宽均分 --- */
.main-page .demo-tabs>.el-tabs__header{overflow:visible!important;margin:0 0 9px!important}
.main-page .demo-tabs .el-tabs__nav-wrap{overflow:visible!important;border-bottom:none!important;padding:0!important}
.main-page .demo-tabs .el-tabs__nav-scroll{overflow:visible!important}
.main-page .demo-tabs .el-tabs__nav-prev,.main-page .demo-tabs .el-tabs__nav-next{display:none!important}
.main-page .demo-tabs .el-tabs__nav{display:flex!important;width:100%!important;align-items:stretch;gap:6px;padding:0!important;border:none!important;border-radius:0!important;background:none!important;box-shadow:none!important;backdrop-filter:none!important;-webkit-backdrop-filter:none!important;transform:none!important}
.main-page .demo-tabs .el-tabs__item{flex:1 1 0!important;min-width:0!important;display:flex!important;align-items:center;justify-content:center;height:30px!important;line-height:30px!important;padding:0 4px!important;border:1px solid rgba(140,200,255,.18)!important;border-radius:11px!important;background:linear-gradient(150deg,rgba(255,255,255,.075),rgba(255,255,255,.02) 46%,rgba(8,18,38,.26))!important;backdrop-filter:blur(10px) saturate(150%);-webkit-backdrop-filter:blur(10px) saturate(150%);box-shadow:inset 0 1px 0 rgba(255,255,255,.14),0 3px 10px rgba(2,8,24,.20);color:var(--hx-ink-dim)!important;font-size:11.5px!important;font-weight:600!important;letter-spacing:.2px;overflow:hidden!important;transition:var(--lg-t)}
.main-page .demo-tabs .el-tabs__item::before{display:none!important}
.main-page .demo-tabs .el-tabs__item:hover{color:var(--hx-ink)!important;border-color:rgba(140,200,255,.34)!important;background:linear-gradient(150deg,rgba(255,255,255,.14),rgba(255,255,255,.04) 46%,rgba(8,18,38,.30))!important;transform:translateY(-2px);box-shadow:0 6px 16px rgba(2,8,24,.30),inset 0 1px 0 rgba(255,255,255,.24)}
.main-page .demo-tabs .el-tabs__item.is-active{color:#fff!important;border-color:rgba(56,226,255,.46)!important;background:linear-gradient(155deg,rgba(56,226,255,.26),rgba(74,140,255,.14) 44%,rgba(155,107,255,.22))!important;transform:translateY(-2px);text-shadow:0 0 12px rgba(56,226,255,.65);box-shadow:0 6px 18px rgba(2,8,24,.40),0 0 18px rgba(56,226,255,.36),inset 0 1px 0 rgba(255,255,255,.34)!important;animation:hxTabGlow 2.8s ease-in-out infinite}
@keyframes hxTabGlow{0%,100%{box-shadow:0 6px 18px rgba(2,8,24,.40),0 0 18px rgba(56,226,255,.34),inset 0 1px 0 rgba(255,255,255,.34)}50%{box-shadow:0 8px 22px rgba(2,8,24,.46),0 0 30px rgba(56,226,255,.62),inset 0 1px 0 rgba(255,255,255,.42)}}

/* --- C. 标题栏的两个按钮各自一枚玻璃胶囊 --- */
.main-page .card-header .zoom-icon{display:inline-flex!important;align-items:center;justify-content:center;width:22px;height:22px;border-radius:8px;border:1px solid rgba(140,200,255,.20)!important;background:linear-gradient(150deg,rgba(255,255,255,.10),rgba(255,255,255,.02) 46%,rgba(8,18,38,.26))!important;backdrop-filter:blur(10px) saturate(150%);-webkit-backdrop-filter:blur(10px) saturate(150%);box-shadow:inset 0 1px 0 rgba(255,255,255,.16),0 2px 8px rgba(2,8,24,.22);color:var(--hx-ink-dim)!important;transition:var(--lg-t)}
.main-page .card-header .zoom-icon+.zoom-icon{margin-left:7px}
.main-page .card-header .zoom-icon:hover{color:var(--hx-cyan)!important;border-color:rgba(56,226,255,.44)!important;background:linear-gradient(150deg,rgba(56,226,255,.18),rgba(56,226,255,.05) 46%,rgba(8,18,38,.28))!important;transform:translateY(-1px) scale(1.05);box-shadow:0 0 16px rgba(56,226,255,.38),inset 0 1px 0 rgba(255,255,255,.30)}
.main-page .card-header .zoom-icon:active{transform:translateY(0) scale(.94)}

/* --- D. 最小化态美化：整条做成悬浮发光胶囊，标题居中，副提示同材质 --- */
.main-page .el-card:has(.card_content[style*='display: none']) .el-card__header{padding:0!important;background:none!important;border-bottom:none!important}
.main-page .el-card:has(.card_content[style*='display: none']) .card-header{padding:7px 9px!important;border-radius:14px;border:1px solid rgba(56,226,255,.34)!important;background:linear-gradient(120deg,rgba(56,226,255,.26),rgba(74,140,255,.14) 46%,rgba(155,107,255,.26))!important;backdrop-filter:blur(18px) saturate(165%);-webkit-backdrop-filter:blur(18px) saturate(165%);animation:hxMiniGlow 3.2s ease-in-out infinite}
.main-page .el-card:has(.card_content[style*='display: none']) .card-header .title{flex:1 1 auto;justify-content:center}
.main-page .el-card:has(.card_content[style*='display: none']) .card-header .title span{font-size:13px;letter-spacing:.9px}
.main-page .el-card:has(.card_content[style*='display: none']) .card-header__logo{width:22px;height:22px}
.main-page .minus{display:flex;align-items:center;justify-content:center;padding:7px 10px 9px!important;color:var(--hx-ink-dim)!important}
.main-page .minus .el-text{font-size:11px!important;letter-spacing:.4px;opacity:.94}
.main-page .minus .compact-divider{display:none!important}
@keyframes hxMiniGlow{0%,100%{box-shadow:0 10px 26px rgba(2,8,24,.46),0 0 18px rgba(56,226,255,.18),inset 0 1px 0 rgba(255,255,255,.28)}50%{box-shadow:0 12px 30px rgba(2,8,24,.52),0 0 30px rgba(56,226,255,.36),inset 0 1px 0 rgba(255,255,255,.36)}}
@media (prefers-reduced-motion:reduce){.main-page .demo-tabs .el-tabs__item.is-active,.main-page .el-card:has(.card_content[style*='display: none']) .card-header{animation:none}}
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
ANCHOR = 'const layoutCss = LAYOUT_CSS_PARTS.join("");'
n = s.count(ANCHOR)
w("anchor layoutCss count=" + str(n))
if n != 1:
    fail("layoutCss 锚点数量异常")

REQUIRED = [
    "const HX_BUILD = \"0.4.4\";",
    ".main-page .whale-hero.is-busy{flex-direction:row;gap:9px;padding:2px 2px 0}",
    ".main-page .whale-hero__balance{flex:0 0 auto;display:flex;align-items:center;justify-content:center;width:100%;min-height:0;",
    ".main-page .whale-hero.is-busy .whale-hero__balance{opacity:0;transform:translateY(-4px);height:0;overflow:hidden;pointer-events:none}",
    'const _hoisted_3 = { class: "minus" };',
    "class: \"card_content\"",
    ".main-page .card-header .zoom-icon{color:var(--hx-ink-dim)!important;",
]
for r in REQUIRED:
    c = s.count(r)
    w("needle[" + str(c) + "] " + r[:70])
    if c != 1:
        fail("锚点缺失或重复: " + r[:70])

# ---- 版本号上下文（写入前先看清楚）----
w("")
w("---- 0.4.4 occurrences: " + str(s.count("0.4.4")) + " ----")
for m in re.finditer(r"0\.4\.4", s):
    a = max(0, m.start() - 70)
    b = min(len(s), m.end() + 40)
    ctx = s[a:b].replace("\n", "\\n")
    w("  ..." + ctx + "...")

ALLOW = re.compile(r"(HX_BUILD|@version|v0\.4\.4|liquid glass|Liquid Glass|\u9762\u677f|MIT License)")
bad = [m for m in re.finditer(r"0\.4\.4", s) if not ALLOW.search(s[max(0, m.start() - 60): m.end() + 60])]
if bad:
    w("!! 可疑的 0.4.4 出现位置: " + str(len(bad)))
    for m in bad:
        w("   @" + str(m.start()) + " ..." + s[max(0, m.start() - 70): m.end() + 40].replace("\n", "\\n"))
    if not DRY:
        fail("存在可疑版本号位置，已中止")
else:
    w("全部 0.4.4 均为版本字面量，可安全全局替换")

# ---- 生成 JS 插入块 ----
lines = [ln.strip() for ln in CSS_TEXT.strip().split("\n")]
lines = [ln for ln in lines if ln]
if not lines:
    fail("CSS_TEXT 为空")
w("")
w("new_css_lines=" + str(len(lines)))
if any('"' in ln for ln in lines):
    fail("CSS 行内含双引号，会破坏 JS 字符串")

js = ("  // ---- v0.4.5 ----\n"
      "  LAYOUT_CSS_PARTS.push(\n"
      '    "' + '"\n    + "'.join("\\n" + ln for ln in lines) + '"\n'
      "  );\n\n")

if not DRY:
    # 1) 插入新 CSS 块（成为最后一个 push -> 优先级最高）
    s = s.replace(ANCHOR, js + ANCHOR, 1)
    # 2) 版本号
    s = s.replace("0.4.4", "0.4.5")

    # 3) 结构断言
    checks = [
        ("HX_BUILD 0.4.5", s.count('const HX_BUILD = "0.4.5";'), 1),
        ("0.4.4 残留", s.count("0.4.4"), 0),
        ("push 次数", s.count("LAYOUT_CSS_PARTS.push("), 5),
        ("hxTabGlow 定义", s.count("@keyframes hxTabGlow{"), 1),
        ("hxMiniGlow 定义", s.count("@keyframes hxMiniGlow{"), 1),
        ("hxTabGlow 引用", s.count("animation:hxTabGlow"), 1),
        ("hxMiniGlow 引用", s.count("animation:hxMiniGlow"), 1),
        ("busy balance 归零", s.count(".main-page .whale-hero.is-busy .whale-hero__balance{flex:0 0 0px;width:0;min-width:0;"), 1),
        ("avatar 不收缩", s.count(".main-page .whale-hero__avatar{flex:0 0 auto}"), 1),
        ("旧标签须条", s.count("const layoutCss = LAYOUT_CSS_PARTS.join"), 1),
    ]
    ok = True
    for name, got, exp in checks:
        mark = "OK" if got == exp else "BAD"
        if got != exp:
            ok = False
        w("  [" + mark + "] " + name + " = " + str(got) + " (expect " + str(exp) + ")")
    if not ok:
        fail("结构断言未通过")

    # 4) 落盘（强制 CRLF）
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
