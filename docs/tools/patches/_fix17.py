# -*- coding: utf-8 -*-
import io, shutil

P = r"C:\Users\D_A\DoubaoWork\chats\2026-10-05\new-chat-4\海底小纵队·探矿鲸娘.user.js"
src = io.open(P, "r", encoding="utf-8").read()
log = []

def rep(old, new, tag, expect=1):
    global src
    n = src.count(old)
    log.append("[%s] count=%d" % (tag, n))
    assert n == expect, "unexpected count for " + tag
    src = src.replace(old, new)

shutil.copyfile(P, P + ".bak-fix17")
log.append("backup -> .bak-fix17")

# ---- 1) 拔掉把 .main-page 的 position:fixed 顶成 relative 的那条规则（真凶）----
old1 = ".main-page{position:relative;font-family:var(--hx-font);color:var(--hx-ink)}"
i = src.find(old1)
log.append("rule1 found at char %d" % i)
if i >= 0:
    log.append("ctx: " + src[max(0, i - 70): i + len(old1) + 15].replace("\n", "||"))
rep(old1, ".main-page{font-family:var(--hx-font);color:var(--hx-ink)}", "kill-position-relative")

# ---- 2) 面板外框宽回到 334（= 310 内容 + 12*2 内边距）----
rep("  const PANEL_WIDTH = 342;", "  const PANEL_WIDTH = 334;", "panel-width-334")

# ---- 3) 清掉答题页 push 开头遗留的字面 \n（双重转义），让整段真正生效 ----
rep('"\\\\n/* 答题页自适应', '"\\n/* 答题页自适应', "fix-literal-backslash-n")

# ---- 4) 高度 610 -> 310（用户改口：310 x 310 正方形）----
rep("  const PANEL_HEIGHT = 610;", "  const PANEL_HEIGHT = 310;", "panel-height-310")

# ---- 5) 背景图尺寸锁 310 x 310 ----
rep(
    "background:var(--hx-bg) center/cover no-repeat!important;",
    "background:var(--hx-bg) center/cover no-repeat!important;background-size:310px 310px!important;",
    "bg-size-310",
)

io.open(P, "w", encoding="utf-8").write(src)
log.append("written utf-8 bytes = %d" % len(src.encode("utf-8")))
io.open(r"C:\Users\D_A\WorkBuddy\2026-10-05-13-53-42\_fix17.txt", "w", encoding="utf-8").write("\n".join(log))
print("ok")
