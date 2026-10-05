# -*- coding: utf-8 -*-
"""fix36：答题页底部用量统计栏 + 空状态上移。

统计栏 5 个指标（用户点名）：请求次数 / 消耗 Token / Token 速率 / 花费 / 峰谷
价格（元 per 百万 token，2026-08-17 起的峰谷定价）：
  deepseek-flash   平峰 0.05 / 1.5 / 4.5    高峰 0.10 / 3 / 9
  deepseek-v4-pro  平峰 0.15 / 4.5 / 13.5   高峰 0.30 / 9 / 27
  顺序 = 缓存命中输入 / 未命中输入 / 输出
高峰时段：北京时间工作日 09:00-12:00 与 14:00-18:00；周末与法定节假日为平峰。
（法定节假日无法程序化判定，预留 HOLIDAYS 常量）
"""
import io, os, re

P = r"C:\Users\D_A\DoubaoWork\chats\2026-10-05\new-chat-4\海底小纵队·探矿鲸娘.user.js"
L = []
src = io.open(P, encoding="utf-8", newline="").read()
NL = u"\r\n"
orig_len = len(src)

def rep(name, pattern, repl, count=1):
    global src
    rx = re.compile(pattern)
    n = len(rx.findall(src))
    if n != count:
        L.append(u"!! %s 命中 %d（期望 %d）" % (name, n, count))
        return False
    src = rx.sub(lambda m: repl, src, count=count)
    L.append(u"ok %s" % name)
    return True

# ================= 1) 统计模块（插在 callAIChat 之前） =================
STATS = (u'''  const USAGE_STATS_KEY = "hx_usage_stats_v1";
  const MODEL_PRICES = {
    "deepseek-flash": {
      off: { hit: 0.05, miss: 1.5, out: 4.5 },
      peak: { hit: 0.1, miss: 3, out: 9 }
    },
    "deepseek-v4-pro": {
      off: { hit: 0.15, miss: 4.5, out: 13.5 },
      peak: { hit: 0.3, miss: 9, out: 27 }
    }
  };
  const HOLIDAYS = [];
  const readUsageStats = () => {
    try {
      const raw = _GM_getValue(USAGE_STATS_KEY);
      if (raw && typeof raw === "object") return raw;
      if (typeof raw === "string" && raw) return JSON.parse(raw);
    } catch (error) {
      console.error(error);
    }
    return null;
  };
  const usageStore = vue.reactive({
    requests: 0, ok: 0, failed: 0,
    promptTokens: 0, completionTokens: 0,
    cacheHitTokens: 0, cacheMissTokens: 0, totalTokens: 0,
    elapsedMs: 0, cost: 0
  });
  (() => {
    const stored = readUsageStats();
    if (!stored) return;
    Object.keys(usageStore).forEach((key) => {
      const value = Number(stored[key]);
      if (isFinite(value) && value >= 0) usageStore[key] = value;
    });
  })();
  const persistUsageStats = () => {
    try {
      _GM_setValue(USAGE_STATS_KEY, JSON.stringify(Object.assign({}, usageStore)));
    } catch (error) {
      console.error(error);
    }
  };
  const beijingDate = (timestamp) => new Date((timestamp ?? Date.now()) + 288e5);
  const isPeakHour = (timestamp) => {
    const d = beijingDate(timestamp);
    const day = d.getUTCDay();
    const stamp = d.getUTCFullYear() * 1e4 + (d.getUTCMonth() + 1) * 100 + d.getUTCDate();
    if (day === 0 || day === 6 || HOLIDAYS.indexOf(stamp) >= 0) return false;
    const hour = d.getUTCHours();
    return hour >= 9 && hour < 12 || hour >= 14 && hour < 18;
  };
  const recordUsage = ({ model, usage, elapsedMs, success }) => {
    usageStore.requests += 1;
    if (success) usageStore.ok += 1;
    else usageStore.failed += 1;
    usageStore.elapsedMs += Math.max(Number(elapsedMs) || 0, 0);
    if (usage) {
      const num = (value) => isFinite(Number(value)) ? Number(value) : 0;
      const promptTokens = num(usage.prompt_tokens);
      const completionTokens = num(usage.completion_tokens);
      const totalTokens = num(usage.total_tokens) || promptTokens + completionTokens;
      const hitTokens = Math.max(num(usage.prompt_cache_hit_tokens), 0);
      const missTokens = Math.max(num(usage.prompt_cache_miss_tokens) || promptTokens - hitTokens, 0);
      const table = MODEL_PRICES[model] || MODEL_PRICES["deepseek-flash"];
      const rate = isPeakHour() ? table.peak : table.off;
      usageStore.promptTokens += promptTokens;
      usageStore.completionTokens += completionTokens;
      usageStore.cacheHitTokens += hitTokens;
      usageStore.cacheMissTokens += missTokens;
      usageStore.totalTokens += totalTokens;
      usageStore.cost += (hitTokens * rate.hit + missTokens * rate.miss + completionTokens * rate.out) / 1e6;
    }
    persistUsageStats();
  };
  const formatTokenCount = (value) => {
    const v = Number(value) || 0;
    if (v <= 0) return "0";
    if (v < 1e3) return String(Math.round(v));
    if (v < 1e4) return (v / 1e3).toFixed(1) + "k";
    if (v < 1e6) return (v / 1e4).toFixed(1) + "\\u4e07";
    return (v / 1e6).toFixed(2) + "M";
  };
  const formatCost = (value) => {
    const v = Number(value) || 0;
    if (v <= 0) return "\\u00a50";
    if (v < 0.01) return "\\u00a5" + v.toFixed(4);
    return "\\u00a5" + v.toFixed(2);
  };
  const formatRate = (store) => {
    const seconds = store.elapsedMs / 1e3;
    if (!seconds || !store.completionTokens) return "\\u2014";
    const rate = store.completionTokens / seconds;
    return (rate >= 100 ? rate.toFixed(0) : rate.toFixed(1)) + " tok/s";
  };
  const buildUsageBarHtml = (store, peak) => {
    const cells = [
      ["\\u8bf7\\u6c42", String(store.requests)],
      ["Token", formatTokenCount(store.totalTokens)],
      ["\\u82b1\\u8d39", formatCost(store.cost)]
    ].map(([label, value]) => '<div class="usage-cell"><span class="usage-cell__k">' + label
      + '</span><span class="usage-cell__v">' + value + "</span></div>").join("");
    return '<div class="usage-main">' + cells + "</div>"
      + '<div class="usage-sub">'
      + '<span class="usage-tag ' + (peak ? "is-peak" : "is-off") + '">' + (peak ? "\\u9ad8\\u5cf0" : "\\u5e73\\u5cf0") + "</span>"
      + '<span class="usage-rate">' + formatRate(store) + "</span>"
      + "</div>";
  };
  const usageTick = vue.ref(0);
  setInterval(() => {
    usageTick.value += 1;
  }, 6e4);
  const usageBarHtml = vue.computed(() => {
    void usageTick.value;
    return buildUsageBarHtml(usageStore, isPeakHour());
  });
''').replace(u"\n", NL)

