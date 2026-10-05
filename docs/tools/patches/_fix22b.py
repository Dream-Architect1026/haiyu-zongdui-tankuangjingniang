# -*- coding: utf-8 -*-
"""fix22b: 复原 CRLF 并核对 footer / vnode 计数"""
import io, re

P = r"C:\Users\D_A\DoubaoWork\chats\2026-10-05\new-chat-4\海底小纵队·探矿鲸娘.user.js"

# 1) 以二进制读入，统一回 CRLF
raw = open(P, "rb").read()
n_before = raw.count(b"\r\n")
raw = raw.replace(b"\r\n", b"\n").replace(b"\n", b"\r\n")
open(P, "wb").write(raw)

src = io.open(P, encoding="utf-8", newline="").read()
out = []
out.append("CRLF restored: %d -> %d" % (n_before, raw.count(b"\r\n")))
out.append("bytes=%d" % len(raw))
out.append("")

# 2) 核对静态 vnode 计数与 footer
m = re.search(r"createStaticVNode\((.{0,80})", src)
out.append("guide footer 出现次数 = %d" % src.count("guide-footer"))
mm = re.search(r"guide-footer.*?', (\d)\);", src, re.S)
out.append("guide static vnode 计数 = %s" % (mm.group(1) if mm else "未匹配"))
out.append("guide-footer 片段 = %s" % (re.search(r"<footer class=\"guide-footer\">.*?</footer>', \d\);", src, re.S).group(0)[:220] if re.search(r"<footer class=\"guide-footer\">.*?</footer>', \d\);", src, re.S) else "无"))
out.append("")

# 3) 修复前的静态 vnode 列表（确认只有 guide 从 2 变 3）
out.append("所有 createStaticVNode 计数：")
for mm in re.finditer(r"createStaticVNode\('(.{0,40}).*?', (\d)\)", src, re.S):
    head = mm.group(1).replace("\n", " ")[:34]
    out.append("   count=%s  head=%s" % (mm.group(2), head))
out.append("")

# 4) 鲁棒性新增点
for k in ["BOOTSTRAP_MAX_ATTEMPTS", "PANEL_MARK_ATTR", "CAN_USE_ADOPTED_SHEETS",
          "documentStyleInjected", "applyShadowStyles", "isPanelMounted", "injectDocumentStyle"]:
    out.append("%-24s = %d" % (k, src.count(k)))
out.append("")
out.append("字面 \\\\n 残留 = %d" % src.count("\\n"))

open(r"C:\Users\D_A\WorkBuddy\2026-10-05-13-53-42\_fix22b.txt", "w", encoding="utf-8").write("\n".join(out))
print("done")
