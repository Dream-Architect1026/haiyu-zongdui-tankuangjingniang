# -*- coding: utf-8 -*-
"""
0.4.9 -> 0.4.10
A  状态灯：删掉「最近 6 条里凡 danger/error 就判红」的误报逻辑
B  用量栏：请求→本次(本次请求数) / 花费→总花费 / 空闲/高峰→好感度 / 删 tok/s 速率 / 删原「本次¥」胶囊
C  .el-card 补 position:relative + 液态玻璃描边（边框玻璃质感）
D  光晕统一 ×0.618
E  配置页 考试 → 测试（含迁移表新增 "考试" 别名）
F  必填红星标签 + AI 卡三字段 → 小胶囊 dock
G  好感度卡片：落点多级降级 + MutationObserver 抗 Vue 重渲染移除（这就是"没展示"的真因）
H  智能路由：答题中一律不跳状态页；答题结束后才跳状态页（再 10s 回鲸娘页）
"""
import os
import re
import sys

P = r"C:\Users\D_A\DoubaoWork\chats\2026-10-05\new-chat-4\海底小纵队·探矿鲸娘.user.js"
OUT = r"C:\Users\D_A\WorkBuddy\2026-10-05-13-53-42\_f50out.txt"
DRY = "--dry" in sys.argv
OLD_VER = "0.4.9"
NEW_VER = "0.4.10"

log = []


def w(s):
    log.append(str(s))


def flush(code=0):
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    open(OUT, "w", encoding="utf-8").write("\n".join(log))
    sys.exit(code)


raw = open(P, "rb").read().decode("utf-8")
s = raw.replace("\r\n", "\n")

# ── 0. 版本号替换（白名单闸门）──────────────────────────────
hits = list(re.finditer(re.escape(OLD_VER), s))
w("=== 版本号 " + OLD_VER + " 出现 " + str(len(hits)) + " 处 ===")
bad = []
for m in hits:
    ctx = s[max(0, m.start() - 48): m.end() + 48].replace("\n", "\\n")
    ok = bool(re.search(r"(@version|HX_BUILD|v0\.|/\*|// ----|License|面板|已就位|开工|液态玻璃|标签|hero)", ctx))
    w("  [" + ("OK" if ok else "??") + "] " + ctx)
    if not ok:
        bad.append(ctx)
if bad:
    w("!! 有非版本字面量的 " + OLD_VER + "，已中止")
    flush(1)

ver_hits_before = len(hits)
s = s.replace(OLD_VER, NEW_VER)

NEW_PARTS = []


def span_replace(src, start, end, new, label, expect=1):
    if src.count(start) != expect:
        raise SystemExit("!! [" + label + "] 起始锚点期望 " + str(expect) + " 处，实际 " + str(src.count(start)) + " 处")
    if src.count(end) < 1:
        raise SystemExit("!! [" + label + "] 结束锚点找不到")
    i = src.index(start)
    j = src.index(end, i + len(start)) + len(end)
    w("  [OK] " + label + " 区间替换 " + str(j - i) + " 字符 -> " + str(len(new)))
    NEW_PARTS.append(new)
    return src[:i] + new + src[j:]


def lit_replace(src, old, new, label, expect=1):
    if src.count(old) != expect:
        raise SystemExit("!! [" + label + "] 期望 " + str(expect) + " 处，实际 " + str(src.count(old)) + " 处")
    NEW_PARTS.append(new)
    return src.replace(old, new)


# ══════════════════ A. 状态灯判定重写 ══════════════════
STATUS_START = '  const HX_STATUS_TEXT = { run: "运行中", busy: "答题中", stop: "已终止" };'
STATUS_END = '    return dead ? "stop" : "run";\n  };'

