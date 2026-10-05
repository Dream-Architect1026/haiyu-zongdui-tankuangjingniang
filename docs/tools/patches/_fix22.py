# -*- coding: utf-8 -*-
"""fix22: 首页通知卡片化 / 答题页美化 / 协议页底部署名 / 鲁棒性加固"""
import io, os, re, shutil, sys

P = r"C:\Users\D_A\DoubaoWork\chats\2026-10-05\new-chat-4\海底小纵队·探矿鲸娘.user.js"
LOG = []
src = io.open(P, encoding="utf-8").read()
orig_len = len(src)

def sub_once(name, old, new, must=1):
    global src
    n = src.count(old)
    if n != must:
        LOG.append("!! %s: 命中 %d 次（期望 %d）" % (name, n, must))
        return False
    src = src.replace(old, new, 1)
    LOG.append("ok %s" % name)
    return True

# ============ 1. 新增 CSS 块（追加到 LAYOUT_CSS_PARTS 末尾） ============
CSS_LINES = [
    r'    + "\n/* ================= 首页通知（日志）卡片化 ================= */"',
    r'    + "\n.main-page .script-home .el-scrollbar__view>div{position:relative;margin:0 0 6px;padding:7px 9px 8px;border:1px solid var(--hx-line);border-radius:10px;background:linear-gradient(135deg,rgba(18,32,62,.62),rgba(12,22,44,.40));box-shadow:0 4px 14px rgba(2,8,24,.22);backdrop-filter:blur(8px) saturate(140%);-webkit-backdrop-filter:blur(8px) saturate(140%);transition:border-color .18s,background .18s}"',
    r'    + "\n.main-page .script-home .el-scrollbar__view>div:hover{border-color:rgba(56,226,255,.40);background:linear-gradient(135deg,rgba(22,40,74,.66),rgba(14,26,52,.46))}"',
    r'    + "\n.main-page .script-home .el-scrollbar__view>div:last-child{margin-bottom:0}"',
    r'    + "\n.main-page .script-home .el-text{display:inline;vertical-align:baseline}"',
    r'    + "\n.main-page .script-home .log-time{display:block;margin:0 0 3px;font-size:10.5px;line-height:1.4;letter-spacing:.5px;font-variant-numeric:tabular-nums;color:#7089a8!important;text-shadow:none}"',
    r'    + "\n.main-page .script-home .el-scrollbar__view>div>.el-text:not(.log-time){display:block;padding-left:9px;border-left:3px solid var(--hx-blue);border-radius:2px;font-size:12px;line-height:1.62;letter-spacing:.1px;overflow-wrap:anywhere;word-break:break-word;transition:border-color .18s}"',
    r'    + "\n.main-page .script-home .el-scrollbar__view>div>.el-text--primary{border-left-color:var(--hx-cyan);color:#d6e6ff!important}"',
    r'    + "\n.main-page .script-home .el-scrollbar__view>div>.el-text--success{border-left-color:#4ade80;color:#86efac!important}"',
    r'    + "\n.main-page .script-home .el-scrollbar__view>div>.el-text--warning{border-left-color:#ffc46b;color:#ffd79a!important}"',
    r'    + "\n.main-page .script-home .el-scrollbar__view>div>.el-text--danger{border-left-color:#ff7a7a;color:#ffb0b0!important}"',
    r'    + "\n.main-page .script-home .el-scrollbar__view>div>.el-text--info{border-left-color:#7f96b8;color:var(--hx-ink-dim)!important}"',
    r'    + "\n.main-page .script-home .log-divider{display:none!important;margin:0!important;height:0!important;border:none!important}"',
    r'    + "\n.main-page .script-home .log-action-link{display:inline-block;margin-left:3px;padding:0 7px;border:1px solid rgba(56,226,255,.45);border-radius:20px;color:var(--hx-cyan)!important;font-size:11px;line-height:17px;text-decoration:none;background:rgba(56,226,255,.10);transition:background .18s,color .18s}"',
    r'    + "\n.main-page .script-home .log-action-link:hover{background:rgba(56,226,255,.24);color:#fff!important}"',
    r'    + "\n/* ================= 答题页美化 ================= */"',
    r'    + "\n.main-page .ai-config{display:grid;grid-template-columns:1fr;gap:6px;padding:9px 10px!important;margin-bottom:8px}"',
    r'    + "\n.main-page .answer-legend{display:flex;flex-wrap:wrap;gap:6px;justify-content:center!important;margin:0 0 8px;padding:7px 8px;border:1px solid var(--hx-line);border-radius:10px;background:rgba(6,14,30,.42)}"',
    r'    + "\n.main-page .answer-legend>span{position:relative;padding:1px 8px 1px 16px;border-radius:20px;font-size:10.5px;line-height:17px;white-space:nowrap;background:rgba(255,255,255,.05);border:1px solid rgba(120,190,255,.16)}"',
    r'    + "\n.main-page .answer-legend>span:before{content:\'\';position:absolute;left:6px;top:50%;transform:translateY(-50%);width:6px;height:6px;border-radius:50%;background:currentColor;box-shadow:0 0 6px currentColor}"',
    r'    + "\n.main-page .answer-legend>.answer-result--success{color:#4ade80!important;border-color:rgba(74,222,128,.34)}"',
    r'    + "\n.main-page .answer-legend>.answer-result--searching{color:var(--hx-cyan)!important;border-color:rgba(56,226,255,.34)}"',
    r'    + "\n.main-page .answer-legend>.answer-result--pending{color:#a8bcd8!important;border-color:rgba(168,188,216,.28)}"',
    r'    + "\n.main-page .answer-legend>.answer-result--error{color:#ff8a8a!important;border-color:rgba(255,138,138,.34)}"',
    r'    + "\n.main-page .question_table{border:1px solid var(--hx-line);border-radius:12px;background:rgba(8,16,34,.30);padding:0 0 2px}"',
    r'    + "\n.main-page .question-list{border-radius:12px;overflow:hidden}"',
    r'    + "\n.main-page .question-list .el-table__cell{padding:6px 8px!important;font-size:11.5px;line-height:1.6}"',
    r'    + "\n.main-page .question-list th.el-table__cell{position:sticky;top:0;z-index:2;backdrop-filter:blur(8px);-webkit-backdrop-filter:blur(8px)}"',
    r'    + "\n.main-page .question-list .cell{overflow-wrap:anywhere;word-break:break-word}"',
    r'    + "\n.main-page .answer-result{display:inline-block;font-size:11.5px;line-height:1.6}"',
    r'    + "\n.main-page .answer-result--searching{animation:hxPulse 1.4s ease-in-out infinite}"',
    r'    + "\n@keyframes hxPulse{0%,100%{opacity:.55}50%{opacity:1}}"',
    r'    + "\n/* ================= 协议页：底部署名 ================= */"',
    r'    + "\n.main-page .guide-page{padding-bottom:10px!important}"',
    r'    + "\n.main-page .guide-footer{margin:10px 0 2px;padding:11px 12px;border:1px solid var(--hx-line);border-radius:12px;background:linear-gradient(120deg,rgba(56,226,255,.12),rgba(155,107,255,.12));text-align:center;box-shadow:0 6px 18px rgba(2,8,24,.26);backdrop-filter:blur(10px) saturate(140%);-webkit-backdrop-filter:blur(10px) saturate(140%)}"',
    r'    + "\n.main-page .guide-sign{margin:0;font-size:11.5px;line-height:1.7;letter-spacing:.3px;color:var(--hx-ink)!important}"',
    r'    + "\n.main-page .guide-sign strong{color:var(--hx-cyan)!important;font-weight:700;letter-spacing:.6px;text-shadow:0 0 12px rgba(56,226,255,.45)}"',
    r'    + "\n.main-page .guide-meta{margin:5px 0 0;font-size:10px;line-height:1.6;letter-spacing:.4px;color:var(--hx-ink-dim)!important;opacity:.9}"',
    r'    + "\n/* ================= 鲁棒性 ================= */"',
    r'    + "\n.main-page .el-card{max-height:calc(100vh - 24px);max-height:calc(100dvh - 24px)}"',
    r'    + "\n.main-page .el-tab-pane,.main-page .guide-page,.main-page .setting{-webkit-overflow-scrolling:touch}"',
]

