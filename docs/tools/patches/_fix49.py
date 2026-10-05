# -*- coding: utf-8 -*-
"""
0.4.9 硬化补丁（不换版本号）：
1. hxFavCost 增加「直读 GM 存储」兜底 —— 万一 usageStore 不在同作用域，
   也能拿到累计花费，而不是静默停在 Lv.1
2. 新增 hxFavMoney 自带格式化，去掉对 formatCost 的作用域依赖
3. paintFavCard 调用点加 try/catch，避免格式化异常导致整块挂不上
4. 说明文案措辞修正
"""
import os
import re
import sys

P = r"C:\Users\D_A\DoubaoWork\chats\2026-10-05\new-chat-4\海底小纵队·探矿鲸娘.user.js"
OUT = r"C:\Users\D_A\WorkBuddy\2026-10-05-13-53-42\_f49out.txt"
DRY = "--dry" in sys.argv

log = []
def w(x):
    log.append(str(x))

s = open(P, "rb").read().decode("utf-8").replace("\r\n", "\n")
orig_len = len(s)

# ── 1. hxFavCost 硬化 + hxFavMoney ────────────────────────
OLD_COST = (
    '  const hxFavCost = () => {\n'
    '    try {\n'
    '      const c = Number(usageStore.cost);\n'
    '      if (isFinite(c) && c > 0) return c;\n'
    '    } catch (error) { /* 忽略 */ }\n'
    '    return 0;\n'
    '  };\n'
)
NEW_COST = (
    '  const hxFavMoney = (value) => {\n'
    '    const n = Number(value) || 0;\n'
    '    if (n <= 0) return "\u00a50";\n'
    '    return "\u00a5" + (n < 0.01 ? n.toFixed(4) : n.toFixed(2));\n'
    '  };\n'
    '  const hxFavCost = () => {\n'
    '    try {\n'
    '      const c = Number(usageStore.cost);\n'
    '      if (isFinite(c) && c > 0) return c;\n'
    '    } catch (error) { /* 忽略 */ }\n'
    '    try {\n'
    '      const rawStats = _GM_getValue("hx_usage_stats_v1");\n'
    '      if (rawStats) {\n'
    '        const parsedStats = typeof rawStats === "string" ? JSON.parse(rawStats) : rawStats;\n'
    '        const c2 = Number(parsedStats && parsedStats.cost);\n'
    '        if (isFinite(c2) && c2 > 0) return c2;\n'
    '      }\n'
    '    } catch (error) { /* 忽略 */ }\n'
    '    return 0;\n'
    '  };\n'
)

# ── 2. 去掉 formatCost 依赖 ───────────────────────────────
OLD_LEFT = "const left = '\u7d2f\u8ba1 ' + formatCost(cost) + ' \u00b7 \u5df2\u89e3\u9501 '"
NEW_LEFT = "const left = '\u7d2f\u8ba1 ' + hxFavMoney(cost) + ' \u00b7 \u5df2\u89e3\u9501 '"
OLD_RIGHT = "' \u8fd8\u5dee ' + formatCost(Math.max(next.at - cost, 0))"
NEW_RIGHT = "' \u8fd8\u5dee ' + hxFavMoney(Math.max(next.at - cost, 0))"

# ── 3. 调用点加 try/catch ─────────────────────────────────
OLD_CALL = "    el.classList.toggle('is-open', hxFavOpen);\n    paintFavCard(el);\n    return true;\n"
NEW_CALL = ("    el.classList.toggle('is-open', hxFavOpen);\n"
            "    try { paintFavCard(el); } catch (error) { /* \u5ffd\u7565 */ }\n"
            "    return true;\n")

# ── 4. 说明文案 ───────────────────────────────────────────
OLD_NOTE = "' \u6761\u3002\u8bed\u5f55\u53ea\u5728\u5979\u7a7a\u95f2\u65f6\u6eda\u52a8\u64ad\u653e\uff1b\u53d6\u7684\u300c\u5c0f\u540d\u300d\u4f1a\u81ea\u52a8\u66ff\u6389\u8bed\u5f55\u91cc\u7684\u300c\u5c0f\u9cb8\u5a18\u300d\u3002</div>'"
NEW_NOTE = "' \u6761\u3002\u8bed\u5f55\u53ea\u5728\u5979\u7a7a\u95f2\u65f6\u6eda\u52a8\u64ad\u653e\uff1b\u53d6\u7684\u300c\u5c0f\u540d\u300d\u4f1a\u66ff\u8fdb\u6bcf\u4e00\u6761\u8bed\u5f55\u3002</div>'"

patches = [
    ("hxFavCost 硬化 + hxFavMoney", OLD_COST, NEW_COST, 1),
    ("meta-left 去 formatCost", OLD_LEFT, NEW_LEFT, 1),
    ("meta-right 去 formatCost", OLD_RIGHT, NEW_RIGHT, 1),
    ("paintFavCard 调用点 try", OLD_CALL, NEW_CALL, 1),
    ("说明文案措辞", OLD_NOTE, NEW_NOTE, 1),
]

w("=== 预检（共 %d 项）===" % len(patches))
fails = []
for name, old, new, exp in patches:
    cnt = s.count(old)
    flag = "OK" if cnt == exp else "NG"
    w("  [%s] %-26s 期望=%d 实际=%d" % (flag, name, exp, cnt))
    if cnt != exp:
        fails.append("%s: 期望 %d 实际 %d" % (name, exp, cnt))
        w("       << %s" % old[:120].replace("\n", "\\n"))

w("")
w("负向自检：fav 块内 formatCost 残留 = %d（应为 0）"
  % (s[s.index("const hxFavTierRows"): s.index("const mountFavCard")].count("formatCost")))
if s[s.index("const hxFavTierRows"): s.index("const mountFavCard")].count("formatCost") != 2:
    fails.append("fav 块内 formatCost 计数不符（预期恰好 2 处待替换）")

if fails:
    w("")
    w("!! 预检失败，未写入：")
    for f in fails:
        w("   - " + f)
    open(OUT, "w", encoding="utf-8").write("\n".join(log))
    sys.exit(1)

for name, old, new, exp in patches:
    s = s.replace(old, new)

seg = s[s.index("const hxFavTierRows"): s.index("const mountFavCard")]
w("")
w("写入后：fav 块内 formatCost 残留 = %d（应为 0）" % seg.count("formatCost"))
w("        hxFavMoney 定义 = %d，引用 = %d" % (s.count("const hxFavMoney = (value) => {"), s.count("hxFavMoney(")))
w("        _GM_getValue 兜底 = %d" % s.count('_GM_getValue("hx_usage_stats_v1")'))
if seg.count("formatCost") != 0:
    w("!! 仍有 formatCost 依赖，判定失败")
    open(OUT, "w", encoding="utf-8").write("\n".join(log))
    sys.exit(1)

out_bytes = s.replace("\n", "\r\n").encode("utf-8")
w("")
w("orig_chars=%d  new_chars=%d" % (orig_len, len(s)))
w("bytes=%d  crlf=%d  bare_lf=0" % (len(out_bytes), s.count("\n")))

if DRY:
    w("")
    w("DRY RUN —— 未写入文件")
else:
    open(P, "wb").write(out_bytes)
    w("")
    w("已写入：%s" % P)

open(OUT, "w", encoding="utf-8").write("\n".join(log))
