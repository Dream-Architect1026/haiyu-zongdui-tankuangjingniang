# -*- coding: utf-8 -*-
# fix38: 校准 deepseek-flash 价格 + 措辞改官方术语(高峰/空闲) + 补规则出处注释
import io, sys

P = r"C:\Users\D_A\DoubaoWork\chats\2026-10-05\new-chat-4\海底小纵队·探矿鲸娘.user.js"
CRLF = "\r\n"
J = lambda *lines: CRLF.join(lines) + CRLF

with io.open(P, "r", encoding="utf-8", newline="") as f:
    t = f.read()

orig_len = len(t)
log = []


def sub_once(old, new, tag):
    global t
    assert t.count(old) == 1, "%s 锚点命中 %d 次" % (tag, t.count(old))
    t = t.replace(old, new, 1)
    log.append("ok " + tag)


# ---------- A: deepseek-flash 价格修正（官方 api-docs.deepseek.com/zh-cn/quick_start/pricing） ----------
oldA = J(
    '  const MODEL_PRICES = {',
    '    "deepseek-flash": {',
    '      off: { hit: 0.05, miss: 1.5, out: 4.5 },',
    '      peak: { hit: 0.1, miss: 3, out: 9 }',
    '    },',
)
newA = J(
    '  // 单价单位：元 / 百万 tokens；来源 api-docs.deepseek.com/zh-cn/quick_start/pricing',
    '  // 高峰 = 北京时间周一至周五 09:00-12:00、14:00-18:00；其余为空闲时段（空闲价 = 高峰价的一半）',
    '  const MODEL_PRICES = {',
    '    "deepseek-flash": {',
    '      off: { hit: 0.02, miss: 1, out: 4 },',
    '      peak: { hit: 0.04, miss: 2, out: 8 }',
    '    },',
)
sub_once(oldA, newA, "A deepseek-flash 价格 0.05/1.5/4.5 -> 0.02/1/4")

# ---------- B: 措辞 平峰 -> 空闲（官方术语） ----------
oldB = '(peak ? "\\u9ad8\\u5cf0" : "\\u5e73\\u5cf0")'
newB = '(peak ? "\\u9ad8\\u5cf0" : "\\u7a7a\\u95f2")'
sub_once(oldB, newB, "B 平峰 -> 空闲")

# ---------- C: 给 isPeakHour 补规则出处注释 ----------
oldC = J(
    '  const isPeakHour = (timestamp) => {',
)
newC = J(
    '  // 高峰时段判定：北京时间 周一至周五 09:00-12:00、14:00-18:00',
    '  // 依据：https://api-docs.deepseek.com/zh-cn/quick_start/pricing （2026 版，已取代旧的 00:30-08:30 错峰规则）',
    '  const isPeakHour = (timestamp) => {',
)
sub_once(oldC, newC, "C isPeakHour 注释")

# ---------- 复核 ----------
chk = {
    '"deepseek-flash"': t.count('"deepseek-flash"'),
    'off: { hit: 0.02': t.count('off: { hit: 0.02'),
    'peak: { hit: 0.04': t.count('peak: { hit: 0.04'),
    '平峰': t.count("\\u5e73\\u5cf0"),
    '空闲': t.count("\\u7a7a\\u95f2"),
    '0.05/1.5': t.count("0.05, miss: 1.5"),
}
log.append("chk: flash=%d off0.02=%d peak0.04=%d 旧平峰=%d 新空闲=%d 旧价残留=%d" % (
    chk['"deepseek-flash"'], chk['off: { hit: 0.02'], chk['peak: { hit: 0.04'],
    chk['平峰'], chk['空闲'], chk['0.05/1.5']))
assert chk['off: { hit: 0.02'] == 1 and chk['peak: { hit: 0.04'] == 1
assert chk['0.05/1.5'] == 0 and chk['平峰'] == 0 and chk['空闲'] == 1

crlf = t.count("\r\n")
bare = t.count("\n") - crlf
log.append("chars: %d -> %d ; CRLF=%d bareLF=%d" % (orig_len, len(t), crlf, bare))

with io.open(P, "w", encoding="utf-8", newline="") as f:
    f.write(t)

sys.stdout.write("\n".join(log) + "\n")
