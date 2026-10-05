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

shutil.copyfile(P, P + ".bak-fix18")
log.append("backup -> .bak-fix18")

# ---- 1) 外框宽度显式锁死 = DEFAULT_CARD_WIDTH（否则竖向滚动条会把 310 挤成 8px 偏差）----
rep(
    '    + "\\n.main-page .el-card{display:flex;flex-direction:column;box-sizing:border-box;height:" + PANEL_HEIGHT + "px;max-height:calc(100vh - 24px);overflow:hidden}"',
    '    + "\\n.main-page .el-card{display:flex;flex-direction:column;box-sizing:border-box;width:" + DEFAULT_CARD_WIDTH + ";height:" + PANEL_HEIGHT + "px;max-height:calc(100vh - 24px);overflow:hidden}"',
    "lock-outer-width",
)

# ---- 2) 注释同步（310 x 310）----
rep(
    '    "\\n/* ==== panel window hard lock: overflow scrolls inside ==== */"',
    '    "\\n/* ==== panel window hard lock: 310x310 (bg image fills it exactly) ==== */"',
    "lock-comment",
)

# ---- 3) 拖拽边界 = 外框宽 310 ----
rep("  const PANEL_WIDTH = 334;", "  const PANEL_WIDTH = 310;", "panel-width-310")

io.open(P, "w", encoding="utf-8").write(src)
log.append("written utf-8 bytes = %d" % len(src.encode("utf-8")))
io.open(r"C:\Users\D_A\WorkBuddy\2026-10-05-13-53-42\_fix18.txt", "w", encoding="utf-8").write("\n".join(log))
print("ok")
