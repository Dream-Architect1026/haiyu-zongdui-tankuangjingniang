# -*- coding: utf-8 -*-
import io, shutil

P = r"C:\Users\D_A\DoubaoWork\chats\2026-10-05\new-chat-4\海底小纵队·探矿鲸娘.user.js"
log = []
def L(s=""):
    log.append(s)

src = io.open(P, "r", encoding="utf-8", newline="").read()
orig_len = len(src)

bak = P + ".bak-fix14"
shutil.copy2(P, bak)
L("备份 -> " + bak)
L("")

edits = [
    # A1：把「限宽 + 横向滚动」从内层表格搬到真正溢出的外层容器 .question_table
    ("A1 容器限宽",
     ".main-page .question-list{max-width:100%;overflow-x:auto;border-radius:10px}",
     ".main-page .question_table{max-width:100%;overflow-x:auto;border-radius:10px}"
     ".main-page .question-list{width:625px}"),
    # A2/A3：滚动条样式跟着挪到容器上
    ("A2 滚动条槽",
     ".main-page .question-list::-webkit-scrollbar{height:6px}",
     ".main-page .question_table::-webkit-scrollbar{height:6px}"),
    ("A3 滚动条块",
     ".main-page .question-list::-webkit-scrollbar-thumb",
     ".main-page .question_table::-webkit-scrollbar-thumb"),
    # B1：删掉「校友打卡 0.88」整句
    ("B1 删句",
     u"· <strong>矿大北京的学弟学妹们不要白嫖哦</strong>，校友打卡<strong>上限 0.88 元</strong>，一分也是爱。",
     u""),
]

for tag, o, n in edits:
    c = src.count(o)
    L("%-14s 命中=%d" % (tag, c))
    if c > 0:
        src = src.replace(o, n)

io.open(P, "w", encoding="utf-8", newline="").write(src)

L("")
L("原字符数 = %d" % orig_len)
L("新字符数 = %d" % len(src))
L("")
L("--- 残留检查（应全为 0）---")
for pat in [u"校友打卡", u"0.88", u"一分也是爱", u".question-list{max-width", u"question-list::-webkit-scrollbar"]:
    L("  %-32s 剩余=%d" % (pat, src.count(pat)))
L("")
L("--- 目标规则现状 ---")
i = src.find(".question_table{max-width")
L("  " + (src[i-60:i+150].replace("\n", " ") if i >= 0 else "未找到新的 question_table 限宽规则"))
j = src.find(u"如果脚本帮到了你")
L("  " + (src[j:j+220].replace("\n", " ") if j >= 0 else "未找到打赏文案"))

io.open(r"C:\Users\D_A\WorkBuddy\2026-10-05-13-53-42\_fix14.txt", "w", encoding="utf-8").write("\n".join(log))
print("ok")
