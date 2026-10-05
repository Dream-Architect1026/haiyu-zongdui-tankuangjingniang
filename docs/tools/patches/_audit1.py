# -*- coding: utf-8 -*-
"""最终完整性审计：把用户提过的每一个点都逐条复核。"""
import io, re

P = r"C:\Users\D_A\DoubaoWork\chats\2026-10-05\new-chat-4\海底小纵队·探矿鲸娘.user.js"
src = io.open(P, "r", encoding="utf-8").read()

out = []
def L(s=""):
    out.append(s)

def c(pat, flags=0):
    return len(re.findall(pat, src, flags))

L("=" * 74)
L("完整性审计  文件字符数 = %d" % len(src))
L("=" * 74)

L("")
L("【1】尺寸常量（两页必须同一值 = 固定死一个窗口大小）")
for m in re.finditer(r"const (DEFAULT_CARD_WIDTH|ANSWER_CARD_WIDTH) = [^;]+;", src):
    L("    " + m.group(0))

L("")
L("【2】答题页限宽（本轮修复点）")
L("    .question_table 限宽规则     : %d 处" % c(r"\.question_table\{max-width:100%;overflow-x:auto"))
L("    .question_table 基础 625px   : %d 处" % c(r"\.question_table\{width:625px\}"))
L("    .question-list 定宽 625px    : %d 处" % c(r"\.question-list\{width:625px\}"))
L("    .card_content 限宽+裁切      : %d 处" % c(r"\.card_content\{max-width:100%;overflow:hidden\}"))
L("    旧的内层滚动写法（应为 0）    : %d 处" % c(r"\.question-list\{max-width:100%"))

L("")
L("【3】模型清单（服务端真实只认 flash / v4-pro）")
L("    DEFAULT_AI_MODEL             : %s" % (re.search(r"const DEFAULT_AI_MODEL = [^;]+;", src).group(0) if re.search(r"const DEFAULT_AI_MODEL = [^;]+;", src) else "未找到"))
L("    ALLOWED_AI_MODELS            : %s" % (re.search(r"const ALLOWED_AI_MODELS = \[[^\]]*\]", src).group(0) if re.search(r"const ALLOWED_AI_MODELS = \[[^\]]*\]", src) else "未找到"))
L("    ElOption 下拉项              :")
for m in re.finditer(r'ElOption, \{ value: "([^"]+)", label: "([^"]+)"', src):
    L("        value=%-18s label=%s" % (m.group(1), m.group(2)))
L("    旧模型名残留(v4.1-flash)     : %d 处" % c(r"deepseek-v4\.1"))
L("    旧模型名残留(deepseek-chat)  : %d 处" % c(r"deepseek-chat"))
L("    下拉缺失(deepseek-missing)   : %d 处" % c(r"deepseek-missing"))
L("    一次性迁移标记               : %d 处" % c(r"MODEL_MIGRATION|migration|__aiModelMigrated"))

L("")
L("【4】打赏卡片文案")
for m in re.finditer(r"const DONATE_CARD_HTML = '(.*?)';", src, re.S):
    seg = m.group(1)
    L("    含「校友打卡」: %d  (应为 0)" % seg.count(u"校友打卡"))
    L("    含「0.88」   : %d  (应为 0)" % seg.count(u"0.88"))
    L("    含「一分也是爱」: %d (应为 0)" % seg.count(u"一分也是爱"))
    L("    含「不要白嫖」: %d  (应保留 1)" % seg.count(u"不要白嫖"))
    L("    含 1.88      : %d" % seg.count(u"1.88"))
    L("    图片宽度 236px: %d" % seg.count(u"width:236px"))
    txt = re.sub(r"<[^>]+>", "", seg)
    L("    纯文本预览    : " + txt[:150])

L("")
L("【5】下拉弹层修复（el-select 在 shadow 外）")
L("    document 级 EP 注入          : %d 处" % c(r"GM_addStyle\(elementPlusCss\)"))
L("    POPPER_CSS 定义              : %d 处" % c(r"const POPPER_CSS"))
L("    POPPER_CSS 注入              : %d 处" % c(r"GM_addStyle\(POPPER_CSS\)"))
L("    超高 z-index                 : %d 处" % c(r"2147483000"))

L("")
L("【6】其它此前确认过的修复点")
L("    ResizeObserver 报错过滤      : %d 处" % c(r"ResizeObserver"))
L("    良性错误白名单 isBenign      : %d 处" % c(r"isBenign"))
L("    iframe api/work 判定         : %d 处" % c(r"api/work"))

L("")
L("【7】潜在缺失：选择题下拉是否可选 + 默认值对齐")
L("    ai.deepseek.model 绑定       : %d 处" % c(r"ai\.deepseek\.model"))
L("    sanitizeAiConfig 存在        : %d 处" % c(r"sanitizeAiConfig"))
L("    runScript/答题入口           : %d 处" % c(r"开始答题|startAnswer|autoAnswer"))

io.open(r"C:\Users\D_A\WorkBuddy\2026-10-05-13-53-42\_audit1.txt", "w", encoding="utf-8").write("\n".join(out))
print("ok")
