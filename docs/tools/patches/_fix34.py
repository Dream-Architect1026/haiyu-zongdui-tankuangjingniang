# -*- coding: utf-8 -*-
"""fix34：去掉 el-switch 的 inline-prompt / 开-关文字（small 尺寸核心仅 30px，易被裁）。

保留：选中态 = 青蓝渐变（脚本原有 .main-page .el-switch 样式），未选中 = 灰色。
同步：探针里的滑块文字也清空，保证探针与真实 EP 表现一致。
"""
import io, os, re

W = r"C:\Users\D_A\WorkBuddy\2026-10-05\13-53-42".replace("13-53-42", "13-53-42")
W = r"C:\Users\D_A\WorkBuddy\2026-10-05-13-53-42"
P = r"C:\Users\D_A\DoubaoWork\chats\2026-10-05\new-chat-4\海底小纵队·探矿鲸娘.user.js"
L = []

# ---------- 1) user.js：删掉三个 prop ----------
src = io.open(P, encoding="utf-8", newline="").read()
pat = re.compile(u'\\s*"inline-prompt": true,\\s*"active-text": "[^"]*",\\s*"inactive-text": "[^"]*",')
hits = pat.findall(src)
if len(hits) == 2:
    src = pat.sub(u'', src)
    io.open(P, "w", encoding="utf-8", newline="").write(src)
    L.append(u"ok 1 user.js 清理 2 处 inline-prompt")
else:
    L.append(u"!! 1 命中 %d" % len(hits))

# ---------- 2) 探针：清空滑块文字 ----------
probe_pairs = [
    ("_mkuiprobe.cjs",
     u"""'<span class="el-switch__core"><span class="el-switch__action">' + (k % 2 ? \u201c\u5f00\u201d : \u201c\u5173\u201d) + '</span></span>'"""),
    ("_mkshot.cjs",
     u"""'<span class="el-switch__core"><span class="el-switch__action">\u5f00</span></span>'"""),
]
FIXED = u"""'<span class="el-switch__core"><span class="el-switch__action"></span></span>'"""
for f, old in probe_pairs:
    p = os.path.join(W, f)
    s = io.open(p, encoding="utf-8", newline="").read()
    # 探针里用的是 ASCII 双引号
    old_ascii = old.replace(u"\u201c", u'"').replace(u"\u201d", u'"')
    n = s.count(old_ascii)
    if n == 1:
        s = s.replace(old_ascii, FIXED, 1)
        io.open(p, "w", encoding="utf-8", newline="").write(s)
        L.append(u"ok 2 %s" % f)
    else:
        L.append(u"!! 2 %s 命中 %d" % (f, n))

io.open(os.path.join(W, "_fix34.txt"), "w", encoding="utf-8").write(u"\n".join(L))
print(u"\n".join(L))