STATUS_NEW = '''  const HX_STATUS_TEXT = { run: "运行中", busy: "答题中", stop: "已终止" };
  /* 判定优先级：正在答题(黄) > 明确中断(红) > 其余(绿)
     改版原因：旧逻辑是「最近 6 条日志里只要出现 danger/error 就判红」，
     但脚本日常运行本来就有一堆 danger/error 级日志
     （自动翻题关掉了哦 / 正确率不达标先攒着 / 这页没活儿歇会儿 / 第 n 题绊了一跤），
     所以「运行中」也会被误判成「已终止」。现改为：从最新一条往前扫，
     取第一个有语义的事件定色；日常噪音一条都不匹配，于是既不误红，
     也能在真正中断 / 真正恢复时正确翻色。 */
  const HX_FATAL_RE = /已停止|已终止|中止|中断|失败|报错|异常|未配置|没配置|密钥|API ?Key|无响应|连不上|崩溃|卡住|无法|拒绝/;
  const HX_RESUME_RE = /开动|开工|就位|开始|潜入|游向|进考场|到手|拿下|翻到|清空|搞定|读完|放完|跳过|已加载|数钱|归零|返回/;
  const readPanelStatus = () => {
    let busy = false;
    try {
      const questionStore = useQuestionStore();
      const list = questionStore && questionStore.questionList;
      busy = Array.isArray(list) && list.length > 0;
    } catch (error) { /* 忽略 */ }
    if (busy)
      return "busy";
    try {
      const logStore2 = useLogStore();
      const logs = logStore2 && Array.isArray(logStore2.logList) ? logStore2.logList : [];
      const from = Math.max(logs.length - 24, 0);
      for (let i = logs.length - 1; i >= from; i -= 1) {
        const item = logs[i];
        const msg = String((item && item.message) || "");
        if (HX_RESUME_RE.test(msg))
          return "run";
        if (HX_FATAL_RE.test(msg))
          return "stop";
      }
    } catch (error) { /* 忽略 */ }
    return "run";
  };'''

s = span_replace(s, STATUS_START, STATUS_END, STATUS_NEW, "A 状态灯判定")

# ══════════════════ B. 用量栏改版 ══════════════════
USE_START = "  const buildUsageBarHtml = (store, peak) => {"
USE_END = '''      + '<span class="usage-uptime" title="本次启用脚本后的运行时长">运行 ' + formatUptime(upMs) + "</span>"
      + "</div>";
  };'''

USE_NEW = '''  const buildUsageBarHtml = (store, peak) => {
    const sess = sessionUsage();
    const upMs = Math.max(Date.now() - (sessionBase.at || Date.now()), 0);
    let favLv = 1;
    let favName = "初见";
    try {
      const favTier = HX_FAV_TIERS[hxFavLevelIdx()] || HX_FAV_TIERS[0];
      favLv = favTier.lv;
      favName = favTier.name;
    } catch (error) { /* 忽略：极早期渲染时好感度表可能尚未就绪，下一拍会自愈 */ }
    const sessTitle = "本次启用脚本后：请求 " + sess.requests + " 次 · " + formatTokenCount(sess.totalTokens)
      + " token · " + formatCost(sess.cost);
    const favTitle = "好感度 Lv." + favLv + " · " + favName + " ｜ 累计花费 " + formatCost(store.cost)
      + (peak ? " ｜ 当前高峰时段" : " ｜ 当前空闲时段");
    const cells = [
      ["本次", String(sess.requests), sessTitle],
      ["Token", formatTokenCount(store.totalTokens), "脚本统计的累计 token 用量"],
      ["总花费", formatCost(store.cost), "脚本统计的累计花费"]
    ].map(([label, value, tip]) => '<div class="usage-cell" title="' + tip + '"><span class="usage-cell__k">' + label
      + '</span><span class="usage-cell__v">' + value + "</span></div>").join("");
    return '<div class="usage-main">' + cells + "</div>"
      + '<div class="usage-sub" data-hx-build="' + HX_BUILD + '">'
      + '<span class="usage-fav" title="' + favTitle + '">'
      + '<span class="usage-fav__k">好感度</span>'
      + '<span class="usage-fav__v">Lv.' + favLv + " · " + favName + "</span>"
      + "</span>"
      + '<span class="usage-uptime" title="本次启用脚本后的运行时长">运行 ' + formatUptime(upMs) + "</span>"
      + "</div>";
  };'''

s = span_replace(s, USE_START, USE_END, USE_NEW, "B 用量栏改版")

# ══════════════════ E. 考试 -> 测试 ══════════════════
s = lit_replace(s, '    "考试模式": "考试",', '    "考试模式": "测试",', "E1 迁移-考试模式")
s = lit_replace(s, '    "考试设置": "考试",', '    "考试设置": "测试",', "E2 迁移-考试设置")
s = lit_replace(s, '    "课程任务": "任务",', '    "课程任务": "任务",\n    "考试": "测试",', "E3 迁移-新增考试别名")
s = lit_replace(s, '                name: "考试",', '                name: "测试",', "E4 参数组名")

