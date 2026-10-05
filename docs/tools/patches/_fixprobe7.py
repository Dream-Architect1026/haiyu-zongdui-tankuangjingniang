# -*- coding: utf-8 -*-
"""fixprobe7：探针里的协议 05 文案同步去掉括号。"""
import io, os

W = r"C:\Users\D_A\WorkBuddy\2026-10-05-13-53-42"
OLD = u'\u4ea7\u751f\u51b2\u7a81\uff08\u5982\u9891\u7e41\u8bf7\u6c42\u89e6\u53d1\u9650\u6d41\uff09\uff0c'
NEW = u'\u4ea7\u751f\u51b2\u7a81\uff0c'
L = []
for f in ("_mkuiprobe.cjs", "_mkshot.cjs"):
    p = os.path.join(W, f)
    s = io.open(p, encoding="utf-8", newline="").read()
    n = s.count(OLD)
    if n == 1:
        s = s.replace(OLD, NEW, 1)
        io.open(p, "w", encoding="utf-8", newline="").write(s)
    L.append(u"%s : %d" % (f, n))
io.open(os.path.join(W, "_fixprobe7.txt"), "w", encoding="utf-8").write(u"\n".join(L))
print(u"\n".join(L))