anchor_css = r'''    + "\n.main-page .ai-config .el-select,.main-page .ai-config .el-input{justify-self:center;width:100%!important}"
  );'''
sub_once("CSS 块插入", anchor_css, r'''    + "\n.main-page .ai-config .el-select,.main-page .ai-config .el-input{justify-self:center;width:100%!important}"
''' + "\n".join(CSS_LINES) + r'''
  );''')

# ============ 2. 协议页底部署名（注意静态 vnode 计数 2 -> 3）============
FOOTER = ('<footer class="guide-footer"><p class="guide-sign">Developed by <strong>X.H</strong>（星虹）</p>'
          '<p class="guide-meta">海底小纵队 · 探矿鲸娘 · v0.4.0 · MIT License</p></footer>')
anchor_guide = "发现问题可通过项目仓库反馈。</p></li></ol>', 2);"
sub_once("协议页 footer 注入 + 计数 2->3",
         anchor_guide,
         "发现问题可通过项目仓库反馈。</p></li></ol>" + FOOTER + "', 3);")

# ============ 3. 鲁棒性：单实例守卫 + 样式兜底 ============
anchor_consts = '''  const BOOTSTRAP_INTERVAL = 100;
  const COMPLETE_READY_STATE = "complete";'''
new_consts = '''  const BOOTSTRAP_INTERVAL = 100;
  const BOOTSTRAP_MAX_ATTEMPTS = 200;
  const COMPLETE_READY_STATE = "complete";
  const PANEL_MARK_ATTR = "data-hx-panel";
  const CAN_USE_ADOPTED_SHEETS = (() => {
    try {
      if (typeof CSSStyleSheet !== "function" || !("replaceSync" in CSSStyleSheet.prototype))
        return false;
      const probe = document.createElement("div").attachShadow({ mode: "open" });
      return Array.isArray(probe.adoptedStyleSheets);
    } catch (error) {
      return false;
    }
  })();
  const documentStyleInjected = /* @__PURE__ */ Object.create(null);
  const injectDocumentStyle = (key, cssText) => {
    if (!cssText || documentStyleInjected[key])
      return;
    documentStyleInjected[key] = true;
    GM_addStyle(cssText);
  };
  const applyShadowStyles = (shadowRoot, sheets) => {
    const usable = sheets.filter(Boolean);
    if (CAN_USE_ADOPTED_SHEETS) {
      shadowRoot.adoptedStyleSheets = usable.map(createStyleSheet);
      return;
    }
    const style = document.createElement("style");
    style.textContent = usable.join("\\n");
    shadowRoot.appendChild(style);
  };'''
