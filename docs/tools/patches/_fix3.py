# -*- coding: utf-8 -*-
import io, re, shutil, json

P = r"C:\Users\D_A\DoubaoWork\chats\2026-10-05\new-chat-4\海底小纵队·探矿鲸娘.user.js"
shutil.copyfile(P, P + ".bak4")
src = io.open(P, encoding="utf-8").read()
rep = []

# ─────────────────────────────────────────────
# FIX 1: _hoisted_2$2 截断到 </ol>，去掉半截的 donate section
# ─────────────────────────────────────────────
old_tail = '</ol><section class="donate-card"'
k = src.find(old_tail)
assert k != -1, "找不到 donate section 起点"
end = src.find("', 2);", k)
assert end != -1, "找不到 ', 2); 结尾"
src = src[:k] + "</ol>'" + src[end + len("'"):]
rep.append("FIX1 _hoisted_2$2 截断: 删除 %d 字符" % (end - k))

# ─────────────────────────────────────────────
# FIX 2: 打赏卡整体改为动态 vnode + innerHTML
# ─────────────────────────────────────────────
start_marker = "  const _hoisted_donate = {\n    src: decryptDonateImage(),"
a = src.find(start_marker)
assert a != -1, "找不到 _hoisted_donate 定义"

end_marker = "  const _hoisted_4$1 = [\n    _hoisted_2$2,\n    _hoisted_donateImg9,\n    _hoisted_donateTail9\n  ];"
b = src.find(end_marker, a)
assert b != -1, "找不到 _hoisted_4$1 数组"
b2 = b + len(end_marker)

CARD_HTML = (
    '<h3 style="margin:0 0 7px;font-size:13px">赞助开发 · 随缘打赏</h3>'
    '<p style="margin:0 0 9px;font-size:11px;line-height:1.85;text-align:left">'
    '如果脚本帮到了你，欢迎扫码请作者喝杯奶茶～<br>· 单人打赏<strong>上限 1.88 元</strong>，不设下限，心意到即可；'
    '<br>· <strong>矿大北京的学弟学妹们不要白嫖哦</strong>，校友打卡<strong>上限 0.88 元</strong>，一分也是爱。'
    '</p><img src="\' + DONATE_IMG_SRC + \'" alt="支付宝赞助码" style="width:236px;display:block;margin:0 auto">'
    '<p style="margin:9px 0 0;text-align:center;font-size:11px">打开支付宝「扫一扫」</p>'
)

new_block = (
    "  const DONATE_IMG_SRC = decryptDonateImage();\n"
    "  const DONATE_CARD_HTML = '" + CARD_HTML + "';\n"
    "  const _hoisted_donate9 = /* @__PURE__ */ vue.createVNode(\"section\", {\n"
    "    class: \"donate-card\",\n"
    "    style: {\n"
    "      margin: \"14px 0 6px\",\n"
    "      padding: \"13px\"\n"
    "    },\n"
    "    innerHTML: DONATE_CARD_HTML\n"
    "  }, null, 16);\n"
    "  const _hoisted_4$1 = [\n"
    "    _hoisted_2$2,\n"
    "    _hoisted_donate9\n"
    "  ];"
)
src = src[:a] + new_block + src[b2:]
rep.append("FIX2 打赏卡改为动态 vnode(innerHTML): 替换 %d 字符 -> %d 字符" % (b2 - a, len(new_block)))

# ─────────────────────────────────────────────
# FIX 3: CSS push 必须在 join 之前
# ─────────────────────────────────────────────
join_stmt = 'const layoutCss = LAYOUT_CSS_PARTS.join("");'
j = src.find(join_stmt)
assert j != -1, "找不到 layoutCss join"

# 找 join 之后的 push 语句
p = src.find("LAYOUT_CSS_PARTS.push(", j)
assert p != -1, "找不到 layoutCss push"
# 精确扫描 JS 字符串字面量，找到 push(...) 的结束
q = src.find('"', p)
assert q != -1
i = q + 1
while i < len(src):
    if src[i] == "\\":
        i += 2
        continue
    if src[i] == '"':
        break
    i += 1
close = src.find(");", i)
assert close != -1
push_end = src.find("\n", close) + 1
push_stmt = src[p:push_end]
rep.append("FIX3 push 语句长度 %d, 尾部 %r" % (len(push_stmt), push_stmt[-60:]))

# 去掉 join 行，把 join 放到 push 之后
line_end = src.find("\n", j) + 1
new_join = "  " + join_stmt + "\n"
src2 = src[:j - 2] + src[line_end:]          # 删掉 join 行（含前导两空格）
p2 = src2.find("LAYOUT_CSS_PARTS.push(", j - 2)
assert p2 != -1
pe2 = src2.find("\n", src2.find(");", src2.find('"', p2))) + 1
src = src2[:pe2] + new_join + src2[pe2:]
rep.append("FIX3 完成: join 已移动到 push 之后")

io.open(P, "w", encoding="utf-8", newline="").write(src)

# ─────────────────────────────────────────────
# 报告
# ─────────────────────────────────────────────
s = io.open(P, encoding="utf-8").read()
rep.append("")
rep.append("=== 结果核对 ===")
rep.append("", )
rep.append("半截 '<img src=\"' 残留: %d   (应为 0)" % s.count('<img src="\', 2)'))
rep.append("DONATE_CARD_HTML: %d" % s.count("DONATE_CARD_HTML"))
rep.append("_hoisted_donateTail9 残留: %d  (应为 0)" % s.count("_hoisted_donateTail9"))
rep.append("_hoisted_donate9: %d" % s.count("_hoisted_donate9"))
rep.append("GM_addStyle: %d" % s.count("GM_addStyle"))

i = s.find("const layoutCss =")
rep.append("")
rep.append("=== layoutCss 附近 700 字符 ===")
rep.append(s[i - 700:i + 80])

i = s.find("ANSWER_CARD_WIDTH")
rep.append("")
rep.append("=== 宽度常量 ===")
rep.append(s[max(0, i - 200):i + 400])

io.open(r"C:\Users\D_A\WorkBuddy\2026-10-05-13-53-42\_fix3.txt", "w", encoding="utf-8").write("\n".join(rep))
print("OK")
