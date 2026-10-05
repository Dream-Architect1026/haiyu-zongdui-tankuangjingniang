# -*- coding: utf-8 -*-
"""fix41: 0.4.3 —— 自报版本 + 旧版面板清场 + 可见版本角标"""
import io, sys

P = r"C:\Users\D_A\DoubaoWork\chats\2026-10-05\new-chat-4\海底小纵队·探矿鲸娘.user.js"
src = io.open(P, "r", encoding="utf-8", newline="").read()
orig = src

def sub_once(old, new, tag):
    global src
    n = src.count(old)
    assert n == 1, "%s : 期望 1 处，实际 %d 处" % (tag, n)
    src = src.replace(old, new, 1)
    print("[OK] %s" % tag)

def crlf(s):
    return s.replace("\r\n", "\n").replace("\n", "\r\n")

# ---------- A. 版本号 ----------
sub_once("// @version      0.4.2", "// @version      0.4.3", "A @version -> 0.4.3")
sub_once("面板 0.4.2 \\u00b7", "面板 0.4.3 \\u00b7", "A2 通知日志 -> 0.4.3")
sub_once("探矿鲸娘 · v0.4.2 · MIT License", "探矿鲸娘 · v0.4.3 · MIT License", "A3 教程页页脚 -> 0.4.3")

# ---------- B. 构建标识常量 ----------
sub_once(
    "  const buildUsageBarHtml = (store, peak) => {",
    '  const HX_BUILD = "0.4.3";\r\n'
    '  const HX_RUN_ID = "hx" + Date.now().toString(36) + Math.random().toString(36).slice(2, 6);\r\n'
    "  let hxShadow = null;\r\n"
    "  const buildUsageBarHtml = (store, peak) => {",
    "B 注入 HX_BUILD / HX_RUN_ID / hxShadow")

# ---------- C. 用量栏版本角标 ----------
sub_once(
    "      + '<span class=\"usage-rate\">' + formatRate(store) + \"</span>\"\r\n      + \"</div>\";",
    "      + '<span class=\"usage-rate\">' + formatRate(store) + \"</span>\"\r\n"
    "      + '<span class=\"usage-build\">v' + HX_BUILD + \"</span>\"\r\n"
    "      + \"</div>\";",
    "C 用量栏加版本角标")

# ---------- D. 角标 CSS ----------
sub_once(
    '    + "\\n.main-page .usage-sub{display:flex;align-items:center;justify-content:space-between;gap:6px;margin-top:5px;padding:0 2px}"',
    '    + "\\n.main-page .usage-sub{display:flex;align-items:center;justify-content:flex-start;gap:6px;margin-top:5px;padding:0 2px}"\r\n'
    '    + "\\n.main-page .usage-build{margin-left:auto;font-size:9.5px;line-height:15px;letter-spacing:.02em;color:rgba(150,215,255,.5);white-space:nowrap}"',
    "D 角标 CSS（usage-sub 改 flex-start + .usage-build）")

# ---------- E. 清场 + 自诊断 ----------
SWEEP = '''  const HX_SWEEP_DELAYS = [0, 600, 1500, 3200];
  const ownPanelHost = () => document.querySelector("[" + PANEL_MARK_ATTR + '="' + HX_RUN_ID + '"]');
  const hostsShadowTree = (el) => {
    try {
      el.attachShadow({ mode: "open" });
      return false;
    } catch (error) {
      return true;
    }
  };
  /* 旧版（0.4.0）的面板宿主是「无任何属性的裸 div」，且旧版没有去重保护。
     新旧两份同时存在时会各挂一个面板、旧面板压在新面板之上 ——
     表现就是「代码明明改了，界面一点没变」。
     这里把非自身的面板宿主隐藏（display:none，刷新即恢复，不做删除），
     并把自身宿主移到 body 末尾，保证新版面板始终在最上层。 */
  const sweepOtherPanels = () => {
    const mine = ownPanelHost();
    let hidden = 0;
    document.querySelectorAll("[" + PANEL_MARK_ATTR + "]").forEach((el) => {
      if (el === mine || el.getAttribute(PANEL_MARK_ATTR) === HX_RUN_ID)
        return;
      el.style.display = "none";
      hidden += 1;
    });
    Array.from(document.body.children).forEach((el) => {
      if (el.tagName !== "DIV" || el.attributes.length !== 0 || el.childNodes.length !== 0)
        return;
      if (hostsShadowTree(el)) {
        el.style.display = "none";
        hidden += 1;
      }
    });
    if (mine && document.body.lastElementChild !== mine)
      document.body.append(mine);
    return hidden;
  };
  /* 供在页面控制台一键盘点：__HX_BUILD__ / __HX_DIAG__() */
  const exposeDiagnostics = () => {
    try {
      const w = typeof unsafeWindow !== "undefined" ? unsafeWindow : window;
      w.__HX_BUILD__ = HX_BUILD;
      w.__HX_DIAG__ = () => {
        const sr = hxShadow;
        const q = (sel) => (sr ? Boolean(sr.querySelector(sel)) : false);
        return {
          build: HX_BUILD,
          runId: HX_RUN_ID,
          mounted: Boolean(ownPanelHost()),
          newGenPanelHosts: document.querySelectorAll("[" + PANEL_MARK_ATTR + "]").length,
          legacyBareHosts: Array.from(document.body.children).filter((el) => el.tagName === "DIV" && el.attributes.length === 0 && el.childNodes.length === 0).length,
          answerTab: {
            whaleHero: q(".whale-hero"),
            idle: q(".whale-hero.is-idle"),
            busy: q(".whale-hero.is-busy"),
            questionTable: q(".question_table"),
            usageBar: q(".usage-bar"),
            buildBadge: q(".usage-build"),
            oldEmptyState: q(".el-empty")
          },
          configTab: {
            aiCard: q(".setting-ai"),
            apiKey: q(".setting-ai .el-input"),
            model: q(".setting-ai .el-select")
          },
          tabs: sr ? Array.from(sr.querySelectorAll(".el-tabs__item")).map((el) => (el.textContent || "").trim()) : []
        };
      };
    } catch (error) { /* 忽略 */ }
  };
'''
sub_once('  const PANEL_MARK_ATTR = "data-hx-panel";',
         '  const PANEL_MARK_ATTR = "data-hx-panel";\r\n' + crlf(SWEEP),
         "E1 插入清场+自诊断")

