# -*- coding: utf-8 -*-
"""修 _mkshot.cjs 残留的多余 `}`（用更精准的锚点）。"""
import io, os

W = r"C:\Users\D_A\WorkBuddy\2026-10-05-13-53-42"
p = os.path.join(W, "_mkshot.cjs")
s = io.open(p, encoding="utf-8", newline="").read()
L = []
old = u'+ cards + "</div></div>";'
n = s.count(old)
L.append(u"anchor count = %d" % n)
if n == 1:
    i = s.index(old) + len(old)
    j = s.index(u"}", i)
    k = j + 1
    while k < len(s) and s[k] in u"\r\n \t":
        k += 1
    if k < len(s) and s[k] == u"}":
        s = s[:k] + s[k + 1:]
        io.open(p, "w", encoding="utf-8", newline="").write(s)
        L.append(u"ok 删除多余 '}'")
    else:
        L.append(u"ok 无多余 '}'")
io.open(os.path.join(W, "_fixprobe4.txt"), "w", encoding="utf-8").write(u"\n".join(L))
print(u"\n".join(L))