# ══════════════════ G. 好感度挂载加固 ══════════════════
MOUNT_OLD = """  const mountFavCard = () => {
    const root = hxShadow;
    if (!root) return false;
    const pet = root.querySelector('.setting-ai .setting-pet-field');
    if (!pet || !pet.parentNode) return false;
    let el = root.querySelector('.setting-ai .setting-fav-field');
    if (!el) {
      el = document.createElement('div');
      el.className = 'setting-fav-field';
      el.innerHTML = hxFavShellHtml();
      pet.parentNode.insertBefore(el, pet.nextSibling);
      const info = el.querySelector('.fav-info');
      if (info) {
        const toggle = (ev) => {
          if (ev) { ev.preventDefault(); ev.stopPropagation(); }
          hxFavOpen = !hxFavOpen;
          el.classList.toggle('is-open', hxFavOpen);
        };
        info.addEventListener('click', toggle);
        info.addEventListener('keydown', (ev) => {
          if (ev && (ev.key === 'Enter' || ev.key === ' ')) toggle(ev);
        });
      }
    }
    el.classList.toggle('is-open', hxFavOpen);
    try { paintFavCard(el); } catch (error) { /* 忽略 */ }
    return true;
  };
  const bindFavCard = () => {
    const ensure = () => {
      try { mountFavCard(); } catch (error) { /* 忽略 */ }
    };
    ensure();
    if (hxFavTimer === null) hxFavTimer = setInterval(ensure, 1500);
  };"""

MOUNT_NEW = '''  /* 好感度卡片为什么之前"没展示"：我们注入的节点是 Vue 模板 div.setting-ai 的
     第 5 个子节点，而那个 div 每次重渲染只认原本的 4 个（分隔线/API Key/模型/小名），
     多出来的第 5 个会被 Vue 在 patchUnkeyedChildren 阶段直接移除 —— 于是卡片刚插进去
     就被删掉，用户看不到。修法：① 落点从「只认小名字段」改成多级降级；
     ② 用 MutationObserver 盯住容器，一旦发现卡片被移除就立刻补回。 */
  let hxFavAnchor = "";
  let hxFavObs = null;
  let hxFavObsTarget = null;
  let hxFavInserts = 0;
  const hxFavObserve = (host) => {
    if (typeof MutationObserver !== "function") return;
    if (hxFavObs && hxFavObsTarget === host) return;
    if (hxFavObs) { try { hxFavObs.disconnect(); } catch (error) { /* 忽略 */ } }
    hxFavObs = null;
    hxFavObsTarget = null;
    try {
      hxFavObs = new MutationObserver(() => {
        try {
          if (!host.isConnected) return;
          if (host.querySelector(".setting-fav-field")) return;
          mountFavCard();
        } catch (error) { /* 忽略 */ }
      });
      hxFavObs.observe(host, { childList: true });
      hxFavObsTarget = host;
    } catch (error) { hxFavObs = null; hxFavObsTarget = null; }
  };
  const hxFavAnchorPick = (root) => {
    const probes = [
      [".setting>div.setting-ai", "container"],
      [".setting-ai", "container"],
      [".setting .setting-pet-field", "after"],
      [".setting", "container"]
    ];
    for (let i = 0; i < probes.length; i += 1) {
      const node = root.querySelector(probes[i][0]);
      if (node && node.parentNode) {
        hxFavAnchor = probes[i][0];
        return { node: node, mode: probes[i][1] };
      }
    }
    hxFavAnchor = "";
    return null;
  };
  const mountFavCard = () => {
    const root = hxShadow;
    if (!root) return false;
    const hit = hxFavAnchorPick(root);
    if (!hit) return false;
    const host = hit.mode === "after" ? hit.node.parentNode : hit.node;
    if (!host) return false;
    let el = host.querySelector(".setting-fav-field");
    if (!el) {
      el = root.querySelector(".setting-fav-field");
      if (el && el.parentNode !== host) {
        try { el.parentNode.removeChild(el); } catch (error) { el = null; }
      }
    }
    if (!el) {
      el = document.createElement("div");
      el.className = "setting-fav-field";
      el.innerHTML = hxFavShellHtml();
      const info = el.querySelector(".fav-info");
      if (info) {
        const toggle = (ev) => {
          if (ev) { ev.preventDefault(); ev.stopPropagation(); }
          hxFavOpen = !hxFavOpen;
          el.classList.toggle("is-open", hxFavOpen);
        };
        info.addEventListener("click", toggle);
        info.addEventListener("keydown", (ev) => {
          if (ev && (ev.key === "Enter" || ev.key === " ")) toggle(ev);
        });
      }
    }
    if (hit.mode === "after") {
      if (el.previousSibling !== hit.node) host.insertBefore(el, hit.node.nextSibling);
    } else if (host.lastElementChild !== el) {
      host.appendChild(el);
    }
    if (el.parentNode !== host) return false;
    hxFavInserts += 1;
    hxFavObserve(host);
    el.classList.toggle("is-open", hxFavOpen);
    try { paintFavCard(el); } catch (error) { /* 忽略 */ }
    try {
      const nowLv = hxFavLevelIdx();
      if (hxFavBarLv !== nowLv) {
        hxFavBarLv = nowLv;
        usageTick.value += 1;
      }
    } catch (error) { /* 忽略 */ }
    return true;
  };
  let hxFavBarLv = -1;
  const bindFavCard = () => {
    const ensure = () => {
      try { mountFavCard(); } catch (error) { /* 忽略 */ }
    };
    ensure();
    [220, 700, 1500, 3000, 5200].forEach((delay) => setTimeout(ensure, delay));
    if (hxFavTimer === null) hxFavTimer = setInterval(ensure, 1500);
  };'''

