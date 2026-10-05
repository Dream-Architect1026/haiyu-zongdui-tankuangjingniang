# -*- coding: utf-8 -*-
"""核心修复：科技风 CSS 从「主文档 GM_addStyle 注入」改为「并入 layoutCss 走 shadow root」。

原因：面板挂载在 attachShadow({mode:"closed"}) 里，shadow DOM 有样式隔离，
      注入 document.head 的样式对 shadow 内元素完全无效；且大体积主文档注入
      会与页面脚本产生冲突（表现为 (intermediate value)(...) is not a function）。
做法：HX_CSS 保留为分片数组，但不再单独注入；改为与旧 layoutCss 拼接后
      由 createShadowMountNode 的 adoptedStyleSheets 注入。
"""
import io, re, json

P = r"C:\Users\D_A\DoubaoWork\chats\2026-10-05\new-chat-4\海底小纵队·探矿鲸娘.user.js"
with io.open(P, encoding="utf-8") as f:
    src = f.read()

# 1) 删除旧的独立注入器调用（(e=>{...})(HX_CSS) 那一行）
inj = re.search(r"\(e=>\{if\(typeof GM_addStyle.*?\}\)\(HX_CSS\)", src, re.S)
if inj:
    src = src[:inj.start()] + src[inj.end():]
    src = src.replace("\n\n\n", "\n\n", 1)
    print("[1] removed standalone injector")
else:
    print("[1] injector not found (maybe already removed)")

# 2) 取出 HX_CSS 分片内容
m = re.search(r"  const HX_CSS = \[([\s\S]*?)\]\.join\(\"\"\);", src)
if m:
    chunks = re.findall(r'^\s*("(?:[^"\\]|\\.)*"),?\s*$', m.group(1), re.M)
    css = "".join(json.loads(c) for c in chunks)
    print("[2] css recovered: %d chars, %d chunks" % (len(css), len(chunks)))
else:
    raise SystemExit("HX_CSS array not found")

# 3) 把 HX_CSS 改名并移到 layoutCss 定义之后，拼成 shadow 样式
# 3a. 从原位置摘掉 HX_CSS 块
a = src.find("  const HX_CSS = [")
b = src.find('].join("");', a) + len('].join("");')
block = src[a:b]
src = src[:a] + src[b:]

# 3b. 重命名为 HX_STYLE_PARTS（保留分片形式，避免超长行）
new_block = block.replace("const HX_CSS = [", "const HX_STYLE_PARTS = [").replace(
    '].join("");', '];')

# 3c. 在 layoutCss 定义前插入，并让 layoutCss 合并两者
i = src.find("  const layoutCss = '")
j = src.find("';\n", i)
old_layout = src[i + len("  const layoutCss = '"):j]
print("[3] old layoutCss: %d chars" % len(old_layout))

merged = old_layout + "\\n" + css
js_merged = merged.replace("\\", "\\\\").replace("'", "\\'").replace("\n", "\\n")

# 用「分片 + 拼接」方式构造 layoutCss，避免单行过长
CH = 1200
parts = [js_merged[k:k+CH] for k in range(0, len(js_merged), CH)]
layout_block = (
    "  const LAYOUT_CSS_PARTS = [\n"
    + ",\n".join('    "%s"' % p for p in parts)
    + "\n  ];\n"
    + "  const layoutCss = LAYOUT_CSS_PARTS.join(\"\");\n"
)

src = src[:i] + new_block + "\n" + layout_block + src[j + len("';\n"):]
print("[3] merged layoutCss: %d chars in %d parts" % (len(merged), len(parts)))

with io.open(P, "w", encoding="utf-8", newline="") as f:
    f.write(src)

# 校验
with io.open(P, encoding="utf-8") as f:
    chk = f.read()
print("\n--- verify ---")
print("HX_CSS 残留:", chk.count("HX_CSS"))
print("HX_STYLE_PARTS:", chk.count("HX_STYLE_PARTS"))
print("LAYOUT_CSS_PARTS:", chk.count("LAYOUT_CSS_PARTS"))
print("独立注入器:", chk.count("(HX_CSS)"))
print("adoptedStyleSheets 仍在:", chk.count("adoptedStyleSheets"))
lines = chk.split("\n")
big = sorted(((len(l), n + 1) for n, l in enumerate(lines)), reverse=True)[:3]
print("最长行:", ", ".join("#%d=%d" % (n, ln) for ln, n in big))
