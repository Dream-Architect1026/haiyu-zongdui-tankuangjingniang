# -*- coding: utf-8 -*-
"""fix29：通知（日志）文案全面精简
规则：① 每条 ≤ ~13 个汉字（配合 310 宽面板 + 时间内联徽章，保证单行不折行）
      ② 不出现括号（半角/全角）、不出现英文长句
      ③ 保留原语义与 type（颜色）不变
"""
import io, os, shutil, sys

P = r"C:\Users\D_A\DoubaoWork\chats\2026-10-05\new-chat-4\海底小纵队·探矿鲸娘.user.js"
OUT = r"C:\Users\D_A\WorkBuddy\2026-10-05-13-53-42"
L = []

src = io.open(P, encoding="utf-8", newline="").read()
orig_len = len(src)

PAIRS = [
    # --- 题目解析 / 搜索 ---
    (u'`\u6210\u529f\u89e3\u6790\u5230${this.questions.length}\u4e2a\u9898\u76ee`',
     u'`\u89e3\u6790\u5230${this.questions.length}\u9053\u9898`'),
    (u'`\u7b2c${index + 1}\u9053\u9898\u641c\u7d22\u6210\u529f`',
     u'`\u7b2c${index + 1}\u9898\u6210\u529f`'),
    (u'`\u7b2c${index + 1}\u9053\u9898\u641c\u7d22\u5931\u8d25\uff0c<a class="log-action-link" href="#" data-log-action="show-answer-tab">\u70b9\u51fb\u67e5\u770b\u539f\u56e0</a>`',
     u'`\u7b2c${index + 1}\u9898\u5931\u8d25<space><a class="log-action-link" href="#" data-log-action="show-answer-tab">\u67e5\u770b\u539f\u56e0</a>`'),
    (u'"\u672a\u89e3\u6790\u5230\u9898\u76ee\uff0c\u8bf7\u8fdb\u5165\u6b63\u786e\u9875\u9762"',
     u'"\u672a\u89e3\u6790\u5230\u9898\u76ee"'),
    (u'"\u8be5\u9875\u9762\u65e0\u4efb\u52a1\uff0c\u8bf7\u8fdb\u5165\u7ae0\u8282\u6216\u7b54\u9898\u9875\u9762\u4f7f\u7528"',
     u'"\u6b64\u9875\u65e0\u4efb\u52a1"'),

    # --- 章节页 ---
    (u'`\u68c0\u6d4b\u5230\u7528\u6237\u8fdb\u5165\u5230\u7ae0\u8282\u5b66\u4e60\u9875\u9762`',
     u'`\u5df2\u8fdb\u5165\u7ae0\u8282\u9875`'),
    (u'`\u6b63\u5728\u89e3\u6790\u4efb\u52a1\u70b9\uff0c\u8bf7\u7a0d\u7b495-10\u79d2\uff08\u5982\u679c\u957f\u65f6\u95f4\u6ca1\u6709\u53cd\u5e94\uff0c\u8bf7\u5237\u65b0\u9875\u9762\uff09`',
     u'`\u6b63\u5728\u89e3\u6790\u4efb\u52a1\u70b9`'),
    (u'`\u672c\u9875\u4efb\u52a1\u70b9\u5df2\u5168\u90e8\u5b8c\u6210\uff0c\u6b63\u524d\u5f80\u4e0b\u4e00\u7ae0\u8282`',
     u'`\u672c\u9875\u5b8c\u6210\uff0c\u524d\u5f80\u4e0b\u4e00\u7ae0`'),
    (u'`\u5df2\u7ecf\u5230\u8fbe\u6700\u540e\u4e00\u7ae0\u8282\uff0c\u65e0\u6cd5\u8df3\u8f6c`',
     u'`\u5df2\u5230\u6700\u540e\u4e00\u7ae0`'),
    (u'`\u5df2\u7ecf\u5173\u95ed\u81ea\u52a8\u4e0b\u4e00\u7ae0\u8282\uff0c\u5728\u8bbe\u7f6e\u91cc\u53ef\u66f4\u6539`',
     u'`\u81ea\u52a8\u4e0b\u4e00\u7ae0\u5df2\u5173\u95ed`'),
    (u'`\u4efb\u52a1\u5904\u7406\u5931\u8d25\uff1a${String(error)}`',
     u'`\u4efb\u52a1\u5904\u7406\u5931\u8d25`'),

    # --- 媒体播放 ---
    (u'`\u53d1\u73b0\u4e00\u4e2a${mediaType}\uff0c\u6b63\u5728\u89e3\u6790`',
     u'`\u53d1\u73b0${mediaType}\uff0c\u89e3\u6790\u4e2d`'),
    (u'`\u6b63\u5728\u5c1d\u8bd5\u64ad\u653e${mediaType}\uff0c\u8bf7\u7a0d\u7b495s`',
     u'`\u6b63\u5728\u64ad\u653e${mediaType}`'),
    (u'`${mediaType}\u5df2\u64ad\u653e\u5b8c\u6210`',
     u'`${mediaType}\u64ad\u653e\u5b8c\u6210`'),
    (u'`${mediaType}\u4efb\u52a1\u70b9\u5df2\u5b8c\u6210\uff0c\u8df3\u8fc7`',
     u'`${mediaType}\u5df2\u5b8c\u6210\uff0c\u8df3\u8fc7`'),

    # --- 作业 ---
    (u'"\u53d1\u73b0\u4e00\u4e2a\u4f5c\u4e1a\uff0c\u6b63\u5728\u89e3\u6790"',
     u'"\u53d1\u73b0\u4f5c\u4e1a\uff0c\u89e3\u6790\u4e2d"'),
    (u'"\u4f5c\u4e1a\u5df2\u7ecf\u5b8c\u6210\uff0c\u8df3\u8fc7"',
     u'"\u4f5c\u4e1a\u5df2\u5b8c\u6210\uff0c\u8df3\u8fc7"'),
    (u'`\u9898\u76ee\u5217\u8868\u83b7\u53d6\u6210\u529f`',
     u'`\u9898\u76ee\u83b7\u53d6\u6210\u529f`'),
    (u'"\u81ea\u52a8\u63d0\u4ea4\u5df2\u5f00\u542f\uff0c\u5c1d\u8bd5\u63d0\u4ea4"',
     u'"\u5c1d\u8bd5\u81ea\u52a8\u63d0\u4ea4"'),
    (u'`\u6b63\u786e\u7387\u5c0f\u4e8e${configStore.otherParams.params[1].value}%\uff0c\u6682\u5b58`',
     u'`\u6b63\u786e\u7387\u4e0d\u8db3${configStore.otherParams.params[1].value}%\uff0c\u6682\u5b58`'),
    (u'`\u6b63\u786e\u7387\u5927\u4e8e${configStore.otherParams.params[1].value}%\uff0c\u63d0\u4ea4`',
     u'`\u6b63\u786e\u7387\u8fbe\u6807\uff0c\u63d0\u4ea4`'),
    (u'"\u672a\u5f00\u542f\u81ea\u52a8\u63d0\u4ea4\uff0c\u6682\u5b58"',
     u'"\u672a\u5f00\u542f\u63d0\u4ea4\uff0c\u6682\u5b58"'),

    # --- 文档 / 电子书 ---
    (u'"\u53d1\u73b0\u4e00\u4e2a\u6587\u6863\uff0c\u6b63\u5728\u89e3\u6790"',
     u'"\u53d1\u73b0\u6587\u6863\uff0c\u89e3\u6790\u4e2d"'),
    (u'"\u53d1\u73b0\u4e00\u4e2a\u7535\u5b50\u4e66\uff0c\u6b63\u5728\u89e3\u6790"',
     u'"\u53d1\u73b0\u7535\u5b50\u4e66\uff0c\u89e3\u6790\u4e2d"'),

    # --- 任务点 / 只答题 ---
    (u'"\u53d1\u73b0\u4e00\u4e2a\u5df2\u5b8c\u6210\u4efb\u52a1\u70b9"',
     u'"\u4efb\u52a1\u70b9\u5df2\u5b8c\u6210"'),
    (u'"\u53ea\u7b54\u9898\uff0c\u4e0d\u505a\u5176\u4ed6\u5df2\u5f00\u542f\uff0c\u53ef\u5728\u8bbe\u7f6e\u91cc\u8c03\u6574"',
     u'"\u53ea\u7b54\u9898\u6a21\u5f0f\u5df2\u5f00\u542f"'),

    # --- 作业页 / 考试页 ---
    (u'`\u8fdb\u5165\u65b0\u7248\u4f5c\u4e1a\u9875\u9762\uff0c\u5f00\u59cb\u51c6\u5907\u7b54\u9898`',
     u'`\u8fdb\u5165\u4f5c\u4e1a\u9875\uff0c\u51c6\u5907\u7b54\u9898`'),
    (u'`\u6b63\u5728\u89e3\u6790\u9898\u76ee, \u8bf7\u7b49\u5f855s`',
     u'`\u6b63\u5728\u89e3\u6790\u9898\u76ee`'),
    (u'"\u8fdb\u5165\u65b0\u7248\u8003\u8bd5\u9875\u9762\uff0c\u5f00\u59cb\u51c6\u5907\u7b54\u9898"',
     u'"\u8fdb\u5165\u8003\u8bd5\u9875\uff0c\u51c6\u5907\u7b54\u9898"'),
    (u'"\u6b63\u5728\u89e3\u6790\u9898\u76ee\uff0c\u8bf7\u7a0d\u7b49"',
     u'"\u6b63\u5728\u89e3\u6790\u9898\u76ee"'),
    (u'"\u81ea\u52a8\u5207\u6362\u5df2\u5f00\u542f\uff0c\u6b63\u5728\u524d\u5f80\u4e0b\u4e00\u9898"',
     u'"\u81ea\u52a8\u5207\u6362\u5230\u4e0b\u4e00\u9898"'),
    (u'"\u5df2\u7ecf\u5230\u6700\u540e\u4e00\u9898\uff0c\u6b63\u5728\u70b9\u51fb\u4e0b\u4e00\u6b65"',
     u'"\u5df2\u5230\u6700\u540e\u4e00\u9898"'),
    (u'"\u5df2\u7ecf\u5173\u95ed\u81ea\u52a8\u5207\u6362\uff0c\u5728\u8bbe\u7f6e\u91cc\u53ef\u66f4\u6539"',
     u'"\u81ea\u52a8\u5207\u6362\u5df2\u5173\u95ed"'),

    # --- 启动 ---
    (u'"\u7528\u6237\u6089\u77e5\uff1a\u4f7f\u7528\u811a\u672c\u5373\u4e3a\u5b8c\u5168\u540c\u610f\u7528\u6237\u534f\u8bae"',
     u'"\u5df2\u540c\u610f\u7528\u6237\u534f\u8bae"'),
    (u'"\u811a\u672c\u51fa\u73b0\u5f02\u5e38\u8bf7\u4f7f\u7528 Edge \u6d4f\u89c8\u5668\uff0c\u672c\u811a\u672c\u53ea\u9488\u5bf9 Edge \u8fdb\u884c\u9002\u914d"',
     u'"\u5f02\u5e38\u8bf7\u6539\u7528 Edge \u6d4f\u89c8\u5668"'),
]

for i, (old, new) in enumerate(PAIRS, 1):
    n = src.count(old)
    if n != 1:
        L.append("!! #%d 命中 %d 次: %s" % (i, n, old[:40]))
        continue
    src = src.replace(old, new, 1)
    L.append("ok #%d" % i)

bad = [x for x in L if x.startswith("!!")]
if bad:
    io.open(os.path.join(OUT, "_fix29.txt"), "w", encoding="utf-8").write("\n".join(L))
    print("\n".join(L)); print("ABORT"); sys.exit(1)

# 链接间隙用真实空格（先占位再替换，避免 Python 字符串里直接写空格被误改）
src = src.replace(u'\u5931\u8d25<space><a class="log-action-link"', u'\u5931\u8d25 <a class="log-action-link"')

shutil.copy2(P, P + ".bak-fix29")
io.open(P, "w", encoding="utf-8", newline="").write(src)
L.append("bytes: %d -> %d chars" % (orig_len, len(src)))
L.append("CRLF=%d bareLF=%d" % (src.count("\r\n"), src.count("\n") - src.count("\r\n")))
io.open(os.path.join(OUT, "_fix29.txt"), "w", encoding="utf-8").write("\n".join(L))
print("done")
