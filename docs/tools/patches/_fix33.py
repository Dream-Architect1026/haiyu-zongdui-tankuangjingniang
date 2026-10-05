# -*- coding: utf-8 -*-
"""fix33：删除界面上所有带括号的文案（全角/半角）。

清单（全部为界面可见文本）：
 1) 协议 05：使用脚本可能与相应平台产生冲突（如频繁请求触发限流），…
 2) 配置项：操作间隔（秒） -> 操作间隔（并加迁移，避免老配置丢值）
 3) 日志：网络错误，无法连接 AI 服务（本地服务是否已启动？）
 4) 输入框占位：DeepSeek API Key（sk- 开头）
 5) 模型下拉：DeepSeek V4 Pro（最强）
 6) 模型下拉 + 教程页：Flash（默认·推荐）
不改动：AI 提示词内部的括号（工程用）、正则里的括号、CSS 注释里的括号。
"""
import io, os, re

P = r"C:\Users\D_A\DoubaoWork\chats\2026-10-05\new-chat-4\海底小纵队·探矿鲸娘.user.js"
L = []

src = io.open(P, encoding="utf-8", newline="").read()
orig_len = len(src)

# ---------- 1) 精确替换 ----------
PAIRS = [
    # 协议 05
    (u'\u4ea7\u751f\u51b2\u7a81\uff08\u5982\u9891\u7e41\u8bf7\u6c42\u89e6\u53d1\u9650\u6d41\uff09\uff0c',
     u'\u4ea7\u751f\u51b2\u7a81\uff0c'),
    # 配置项名
    (u'\u64cd\u4f5c\u95f4\u9694\uff08\u79d2\uff09', u'\u64cd\u4f5c\u95f4\u9694'),
    # 日志
    (u'\uff08\u672c\u5730\u670d\u52a1\u662f\u5426\u5df2\u542f\u52a8\uff1f\uff09', u''),
    # 占位符
    (u'DeepSeek API Key\uff08sk- \u5f00\u5934\uff09', u'DeepSeek API Key'),
    # 模型下拉
    (u'DeepSeek V4 Pro\uff08\u6700\u5f3a\uff09', u'DeepSeek V4 Pro'),
]
for i, (old, new) in enumerate(PAIRS, 1):
    n = src.count(old)
    if n != 1:
        L.append(u"!! P%d 命中 %d" % (i, n))
    else:
        src = src.replace(old, new, 1)
        L.append(u"ok P%d" % i)

# ---------- 2) Flash（默认·推荐）—— 含不确定中间点，用正则 ----------
pat = re.compile(u'Flash\uff08[^\uff09]*\uff09')
hits = pat.findall(src)
if len(hits) == 2:
    src = pat.sub(u'Flash', src)
    L.append(u"ok P6 Flash（…）x2")
else:
    L.append(u"!! P6 命中 %d : %s" % (len(hits), hits))

# ---------- 3) 迁移：操作间隔（秒） -> 操作间隔 ----------
anchor = u'["\u7b54\u6848\u76f8\u4f3c\u5ea6\u9608\u503c", "\u76f8\u4f3c\u5ea6\u9608\u503c"]'
if src.count(anchor) == 1:
    src = src.replace(anchor, anchor + u',\r\n    ["\u64cd\u4f5c\u95f4\u9694", "\u64cd\u4f5c\u95f4\u9694"]', 1)
    L.append(u"ok P7 加操作间隔迁移")
else:
    L.append(u"!! P7 命中 %d" % src.count(anchor))

bad = [x for x in L if x.startswith("!!")]
io.open(P, "w", encoding="utf-8", newline="").write(src)
crlf = src.count(u"\r\n")
bare = src.count(u"\n") - crlf
L.append(u"chars: %d -> %d ; CRLF=%d bareLF=%d" % (orig_len, len(src), crlf, bare))
io.open(r"C:\Users\D_A\WorkBuddy\2026-10-05-13-53-42\_fix33.txt", "w", encoding="utf-8").write(u"\n".join(L))
print(u"\n".join(L))
if bad:
    print("HAS_FAIL")