anchor1 = u"  const callAIChat = ({ url, apiKey, body }) => new Promise((resolve) => {"
if src.count(anchor1) == 1:
    src = src.replace(anchor1, STATS + anchor1, 1)
    L.append(u"ok 1 统计模块已插入")
else:
    L.append(u"!! 1 命中 %d" % src.count(anchor1))

# ================= 2) 计时起点 =================
rep(u"2 计时起点",
    u'    const headers = \\{ "Content-Type": "application/json" \\};',
    u'    const headers = { "Content-Type": "application/json" };' + NL + u'    const startedAt = Date.now();')

# ================= 3) 成功分支记账 =================
rep(u"3 成功分支记账",
    u'          if \\(!values\\.length && message\\.reasoning_content\\) values = extractAnswerFromReasoning\\(message\\.reasoning_content\\);',
    u'          if (!values.length && message.reasoning_content) values = extractAnswerFromReasoning(message.reasoning_content);' + NL
    + u'          recordUsage({ model: body && body.model, usage: parsed.usage, elapsedMs: Date.now() - startedAt, success: values.length > 0 });')

# ================= 4) HTTP 失败分支记账 =================
rep(u"4 HTTP 失败记账",
    u'        const m = parsed && parsed\\.error \\? parsed\\.error\\.message : "";',
    u'        recordUsage({ model: body && body.model, usage: null, elapsedMs: Date.now() - startedAt, success: false });' + NL
    + u'        const m = parsed && parsed.error ? parsed.error.message : "";')

# ================= 5) onerror / ontimeout 记账 =================
OLD_TAIL = (u'      onerror: () => resolve({ kind: "fail", msg: "\u7f51\u7edc\u9519\u8bef\uff0c\u65e0\u6cd5\u8fde\u63a5 AI \u670d\u52a1" }),'
            + NL
            + u'      ontimeout: () => resolve({ kind: "fail", msg: "AI \u8bf7\u6c42\u8d85\u65f6\uff0c\u8bf7\u7a0d\u540e\u91cd\u8bd5" })')
NEW_TAIL = (u'      onerror: () => {' + NL
            + u'        recordUsage({ model: body && body.model, usage: null, elapsedMs: Date.now() - startedAt, success: false });' + NL
            + u'        resolve({ kind: "fail", msg: "\u7f51\u7edc\u9519\u8bef\uff0c\u65e0\u6cd5\u8fde\u63a5 AI \u670d\u52a1" });' + NL
            + u'      },' + NL
            + u'      ontimeout: () => {' + NL
            + u'        recordUsage({ model: body && body.model, usage: null, elapsedMs: Date.now() - startedAt, success: false });' + NL
            + u'        resolve({ kind: "fail", msg: "AI \u8bf7\u6c42\u8d85\u65f6\uff0c\u8bf7\u7a0d\u540e\u91cd\u8bd5" });' + NL
            + u'      }')
