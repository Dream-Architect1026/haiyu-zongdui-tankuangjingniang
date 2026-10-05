# -*- coding: utf-8 -*-
import io, shutil

P = r"C:\Users\D_A\DoubaoWork\chats\2026-10-05\new-chat-4\海底小纵队·探矿鲸娘.user.js"
src = io.open(P, "r", encoding="utf-8").read()
log = []

def rep(old, new, tag, expect=1):
    global src
    n = src.count(old)
    log.append("[%s] count=%d" % (tag, n))
    assert n == expect, "unexpected count for " + tag
    src = src.replace(old, new)

shutil.copyfile(P, P + ".bak-fix21")
log.append("backup -> .bak-fix21")

# ------------------------------------------------------------------
# 逐条 CSS（全部用单引号，避免 JS 字符串转义）
# ------------------------------------------------------------------
r = []
A = r.append

# ---- 1) 外壳：Hero 钉死 + 单滚动区 ----
A('.main-page .el-card__header{flex:0 0 auto;position:relative;z-index:3}')
A('.main-page .el-card__body{flex:1 1 auto;min-height:0;overflow:hidden!important}')
A('.main-page .card_content{display:flex;flex-direction:column;height:100%;min-height:0;margin:0 auto;box-sizing:border-box;max-width:100%}')
A('.main-page .demo-tabs{display:flex!important;flex-direction:column;height:100%;min-height:0}')
A('.main-page .demo-tabs>.el-tabs__header{flex:0 0 auto;margin:0 0 8px!important}')
A('.main-page .demo-tabs>.el-tabs__content{flex:1 1 auto;min-height:0;display:flex;flex-direction:column;overflow:hidden;padding:0!important}')
A('.main-page .demo-tabs>.el-tabs__content>.el-tab-pane{flex:1 1 auto;min-height:0;display:flex;flex-direction:column;overflow-y:auto;overflow-x:hidden;padding:0 1px 2px 1px}')
A('.main-page .el-tab-pane>.el-scrollbar,.main-page .el-tab-pane>.setting,.main-page .el-tab-pane>.guide-page,.main-page .el-tab-pane>.question_table{flex:1 1 auto;min-height:0}')

# ---- 2) 去掉右侧竖向滚动条（保留滚轮滚动 + 表格横向条）----
A('.main-page .el-card__body,.main-page .el-tab-pane,.main-page .setting,.main-page .el-scrollbar__wrap{scrollbar-width:none}')
A('.main-page .el-card__body::-webkit-scrollbar,.main-page .el-tab-pane::-webkit-scrollbar,.main-page .setting::-webkit-scrollbar,.main-page .script-home .el-scrollbar__wrap::-webkit-scrollbar{width:0!important;height:0!important;display:none!important}')
A('.main-page .el-scrollbar__bar.is-vertical{display:none!important}')

# ---- 3) 首页：日志区撑满下方空白 ----
A('.main-page .script-home{flex:1 1 auto;min-height:0;display:flex;flex-direction:column;padding-top:2px}')
A('.main-page .script-home>.el-scrollbar.log{flex:1 1 auto;min-height:0;max-height:none!important;height:auto!important}')
A('.main-page .script-home .el-scrollbar__wrap{height:100%;overflow-x:hidden}')
A('.main-page .script-home .el-scrollbar__view{padding:0 2px 2px 0}')
A('.main-page .log-divider{margin:3px 0!important;opacity:.45}')

# ---- 4) 设置页：撑满 + 美化 ----
A('.main-page .setting{flex:1 1 auto;min-height:0;overflow-y:auto;overflow-x:hidden;display:flex;flex-direction:column;gap:10px;padding:2px 1px 8px 1px;margin-top:0!important;font-size:12px}')
A('.main-page .setting>div{flex:0 0 auto;display:flex;flex-direction:column;gap:8px;padding:10px 11px;border:1px solid var(--hx-line);border-radius:12px;background:var(--hx-glass);box-shadow:0 6px 18px rgba(2,8,24,.26);backdrop-filter:blur(10px) saturate(140%);-webkit-backdrop-filter:blur(10px) saturate(140%)}')
A('.main-page .setting .el-divider{margin:0!important;background:transparent!important;border-top:1px solid var(--hx-line)!important}')
A('.main-page .setting-section-title{display:inline-flex;align-items:center;gap:6px;font-size:12.5px;font-weight:700;color:var(--hx-cyan)!important;letter-spacing:.4px}')
A('.main-page .setting-section-title:before{content:"";width:3px;height:12px;border-radius:2px;background:linear-gradient(180deg,var(--hx-cyan),var(--hx-violet));box-shadow:0 0 8px rgba(56,226,255,.6)}')
A('.main-page .setting-checkbox{display:flex;align-items:center;height:28px;margin:0!important;padding:0 9px;border:1px solid var(--hx-line);border-radius:9px;background:rgba(6,14,30,.42);transition:border-color .2s,background .2s}')
A('.main-page .setting-checkbox:hover{border-color:rgba(56,226,255,.42);background:rgba(56,226,255,.08)}')
A('.main-page .setting .el-checkbox__label{font-size:12px;color:var(--hx-ink)!important}')
A('.main-page .setting .el-form-item{display:flex;align-items:center;margin:0!important}')
A('.main-page .setting .el-form-item__label{flex:1 1 auto;justify-content:flex-start!important;height:auto!important;line-height:1.5!important;padding:0!important;color:var(--hx-ink-dim)!important;font-size:12px}')
A('.main-page .setting .el-form-item__content{flex:0 0 auto;margin-left:8px!important}')
A('.main-page .setting .el-input-number{width:112px!important}')

# ---- 5) 教程 / 答题页也撑满，并把若干内容居中 ----
A('.main-page .guide-page{max-height:none!important}')
A('.main-page .answer-legend{justify-content:center!important}')
A('.main-page .ai-config .el-select,.main-page .ai-config .el-input{justify-self:center;width:100%!important}')

js_lines = []
js_lines.append('  // ---- v0.5 UI: pinned hero / panes fill remaining space / no vertical scrollbar / centered ----')
js_lines.append('  LAYOUT_CSS_PARTS.push(')
js_lines.append('    "\\n/* ==== v0.5 UI: pinned hero, fill panes, no vertical scrollbar, centered ==== */"')
for i, line in enumerate(r):
    suffix = '' if i == len(r) - 1 else ''
    js_lines.append('    + "\\n' + line + '"' + suffix)
js_lines.append('  );')
js_lines.append('')
block = "\n".join(js_lines) + "\n"

anchor = '  const layoutCss = LAYOUT_CSS_PARTS.join("");'
assert src.count(anchor) == 1, "join anchor not unique"
src = src.replace(anchor, block + anchor)
log.append("[ui-block] inserted %d css lines before join" % len(r))

io.open(P, "w", encoding="utf-8").write(src)
log.append("written utf-8 bytes = %d" % len(src.encode("utf-8")))
io.open(r"C:\Users\D_A\WorkBuddy\2026-10-05-13-53-42\_fix21.txt", "w", encoding="utf-8").write("\n".join(log))
print("ok")
