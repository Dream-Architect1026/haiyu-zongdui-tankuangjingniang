# -*- coding: utf-8 -*-
import io, os, shutil

P = r"C:\Users\D_A\DoubaoWork\chats\2026-10-05\new-chat-4\海底小纵队·探矿鲸娘.user.js"
BAK = P + ".bak9"
shutil.copyfile(P, BAK)

src = io.open(P, encoding="utf-8").read()
log = []
log.append("备份: %s" % os.path.basename(BAK))
log.append("修改前字符数: %d" % len(src))
log.append("")

def rep(old, new, tag, expect=1):
    global src
    n = src.count(old)
    if n != expect:
        log.append("[!! 跳过] %s —— 命中 %d 次（期望 %d）" % (tag, n, expect))
        return False
    src = src.replace(old, new, expect)
    log.append("[OK ] %s" % tag)
    return True

ANCHOR = '  const layoutCss = LAYOUT_CSS_PARTS.join("");'

PATCH = ANCHOR + '''

  // ── 下拉/提示弹层补丁（关键）────────────────────────────────────────
  // Element Plus 的 el-select 弹层默认 Teleport 到 document.body，位于 shadow root 之外：
  //   ① shadow root 的 adoptedStyleSheets 对它完全无效 → 必须 GM_addStyle 注入 document 级样式；
  //   ② 它的 z-index 只有 2000 上下，而 .main-page 是 z-index:100003 → 弹层被不透明面板盖住，
  //      表现就是「点模型选择框没有任何下拉列表」。这里强制一个超高 z-index 顶到最上层。
  const POPPER_CSS = [
    ".el-select__popper,.el-popper,.el-select-dropdown{z-index:2147483000!important}",
    ".el-select__popper{background:transparent!important;border:none!important}",
    ".el-select-dropdown,.el-popper.is-light{border:1px solid rgba(120,190,255,.18)!important;border-radius:10px!important;background:rgba(14,26,50,.96)!important;color:#e8f4ff!important;backdrop-filter:blur(14px);-webkit-backdrop-filter:blur(14px);box-shadow:0 18px 48px rgba(2,8,24,.55)!important}",
    ".el-select-dropdown__item{height:32px;line-height:32px;color:#9fb4d0!important;font-size:13px}",
    ".el-select-dropdown__item.is-hovering{background:rgba(56,226,255,.14)!important;color:#fff!important}",
    ".el-select-dropdown__item.is-selected{color:#38e2ff!important;font-weight:600}",
    ".el-popper__arrow::before{background:rgba(14,26,50,.96)!important;border-color:rgba(120,190,255,.18)!important}",
    ".el-popper.is-dark{background:rgba(8,16,34,.96)!important;border:1px solid rgba(120,190,255,.18)!important;color:#e8f4ff!important}"
  ].join("");
  GM_addStyle(POPPER_CSS);'''

rep(ANCHOR, PATCH, "① 注入 document 级弹层样式 + 超高 z-index")

io.open(P, "w", encoding="utf-8", newline="").write(src)

log.append("")
log.append("修改后字符数: %d" % len(src))
log.append("")
log.append("=== 复核 ===")
for pat in ["2147483000", "GM_addStyle(POPPER_CSS)", 'z-index:100003', "deepseek-chat",
            "deepseek-v4.1-flash", "deepseek-v4-pro", "deepseek-flash"]:
    log.append("  %-32s x%d" % (pat, src.count(pat)))

io.open(r"C:\Users\D_A\WorkBuddy\2026-10-05-13-53-42\_fix7.txt", "w", encoding="utf-8").write("\n".join(log))
print("ok")
