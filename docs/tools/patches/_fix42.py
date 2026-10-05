# -*- coding: utf-8 -*-
"""fix42: 探矿鲸娘 0.4.3 -> 0.4.4
1) 用量卡片：去掉版本号，改为「本次」= 本次启用脚本后的累计花费（sessionStorage 记基线）
2) 空闲态：鲸娘下方显示 DeepSeek 账户余额（GET /user/balance）
3) 液态玻璃系统：顶部标签 / 用量卡片 / 各页卡片（不同模糊）双态（静止 / 悬停·吸顶滚动）
4) 去掉用量卡片里的竖分隔线 + 顶部标签页的横下划线，元素整体悬浮
5) 顶部标题栏美化：加鲸娘徽标 + 与下方同材质，消除割裂感
"""
import sys, io, os

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

P = r"C:\Users\D_A\DoubaoWork\chats\2026-10-05\new-chat-4\海底小纵队·探矿鲸娘.user.js"

raw = open(P, "rb").read()
t = raw.decode("utf-8")
assert "\r\n" in t, "文件应为 CRLF"
t = t.replace("\r\n", "\n").replace("\r", "\n")
old_len = len(t)

def sub1(old, new, tag):
    global t
    n = t.count(old)
    assert n == 1, f"[{tag}] 期望 1 处，实际 {n} 处"
    t = t.replace(old, new, 1)
    print(f"  [OK] {tag}")

# ────────────────────────────────────────────────────────────
# P1 版本号
# ────────────────────────────────────────────────────────────
sub1("// @version      0.4.3", "// @version      0.4.4", "P1a @version")
sub1('  const HX_BUILD = "0.4.3";', '  const HX_BUILD = "0.4.4";', "P1b HX_BUILD")
sub1(r'"面板 0.4.3 \u00b7 \u65b0\u7248\u5e03\u5c40\u5df2\u52a0\u8f7d"',
     r'"面板 0.4.4 \u00b7 \u6db2\u6001\u73bb\u7483\u5df2\u52a0\u8f7d"',
     "P1c 启动日志")
sub1("v0.4.3 · MIT License", "v0.4.4 · MIT License", "P1d 教程页页脚")

# ────────────────────────────────────────────────────────────
# P2 本次用量（sessionStorage 基线）
# ────────────────────────────────────────────────────────────
SESSION_CODE = '''
  /* ── 「本次」用量：以本次启用脚本为界 ─────────────────────────────
     基线落在 sessionStorage：同一标签页内刷新 / 页面跳转沿用，
     新开标签页或关掉标签页后重新计。面板显示 = 当前累计 − 基线。 */
  const HX_SESSION_KEY = "hx_session_base_v1";
  const hxSessionStore = (() => {
    try {
      const store = typeof unsafeWindow !== "undefined" && unsafeWindow.sessionStorage
        ? unsafeWindow.sessionStorage : sessionStorage;
      store.setItem("hx_probe", "1");
      store.removeItem("hx_probe");
      return store;
    } catch (error) { return null; }
  })();
  const readSessionBase = () => {
    if (!hxSessionStore) return null;
    try {
      const raw2 = hxSessionStore.getItem(HX_SESSION_KEY);
      if (!raw2) return null;
      const obj = JSON.parse(raw2);
      if (!obj) return null;
      const cost = Number(obj.cost), tokens = Number(obj.totalTokens), reqs = Number(obj.requests);
      if (!isFinite(cost) || !isFinite(tokens) || !isFinite(reqs)) return null;
      return { cost, totalTokens: tokens, requests: reqs };
    } catch (error) { return null; }
  };
  const writeSessionBase = (obj) => {
    if (!hxSessionStore) return;
    try { hxSessionStore.setItem(HX_SESSION_KEY, JSON.stringify(obj)); } catch (error) {}
  };
  let sessionBase = readSessionBase();
  if (!sessionBase) {
    sessionBase = { cost: usageStore.cost, totalTokens: usageStore.totalTokens, requests: usageStore.requests };
    writeSessionBase(sessionBase);
  }
  const sessionUsage = () => ({
    requests: Math.max(usageStore.requests - sessionBase.requests, 0),
    totalTokens: Math.max(usageStore.totalTokens - sessionBase.totalTokens, 0),
    cost: Math.max(usageStore.cost - sessionBase.cost, 0)
  });
  const resetSessionUsage = () => {
    sessionBase = { cost: usageStore.cost, totalTokens: usageStore.totalTokens, requests: usageStore.requests };
    writeSessionBase(sessionBase);
    try { usageTick.value += 1; } catch (error) {}
    return sessionUsage();
  };
'''
sub1("  let hxShadow = null;\n", "  let hxShadow = null;\n" + SESSION_CODE, "P2 本次用量基线")

