# -*- coding: utf-8 -*-
"""
0.4.10 -> 0.4.11
A  智能路由：状态页停留时长 HX_TAB_RETURN_MS 10000 -> 3000（3 秒无变化即回鲸娘页）
B  配置页四个数值参数（倍速 / 操作间隔 / 正确阈值 / 相似阈值）：
   B1 包裹标题的小胶囊颜色 -> 由粉红特殊色回归常规玻璃色（与 AI 卡三字段一致）
   B2 标题前必填星号 -> 隐藏
   B3 调节控件回归"行右侧"：标签改成小胶囊后 flex 由 1 1 auto 收缩为 0 0 auto，
      不再撑开行、控件被拉到左边 —— 显式给 content 加 margin-left:auto 推回右侧。

   注意：模板里的 required: "" 必须保留 —— 小胶囊的样式选择器就是 .is-required，
   删掉属性会连胶囊一起消失。所以只从 CSS 侧隐藏星号。
"""
import os
import re
import sys

P = r"C:\Users\D_A\DoubaoWork\chats\2026-10-05\new-chat-4\海底小纵队·探矿鲸娘.user.js"
OUT = r"C:\Users\D_A\WorkBuddy\2026-10-05-13-53-42\_f52out.txt"
DRY = "--dry" in sys.argv
OLD_VER = "0.4.10"
NEW_VER = "0.4.11"

log = []


def w(s):
    log.append(str(s))


def flush(code=0):
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    open(OUT, "w", encoding="utf-8").write("\n".join(log))
    sys.exit(code)


raw = open(P, "rb").read().decode("utf-8")
s = raw.replace("\r\n", "\n")

# ── 0. 版本号替换（白名单闸门）──────────────────────────────
hits = list(re.finditer(re.escape(OLD_VER), s))
w("=== 版本号 " + OLD_VER + " 出现 " + str(len(hits)) + " 处 ===")
bad = []
for m in hits:
    ctx = s[max(0, m.start() - 48): m.end() + 48].replace("\n", "\\n")
    ok = bool(re.search(r"(@version|HX_BUILD|v0\.|/\*|// ----|License|面板|已就位|开工)", ctx))
    w("  [" + ("OK" if ok else "??") + "] " + ctx)
    if not ok:
        bad.append(ctx)
if bad:
    w("!! 有非版本字面量的 " + OLD_VER + "，已中止")
    flush(1)

ver_before = len(hits)
s = s.replace(OLD_VER, NEW_VER)


def lit_replace(src, old, new, label, expect=1):
    n = src.count(old)
    if n != expect:
        raise SystemExit("!! [" + label + "] 期望 " + str(expect) + " 处，实际 " + str(n) + " 处")
    w("  [OK] " + label + "  " + str(len(old)) + " 字符 -> " + str(len(new)))
    return src.replace(old, new)


# ══════════════════ A. 状态页停留 10s -> 3s ══════════════════
w("")
w("=== A. 智能路由：状态页停留时长 ===")
w("  HX_TAB_RETURN_MS 出现 " + str(s.count("HX_TAB_RETURN_MS")) + " 次")
for kw in ["10 秒", "10秒", "十秒"]:
    c = s.count(kw)
    if c:
        w("  !! 文案里出现「" + kw + "」" + str(c) + " 处，需人工确认是否同步改：")
        for i, ln in enumerate(s.split("\n")):
            if kw in ln:
                w("     " + str(i + 1) + ": " + ln.strip()[:200])

s = lit_replace(s, "const HX_TAB_RETURN_MS = 10000;",
                "const HX_TAB_RETURN_MS = 3000;", "A1 停留时长 10000 -> 3000")

# ══════════════════ B. 四个数值参数的行样式 ══════════════════
w("")
w("=== B. 四个数值参数的标题胶囊与行排布 ===")

OLD_REQ = r'''  + "\n.main-page .setting .el-form-item.is-required>.el-form-item__label{flex:0 0 auto!important;align-self:center;margin:0 7px 0 0!important;padding:1px 8px!important;border:1px solid rgba(255,152,152,.30)!important;border-radius:8px!important;background:linear-gradient(150deg,rgba(255,140,140,.13),rgba(255,140,140,.03))!important;box-shadow:inset 0 1px 0 rgba(255,255,255,.15)!important;font-size:11.5px!important;line-height:17px!important;height:auto!important;color:var(--hx-ink)!important}"'''

