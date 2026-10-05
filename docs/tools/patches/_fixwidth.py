# -*- coding: utf-8 -*-
"""修复：面板宽度固定，不再因切到「答题」页而撑大到 630px。
答题表格改为在固定宽度内横向滚动，保证信息完整可读。"""
import io, re

P = r"C:\Users\D_A\DoubaoWork\chats\2026-10-05\new-chat-4\海底小纵队·探矿鲸娘.user.js"
with io.open(P, encoding="utf-8") as f:
    src = f.read()

# 1) 统一面板宽度
old = '''  const DEFAULT_CARD_WIDTH = "310px";
  const ANSWER_CARD_WIDTH = "630px";'''
new = '''  const DEFAULT_CARD_WIDTH = "360px";
  const ANSWER_CARD_WIDTH = DEFAULT_CARD_WIDTH;'''
assert old in src, "width consts not found"
src = src.replace(old, new, 1)
print("[1] width unified -> 360px")

# 2) 追加答题页自适应样式（随 layoutCss 注入 shadow root）
add_css = (
    "\n/* 答题页自适应：固定面板宽度，表格横向滚动 */"
    ".main-page .card_content{max-width:100%;overflow:hidden}"
    ".main-page .script-answer{overflow:hidden}"
    ".main-page .question-list{max-width:100%;overflow-x:auto;border-radius:10px}"
    ".main-page .question-list::-webkit-scrollbar{height:6px}"
    ".main-page .question-list::-webkit-scrollbar-thumb{background:linear-gradient(90deg,var(--hx-cyan),var(--hx-violet));border-radius:3px}"
    ".main-page .ai-config{display:grid;gap:8px;margin:0 0 10px}"
    ".main-page .ai-config .el-select,.main-page .ai-config .el-input{width:100%}"
    ".main-page .answer-result{word-break:break-word}"
    "\\n"
)

m = re.search(r"  const layoutCss = LAYOUT_CSS_PARTS\.join\(\"\"\);\n", src)
if m:
    # 直接改 join 参数：把追加样式作为额外一片
    ins = m.start() + len("  const layoutCss = LAYOUT_CSS_PARTS.join(\"\");\n")
    inject = "  LAYOUT_CSS_PARTS.push(%s);\n" % (
        '"' + add_css.replace("\\", "\\\\").replace('"', '\\"') + '"'
    )
    src = src[:ins] + inject + src[ins:]
    print("[2] answer-tab css appended")
else:
    print("[2] WARN layoutCss join not found; fallback to const append")
    # 回退：直接在 layoutCss 定义后追加
    lm = re.search(r"  const layoutCss = LAYOUT_CSS_PARTS\.join\(\"\"\);\n", src)
    if lm:
        src = src[:lm.end()] + "  const ANSWER_TAB_CSS = %s;\n" % (
            '"' + add_css.replace("\\", "\\\\").replace('"', '\\"') + '"'
        ) + "  const layoutCssAll = layoutCss + ANSWER_TAB_CSS;\n" + src[lm.end():]
        src = src.replace("createStyleSheet(layoutCss)", "createStyleSheet(layoutCssAll)")

with io.open(P, "w", encoding="utf-8", newline="") as f:
    f.write(src)

chk = io.open(P, encoding="utf-8").read()
print("\n--- verify ---")
print("DEFAULT_CARD_WIDTH :", re.search(r'DEFAULT_CARD_WIDTH = "([^"]+)"', chk).group(1))
print("ANSWER_CARD_WIDTH  :", re.search(r'ANSWER_CARD_WIDTH = ([^;]+);', chk).group(1))
print("LAYOUT push        :", chk.count("LAYOUT_CSS_PARTS.push"))