# ────────────────────────────────────────────────────────────
# P3 用量卡片：版本号 -> 本次花费
# ────────────────────────────────────────────────────────────
sub1('''      + '<span class="usage-build">v' + HX_BUILD + "</span>"
      + "</div>";
  };''',
     '''      + '<span class="usage-session" title="' + sessTitle + '">'
      + '<span class="usage-session__k">本次</span>'
      + '<span class="usage-session__v">' + formatCost(sess.cost) + "</span>"
      + "</span>"
      + "</div>";
  };''', "P3a 徽标 -> 本次")

sub1('''    ].map(([label, value]) => '<div class="usage-cell"><span class="usage-cell__k">' + label
      + '</span><span class="usage-cell__v">' + value + "</span></div>").join("");
    return '<div class="usage-main">' + cells + "</div>"
      + '<div class="usage-sub">\'''',
     '''    ].map(([label, value]) => '<div class="usage-cell"><span class="usage-cell__k">' + label
      + '</span><span class="usage-cell__v">' + value + "</span></div>").join("");
    const sess = sessionUsage();
    const sessTitle = "本次启用脚本后：请求 " + sess.requests + " 次 · " + formatTokenCount(sess.totalTokens)
      + " token · " + formatCost(sess.cost) + "（点击可重置基线）";
    return '<div class="usage-main">' + cells + "</div>"
      + '<div class="usage-sub" data-hx-build="' + HX_BUILD + '">\'''', "P3b 本次用量计算")

# 旧的 .usage-build 样式已无用，去掉
sub1('''    + "\\n.main-page .usage-build{margin-left:auto;font-size:9.5px;line-height:15px;letter-spacing:.02em;color:rgba(150,215,255,.5);white-space:nowrap}"
''', "", "P3c 移除 .usage-build 样式")