s = lit_replace(s, MOUNT_OLD, MOUNT_NEW, "G 好感度挂载加固")

# ── 探针补 anchor / inserts ────────────────────────────────
s = lit_replace(s,
                "nextAt: nx ? nx.at : null, note: hxFavOpen, mounted:",
                "nextAt: nx ? nx.at : null, note: hxFavOpen, anchor: hxFavAnchor, inserts: hxFavInserts, mounted:",
                "G5 探针 __HX_FAV__")
s = lit_replace(s,
                "total: hxFavTotalLines(), mounted: !!(hxShadow && hxShadow.querySelector('.setting-fav-field')) },",
                "total: hxFavTotalLines(), anchor: hxFavAnchor, inserts: hxFavInserts, mounted: !!(hxShadow && hxShadow.querySelector('.setting-fav-field')) },",
                "G6 探针 __HX_DIAG__")

# ══════════════════ H. 智能路由：答题中不跳状态页 ══════════════════
s = lit_replace(s, '  let hxRouteReadyAt = 0;', '  let hxRouteReadyAt = 0;\n  let hxWasBusy = false;', "H1 路由状态变量")

ROUTE_OLD = '''  const hxRouteTick = () => {
    const items = hxTabItems();
    if (items.length === 0) return;
    if (!hxDefaultTabApplied) {
      hxDefaultTabApplied = true;
      if (hxActiveTabIndex() === hxTabIdIndex(HX_TAB_LOG)) hxSwitchTab(hxTabIdIndex(HX_TAB_MAIN));
      hxLastLogSig = hxLogSignature();
      return;
    }
    const sig = hxLogSignature();
    if (sig === hxLastLogSig) return;
    hxLastLogSig = sig;
    if (Date.now() < hxRouteReadyAt) return;
    const active = hxActiveTabIndex();
    const logIdx = hxTabIdIndex(HX_TAB_LOG);
    if (active === logIdx || active === hxTabIdIndex(HX_TAB_MAIN)) {
      if (hxSwitchTab(logIdx)) hxAutoJumped = true;
    }
    if (!hxAutoJumped) return;
    if (hxAutoTabTimer) clearTimeout(hxAutoTabTimer);
    hxAutoTabTimer = setTimeout(() => { try { hxReturnToMain(); } catch (error) { /* 忽略 */ } }, HX_TAB_RETURN_MS);
  };'''

