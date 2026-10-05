# -*- coding: utf-8 -*-
"""
0.4.11 收尾：把两处过时注释里的「10s」同步为「3s」（不涉及代码，纯注释一致性）
"""
import os
import sys

P = r"C:\Users\D_A\DoubaoWork\chats\2026-10-05\new-chat-4\海底小纵队·探矿鲸娘.user.js"
OUT = r"C:\Users\D_A\WorkBuddy\2026-10-05-13-53-42\_f53out.txt"
DRY = "--dry" in sys.argv

log = []


def w(s):
    log.append(str(s))


def flush(code=0):
    open(OUT, "w", encoding="utf-8").write("\n".join(log))
    sys.exit(code)


raw = open(P, "rb").read().decode("utf-8")
s = raw.replace("\r\n", "\n")

pairs = [
    ("C1 路由头注释",
     "安静 10s 回鲸娘",
     "安静 3s 回鲸娘"),
    ("C2 战果注释",
     "（随后 10s 自动回鲸娘页）",
     "（随后 3s 自动回鲸娘页）"),
]

for label, old, new in pairs:
    n = s.count(old)
    if n != 1:
        w("!! [" + label + "] 期望 1 处，实际 " + str(n) + " 处 —— 未写入")
        flush(1)
    s = s.replace(old, new)
    w("  [OK] " + label + "  " + old + "  ->  " + new)

# 结构不变量
w("")
w("=== 结构不变量 ===")
checks = [
    ("版本仍为 0.4.11", s.count('const HX_BUILD = "0.4.11";'), 1),
    ("停留时长仍 3000", s.count("const HX_TAB_RETURN_MS = 3000;"), 1),
    ("注释里已无 10s 回鲸娘", s.count("安静 10s 回鲸娘"), 0),
    ("注释里已无随后 10s", s.count("随后 10s 自动回鲸娘页"), 0),
    ("新注释 3s 就位", s.count("安静 3s 回鲸娘") + s.count("随后 3s 自动回鲸娘页"), 2),
]
fails = []
for name, got, exp in checks:
    ok = got == exp
    w("  [" + ("OK" if ok else "NG") + "] " + name.ljust(22) + " got=" + str(got) + " exp=" + str(exp))
    if not ok:
        fails.append(name)
if fails:
    w("!! 未写入：" + ", ".join(fails))
    flush(1)

w("  dry=" + str(DRY))
if DRY:
    w("  [DRY] 未写盘")
    flush(0)

crlf = s.replace("\n", "\r\n").encode("utf-8")
open(P, "wb").write(crlf)
w("  已写盘 bytes=" + str(len(crlf)) + " crlf=" + str(s.count("\n")) + " bareLF=0")
flush(0)
