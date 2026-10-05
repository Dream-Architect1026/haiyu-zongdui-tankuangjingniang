# -*- coding: utf-8 -*-
"""fix31：协议页合规文案补充 + 配置项「只答题不刷课」->「仅作答」

1) 01 学习与研究用途：补充「所用平台的用户协议与服务条款」，并加免责句
   （违反规定的一切后果由使用者自行承担），避免开发者承担连带责任。
2) 05 风险自担：把「学校教学系统」改为「相应平台」（覆盖超星/学习通等所有平台）。
3) 配置项：只答题不刷课 -> 仅作答（并同步加迁移映射，避免老配置丢值）
"""
import io, os

P = r"C:\Users\D_A\DoubaoWork\chats\2026-10-05\new-chat-4\海底小纵队·探矿鲸娘.user.js"
L = []

src = io.open(P, encoding="utf-8", newline="").read()
orig_len = len(src)

PAIRS = [
    # ---- 1) 01 条：补充平台合规 + 免责 ----
    (u'\u6559\u5b66\u7ba1\u7406\u89c4\u5b9a\u4e0e\u5b66\u672f\u8bda\u4fe1\u8981\u6c42\uff0c\u52ff\u7528\u4e8e\u4ee3\u5199\u4f5c\u4e1a\u3001\u66ff\u8003\u7b49\u884c\u4e3a\u3002',
     u'\u6559\u5b66\u7ba1\u7406\u89c4\u5b9a\u3001\u5b66\u672f\u8bda\u4fe1\u8981\u6c42\uff0c'
     u'\u4ee5\u53ca\u6240\u7528\u5e73\u53f0\u7684\u7528\u6237\u534f\u8bae\u4e0e\u670d\u52a1\u6761\u6b3e\uff0c'
     u'\u52ff\u7528\u4e8e\u4ee3\u5199\u4f5c\u4e1a\u3001\u66ff\u8003\u7b49\u8fdd\u89c4\u7528\u9014\u3002'
     u'\u56e0\u8fdd\u53cd\u4e0a\u8ff0\u89c4\u5b9a\u4ea7\u751f\u7684\u4e00\u5207\u540e\u679c\uff0c'
     u'\u7531\u4f7f\u7528\u8005\u81ea\u884c\u627f\u62c5\u3002'),
    # ---- 2) 05 条：学校教学系统 -> 相应平台 ----
    (u'\u5b66\u6821\u6559\u5b66\u7cfb\u7edf', u'\u76f8\u5e94\u5e73\u53f0'),
    # ---- 3) 配置项改名 ----
    (u'name: "\u53ea\u7b54\u9898\u4e0d\u5237\u8bfe"', u'name: "\u4ec5\u4f5c\u7b54"'),
    # ---- 4) 迁移表追加 ----
    (u'"\u81ea\u52a8\u7ffb\u5230\u4e0b\u4e00\u9898": "\u81ea\u52a8\u5207\u9898",',
     u'"\u81ea\u52a8\u7ffb\u5230\u4e0b\u4e00\u9898": "\u81ea\u52a8\u5207\u9898",\r\n'
     u'    "\u53ea\u7b54\u9898\u4e0d\u5237\u8bfe": "\u4ec5\u4f5c\u7b54",'),
]

for i, (old, new) in enumerate(PAIRS, 1):
    n = src.count(old)
    if n != 1:
        L.append(u"!! #%d 命中 %d" % (i, n))
    else:
        src = src.replace(old, new, 1)
        L.append(u"ok #%d" % i)

bad = [x for x in L if x.startswith("!!")]
io.open(P, "w", encoding="utf-8", newline="").write(src)
crlf = src.count(u"\r\n")
bare = src.count(u"\n") - crlf
L.append(u"chars: %d -> %d ; CRLF=%d bareLF=%d" % (orig_len, len(src), crlf, bare))
io.open(r"C:\Users\D_A\WorkBuddy\2026-10-05-13-53-42\_fix31.txt", "w", encoding="utf-8").write(u"\n".join(L))
print(u"\n".join(L))
if bad:
    print("HAS_FAIL")