ROUTE_NEW = '''  const hxIsBusy = () => {
    try {
      const questionStore = useQuestionStore();
      const list = questionStore && questionStore.questionList;
      return Array.isArray(list) && list.length > 0;
    } catch (error) { return false; }
  };
  const hxJumpToLog = () => {
    const logIdx = hxTabIdIndex(HX_TAB_LOG);
    if (hxSwitchTab(logIdx)) hxAutoJumped = true;
    if (!hxAutoJumped) return;
    if (hxAutoTabTimer) clearTimeout(hxAutoTabTimer);
    hxAutoTabTimer = setTimeout(() => { try { hxReturnToMain(); } catch (error) { /* 忽略 */ } }, HX_TAB_RETURN_MS);
  };
  const hxRouteTick = () => {
    const items = hxTabItems();
    if (items.length === 0) return;
    if (!hxDefaultTabApplied) {
      hxDefaultTabApplied = true;
      if (hxActiveTabIndex() === hxTabIdIndex(HX_TAB_LOG)) hxSwitchTab(hxTabIdIndex(HX_TAB_MAIN));
      hxLastLogSig = hxLogSignature();
      hxWasBusy = hxIsBusy();
      return;
    }
    const busy = hxIsBusy();
    const sig = hxLogSignature();
    /* ① 答题中：日志再变也不跳，老老实实留在鲸娘页看小鲸娘干活 */
    if (busy) {
      hxWasBusy = true;
      hxLastLogSig = sig;
      return;
    }
    /* ② 答题刚结束：这一次一定要把主人带回状态页看战果（随后 10s 自动回鲸娘页） */
    if (hxWasBusy) {
      hxWasBusy = false;
      hxLastLogSig = sig;
      if (Date.now() < hxRouteReadyAt) return;
      const was = hxActiveTabIndex();
      if (was === hxTabIdIndex(HX_TAB_LOG) || was === hxTabIdIndex(HX_TAB_MAIN)) hxJumpToLog();
      return;
    }
    /* ③ 空闲期：沿用原规则 —— 状态页有变化才跳过去看一眼 */
    if (sig === hxLastLogSig) return;
    hxLastLogSig = sig;
    if (Date.now() < hxRouteReadyAt) return;
    const active = hxActiveTabIndex();
    if (active === hxTabIdIndex(HX_TAB_LOG) || active === hxTabIdIndex(HX_TAB_MAIN)) hxJumpToLog();
  };'''

s = lit_replace(s, ROUTE_OLD, ROUTE_NEW, "H2 hxRouteTick 重写")

# 探针补 busy
s = lit_replace(s,
                "w.__HX_TAB__ = () => ({ active: hxActiveTabIndex(), labels: hxTabItems().map((el) => (el.textContent || \"\").trim()), autoJumped: hxAutoJumped, applied: hxDefaultTabApplied });",
                "w.__HX_TAB__ = () => ({ active: hxActiveTabIndex(), labels: hxTabItems().map((el) => (el.textContent || \"\").trim()), autoJumped: hxAutoJumped, applied: hxDefaultTabApplied, busy: hxIsBusy(), wasBusy: hxWasBusy });",
                "H3 探针 __HX_TAB__ 补 busy")

