# -*- coding: utf-8 -*-
# fix44: 0.4.5 -> 0.4.6
#   hero 的 5 个标签：取消 hover / 激活态的 translateY 上浮，只保留发光；
#   并把标签行抬到独立层叠层，双保险不与被上方元素叠压。
# 用法: python _fix44.py [--dry]
import re
import sys

SRC = r"C:\Users\D_A\DoubaoWork\chats\2026-10-05\new-chat-4\海底小纵队·探矿鲸娘.user.js"
BAK = r"C:\Users\D_A\WorkBuddy\2026-10-05-13-53-42\_bak_045.user.js"
LOG = r"C:\Users\D_A\WorkBuddy\2026-10-05-13-53-42\_f44out.txt"
DRY = "--dry" in sys.argv

OLD_VER = "0.4.5"
NEW_VER = "0.4.6"
log = []


def w(s):
    log.append(s)


CSS_TEXT = """
/* ==== v0.4.6 : 标签只发光不上浮（消除与上方元素的叠压） ==== */

/* 取消全部位移：hover / 激活 / 按下 都不再 translateY，只留发光与配色变化 */
.main-page .demo-tabs .el-tabs__item:hover,
.main-page .demo-tabs .el-tabs__item.is-active,
.main-page .demo-tabs .el-tabs__item:active{transform:none!important}
.main-page .demo-tabs .el-tabs__item{will-change:box-shadow,background-color,border-color}

/* 标签行独占一层叠层：发光不会被相邻元素盖住，也永不越界压到上方 */
.main-page .demo-tabs>.el-tabs__header{position:relative;z-index:2;isolation:isolate}
.main-page .demo-tabs .el-tabs__nav-wrap,
.main-page .demo-tabs .el-tabs__nav-scroll,
.main-page .demo-tabs .el-tabs__nav{position:relative;z-index:1}

/* 悬停：用「发光 + 描边提亮」替代上浮 */
.main-page .demo-tabs .el-tabs__item:hover{border-color:rgba(56,226,255,.40)!important;box-shadow:0 0 14px rgba(56,226,255,.30),inset 0 1px 0 rgba(255,255,255,.26)!important}

/* 激活：光晕呼吸保留，位移为零 */
.main-page .demo-tabs .el-tabs__item.is-active{box-shadow:0 0 20px rgba(56,226,255,.42),inset 0 1px 0 rgba(255,255,255,.34)!important}
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
    'const HX_BUILD = "0.4.5";',
    'const _hoisted_3 = { class: "minus" };',
    "class: \"card_content\"",
    # 三个待覆盖的旧上浮规则，必须存在（说明确实还有位移在生效）
    ".main-page .demo-tabs .el-tabs__item:hover{color:var(--hx-ink)!important;background:rgba(255,255,255,.07)!important;transform:translateY(-1px);",
    ".main-page .demo-tabs .el-tabs__item.is-active{color:#fff!important;background:var(--lg-tint-hi)!important;border-color:rgba(56,226,255,.32)!important;transform:translateY(-1px);",
    "background:linear-gradient(150deg,rgba(255,255,255,.14),rgba(255,255,255,.04) 46%,rgba(8,18,38,.30))!important;transform:translateY(-2px);",
    "rgba(155,107,255,.22))!important;transform:translateY(-2px);",
]
for r in REQUIRED:
    c = s.count(r)
    w("needle[" + str(c) + "] " + r[:76])
    if c != 1:
        fail("锚点缺失或重复: " + r[:76])

# 旧位移规则总数（用于写入后核对是否已全部被覆盖）
old_shift = len(re.findall(r"\.main-page \.demo-tabs \.el-tabs__item[^{]*\{[^}]*translateY", s))
w("")
w("旧 translateY 标签规则数 = " + str(old_shift))
if old_shift < 4:
    fail("旧位移规则少于预期（4），可能已被改过")

# ---- 版本号审计 ----
w("")
w("---- 0.4.5 occurrences: " + str(s.count(OLD_VER)) + " ----")
for m in re.finditer(re.escape(OLD_VER), s):
    a = max(0, m.start() - 60)
    b = min(len(s), m.end() + 60)
    w("  ..." + s[a:b].replace("\n", "\\n") + "...")

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

# ---- 生成 JS 插入块 ----
lines = [ln.strip() for ln in CSS_TEXT.strip().split("\n")]
lines = [ln for ln in lines if ln]
if not lines:
    fail("CSS_TEXT 为空")
w("")
w("new_css_lines=" + str(len(lines)))
if any('"' in ln for ln in lines):
    fail("CSS 行内含双引号，会破坏 JS 字符串")

js = ("  // ---- v" + NEW_VER + " ----\n"
      "  LAYOUT_CSS_PARTS.push(\n"
      '    "' + '"\n    + "'.join("\\n" + ln for ln in lines) + '"\n'
      "  );\n\n")

if not DRY:
    s = s.replace(ANCHOR, js + ANCHOR, 1)
    s = s.replace(OLD_VER, NEW_VER)

    exp_ver = raw.count(OLD_VER) + 2  # 全局替换 + 新块的两处注释（行注释 + CSS 注释）
    checks = [
        ("HX_BUILD " + NEW_VER, s.count('const HX_BUILD = "' + NEW_VER + '";'), 1),
        (OLD_VER + " 残留", s.count(OLD_VER), 0),
        (NEW_VER + " 出现", s.count(NEW_VER), exp_ver),
        ("push 次数", s.count("LAYOUT_CSS_PARTS.push("), 6),
        ("取消位移规则(悬停选择器)", s.count(".main-page .demo-tabs .el-tabs__item:hover,"), 1),
        ("transform:none 覆写", s.count(".main-page .demo-tabs .el-tabs__item:active{transform:none!important}"), 1),
        ("标签行叠层", s.count(".main-page .demo-tabs>.el-tabs__header{position:relative;z-index:2;isolation:isolate}"), 1),
        ("nav 独立层", s.count(".main-page .demo-tabs .el-tabs__nav{position:relative;z-index:1}"), 1),
        ("旧位移仍在(被覆盖)", len(re.findall(r"\.main-page \.demo-tabs \.el-tabs__item[^{]*\{[^}]*translateY", s)), old_shift),
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
