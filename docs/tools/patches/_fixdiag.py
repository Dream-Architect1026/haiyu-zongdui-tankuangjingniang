# -*- coding: utf-8 -*-
"""把误插在元数据块内部的自诊断代码，移到 ==/UserScript== 之后。"""
import io, re

P = r"C:\Users\D_A\DoubaoWork\chats\2026-10-05\new-chat-4\海底小纵队·探矿鲸娘.user.js"
with io.open(P, encoding="utf-8") as f:
    src = f.read()

start = src.find("// ── 自诊断")
end_marker = "// @name"
end = src.find(end_marker)
assert start != -1 and end != -1 and start < end, (start, end)

block = src[start:end].rstrip()
# 去掉块首尾空行
block = block.strip("\n")
removed = src[start:end]
src = src[:start] + src[end:]

# 现在插到 ==/UserScript== 之后
anchor = "// ==/UserScript==\n"
i = src.find(anchor)
assert i != -1
i += len(anchor)

new = src[:i] + "\n" + block + "\n" + src[i:]
with io.open(P, "w", encoding="utf-8", newline="") as f:
    f.write(new)

# 校验
with io.open(P, encoding="utf-8") as f:
    chk = f.read()
head = chk[:chk.find("// ==/UserScript==")]
print("元数据块内是否还有自诊断:", "自诊断" in head)
print("元数据块首行:", chk.split("\n")[0])
print("自诊断位置(line):", chk[:chk.find("自诊断")].count("\n") + 1)
i2 = chk.find("// ==/UserScript==")
print("UserScript 结束位置(line):", chk[:i2].count("\n") + 1)
print("自诊断在结束之后:", chk.find("自诊断") > i2)
