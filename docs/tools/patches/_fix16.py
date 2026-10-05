# -*- coding: utf-8 -*-
import io, shutil

P = r"C:\Users\D_A\DoubaoWork\chats\2026-10-05\new-chat-4\海底小纵队·探矿鲸娘.user.js"
src = io.open(P, "r", encoding="utf-8").read()
log = []

def rep(old, new, tag):
    global src
    n = src.count(old)
    log.append("[%s] count=%d" % (tag, n))
    assert n == 1, "pattern not unique: " + tag
    src = src.replace(old, new)

# ---- 0) 备份 ----
shutil.copyfile(P, P + ".bak-fix16")
log.append("backup -> .bak-fix16")

# ---- 1) 卡宽常量 360 -> 310，并新增 PANEL_HEIGHT ----
rep(
    '  const DEFAULT_CARD_WIDTH = "360px";',
    '  const DEFAULT_CARD_WIDTH = "310px";\n'
    '  const PANEL_HEIGHT = 610;',
    "card-width-310",
)

# ---- 2) 拖拽边界常量对齐真实面板宽 310 + 16*2 ----
rep(
    '  const PANEL_WIDTH = 334;',
    '  const PANEL_WIDTH = 342;',
    "panel-width-342",
)

# ---- 3) 追加「窗口硬锁定」CSS（插在答题页自适应 push 之后、join 之前）----
anchor = '  const layoutCss = LAYOUT_CSS_PARTS.join("");'
assert src.count(anchor) == 1, "join anchor not unique"

block = "\n".join([
    '  // -- panel window hard lock: width 310 (cardWidth const) x height PANEL_HEIGHT --',
    '  // Overflow goes INSIDE the panel (body scrolls vertically, question_table scrolls horizontally).',
    '  // The :has() guard releases the fixed height while minimized, so the 35px minimized bar still works.',
    '  LAYOUT_CSS_PARTS.push(',
    '    "\\n/* ==== panel window hard lock: overflow scrolls inside ==== */"',
    '    + "\\n.main-page .el-card{display:flex;flex-direction:column;box-sizing:border-box;height:" + PANEL_HEIGHT + "px;max-height:calc(100vh - 24px);overflow:hidden}"',
    '    + "\\n.main-page .el-card__body{flex:1 1 auto;min-height:0;overflow-y:auto;overflow-x:hidden}"',
    '    + "\\n.main-page .card_content{box-sizing:border-box;max-width:100%}"',
    "    + \"\\n.main-page .el-card:has(.card_content[style*='display: none']),.main-page .el-card:has(.card_content[style*='display:none']){height:auto;max-height:none;overflow:visible}\"",
    '  );',
    '',
])
src = src.replace(anchor, block + anchor)
log.append("[lock-css] inserted before join")

io.open(P, "w", encoding="utf-8").write(src)
log.append("written bytes(utf-8) = %d" % len(src.encode("utf-8")))
io.open(r"C:\Users\D_A\WorkBuddy\2026-10-05-13-53-42\_fix16.txt", "w", encoding="utf-8").write("\n".join(log))
print("ok")