if src.count(OLD_TAIL) == 1:
    src = src.replace(OLD_TAIL, NEW_TAIL, 1)
    L.append(u"ok 5 onerror/ontimeout 记账")
else:
    L.append(u"!! 5 命中 %d" % src.count(OLD_TAIL))

# ================= 6) 渲染：把统计栏加为答题页第 4 个 flex 子节点（底部固定） =================
ANCHOR6 = (u'          ], 512), [' + NL
           + u'            [vue.vShow, !_ctx.questionList.length]' + NL
           + u'          ])' + NL
           + u'        ], 64);')
NEW6 = (u'          ], 512), [' + NL
        + u'            [vue.vShow, !_ctx.questionList.length]' + NL
        + u'          ]),' + NL
        + u'          vue.createElementVNode("div", { class: "usage-bar", innerHTML: usageBarHtml.value }, null, 8, ["innerHTML"])' + NL
        + u'        ], 64);')
if src.count(ANCHOR6) == 1:
    src = src.replace(ANCHOR6, NEW6, 1)
    L.append(u"ok 6 统计栏已挂到答题页底部")
else:
    L.append(u"!! 6 命中 %d" % src.count(ANCHOR6))

# ================= 7) 空状态上移 =================
OLD7 = u'.main-page .el-tab-pane>div:has(>.el-empty){flex:1 1 auto!important;min-height:0!important;display:flex!important;flex-direction:column;align-items:center;justify-content:center;width:100%!important}'
NEW7 = u'.main-page .el-tab-pane>div:has(>.el-empty){flex:1 1 auto!important;min-height:0!important;display:flex!important;flex-direction:column;align-items:center;justify-content:center;width:100%!important;box-sizing:border-box!important;padding-bottom:34px!important}'
if src.count(OLD7) == 1:
    src = src.replace(OLD7, NEW7, 1)
    L.append(u"ok 7 空状态上移 padding-bottom:34px")
else:
    L.append(u"!! 7 命中 %d" % src.count(OLD7))

# ================= 8) 统计栏 CSS =================
OLD8 = u'.main-page .setting .el-switch.is-checked .el-switch__core .el-switch__action{color:var(--hx-cyan,#38e2ff)}"'
if src.count(OLD8) != 1:
    L.append(u"!! 8 CSS 锚点命中 %d" % src.count(OLD8))
else:
    CSS = [
        u'.main-page .usage-bar{flex:0 0 auto!important;margin-top:6px!important;padding:7px 9px 8px!important;border:1px solid var(--hx-line);border-radius:11px;background:linear-gradient(135deg,rgba(18,32,62,.52),rgba(12,22,44,.34));box-shadow:0 3px 10px rgba(2,8,24,.18);box-sizing:border-box;max-width:100%}',
        u'.main-page .usage-main{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:5px}',
        u'.main-page .usage-cell{display:flex;align-items:baseline;justify-content:space-between;gap:4px;min-width:0;padding:3px 6px;border-radius:8px;background:rgba(255,255,255,.045);border:1px solid rgba(120,190,255,.13)}',
        u'.main-page .usage-cell__k{flex:0 0 auto;font-size:10px;line-height:15px;color:var(--hx-ink-dim);white-space:nowrap}',
        u'.main-page .usage-cell__v{flex:1 1 auto;min-width:0;text-align:right;font-size:11.5px;line-height:15px;font-weight:600;color:var(--hx-cyan);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}',
        u'.main-page .usage-sub{display:flex;align-items:center;justify-content:space-between;gap:6px;margin-top:5px;padding:0 2px}',
        u'.main-page .usage-tag{flex:0 0 auto;padding:1px 7px;border-radius:20px;font-size:10px;line-height:15px;border:1px solid;white-space:nowrap}',
        u'.main-page .usage-tag.is-peak{color:#ffc46b;border-color:rgba(255,196,107,.38);background:rgba(255,196,107,.10)}',
        u'.main-page .usage-tag.is-off{color:#4ade80;border-color:rgba(74,222,128,.34);background:rgba(74,222,128,.10)}',
        u'.main-page .usage-rate{flex:0 0 auto;font-size:10.5px;line-height:15px;color:var(--hx-ink-dim);white-space:nowrap}',
    ]
    add = u"".join(NL + u'    + "\\n' + c + u'"' for c in CSS)
    src = src.replace(OLD8, OLD8 + add, 1)
    L.append(u"ok 8 CSS 追加 %d 条" % len(CSS))

bad = [x for x in L if x.startswith("!!")]
io.open(P, "w", encoding="utf-8", newline="").write(src)
crlf = src.count(NL); bare = src.count(u"\n") - crlf
L.append(u"chars: %d -> %d ; CRLF=%d bareLF=%d" % (orig_len, len(src), crlf, bare))
io.open(r"C:\Users\D_A\WorkBuddy\2026-10-05-13-53-42\_fix36.txt", "w", encoding="utf-8").write(u"\n".join(L))
print(u"\n".join(L))
if bad:
    print("HAS_FAIL")
