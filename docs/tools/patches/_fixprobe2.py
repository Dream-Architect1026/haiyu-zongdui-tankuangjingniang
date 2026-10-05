# -*- coding: utf-8 -*-
"""修探针：① 删掉 slice 替换残留的多余 `}`；② 同步协议页新文案。"""
import io, os, re

W = r"C:\Users\D_A\WorkBuddy\2026-10-05-13-53-42"
L = []

def rd(p):
    return io.open(p, encoding="utf-8", newline="").read()

def wr(p, s):
    io.open(p, "w", encoding="utf-8", newline="").write(s)

# ---------- 1) 删多余右花括号 ----------
p1 = os.path.join(W, "_mkuiprobe.cjs")
s = rd(p1)
anchor = u'"</div></div>";'
if s.count(anchor) == 1:
    i = s.index(anchor) + len(anchor)
    j = s.index(u"}", i)          # 函数闭合
    k = j + 1
    while k < len(s) and s[k] in u"\r\n \t":
        k += 1
    if k < len(s) and s[k] == u"}":
        s = s[:k] + s[k + 1:]
        wr(p1, s)
        L.append(u"ok 1 删除 _mkuiprobe.cjs 多余 '}'")
    else:
        L.append(u"ok 1 无多余 '}'（可能已修）")
else:
    L.append(u"!! 1 anchor 命中 %d" % s.count(anchor))

# ---------- 2) 同步协议文案 ----------
NEW01 = (u'\u6559\u5b66\u7ba1\u7406\u89c4\u5b9a\u3001\u5b66\u672f\u8bda\u4fe1\u8981\u6c42\uff0c'
         u'\u4ee5\u53ca\u6240\u7528\u5e73\u53f0\u7684\u7528\u6237\u534f\u8bae\u4e0e\u670d\u52a1\u6761\u6b3e\uff0c'
         u'\u52ff\u7528\u4e8e\u4ee3\u5199\u4f5c\u4e1a\u3001\u66ff\u8003\u7b49\u8fdd\u89c4\u7528\u9014\u3002'
         u'\u56e0\u8fdd\u53cd\u4e0a\u8ff0\u89c4\u5b9a\u4ea7\u751f\u7684\u4e00\u5207\u540e\u679c\uff0c'
         u'\u7531\u4f7f\u7528\u8005\u81ea\u884c\u627f\u62c5\u3002')
OLD01 = (u'\u6559\u5b66\u7ba1\u7406\u89c4\u5b9a\u4e0e\u5b66\u672f\u8bda\u4fe1\u8981\u6c42\uff0c'
         u'\u52ff\u7528\u4e8e\u4ee3\u5199\u4f5c\u4e1a\u3001\u66ff\u8003\u7b49\u884c\u4e3a\u3002')

for f in ("_mkuiprobe.cjs", "_mkshot.cjs"):
    p = os.path.join(W, f)
    s = rd(p)
    hit = 0
    if s.count(OLD01) == 1:
        s = s.replace(OLD01, NEW01, 1); hit += 1
    if s.count(u'\u5b66\u6821\u6559\u5b66\u7cfb\u7edf') == 1:
        s = s.replace(u'\u5b66\u6821\u6559\u5b66\u7cfb\u7edf', u'\u76f8\u5e94\u5e73\u53f0', 1); hit += 1
    if hit:
        wr(p, s)
    L.append(u"%s 文案替换 %d 处" % (f, hit))

io.open(os.path.join(W, "_fixprobe2.txt"), "w", encoding="utf-8").write(u"\n".join(L))
print(u"\n".join(L))