# ────────────────────────────────────────────────────────────
# P4 账户余额
# ────────────────────────────────────────────────────────────
BALANCE_CODE = '''
  /* ── DeepSeek 账户余额（空闲态展示在鲸娘下方）──────────────────────
     接口：GET https://api.deepseek.com/user/balance（Authorization: Bearer <API Key>）
     返回：is_available + balance_infos[]（currency / total_balance / granted_balance / topped_up_balance） */
  const DEEPSEEK_BALANCE_URL = "https://api.deepseek.com/user/balance";
  const readStoredApiKey = () => {
    try {
      const text = getStoredConfigText();
      if (!text) return "";
      const parsed = JSON.parse(text);
      const key = parsed && parsed.ai && parsed.ai.deepseek ? parsed.ai.deepseek.apiKey : "";
      return typeof key === "string" ? key.trim() : "";
    } catch (error) { return ""; }
  };
  const balanceStore = vue.reactive({
    state: "idle", currency: "CNY", total: null, granted: null, topped: null,
    available: null, msg: "", at: 0
  });
  let balanceTimer = null;
  const fetchBalance = () => {
    const apiKey = readStoredApiKey();
    if (!apiKey) {
      balanceStore.state = "nokey";
      balanceStore.msg = "未配置 API Key";
      balanceStore.total = null;
      return;
    }
    if (typeof _GM_xmlhttpRequest !== "function") {
      balanceStore.state = "err";
      balanceStore.msg = "当前环境不支持跨域请求";
      return;
    }
    balanceStore.state = "loading";
    _GM_xmlhttpRequest({
      url: DEEPSEEK_BALANCE_URL,
      method: "GET",
      headers: { Accept: "application/json", Authorization: "Bearer " + apiKey },
      timeout: 15e3,
      onload: (response) => {
        let parsed = null;
        try { parsed = JSON.parse(response.responseText); } catch (error) {}
        const infos = parsed && Array.isArray(parsed.balance_infos) ? parsed.balance_infos : null;
        if (response.status >= 200 && response.status < 300 && infos && infos.length) {
          const info = infos.find((item) => item && String(item.currency).toUpperCase() === "CNY") || infos[0];
          balanceStore.currency = String(info.currency || "CNY").toUpperCase();
          balanceStore.total = Number(info.total_balance);
          balanceStore.granted = Number(info.granted_balance);
          balanceStore.topped = Number(info.topped_up_balance);
          balanceStore.available = parsed.is_available !== false;
          balanceStore.msg = "";
          balanceStore.at = Date.now();
          balanceStore.state = "ok";
          return;
        }
        balanceStore.state = "err";
        balanceStore.msg = response.status === 401 ? "API Key 无效或已过期" : ("HTTP " + response.status);
      },
      onerror: () => { balanceStore.state = "err"; balanceStore.msg = "网络错误"; },
      ontimeout: () => { balanceStore.state = "err"; balanceStore.msg = "请求超时"; }
    });
  };
  const formatMoney = (value, currency) => {
    const v = Number(value);
    if (!isFinite(v)) return "—";
    const sign = String(currency || "CNY").toUpperCase() === "USD" ? "$" : "¥";
    if (v === 0) return sign + "0";
    return sign + (v < 1 ? v.toFixed(4) : v.toFixed(2));
  };
  const clockText = (timestamp) => {
    if (!timestamp) return "";
    const d = new Date(timestamp);
    return String(d.getHours()).padStart(2, "0") + ":" + String(d.getMinutes()).padStart(2, "0");
  };
  const heroBalanceHtml = vue.computed(() => {
    const state = balanceStore.state;
    const head = '<span class="hero-balance__k">账户余额</span>';
    if (state === "nokey")
      return '<span class="hero-balance is-void" title="尚未配置 DeepSeek API Key，请到「配置」页填写">'
        + head + '<span class="hero-balance__v">未配置 Key</span></span>';
    if (state === "loading" || state === "idle")
      return '<span class="hero-balance is-loading" title="正在向 api.deepseek.com 查询账户余额">'
        + head + '<span class="hero-balance__v">读取中</span></span>';
    if (state === "err")
      return '<span class="hero-balance is-err" title="余额查询失败：' + (balanceStore.msg || "未知错误")
        + '（点击重试）">' + head + '<span class="hero-balance__v">查询失败</span>'
        + '<span class="hero-balance__hint">点击重试</span></span>';
    const money = formatMoney(balanceStore.total, balanceStore.currency);
    const low = balanceStore.available === false || (balanceStore.total !== null && balanceStore.total <= 1);
    const title = "可用余额 " + money
      + "（赠送 " + formatMoney(balanceStore.granted, balanceStore.currency)
      + " / 充值 " + formatMoney(balanceStore.topped, balanceStore.currency) + "）"
      + (balanceStore.at ? " · 更新于 " + clockText(balanceStore.at) : "")
      + " · 点击刷新";
    return '<span class="hero-balance ' + (low ? "is-low" : "is-ok") + '" title="' + title + '">' + head
      + '<span class="hero-balance__v">' + money + "</span>"
      + (low ? '<span class="hero-balance__hint">余额偏低</span>' : "")
      + "</span>";
  });
'''
sub1("  const usageTick = vue.ref(0);\n", BALANCE_CODE + "  const usageTick = vue.ref(0);\n", "P4 余额查询")

# ────────────────────────────────────────────────────────────
# P5 render: 鲸娘 hero 里插入余额节点
# ────────────────────────────────────────────────────────────
sub1('''              }, vue.toDisplayString(_ctx.questionList.length ? "主人别急，马上就好" : "小鲸娘正在吃白饭"), 1)
            ])
          ], 2),''',
     '''              }, vue.toDisplayString(_ctx.questionList.length ? "主人别急，马上就好" : "小鲸娘正在吃白饭"), 1)
            ]),
            vue.createElementVNode("div", { class: "whale-hero__balance", innerHTML: heroBalanceHtml.value }, null, 8, ["innerHTML"])
          ], 2),''', "P5 hero 余额节点")