sub_once("鲁棒性常量与样式兜底", anchor_consts, new_consts)

anchor_cssfn = '''  const createStyleSheet = (cssText) => {
    const sheet = new CSSStyleSheet();
    sheet.replaceSync(cssText);
    return sheet;
  };'''
new_cssfn = '''  const createStyleSheet = (cssText) => {
    const sheet = new CSSStyleSheet();
    try {
      sheet.replaceSync(cssText);
    } catch (error) {
      console.error("[探矿鲸娘] CSS 解析失败：", error);
    }
    return sheet;
  };'''
sub_once("createStyleSheet 容错", anchor_cssfn, new_cssfn)

anchor_mount = '''  const createShadowMountNode = () => {
    const shadowHost = document.createElement("div");
    const mountNode = document.createElement("div");
    const shadowRoot = shadowHost.attachShadow({ mode: "closed" });
    document.body.append(shadowHost);
    shadowRoot.appendChild(mountNode);
    const elementPlusCss = _GM_getResourceText(ELEMENT_PLUS_STYLE_RESOURCE) ?? "";
    /* el-select 下拉弹层默认 Teleport 到 document.body（在 closed shadow root 之外），
       拿不到 adoptedStyleSheets，必须把同一份 Element Plus 样式补注入到 document 级 */
    if (elementPlusCss) GM_addStyle(elementPlusCss);
    /* 主题覆盖必须晚于 Element Plus 注入，否则同特异性声明会被默认值盖掉 */
    GM_addStyle(POPPER_CSS);
    shadowRoot.adoptedStyleSheets = [
      createStyleSheet(elementPlusCss),
      createStyleSheet(layoutCss)
    ];
    return mountNode;
  };'''