# ══════════════════ C/D/F. 新 CSS 块 ══════════════════
CSS_BLOCK = r'''// ---- v0.4.10 ----
LAYOUT_CSS_PARTS.push(
  "\n/* ==== v0.4.10 · 本轮 : 液态玻璃边框 + 光晕 61.8% + 表单小胶囊 + 用量栏改版 ==== */"
  + "\n/* --- A. 卡座定位：此前 .el-card 没有 position，::before/::after 会挂到祖先盒上 --- */"
  + "\n.main-page .el-card{position:relative}"
  + "\n/* --- B. 边框液态玻璃：亮一档的 1px 描边 + 内侧上高光 + 外侧微辉 --- */"
  + "\n.main-page .el-card{border:1px solid rgba(152,206,255,.30)!important;box-shadow:0 18px 48px rgba(2,8,24,.46),0 0 26px rgba(56,226,255,.12),inset 0 1px 0 rgba(255,255,255,.22),inset 0 0 26px rgba(120,190,255,.07)!important}"
  + "\n.main-page .el-card::after{content:'';position:absolute;inset:0;border-radius:inherit;pointer-events:none;z-index:4;box-shadow:inset 0 0 0 1px rgba(255,255,255,.13),inset 0 1px 0 rgba(255,255,255,.20),inset 0 -1px 0 rgba(120,190,255,.12)}"
  + "\n/* --- C. 状态灯：色彩由 JS 写入，这里只补平滑过渡 --- */"
  + "\n.main-page .hx-status-dot{transition:color .3s ease,box-shadow .3s ease}"
  + "\n/* --- D. 必填红星标签 -> 小胶囊 dock（不再与旁边环境割裂） --- */"
  + "\n.main-page .setting .el-form-item.is-required>.el-form-item__label{flex:0 0 auto!important;align-self:center;margin:0 7px 0 0!important;padding:1px 8px!important;border:1px solid rgba(255,152,152,.30)!important;border-radius:8px!important;background:linear-gradient(150deg,rgba(255,140,140,.13),rgba(255,140,140,.03))!important;box-shadow:inset 0 1px 0 rgba(255,255,255,.15)!important;font-size:11.5px!important;line-height:17px!important;height:auto!important;color:var(--hx-ink)!important}"
  + "\n.main-page .setting .el-form-item.is-required>.el-form-item__label::before{color:#ff9a9a!important;margin-right:3px!important;font-size:11px!important}"
  + "\n/* --- E. AI 卡三字段（API Key / 模型 / 小名）-> 更小的玻璃小胶囊，比卡片小标题弱一档 --- */"
  + "\n.main-page .setting>div.setting-ai .el-form-item.setting-ai-field>.el-form-item__label{flex:0 0 auto!important;min-width:52px!important;align-self:center;justify-content:center!important;margin:0 8px 0 0!important;padding:1px 8px!important;border:1px solid rgba(140,200,255,.24)!important;border-radius:8px!important;background:linear-gradient(150deg,rgba(255,255,255,.09),rgba(255,255,255,.02))!important;box-shadow:inset 0 1px 0 rgba(255,255,255,.16)!important;font-size:11.5px!important;line-height:17px!important;height:auto!important;color:var(--hx-ink)!important}"
  + "\n.main-page .setting>div.setting-ai .el-form-item.setting-ai-field>.el-form-item__label:hover{border-color:rgba(56,226,255,.42)!important}"
  + "\n/* --- F. 用量栏「好感度」胶囊（接替原来的 空闲/高峰 标签位） --- */"
  + "\n.main-page .usage-fav{display:inline-flex;align-items:center;gap:5px;flex:0 0 auto;padding:1px 9px;border:1px solid rgba(255,140,190,.30);border-radius:999px;background:linear-gradient(150deg,rgba(255,140,190,.14),rgba(155,107,255,.10));backdrop-filter:blur(10px) saturate(150%);-webkit-backdrop-filter:blur(10px) saturate(150%);box-shadow:inset 0 1px 0 rgba(255,255,255,.20);font-size:10px;line-height:15px;white-space:nowrap;font-variant-numeric:tabular-nums;transition:var(--lg-t)}"
  + "\n.main-page .usage-fav__k{color:var(--hx-ink-dim)}"
  + "\n.main-page .usage-fav__v{color:#ffb3d1;font-weight:700}"
  + "\n.main-page .usage-fav:hover{border-color:rgba(255,140,190,.55);box-shadow:0 4px 12px rgba(2,8,24,.30),inset 0 1px 0 rgba(255,255,255,.28)}"
  + "\n/* --- G. 光晕统一 x0.618（只改关键帧不透明度 = 整体降到 61.8%） --- */"
  + "\n@keyframes hxHeroGlowA{0%,100%{opacity:.185;transform:scale(.90)}50%{opacity:.587;transform:scale(1.06)}}"
  + "\n@keyframes hxHeroGlowB{0%,100%{opacity:0;transform:scale(.84)}48%{opacity:.544;transform:scale(1.04)}}"
  + "\n@keyframes hxWhaleAura{0%,100%{filter:drop-shadow(0 3px 9px rgba(56,226,255,.278))}50%{filter:drop-shadow(0 7px 18px rgba(155,107,255,.433))}}"
  + "\n@media (prefers-reduced-motion:reduce){.main-page .usage-fav,.main-page .hx-status-dot{transition-duration:.01ms}}"
);

const layoutCss = LAYOUT_CSS_PARTS.join("");'''

s = lit_replace(s, 'const layoutCss = LAYOUT_CSS_PARTS.join("");', CSS_BLOCK, "CDF 新 CSS 块")

