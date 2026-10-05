# -*- coding: utf-8 -*-
"""fix25b: 协议页署名吸底常驻（position:sticky;bottom:0）—— 修正锚点后重跑"""
import io, os, shutil, sys

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

OLD = r'    + "\n.main-page .guide-footer{margin:10px 0 2px;padding:11px 12px;border:1px solid var(--hx-line);border-radius:12px;background:linear-gradient(120deg,rgba(56,226,255,.12),rgba(155,107,255,.12));text-align:center;box-shadow:0 6px 18px rgba(2,8,24,.26);backdrop-filter:blur(10px) saturate(140%);-webkit-backdrop-filter:blur(10px) saturate(140%)}"'

NEW = r'''    + "\n/* ===== 协议页署名：吸底常驻，永远不被折叠线挡住 ===== */"
    + "\n.main-page .guide-page{display:flex!important;flex-direction:column!important;padding-bottom:0!important}"
    + "\n.main-page .guide-page>.guide-list{flex:0 0 auto;padding-bottom:6px!important}"
    + "\n.main-page .guide-footer{position:sticky!important;bottom:0!important;z-index:6;flex:0 0 auto;margin:8px 0 0!important;padding:9px 12px;border:1px solid var(--hx-line);border-radius:12px;background:linear-gradient(120deg,rgba(20,36,68,.95),rgba(28,20,60,.95));text-align:center;box-shadow:0 -8px 22px rgba(2,8,24,.5);backdrop-filter:blur(14px) saturate(150%);-webkit-backdrop-filter:blur(14px) saturate(150%)}"'''

sub_once("署名吸底（修正版）", OLD, NEW)

bad = [x for x in LOG if x.startswith("!!")]
if bad:
    print(NL.join(LOG)); print("ABORT"); sys.exit(1)

shutil.copy2(P, P + ".bak-fix25")
io.open(P, "w", encoding="utf-8", newline="").write(src)
LOG.append("bytes: %d -> %d" % (orig_len, len(src)))
LOG.append("CRLF=%d bareLF=%d" % (src.count("\r\n"), src.count("\n") - src.count("\r\n")))
io.open(os.path.join(OUT, "_fix25.txt"), "w", encoding="utf-8").write(NL.join(LOG))
print("done")