# ────────────────────────────────────────────────────────────
# P6 顶部标题栏加鲸娘徽标
# ────────────────────────────────────────────────────────────
sub1('''                vue.createElementVNode("div", _hoisted_2, [
                  vue.createElementVNode("span", null, vue.toDisplayString(currentPlatformName.value), 1)
                ]),''',
     '''                vue.createElementVNode("div", _hoisted_2, [
                  vue.createElementVNode("img", {
                    class: "card-header__logo",
                    src: HX_LOGO_SRC,
                    alt: ""
                  }),
                  vue.createElementVNode("span", null, vue.toDisplayString(currentPlatformName.value), 1)
                ]),''', "P6 标题徽标")

# ────────────────────────────────────────────────────────────
# P7 诊断探针：补 liquidGlass / session / balance
# ────────────────────────────────────────────────────────────
sub1('''      w.__HX_DIAG__ = () => {''',
     '''      w.__HX_SESSION_RESET__ = () => resetSessionUsage();
      w.__HX_BALANCE__ = () => fetchBalance();
      w.__HX_DIAG__ = () => {''', "P7a 诊断入口")

sub1('''          tabs: sr ? Array.from(sr.querySelectorAll(".el-tabs__item")).map((el) => (el.textContent || "").trim()) : []''',
     '''          liquidGlass: {
            scrolled: sr ? Boolean(sr.querySelector(".main-page.is-scrolled")) : null,
            tabShell: Boolean(q(".demo-tabs .el-tabs__nav")),
            glassCells: sr ? sr.querySelectorAll(".usage-cell,.setting>div,.guide-card,.question-card,.hero-balance").length : 0
          },
          session: sessionUsage(),
          sessionBase: { requests: sessionBase.requests, totalTokens: sessionBase.totalTokens, cost: sessionBase.cost },
          balance: {
            state: balanceStore.state,
            currency: balanceStore.currency,
            total: balanceStore.total,
            at: balanceStore.at,
            msg: balanceStore.msg
          },
          tabs: sr ? Array.from(sr.querySelectorAll(".el-tabs__item")).map((el) => (el.textContent || "").trim()) : []''',
     "P7b 诊断字段")

sub1('''            buildBadge: q(".usage-build"),''', '''            buildBadge: q(".usage-sub[data-hx-build]"),''', "P7c 探针改用 data-hx-build")

# ────────────────────────────────────────────────────────────
# P8 液态玻璃绑定（滚动触发态 + 两个可点元素）
# ────────────────────────────────────────────────────────────
GLASS_BIND = '''
  /* ── 液态玻璃：滚动触发态 + 可点元素（本次用量重置 / 余额刷新）──── */
  const bindLiquidGlass = () => {
    const root = hxShadow;
    if (!root) return false;
    const panel = root.querySelector(".main-page");
    root.addEventListener("scroll", (event) => {
      const target = event.target;
      if (!panel || !target || typeof target.scrollTop !== "number") return;
      panel.classList.toggle("is-scrolled", (target.scrollTop || 0) > 4);
    }, true);
    root.addEventListener("click", (event) => {
      const target = event.target;
      if (!target || typeof target.closest !== "function") return;
      if (target.closest(".usage-session")) {
        resetSessionUsage();
        try { logStore.addLog("本次用量统计已重置", "primary"); } catch (error) {}
        return;
      }
      if (target.closest(".hero-balance")) fetchBalance();
    }, true);
    return true;
  };
'''
sub1("  const CAN_USE_ADOPTED_SHEETS = (() => {", GLASS_BIND + "  const CAN_USE_ADOPTED_SHEETS = (() => {", "P8 液态玻璃绑定")

# ────────────────────────────────────────────────────────────
# P9 启动后接线
# ────────────────────────────────────────────────────────────
sub1('''      });
    } catch (error) {
      console.error("[探矿鲸娘] 面板挂载失败：", error);''',
     '''      });
      try { bindLiquidGlass(); } catch (error2) { /* 忽略 */ }
      setTimeout(() => {
        try { fetchBalance(); } catch (error2) { /* 忽略 */ }
      }, 1200);
      if (balanceTimer === null)
        balanceTimer = setInterval(() => {
          try { fetchBalance(); } catch (error2) { /* 忽略 */ }
        }, 6e5);
    } catch (error) {
      console.error("[探矿鲸娘] 面板挂载失败：", error);''', "P9 启动接线")

