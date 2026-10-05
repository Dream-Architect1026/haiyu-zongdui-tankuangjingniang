# -*- coding: utf-8 -*-
"""
修复"模型下拉列表点不出来"的根因：
  Element Plus 的 el-select 弹层默认 Teleport 到 document.body，
  而脚本用的是 closed Shadow DOM，Element Plus 的 CSS 只进了
  shadowRoot.adoptedStyleSheets —— 体外弹层拿不到任何定位/外观样式。
修法：把同一份 Element Plus CSS 追加注入到 document 级。
"""
import io, os, shutil

P = r"C:\Users\D_A\DoubaoWork\chats\2026-10-05\new-chat-4\海底小纵队·探矿鲸娘.user.js"
OUT = r"C:\Users\D_A\WorkBuddy\2026-10-05-13-53-42\_fix12.txt"
LOG = []
def w(s=""):
    LOG.append(str(s)); print(s)

src = io.open(P, "r", encoding="utf-8", newline="").read()
orig_len = len(src)
w("原始字符数: %d" % orig_len)
w("")

ok = True

# ---------- ① document 级注入 Element Plus 全量 CSS ----------
old1 = '''    shadowRoot.adoptedStyleSheets = [
      createStyleSheet(_GM_getResourceText(ELEMENT_PLUS_STYLE_RESOURCE) ?? ""),
      createStyleSheet(layoutCss)
    ];'''
new1 = '''    const elementPlusCss = _GM_getResourceText(ELEMENT_PLUS_STYLE_RESOURCE) ?? "";
    /* el-select 下拉弹层默认 Teleport 到 document.body（在 closed shadow root 之外），
       拿不到 adoptedStyleSheets，必须把同一份 Element Plus 样式补注入到 document 级 */
    if (elementPlusCss) GM_addStyle(elementPlusCss);
    shadowRoot.adoptedStyleSheets = [
      createStyleSheet(elementPlusCss),
      createStyleSheet(layoutCss)
    ];'''

n1 = src.count(old1)
if n1 == 1:
    src = src.replace(old1, new1)
    w("[OK ] ① Element Plus CSS 追加注入 document 级（供养在 body 下的弹层）  命中 1")
else:
    ok = False
    w("[!! ] ① 目标段命中 %d 次（期望 1）  << 未替换" % n1)

# ---------- ② 弹层补字体（document 级继承不到 --app-font-family） ----------
old2 = '".el-select__popper,.el-popper,.el-select-dropdown{z-index:2147483000!important}",'
new2 = ('".el-select__popper,.el-popper,.el-select-dropdown{z-index:2147483000!important;'
        'font-family:-apple-system,BlinkMacSystemFont,\'Segoe UI\',Roboto,\'Helvetica Neue\',Arial,sans-serif}",')
n2 = src.count(old2)
if n2 == 1:
    src = src.replace(old2, new2)
    w("[OK ] ② 弹层补字体声明  命中 1")
else:
    ok = False
    w("[!! ] ② 字体声明命中 %d 次（期望 1）" % n2)

# ---------- 写回 ----------
if ok:
    bak = P + ".bak13"
    shutil.copy2(P, bak)
    w("")
    w("备份 -> %s" % os.path.basename(bak))
    with io.open(P, "w", encoding="utf-8", newline="") as f:
        f.write(src)
    w("写回完成: %d -> %d" % (orig_len, len(src)))
else:
    w("")
    w("!! 有未命中项，未写回")

# ---------- 复核 ----------
w("")
w("=== 复核：createShadowMountNode ===")
i = src.find("const createShadowMountNode")
j = src.find("const mountApp")
if i > 0 and j > i:
    w(src[i:j].rstrip())

w("")
w("=== 复核：document 级注入点计数 ===")
w("  GM_addStyle(elementPlusCss)      x%d" % src.count("GM_addStyle(elementPlusCss)"))
w("  GM_addStyle(POPPER_CSS)          x%d" % src.count("GM_addStyle(POPPER_CSS)"))
w("  adoptedStyleSheets               x%d" % src.count("adoptedStyleSheets"))
w("  ELEMENT_PLUS_STYLE_RESOURCE 引用 x%d" % src.count("ELEMENT_PLUS_STYLE_RESOURCE"))
w("")
w("OK = %s" % ok)
with io.open(OUT, "w", encoding="utf-8") as f:
    f.write("\n".join(LOG))
