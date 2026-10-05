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

shutil.copyfile(P, P + ".bak-fix19")
log.append("backup -> .bak-fix19")

# 310 x 310 -> 500 x 500（1.5 倍再取整）
rep('  const DEFAULT_CARD_WIDTH = "310px";',
    '  const DEFAULT_CARD_WIDTH = "500px";',
    "card-width-500")

rep('  const PANEL_HEIGHT = 310;',
    '  const PANEL_HEIGHT = 500;',
    "panel-height-500")

# 拖拽边界同步
rep('  const PANEL_WIDTH = 310;',
    '  const PANEL_WIDTH = 500;',
    "panel-width-500")

# 背景图同步 500 x 500
rep('background-size:310px 310px!important;',
    'background-size:500px 500px!important;',
    "bg-size-500")

# 注释同步
rep('\\n/* ==== panel window hard lock: 310x310 (bg image fills it exactly) ==== */',
    '\\n/* ==== panel window hard lock: 500x500 (bg image fills it exactly) ==== */',
    "lock-comment")

io.open(P, "w", encoding="utf-8").write(src)
log.append("written utf-8 bytes = %d" % len(src.encode("utf-8")))
io.open(r"C:\Users\D_A\WorkBuddy\2026-10-05-13-53-42\_fix19.txt", "w", encoding="utf-8").write("\n".join(log))
print("ok")