# ────────────────────────────────────────────────────────────
# P10 液态玻璃样式表
# ────────────────────────────────────────────────────────────
RULES = [
    ".main-page{--lg-rim:rgba(255,255,255,.30);--lg-rim-dim:rgba(255,255,255,.14);--lg-edge:rgba(140,200,255,.22);--lg-tint-hi:linear-gradient(155deg,rgba(255,255,255,.20),rgba(255,255,255,.07) 34%,rgba(10,22,46,.34) 100%);--lg-shadow-hi:0 12px 28px rgba(2,8,24,.42),0 0 20px rgba(56,226,255,.16),inset 0 1px 0 var(--lg-rim);--lg-t:background .28s ease,border-color .28s ease,box-shadow .28s ease,transform .28s cubic-bezier(.34,1.2,.64,1),backdrop-filter .28s ease,-webkit-backdrop-filter .28s ease,color .2s ease}",

    ".main-page .demo-tabs>.el-tabs__header{overflow:visible!important;margin:0 0 9px!important}",
    ".main-page .demo-tabs .el-tabs__nav-wrap{overflow:visible!important;border-bottom:none!important}",
    ".main-page .demo-tabs .el-tabs__nav-wrap::after{display:none!important;height:0!important;background:none!important}",
    ".main-page .demo-tabs .el-tabs__active-bar{display:none!important;opacity:0!important}",
    ".main-page .demo-tabs .el-tabs__nav{display:flex!important;align-items:center;gap:4px;padding:3px;border:1px solid rgba(140,200,255,.14);border-radius:13px;background:linear-gradient(150deg,rgba(255,255,255,.06),rgba(8,18,38,.24));backdrop-filter:blur(10px) saturate(150%);-webkit-backdrop-filter:blur(10px) saturate(150%);box-shadow:inset 0 1px 0 rgba(255,255,255,.12);transition:var(--lg-t)}",
    ".main-page .demo-tabs .el-tabs__item{position:relative;height:28px!important;line-height:28px!important;padding:0 7px!important;border:1px solid transparent!important;border-radius:10px!important;background:transparent!important;color:var(--hx-ink-dim)!important;font-size:11.5px!important;font-weight:600!important;letter-spacing:.2px;overflow:visible!important;transition:var(--lg-t)}",
    ".main-page .demo-tabs .el-tabs__item::before{content:'';position:absolute;inset:0;border-radius:9px;pointer-events:none;opacity:0;transition:opacity .28s ease;background:linear-gradient(160deg,rgba(255,255,255,.24),rgba(255,255,255,.05) 42%,transparent 74%)}",
    ".main-page .demo-tabs .el-tabs__item:hover{color:var(--hx-ink)!important;background:rgba(255,255,255,.07)!important;transform:translateY(-1px);box-shadow:0 4px 12px rgba(2,8,24,.26),inset 0 1px 0 rgba(255,255,255,.22)}",
    ".main-page .demo-tabs .el-tabs__item:hover::before{opacity:1}",
    ".main-page .demo-tabs .el-tabs__item.is-active{color:#fff!important;background:var(--lg-tint-hi)!important;border-color:rgba(56,226,255,.32)!important;transform:translateY(-1px);box-shadow:var(--lg-shadow-hi)}",
    ".main-page .demo-tabs .el-tabs__item.is-active::before{opacity:1}",
    ".main-page .demo-tabs .el-tabs__nav-wrap::before{content:none!important;display:none!important}",
    ".main-page .demo-tabs .el-tabs__item+.el-tabs__item{border-left:none!important;border-image:none!important;background-image:none!important}",
    ".main-page .demo-tabs .el-tabs__nav-scroll{overflow:visible!important}",
    ".main-page .demo-tabs .el-tabs__nav{border-left:none!important;border-right:none!important}",

    ".main-page .el-card__header{background:linear-gradient(180deg,rgba(56,226,255,.07),rgba(155,107,255,.03) 58%,transparent)!important;border-bottom:none!important;padding:9px 9px 3px!important}",
    ".main-page .card-header{gap:9px;padding:8px 11px!important;border:1px solid var(--lg-edge);border-radius:14px;background:linear-gradient(120deg,rgba(56,226,255,.14),rgba(74,140,255,.07) 46%,rgba(155,107,255,.14))!important;backdrop-filter:blur(12px) saturate(155%);-webkit-backdrop-filter:blur(12px) saturate(155%);box-shadow:0 6px 18px rgba(2,8,24,.28),inset 0 1px 0 var(--lg-rim);transition:var(--lg-t)}",
    ".main-page .card-header::after{display:none!important}",
    ".main-page .card-header:hover{border-color:rgba(56,226,255,.34);box-shadow:var(--lg-shadow-hi)}",
    ".main-page .card-header__logo{flex:none;width:24px;height:24px;border-radius:8px;object-fit:contain;background:radial-gradient(circle at 50% 42%,rgba(56,226,255,.20),rgba(6,14,30,.30));border:1px solid rgba(56,226,255,.26);box-shadow:0 2px 10px rgba(2,8,24,.32),inset 0 1px 0 rgba(255,255,255,.18);transition:var(--lg-t)}",
    ".main-page .card-header:hover .card-header__logo{transform:scale(1.06) rotate(-2deg);box-shadow:0 3px 14px rgba(56,226,255,.26),inset 0 1px 0 rgba(255,255,255,.26)}",
    ".main-page.is-scrolled .card-header{background:linear-gradient(120deg,rgba(56,226,255,.20),rgba(74,140,255,.12) 46%,rgba(155,107,255,.20))!important;box-shadow:0 10px 26px rgba(2,8,24,.42),inset 0 1px 0 var(--lg-rim)}",
    ".main-page.is-scrolled .demo-tabs .el-tabs__nav{background:linear-gradient(150deg,rgba(255,255,255,.10),rgba(8,18,38,.44));box-shadow:0 8px 22px rgba(2,8,24,.36),inset 0 1px 0 rgba(255,255,255,.18)}",

    ".main-page .usage-bar{--lg-blur:14px;border:1px solid var(--lg-edge)!important;border-radius:14px!important;background:linear-gradient(155deg,rgba(255,255,255,.085),rgba(255,255,255,.02) 40%,rgba(8,18,38,.28))!important;backdrop-filter:blur(var(--lg-blur)) saturate(155%);-webkit-backdrop-filter:blur(var(--lg-blur)) saturate(155%);box-shadow:0 6px 18px rgba(2,8,24,.26),inset 0 1px 0 var(--lg-rim-dim)!important;transition:var(--lg-t)}",
    ".main-page .usage-main{gap:6px}",
    ".main-page .usage-cell{border:none!important;border-radius:9px!important;background:linear-gradient(160deg,rgba(255,255,255,.075),rgba(255,255,255,.018) 58%,rgba(8,18,38,.20))!important;box-shadow:inset 0 1px 0 rgba(255,255,255,.14)!important;transition:var(--lg-t)}",
    ".main-page .usage-cell:hover{background:var(--lg-tint-hi)!important;transform:translateY(-1px);box-shadow:var(--lg-shadow-hi)!important}",
    ".main-page .usage-sub{gap:6px}",
    ".main-page .usage-tag{backdrop-filter:blur(8px);-webkit-backdrop-filter:blur(8px);transition:var(--lg-t)}",
    ".main-page .usage-tag:hover{transform:translateY(-1px)}",
    ".main-page .usage-session{display:inline-flex;align-items:center;gap:5px;margin-left:auto;padding:1px 9px;border:1px solid rgba(56,226,255,.26);border-radius:999px;background:linear-gradient(150deg,rgba(56,226,255,.14),rgba(56,226,255,.04));backdrop-filter:blur(10px) saturate(150%);-webkit-backdrop-filter:blur(10px) saturate(150%);box-shadow:inset 0 1px 0 rgba(255,255,255,.20);font-size:10px;line-height:15px;white-space:nowrap;cursor:pointer;transition:var(--lg-t)}",
    ".main-page .usage-session:hover{transform:translateY(-1px);border-color:rgba(56,226,255,.44);box-shadow:0 4px 12px rgba(2,8,24,.30),inset 0 1px 0 rgba(255,255,255,.28)}",
    ".main-page .usage-session__k{color:var(--hx-ink-dim)}",
    ".main-page .usage-session__v{color:var(--hx-cyan);font-weight:700;font-variant-numeric:tabular-nums}",

    ".main-page .whale-hero__bubble{border:1px solid var(--lg-edge)!important;background:linear-gradient(150deg,rgba(255,255,255,.10),rgba(255,255,255,.025) 40%,rgba(8,18,38,.26))!important;backdrop-filter:blur(16px) saturate(150%);-webkit-backdrop-filter:blur(16px) saturate(150%);box-shadow:0 6px 18px rgba(2,8,24,.26),inset 0 1px 0 var(--lg-rim-dim)!important;transition:var(--lg-t)}",
    ".main-page .whale-hero.is-idle .whale-hero__bubble{padding:5px 15px}",
    ".main-page .whale-hero__balance{flex:0 0 auto;display:flex;align-items:center;justify-content:center;width:100%;min-height:0;transition:opacity .28s ease,transform .28s ease,height .28s ease}",
    ".main-page .whale-hero.is-idle .whale-hero__balance{opacity:1;transform:none;margin-top:2px}",
    ".main-page .whale-hero.is-busy .whale-hero__balance{opacity:0;transform:translateY(-4px);height:0;overflow:hidden;pointer-events:none}",
    ".main-page .hero-balance{display:inline-flex;align-items:center;gap:7px;max-width:100%;padding:4px 12px;border:1px solid rgba(140,200,255,.22);border-radius:999px;background:linear-gradient(150deg,rgba(255,255,255,.12),rgba(255,255,255,.03) 38%,rgba(8,18,38,.30));backdrop-filter:blur(16px) saturate(155%);-webkit-backdrop-filter:blur(16px) saturate(155%);box-shadow:0 6px 18px rgba(2,8,24,.28),inset 0 1px 0 rgba(255,255,255,.22);font-size:11.5px;line-height:1.5;white-space:nowrap;cursor:pointer;transition:var(--lg-t)}",
    ".main-page .hero-balance:hover{transform:translateY(-1px);border-color:rgba(56,226,255,.38);box-shadow:var(--lg-shadow-hi)}",
    ".main-page .hero-balance__k{font-size:10.5px;letter-spacing:.3px;color:var(--hx-ink-dim)}",
    ".main-page .hero-balance__v{font-weight:700;font-variant-numeric:tabular-nums;color:var(--hx-cyan)}",
    ".main-page .hero-balance__hint{font-size:10px;color:#ffc46b}",
    ".main-page .hero-balance.is-low .hero-balance__v{color:#ffc46b}",
    ".main-page .hero-balance.is-void .hero-balance__v,.main-page .hero-balance.is-err .hero-balance__v{color:var(--hx-ink-dim);font-weight:600}",
    ".main-page .hero-balance.is-loading .hero-balance__v{animation:hxBalPulse 1.4s ease-in-out infinite}",
    "@keyframes hxBalPulse{0%,100%{opacity:.45}50%{opacity:1}}",

    ".main-page .setting>div{--lg-blur:18px;border:1px solid var(--lg-edge)!important;border-radius:14px!important;background:linear-gradient(155deg,rgba(255,255,255,.09),rgba(255,255,255,.022) 40%,rgba(8,18,38,.30))!important;backdrop-filter:blur(var(--lg-blur)) saturate(155%);-webkit-backdrop-filter:blur(var(--lg-blur)) saturate(155%);box-shadow:0 8px 22px rgba(2,8,24,.30),inset 0 1px 0 var(--lg-rim-dim)!important;transition:var(--lg-t)}",
    ".main-page .setting>div:hover{border-color:rgba(56,226,255,.34)!important;box-shadow:var(--lg-shadow-hi)!important;transform:translateY(-1px)}",
    ".main-page .setting>div.setting-ai{--lg-blur:20px;border-color:rgba(56,226,255,.30)!important}",
    ".main-page .guide-header{--lg-blur:16px;backdrop-filter:blur(var(--lg-blur)) saturate(155%);-webkit-backdrop-filter:blur(var(--lg-blur)) saturate(155%)}",
    ".main-page .guide-card{--lg-blur:12px;border:1px solid var(--lg-edge)!important;border-radius:12px!important;background:linear-gradient(155deg,rgba(255,255,255,.085),rgba(255,255,255,.02) 42%,rgba(8,18,38,.26))!important;backdrop-filter:blur(var(--lg-blur)) saturate(150%);-webkit-backdrop-filter:blur(var(--lg-blur)) saturate(150%);box-shadow:0 5px 16px rgba(2,8,24,.24),inset 0 1px 0 var(--lg-rim-dim)!important;transition:var(--lg-t)}",
    ".main-page .guide-card:hover{transform:translateY(-1px);border-color:rgba(56,226,255,.40)!important;background:var(--lg-tint-hi)!important;box-shadow:var(--lg-shadow-hi)!important}",
    ".main-page .script-home .el-scrollbar__view>div{--lg-blur:11px;backdrop-filter:blur(var(--lg-blur)) saturate(150%);-webkit-backdrop-filter:blur(var(--lg-blur)) saturate(150%);transition:var(--lg-t)}",
    ".main-page .script-home .el-scrollbar__view>div:hover{transform:translateX(1px);border-color:rgba(56,226,255,.34)!important}",
    ".main-page .question-card{--lg-blur:15px;border:1px solid var(--lg-edge)!important;border-radius:12px!important;background:linear-gradient(155deg,rgba(255,255,255,.085),rgba(255,255,255,.02) 44%,rgba(8,18,38,.26))!important;backdrop-filter:blur(var(--lg-blur)) saturate(150%);-webkit-backdrop-filter:blur(var(--lg-blur)) saturate(150%);box-shadow:0 5px 16px rgba(2,8,24,.24),inset 0 1px 0 var(--lg-rim-dim)!important;transition:var(--lg-t)}",
    ".main-page .question-card:hover{transform:translateY(-1px);border-color:rgba(56,226,255,.38)!important;box-shadow:var(--lg-shadow-hi)!important}",
    ".main-page .answer-legend{--lg-blur:10px;backdrop-filter:blur(var(--lg-blur)) saturate(145%);-webkit-backdrop-filter:blur(var(--lg-blur)) saturate(145%)}",
    "@media (prefers-reduced-motion:reduce){.main-page .card-header,.main-page .demo-tabs .el-tabs__item,.main-page .usage-cell,.main-page .usage-session,.main-page .hero-balance,.main-page .setting>div,.main-page .guide-card,.main-page .question-card{transition-duration:.01ms}}",
]

