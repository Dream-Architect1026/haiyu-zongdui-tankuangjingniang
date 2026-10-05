# -*- coding: utf-8 -*-
"""fix24: 末轮收尾 —— 统一 box-sizing 消除 1px 横向溢出 + 锁定 pane 不横向滚"""
import io, os, re, shutil, sys

P = r"C:\Users\D_A\DoubaoWork\chats\2026-10-05\new-chat-4\海底小纵队·探矿鲸娘.user.js"
OUT = r"C:\Users\D_A\WorkBuddy\2026-10-05-13-53-42"
NL = "\r\n"
LOG = []

src = io.open(P, encoding="utf-8", newline="").read()
orig_len = len(src)

def sub_once(name, old, new, must=1):
    global src
    n = src.count(old)
    if n != must:
        LOG.append("!! %s: 命中 %d 次（期望 %d）" % (name, n, must))
        return False
    src = src.replace(old, new, 1)
    LOG.append("ok %s" % name)
    return True

CSS = [
    r'    + "\n/* ===== 末轮收尾：统一盒模型，消除 1px 横向溢出 ===== */"',
    r'    + "\n.main-page .question_table,.main-page .question-list,.main-page .ai-config,.main-page .answer-legend,.main-page .guide-header,.main-page .guide-card,.main-page .guide-footer,.main-page .setting>div,.main-page .script-home .el-scrollbar__view>div{box-sizing:border-box!important;max-width:100%!important}"',
    r'    + "\n.main-page .el-tab-pane{overflow-x:hidden!important;box-sizing:border-box!important;max-width:100%!important}"',
    r'    + "\n.main-page .el-card__body,.main-page .card_content,.main-page .demo-tabs,.main-page .demo-tabs>.el-tabs__content{box-sizing:border-box!important;max-width:100%!important}"',
]

anchor = r'    + "\n.main-page .el-empty__description p{color:var(--hx-ink-dim)!important;font-size:12px;letter-spacing:.5px}"'
sub_once("CSS 收尾", anchor, anchor + NL + NL.join(CSS))

bad = [x for x in LOG if x.startswith("!!")]
if bad:
    print(NL.join(LOG)); print("ABORT"); sys.exit(1)

shutil.copy2(P, P + ".bak-fix24")
io.open(P, "w", encoding="utf-8", newline="").write(src)
LOG.append("bytes: %d -> %d" % (orig_len, len(src)))
LOG.append("CRLF=%d bareLF=%d" % (src.count("\r\n"), src.count("\n") - src.count("\r\n")))
io.open(os.path.join(OUT, "_fix24.txt"), "w", encoding="utf-8").write(NL.join(LOG))
print("done")