# B1 颜色回归「常规玻璃」：与 AI 卡三字段同一套色（冷蓝描边 + 白玻璃底 + 上高光）
# B3 标签收缩后必须把控件显式推回右侧
NEW_REQ = r'''  + "\n.main-page .setting .el-form-item.is-required>.el-form-item__label{flex:0 0 auto!important;align-self:center;margin:0 8px 0 0!important;padding:1px 8px!important;border:1px solid rgba(140,200,255,.24)!important;border-radius:8px!important;background:linear-gradient(150deg,rgba(255,255,255,.09),rgba(255,255,255,.02))!important;box-shadow:inset 0 1px 0 rgba(255,255,255,.16)!important;font-size:11.5px!important;line-height:17px!important;height:auto!important;color:var(--hx-ink)!important}"
  + "\n/* --- B3. 标签变胶囊后 flex:0 0 auto 不再撑开行，调节控件会跑到左边；显式推回本行右侧 --- */"
  + "\n.main-page .setting .el-form-item.is-required>.el-form-item__content{margin-left:auto!important;flex:0 0 auto!important;justify-content:flex-end}"'''

s = lit_replace(s, OLD_REQ, NEW_REQ, "B1+B3 胶囊颜色回归常规 + 控件推回右侧")

OLD_DOT = r'''  + "\n.main-page .setting .el-form-item.is-required>.el-form-item__label::before{color:#ff9a9a!important;margin-right:3px!important;font-size:11px!important}"'''

NEW_DOT = r'''  + "\n/* --- B2. 必填星号已按要求隐藏。注意 required 属性必须留在模板里：小胶囊的样式选择器就是 .is-required，删掉属性会连胶囊一起没了 --- */"
  + "\n.main-page .setting .el-form-item.is-required>.el-form-item__label::before{display:none!important;content:none!important;margin:0!important;width:0!important;min-width:0!important}"'''

s = lit_replace(s, OLD_DOT, NEW_DOT, "B2 隐藏必填星号")

# ══════════════════ 结构不变量 ══════════════════
w("")
w("=== 结构不变量 ===")
checks = [
    ("HX_BUILD " + NEW_VER, s.count('const HX_BUILD = "' + NEW_VER + '";'), 1),
    (OLD_VER + " 残留", s.count(OLD_VER), 0),
    ("停留时长=3000", s.count("const HX_TAB_RETURN_MS = 3000;"), 1),
    ("停留时长旧值已无", s.count("HX_TAB_RETURN_MS = 10000"), 0),
    ("模板 required 保留", s.count('required: ""'), 2),
    ("is-required 胶囊规则仍在", s.count(".el-form-item.is-required>.el-form-item__label{flex:0 0 auto"), 1),
    ("B3 控件推右规则已加", s.count(".el-form-item.is-required>.el-form-item__content{margin-left:auto!important;flex:0 0 auto!important;justify-content:flex-end}"), 1),
    ("行基础排布仍在", s.count(".main-page .setting .el-form-item{display:flex;align-items:center;margin:0!important}"), 1),
    ("粉色描边已清", s.count("rgba(255,152,152,.30)"), 0),
    ("粉色渐变已清", s.count("rgba(255,140,140,.13)"), 0),
    ("粉星号色已清", s.count("#ff9a9a"), 0),
    ("星号隐藏规则已加", s.count("el-form-item__label::before{display:none!important;content:none!important"), 1),
    ("AI 字段胶囊未误伤", s.count(".setting-ai-field>.el-form-item__label{flex:0 0 auto"), 1),
    ("好感度粉色未误伤", s.count("rgba(255,140,190,.30)"), 1),
    ("push 数不变", s.count("LAYOUT_CSS_PARTS.push("), raw.count("LAYOUT_CSS_PARTS.push(")),
    ("layoutCss join", s.count('const layoutCss = LAYOUT_CSS_PARTS.join("")'), 1),
    ("版号字面量数不变", s.count(NEW_VER), ver_before),
]
fails = []
for name, got, exp in checks:
    ok = got == exp
    w("  [" + ("OK" if ok else "NG") + "] " + name.ljust(24) + " got=" + str(got) + " exp=" + str(exp))
    if not ok:
        fails.append(name)
if fails:
    w("")
    w("!! 结构不变量失败：" + ", ".join(fails) + " —— 未写入")
    flush(1)

w("")
w("=== 结果 ===")
w("  dry=" + str(DRY))
w("  LF 行数 = " + str(s.count("\n") + 1))

if DRY:
    w("  [DRY] 未写盘")
    flush(0)

crlf = s.replace("\n", "\r\n").encode("utf-8")
open(P, "wb").write(crlf)
w("  已写盘 bytes=" + str(len(crlf)) + " crlf=" + str(s.count("\n")) + " bareLF=0")
flush(0)
