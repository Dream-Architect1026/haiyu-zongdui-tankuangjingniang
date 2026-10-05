# -*- coding: utf-8 -*-
# rename 正确率阈值 -> 正确阈值 ; 相似度阈值 -> 相似阈值
import io, sys

P = r"C:\Users\D_A\DoubaoWork\chats\2026-10-05\new-chat-4\海底小纵队·探矿鲸娘.user.js"

with io.open(P, "r", encoding="utf-8", newline="") as f:
    t = f.read()

orig_len = len(t)
log = []

# ---------- Step A/B: 全局改名（只匹配带引号的字符串字面量） ----------
n1 = t.count('"正确率阈值"')
n2 = t.count('"相似度阈值"')
n3 = t.count('"正确阈值"')
n4 = t.count('"相似阈值"')
log.append("before: 正确率阈值=%d 相似度阈值=%d 正确阈值=%d 相似阈值=%d" % (n1, n2, n3, n4))
assert n1 == 3, "正确率阈值 预期3处，实际 %d" % n1
assert n2 == 3, "相似度阈值 预期3处，实际 %d" % n2
assert n3 == 0 and n4 == 0, "已存在新名，需人工确认"

t = t.replace('"正确率阈值"', '"正确阈值"')
t = t.replace('"相似度阈值"', '"相似阈值"')
log.append("ok A/B 全局改名完成")

# ---------- Step C: 补 旧别名 -> 新名（存量配置兜底） ----------
CRLF = "\r\n"
anchor = '    "答案相似度超过多少选择": "相似阈值",' + CRLF
assert t.count(anchor) == 1, "锚点 C 命中 %d 次" % t.count(anchor)
inject = (
    '    "正确率阈值": "正确阈值",' + CRLF +
    '    "相似度阈值": "相似阈值",' + CRLF
)
t = t.replace(anchor, anchor + inject, 1)
log.append("ok C 已注入别名 2 条（正确率阈值/相似度阈值）")

# ---------- 校验 ----------
chk = {
    '"正确阈值"': t.count('"正确阈值"'),
    '"相似阈值"': t.count('"相似阈值"'),
    '"正确率阈值"': t.count('"正确率阈值"'),
    '"相似度阈值"': t.count('"相似度阈值"'),
}
log.append("after: 正确阈值=%d 相似阈值=%d | 旧:正确率阈值=%d 相似度阈值=%d" % (
    chk['"正确阈值"'], chk['"相似阈值"'], chk['"正确率阈值"'], chk['"相似度阈值"']))
# 旧名应只作为“别名 key”各出现 1 次
assert chk['"正确率阈值"'] == 1, "别名 key 数量异常"
assert chk['"相似度阈值"'] == 1, "别名 key 数量异常"
assert chk['"正确阈值"'] == 4, "新名 正确阈值 应为4处，实际 %d" % chk['"正确阈值"']
assert chk['"相似阈值"'] == 4, "新名 相似阈值 应为4处，实际 %d" % chk['"相似阈值"']
log.append("ok 校验通过（新名各4处 = 2别名指向 + 迁移表2 + 默认定义2 ... 见下复核）")

crlf = t.count("\r\n")
bare = t.count("\n") - crlf
log.append("chars: %d -> %d ; CRLF=%d bareLF=%d" % (orig_len, len(t), crlf, bare))

with io.open(P, "w", encoding="utf-8", newline="") as f:
    f.write(t)

sys.stdout.write("\n".join(log) + "\n")
