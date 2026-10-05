# -*- coding: utf-8 -*-
import io

P = r"C:\Users\D_A\DoubaoWork\chats\2026-10-05\new-chat-4\海底小纵队·探矿鲸娘.user.js"
log = []
def L(s=""):
    log.append(s)

src = io.open(P, "r", encoding="utf-8", newline="").read()
before = len(src)

# 现状（fix14 之后）残留了一个空 <br> 且把「不要白嫖」整行也删掉了。
# 目标：只删掉「校友打卡上限 0.88 元，一分也是爱。」这一句，保留「不要白嫖」提示，并去掉多余 <br>。
old = u"不要白嫖哦</strong>，校友打卡"
# 1) 恢复第二行提示，并重新收尾
o1 = u"，不设下限，心意到即可；<br></p>"
n1 = u"，不设下限，心意到即可；<br>· <strong>矿大北京的学弟学妹们不要白嫖哦</strong>。</p>"
c1 = src.count(o1)
L("恢复「不要白嫖」行  命中=%d" % c1)
if c1:
    src = src.replace(o1, n1)

io.open(P, "w", encoding="utf-8", newline="").write(src)

L("")
L("字符数 %d -> %d" % (before, len(src)))
L("")
L("--- 打赏卡片完整文案（应只剩 2 条 bullet，且无 0.88）---")
j = src.find(u"如果脚本帮到了你")
k = src.find(u"支付宝「扫一扫」", j)
seg = src[j:k + 30] if j >= 0 else u"未找到"
L(seg.replace("\\n", " "))
L("")
L("--- 残留检查 ---")
for pat in [u"校友打卡", u"0.88", u"一分也是爱", u"<br></p>"]:
    L("  %-14s 剩余=%d" % (pat, src.count(pat)))

io.open(r"C:\Users\D_A\WorkBuddy\2026-10-05-13-53-42\_fix15.txt", "w", encoding="utf-8").write("\n".join(log))
print("ok")
