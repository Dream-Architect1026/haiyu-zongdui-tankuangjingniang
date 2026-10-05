# -*- coding: utf-8 -*-
import re, shutil, os, time

TP = r"C:\Users\D_A\DoubaoWork\chats\2026-10-05\new-chat-4\海底小纵队·探矿鲸娘.user.js"
PP = r"C:\Users\D_A\DoubaoWork\chats\2026-10-05\new-chat-4\星虹网课助手-移动版.user.js"
KEY = "LAYOUT_CSS_PARTS.push("
out = []
def p(*a): out.append(" ".join(str(x) for x in a))


def extract_push(src):
    i = src.index(KEY)
    k = i + len(KEY)
    depth = 1
    in_str = False
    q = None
    while k < len(src):
        c = src[k]
        if in_str:
            if c == "\\":
                k += 2
                continue
            if c == q:
                in_str = False
        else:
            if c in "\"'":
                in_str = True
                q = c
            elif c == "(":
                depth += 1
            elif c == ")":
                depth -= 1
                if depth == 0:
                    break
        k += 1
    return i, k + 1, src[i:k + 1]


T = open(TP, encoding="utf-8").read()
P = open(PP, encoding="utf-8").read()

ti, tj, tseg = extract_push(T)
pi, pj, pseg = extract_push(P)
p("TEST push @%d..%d  len=%d" % (ti, tj, len(tseg)))
p("  %s" % tseg)
p("")
p("PROD push @%d..%d  len=%d" % (pi, pj, len(pseg)))
p("  %s" % pseg)
p("")

# 备份
bak = TP.replace(".user.js", ".bak-%s.user.js" % time.strftime("%H%M%S"))
shutil.copy2(TP, bak)
p("备份 -> %s" % os.path.basename(bak))

new = T

# --- 1) 替换 push 段 ---
if tseg != pseg:
    new = new.replace(tseg, pseg, 1)
    p("[1] push 段已替换")
else:
    p("[1] push 段已一致，跳过")

# --- 2) 常量 ---
before = 'const DEFAULT_CARD_WIDTH = "310px";'
after = 'const DEFAULT_CARD_WIDTH = "360px";'
if before in new:
    new = new.replace(before, after, 1)
    p("[2a] DEFAULT_CARD_WIDTH 310px -> 360px  OK")
else:
    p("[2a] !! 未找到 %s" % before)

before2 = 'const ANSWER_CARD_WIDTH = "630px";'
after2 = 'const ANSWER_CARD_WIDTH = DEFAULT_CARD_WIDTH;'
if before2 in new:
    new = new.replace(before2, after2, 1)
    p("[2b] ANSWER_CARD_WIDTH 630px -> DEFAULT_CARD_WIDTH  OK")
else:
    p("[2b] !! 未找到 %s" % before2)

open(TP, "w", encoding="utf-8", newline="").write(new)
p("")
p("写回完成：%d -> %d 字节" % (len(T), len(new)))

# --- 校验 ---
V = open(TP, encoding="utf-8").read()
p("")
p("=== 校验 ===")
vi, vj, vseg = extract_push(V)
p("push 段与 PROD 一致: %s" % (vseg == pseg))
p("DEFAULT_CARD_WIDTH 行: %s" % re.search(r'const DEFAULT_CARD_WIDTH = [^;]+;', V).group(0))
p("ANSWER_CARD_WIDTH  行: %s" % re.search(r'const ANSWER_CARD_WIDTH = [^;]+;', V).group(0))
p(".question_table 行: %s" % re.search(r'\.question_table\{[^}]*\}', V).group(0))
p("表格列宽: %s" % re.findall(r'width: "(\d+)" \}', V))

open(r"C:\Users\D_A\WorkBuddy\2026-10-05-13-53-42\_fix8.txt", "w", encoding="utf-8").write("\n".join(out))
print("ok")
