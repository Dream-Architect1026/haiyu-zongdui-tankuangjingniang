# -*- coding: utf-8 -*-
"""fix27: 把 fix25 留下的 3 处裸 LF 归一化为 CRLF（纯行尾格式，不动任何内容）。
安全性：已逐字节定位，3 处裸 LF 全部位于 CSS 追加行的行尾（"  结尾 -> 下一行 4 空格+加号），
        不存在于 JS 模板字符串内部，因此归一化不改变任何字符串内容。
"""
import io, os, shutil, sys

P = r"C:\Users\D_A\DoubaoWork\chats\2026-10-05\new-chat-4\海底小纵队·探矿鲸娘.user.js"
OUT = r"C:\Users\D_A\WorkBuddy\2026-10-05-13-53-42"
L = []

b = io.open(P, "rb").read()
orig = len(b)

# 先把所有 CRLF 摘成占位，再把剩余裸 LF 变 CRLF，避免把 CRLF 变 CRCRLF
TMP = b"\x00CRLF\x00"
b2 = b.replace(b"\r\n", TMP)
n_bare = b2.count(b"\n")
b2 = b2.replace(b"\n", b"\r\n")
b2 = b2.replace(TMP, b"\r\n")

L.append("bare LF found = %d" % n_bare)
if n_bare == 0:
    L.append("无需修改")
else:
    shutil.copy2(P, P + ".bak-fix27")
    io.open(P, "wb").write(b2)
    L.append("bytes: %d -> %d" % (orig, len(b2)))
    L.append("backup = .bak-fix27")

bb = io.open(P, "rb").read()
L.append("after: CRLF=%d bareLF=%d" % (bb.count(b"\r\n"), bb.count(b"\n") - bb.count(b"\r\n")))
io.open(os.path.join(OUT, "_fix27.txt"), "w", encoding="utf-8").write("\n".join(L))
print("done")
