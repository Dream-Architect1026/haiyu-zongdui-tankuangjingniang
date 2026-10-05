# -*- coding: utf-8 -*-
"""
收口：修正 CSS 注入顺序。
同一份文档里，同特异性声明后注入者胜出；POPPER_CSS（暗色主题覆盖 + 超高 z-index）
必须在 Element Plus 全量 CSS 之后注入，否则会被其默认值盖掉。
"""
import io, os, shutil

P = r"C:\Users\D_A\DoubaoWork\chats\2026-10-05\new-chat-4\海底小纵队·探矿鲸娘.user.js"
OUT = r"C:\Users\D_A\WorkBuddy\2026-10-05-13-53-42\_fix13.txt"
LOG = []
def w(s=""):
    LOG.append(str(s)); print(s)

src = io.open(P, "r", encoding="utf-8", newline="").read()
orig_len = len(src)
ok = True

# ---- ① 摘掉模块顶层的提前注入 ----
old1 = "  GM_addStyle(POPPER_CSS);\n  const BOOTSTRAP_INTERVAL = 100;"
new1 = "  const BOOTSTRAP_INTERVAL = 100;"
n1 = src.count(old1)
if n1 == 1:
    src = src.replace(old1, new1)
    w("[OK ] ① 移除顶层提前注入的 POPPER_CSS  命中 1")
else:
    ok = False
    w("[!! ] ① 命中 %d 次（期望 1）" % n1)

# ---- ② 改到 Element Plus 之后注入 ----
old2 = "    if (elementPlusCss) GM_addStyle(elementPlusCss);"
new2 = ("    if (elementPlusCss) GM_addStyle(elementPlusCss);\n"
        "    /* 主题覆盖必须晚于 Element Plus 注入，否则同特异性声明会被默认值盖掉 */\n"
        "    GM_addStyle(POPPER_CSS);")
n2 = src.count(old2)
if n2 == 1:
    src = src.replace(old2, new2)
    w("[OK ] ② POPPER_CSS 改到 Element Plus 之后注入  命中 1")
else:
    ok = False
    w("[!! ] ② 命中 %d 次（期望 1）" % n2)

# ---- 写回 ----
if ok:
    bak = P + ".bak14"
    shutil.copy2(P, bak)
    w("")
    w("备份 -> %s" % os.path.basename(bak))
    with io.open(P, "w", encoding="utf-8", newline="") as f:
        f.write(src)
    w("写回完成: %d -> %d" % (orig_len, len(src)))
else:
    w("")
    w("!! 未命中，未写回")

# ---- 复核 ----
w("")
w("=== 复核：createShadowMountNode 最终形态 ===")
i = src.find("const createShadowMountNode")
j = src.find("const mountApp")
w(src[i:j].rstrip() if i > 0 and j > i else "!! 未找到")

w("")
w("=== 复核：注入点计数 ===")
w("  GM_addStyle(elementPlusCss) x%d" % src.count("GM_addStyle(elementPlusCss)"))
w("  GM_addStyle(POPPER_CSS)     x%d" % src.count("GM_addStyle(POPPER_CSS)"))
w("")
w("OK = %s" % ok)
with io.open(OUT, "w", encoding="utf-8") as f:
    f.write("\n".join(LOG))