sub_once('    shadowHost.setAttribute(PANEL_MARK_ATTR, "1");',
         "    shadowHost.setAttribute(PANEL_MARK_ATTR, HX_RUN_ID);",
         "E2 宿主标记改用本次 runId")

sub_once("    document.body.append(shadowHost);\r\n    shadowRoot.appendChild(mountNode);",
         "    document.body.append(shadowHost);\r\n    shadowRoot.appendChild(mountNode);\r\n    hxShadow = shadowRoot;\r\n    exposeDiagnostics();",
         "E3 记录 shadowRoot 并暴露诊断")

sub_once('  const isPanelMounted = () => Boolean(document.querySelector("[" + PANEL_MARK_ATTR + "]"));',
         '  const isPanelMounted = () => Boolean(document.querySelector("[" + PANEL_MARK_ATTR + \'="\' + HX_RUN_ID + \'"]\'));',
         "E4 去重判断限定为自身 runId")

OLD_BOOT = """    if (isPanelMounted())
      return;
    try {
      mountApp();
    } catch (error) {
      console.error("[探矿鲸娘] 面板挂载失败：", error);
    }"""
NEW_BOOT = """    if (isPanelMounted())
      return;
    try {
      mountApp();
      console.info("[探矿鲸娘] build " + HX_BUILD + " 已挂载（run " + HX_RUN_ID + "）");
      HX_SWEEP_DELAYS.forEach((delay) => {
        setTimeout(() => {
          try {
            const hidden = sweepOtherPanels();
            if (hidden)
              console.warn("[探矿鲸娘] 已隐藏 " + hidden + " 个旧版/重复面板宿主，新版面板已置于最上层");
          } catch (error2) { /* 忽略 */ }
        }, delay);
      });
    } catch (error) {
      console.error("[探矿鲸娘] 面板挂载失败：", error);
    }"""
sub_once(crlf(OLD_BOOT), crlf(NEW_BOOT), "E5 挂载后多轮清场")

# ---------- 校验 ----------
counts = {}
for k in ["0.4.2", "0.4.3", "HX_BUILD", "HX_RUN_ID", "sweepOtherPanels", "hostsShadowTree",
          "ownPanelHost", "__HX_DIAG__", "__HX_BUILD__", "exposeDiagnostics", "hxShadow",
          "usage-build", "HX_SWEEP_DELAYS"]:
    counts[k] = src.count(k)
for k in sorted(counts):
    print("  计数 %-18s = %d" % (k, counts[k]))
assert counts["0.4.2"] == 0, "仍有 0.4.2 残留"
assert counts["0.4.3"] == 4
assert counts["sweepOtherPanels"] == 2      # 定义 + 调用
assert counts["hostsShadowTree"] == 2       # 定义 + 调用
assert counts["__HX_DIAG__"] == 2    # 注释 1 + 赋值 1
assert counts["__HX_BUILD__"] == 2   # 注释 1 + 赋值 1
assert counts["exposeDiagnostics"] == 2     # 定义 + 调用
assert counts["HX_RUN_ID"] >= 6
assert counts["HX_BUILD"] >= 3
bare = src.count("\n") - src.count("\r\n")
assert bare == 0, "存在 %d 处裸 LF（必须全 CRLF）" % bare

io.open(P, "w", encoding="utf-8", newline="").write(src)
print("---- 完成 ----")
print("原字节 %d -> 现字节 %d (+%d)" % (len(orig.encode("utf-8")), len(src.encode("utf-8")), len(src.encode("utf-8")) - len(orig.encode("utf-8"))))