new_mount = '''  const createShadowMountNode = () => {
    const shadowHost = document.createElement("div");
    shadowHost.setAttribute(PANEL_MARK_ATTR, "1");
    const mountNode = document.createElement("div");
    const shadowRoot = shadowHost.attachShadow({ mode: "closed" });
    document.body.append(shadowHost);
    shadowRoot.appendChild(mountNode);
    const elementPlusCss = _GM_getResourceText(ELEMENT_PLUS_STYLE_RESOURCE) ?? "";
    /* el-select 下拉弹层默认 Teleport 到 document.body（在 closed shadow root 之外），
       拿不到 adoptedStyleSheets，必须把同一份 Element Plus 样式补注入到 document 级。
       用 key 去重，避免重复挂载时把同一份样式灌进 document 多次。 */
    injectDocumentStyle("element-plus", elementPlusCss);
    /* 主题覆盖必须晚于 Element Plus 注入，否则同特异性声明会被默认值盖掉 */
    injectDocumentStyle("popper", POPPER_CSS);
    applyShadowStyles(shadowRoot, [elementPlusCss, layoutCss]);
    return mountNode;
  };'''
sub_once("单实例标记 + 去重注入", anchor_mount, new_mount)

anchor_timer = '''  const timer = setInterval(() => {
    if (document.readyState !== COMPLETE_READY_STATE)
      return;
    clearInterval(timer);
    mountApp();
  }, BOOTSTRAP_INTERVAL);'''
new_timer = '''  const isPanelMounted = () => Boolean(document.querySelector("[" + PANEL_MARK_ATTR + "]"));
  let bootstrapAttempts = 0;
  const timer = setInterval(() => {
    if (document.readyState !== COMPLETE_READY_STATE) {
      bootstrapAttempts += 1;
      /* 兜底：页面迟迟不到 complete（资源被墙等）也强行挂载，避免定时器永久空转 */
      if (bootstrapAttempts < BOOTSTRAP_MAX_ATTEMPTS)
        return;
    }
    clearInterval(timer);
    if (isPanelMounted())
      return;
    try {
      mountApp();
    } catch (error) {
      console.error("[探矿鲸娘] 面板挂载失败：", error);
    }
  }, BOOTSTRAP_INTERVAL);'''
sub_once("挂载守卫与超时兜底", anchor_timer, new_timer)

# ============ 写回 ============
bad = [x for x in LOG if x.startswith("!!")]
if bad:
    print("\n".join(LOG))
    print("ABORT: 有未命中项，未写盘")
    sys.exit(1)

shutil.copy2(P, P + ".bak-fix22")
with io.open(P, "w", encoding="utf-8", newline="") as f:
    f.write(src)

LOG.append("bytes: %d -> %d" % (orig_len, len(src)))
LOG.append("backup: %s.bak-fix22" % os.path.basename(P))
print("\n".join(LOG))
