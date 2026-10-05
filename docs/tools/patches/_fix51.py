# -*- coding: utf-8 -*-
"""
0.4.10 -> 0.4.10 (清理)
Z  删除已成死代码的 formatRate（tok/s 速率）：声明 1 处、调用 0 处。
   用户已明确要求"Token 每秒那个速率就消除吧，不要了"，
   改版后用量栏不再引用它，留着就是残留。
"""
import os
import re
import sys

P = r"C:\Users\D_A\DoubaoWork\chats\2026-10-05\new-chat-4\海底小纵队·探矿鲸娘.user.js"
OUT = r"C:\Users\D_A\WorkBuddy\2026-10-05-13-53-42\_f51out.txt"
DRY = "--dry" in sys.argv

log = []


def w(s):
    log.append(str(s))


def flush(code=0):
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    open(OUT, "w", encoding="utf-8").write("\n".join(log))
    sys.exit(code)


raw = open(P, "rb").read().decode("utf-8")
s = raw.replace("\r\n", "\n")

w("=== 清理前 ===")
w("  formatRate 出现 = " + str(s.count("formatRate")))
w("  formatRate( 调用 = " + str(s.count("formatRate(")))
w("  tok/s 出现 = " + str(s.count("tok/s")))

OLD = r'''  const formatRate = (store) => {
    const seconds = store.elapsedMs / 1e3;
    if (!seconds || !store.completionTokens) return "\u2014";
    const rate = store.completionTokens / seconds;
    return (rate >= 100 ? rate.toFixed(0) : rate.toFixed(1)) + " tok/s";
  };
  const HX_BUILD = "0.4.10";'''

NEW = '''  const HX_BUILD = "0.4.10";'''

n = s.count(OLD)
w("")
w("=== 目标块匹配 ===")
w("  [%s] formatRate 函数块（含尾锚 HX_BUILD）出现 %d 处（期望 1）" % ("OK" if n == 1 else "NG", n))
if n != 1:
    w("!! 匹配数不为 1，未写入")
    flush(1)

s = s.replace(OLD, NEW)

w("")
w("=== 结构不变量 ===")
checks = [
    ("formatRate 全清", s.count("formatRate"), 0),
    ("tok/s 全清", s.count("tok/s"), 0),
    ("HX_BUILD 保留", s.count('const HX_BUILD = "0.4.10";'), 1),
    ("formatCost 未误伤", s.count("const formatCost = (value) => {"), 1),
    ("formatUptime 未误伤", s.count("const formatUptime = "), 1),
    ("formatTokenCount 未误伤", s.count("const formatTokenCount = "), 1),
    ("push 数不变", s.count("LAYOUT_CSS_PARTS.push("), raw.count("LAYOUT_CSS_PARTS.push(")),
    ("layoutCss join", s.count('const layoutCss = LAYOUT_CSS_PARTS.join("")'), 1),
]
fails = []
for name, got, exp in checks:
    ok = got == exp
    w("  [" + ("OK" if ok else "NG") + "] " + name.ljust(22) + " got=" + str(got) + " exp=" + str(exp))
    if not ok:
        fails.append(name)
if fails:
    w("")
    w("!! 结构不变量失败：" + ", ".join(fails) + " —— 未写入")
    flush(1)

w("")
w("=== 结果 ===")
w("  dry=" + str(DRY))
w("  LF 行数 = " + str(s.count("\n") + 1))

if DRY:
    w("  [DRY] 未写盘")
    flush(0)

crlf = s.replace("\n", "\r\n").encode("utf-8")
open(P, "wb").write(crlf)
w("  已写盘 bytes=" + str(len(crlf)) + " crlf=" + str(s.count("\n")) + " bareLF=0")
flush(0)