# ══════════════════ 结构不变量 ══════════════════
w("")
w("=== 结构不变量 ===")
push_before = raw.count("LAYOUT_CSS_PARTS.push(")
checks = [
    ("HX_BUILD " + NEW_VER, s.count('const HX_BUILD = "' + NEW_VER + '";'), 1),
    (OLD_VER + " 残留", s.count(OLD_VER), 0),
    ("push = 旧+1", s.count("LAYOUT_CSS_PARTS.push("), push_before + 1),
    ("layoutCss join", s.count('const layoutCss = LAYOUT_CSS_PARTS.join("")'), 1),
    ("HX_FATAL_RE 声明", s.count("const HX_FATAL_RE = "), 1),
    ("HX_RESUME_RE 声明", s.count("const HX_RESUME_RE = "), 1),
    ("旧 slice(-6) 已删", s.count("logs.slice(-6).some"), 0),
    ("旧 dead 变量已删", s.count("let dead = false;"), 0),
    ("usage-tag 出参已删", s.count('class="usage-tag '), 0),
    ("usage-rate 出参已删", s.count('class="usage-rate"'), 0),
    ("usage-session 出参已删", s.count('class="usage-session"'), 0),
    ("usage-fav 出参", s.count('class="usage-fav"'), 1),
    ("本次=session.requests", s.count("String(sess.requests)"), 1),
    ("总花费标签", s.count("总花费"), 1),
    ("考试仅剩别名键", s.count("考试"), 3),
    ("测试=参数组名", s.count('name: "测试"'), 1),
    ("迁移 考试->测试", s.count('"考试": "测试"'), 1),
    ("hxFavAnchorPick", s.count("const hxFavAnchorPick = (root) => {"), 1),
    ("hxFavAnchor 声明", s.count('let hxFavAnchor = "";'), 1),
    ("hxFavInserts 声明", s.count("let hxFavInserts = 0;"), 1),
    ("MutationObserver", s.count("new MutationObserver("), raw.count("new MutationObserver(") + 1),
    ("hxFavObserve 定义", s.count("const hxFavObserve = (host) => {"), 1),
    ("hxIsBusy 定义", s.count("const hxIsBusy = () => {"), 1),
    ("hxJumpToLog 定义", s.count("const hxJumpToLog = () => {"), 1),
    ("hxWasBusy 声明", s.count("let hxWasBusy = false;"), 1),
    ("答题中抑制路由", s.count("hxWasBusy = true;"), 1),
    ("新 CSS 块标记", s.count("==== v" + NEW_VER + " \u00b7 \u672c\u8f6e :"), 1),
    ("卡片定位修复", s.count(".main-page .el-card{position:relative}"), 1),
    ("el-card::after 玻璃边", s.count(".main-page .el-card::after{content:''"), 1),
    ("光晕A 61.8%", s.count("@keyframes hxHeroGlowA{0%,100%{opacity:.185;"), 1),
    ("光晕B 61.8%", s.count("@keyframes hxHeroGlowB{0%,100%{opacity:0;transform:scale(.84)}48%{opacity:.544;"), 1),
    ("鲸娘光晕 61.8%", s.count("rgba(56,226,255,.278)"), 1),
    ("必填标签胶囊", s.count(".el-form-item.is-required>.el-form-item__label{flex:0 0 auto"), 1),
    ("AI 字段胶囊", s.count(".setting-ai-field>.el-form-item__label{flex:0 0 auto"), 1),
    ("好感度胶囊样式", s.count(".main-page .usage-fav{"), 1),
]

fails = []
for name, got, exp in checks:
    ok = got == exp
    w("  [" + ("OK" if ok else "NG") + "] " + name.ljust(24) + " got=" + str(got) + " exp=" + str(exp))
    if not ok:
        fails.append(name)

w("")
w("  打印计数：")
for kw in ["formatRate(", "考试模式", "考试设置", "usage-tag", "usage-rate", "usage-session", "usage-fav", "hxFavAnchor", "hxFavInserts", "hxWasBusy", "is-required", "setting-ai-field"]:
    w("    " + kw.ljust(16) + " = " + str(s.count(kw)))

if fails:
    w("")
    w("!! 结构不变量失败：" + ", ".join(fails) + " —— 未写入")
    flush(1)

w("")
w("=== 结果 ===")
w("  dry=" + str(DRY))
w("  LF 行数 = " + str(s.count("\n") + 1))

if DRY:
    w("  [DRY] 未写盘")
    flush(0)

crlf = s.replace("\n", "\r\n").encode("utf-8")
open(P, "wb").write(crlf)
w("  已写盘 bytes=" + str(len(crlf)) + " crlf=" + str(s.count("\n")) + " bareLF=0")
flush(0)