css_js = "  // ---- v0.4.4 液态玻璃（Liquid Glass）：悬浮胶囊 + 双态（静止 / 交互·吸顶滚动）----\n"
css_js += '  LAYOUT_CSS_PARTS.push(\n'
css_js += '    "\\n/* ==== v0.4.4 liquid glass ==== */"'
for r in RULES:
    assert '"' not in r, "CSS 规则里不能出现双引号：" + r
    css_js += '\n    + "\\n' + r + '"'
css_js += "\n  );\n"

sub1("  const layoutCss = LAYOUT_CSS_PARTS.join(\"\");", css_js + "  const layoutCss = LAYOUT_CSS_PARTS.join(\"\");", "P10 液态玻璃样式")

# ────────────────────────────────────────────────────────────
# 收尾：写回（全 CRLF）
# ────────────────────────────────────────────────────────────
assert "\r" not in t, "内部不应残留裸 CR"
out = t.replace("\n", "\r\n")
data = out.encode("utf-8")
open(P, "wb").write(data)

print(f"\n完成：{len(raw)} -> {len(data)} 字节（{len(data) - len(raw):+d}）")
print(f"CRLF = {out.count(chr(13) + chr(10))}")
print(f"裸 LF = {out.replace(chr(13) + chr(10), '').count(chr(10))}")
print(f"HX_BUILD 0.4.4 = {t.count('const HX_BUILD = \"0.4.4\"')}")
print(f"usage-session = {t.count('usage-session')}")
print(f"hero-balance = {t.count('hero-balance')}")
print(f"balanceStore = {t.count('balanceStore')}")
print(f"旧 usage-build 残留 = {t.count('usage-build')}")
