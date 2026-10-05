// _verify47.js —— 0.4.9 回归验收：语法 + CSS 真实求值 + 级联顺序 + 好感度分档数据真实求值 + 旧功能不回归
const fs = require("fs");
const vm = require("vm");
const util = require("util");
const P = "C:\\Users\\D_A\\DoubaoWork\\chats\\2026-10-05\\new-chat-4\\海底小纵队·探矿鲸娘.user.js";
const OUT = "C:\\Users\\D_A\\WorkBuddy\\2026-10-05-13-53-42\\_v47out.txt";
const buf = fs.readFileSync(P);
const src = buf.toString("utf8");
const out = { lines: [], push() { this.lines.push(util.format.apply(null, arguments)); }, join(s) { return this.lines.join(s); } };
const fail = [];

// ---------- 0. 字节 / 行尾 ----------
const crlf = (buf.toString("latin1").match(/\r\n/g) || []).length;
const bareLF = (buf.toString("latin1").replace(/\r\n/g, "").match(/\n/g) || []).length;
out.push("字节数 = %d", buf.length);
out.push("CRLF = %d", crlf);
out.push("裸 LF = %d（应为 0）", bareLF);
if (bareLF !== 0) fail.push("存在裸 LF " + bareLF + " 个");
if (crlf === 0) fail.push("未检测到 CRLF");

// ---------- 0b. 语法 ----------
try { new vm.Script(src, { filename: "whale.user.js" }); out.push("语法解析：通过（vm.Script）"); }
catch (e) { fail.push("语法解析失败：" + e.message); }

// ---------- 1. 好感度分档数据：真实求值 ----------
out.push("");
out.push("好感度分档数据（从源码里把 HX_FAV_TIERS 字面量抠出来真实求值）：");
let tiers = null;
{
  const ti = src.indexOf("const HX_FAV_TIERS = [");
  if (ti < 0) fail.push("找不到 HX_FAV_TIERS 字面量");
  else {
    const open = src.indexOf("[", ti);
    let d = 0, end = -1;
    for (let i = open; i < src.length; i++) {
      if (src[i] === "[") d++;
      else if (src[i] === "]") { d--; if (d === 0) { end = i; break; } }
    }
    const lit = src.slice(open, end + 1);
    try {
      tiers = new Function("return " + lit + ";")();
      out.push("  [OK] 真实求值成功：%d 级", tiers.length);
    } catch (e) { fail.push("HX_FAV_TIERS 求值失败：" + e.message); }
  }
}
if (tiers) {
  const ats = tiers.map((t) => t.at);
  const lvs = tiers.map((t) => t.lv);
  const counts = tiers.map((t) => (t.lines || []).length);
  const total = counts.reduce((a, b) => a + b, 0);
  const allNamed = tiers.every((t) => typeof t.name === "string" && t.name && typeof t.tag === "string" && t.tag);
  const flat = [].concat.apply([], tiers.map((t) => t.lines || []));
  const allPlaceholder = flat.every((x) => x.indexOf("{n}") === 0);
  const uniq = new Set(flat).size;
  out.push("  等级 = %s", lvs.join("/"));
  out.push("  门槛(¥) = %s", ats.join("/"));
  out.push("  每级条数 = %s（合计 %d）", counts.join("/"), total);
  const chk = [
    ["级数 = 5", tiers.length === 5],
    ["门槛 = 0/1/2/5/10", JSON.stringify(ats) === JSON.stringify([0, 1, 2, 5, 10])],
    ["等级号 = 1..5", JSON.stringify(lvs) === JSON.stringify([1, 2, 3, 4, 5])],
    ["每级 10 条", counts.every((n) => n === 10)],
    ["合计 50 条", total === 50],
    ["每级都有名称+称号", allNamed],
    ["每条都以 {n} 开头（小名可替换）", allPlaceholder],
    ["50 条无重复", uniq === 50]
  ];
  for (const [label, ok] of chk) {
    out.push("  [%s] %s", ok ? "OK" : "NG", label);
    if (!ok) fail.push("好感度数据不符：" + label);
  }
  out.push("  首条 = %s", JSON.stringify(flat[0]));
  out.push("  末条 = %s", JSON.stringify(flat[49]));
}

// ---------- 2. CSS 装配区间 + 真实求值 ----------
const MARK = 'const layoutCss = LAYOUT_CSS_PARTS.join("")';
const i0 = src.indexOf("const LAYOUT_CSS_PARTS = [");
const jt = src.indexOf(MARK, i0);
if (i0 < 0 || jt < 0) fail.push("找不到 LAYOUT_CSS_PARTS 区间");
const region = src.slice(i0, jt + MARK.length);
out.push("");
out.push("CSS 装配区间长度 %d", region.length);

const stripped = region
  .replace(/"(?:[^"\\]|\\.)*"/gs, '""')
  .replace(/'(?:[^'\\]|\\.)*'/gs, "''")
  .replace(/\/\*(?:[\s\S]*?)\*\//g, "")
  .replace(/\/\/[^\n]*/g, "");
const ids = new Set();
stripped.replace(/\b([A-Za-z_$][\w$]*)\b/g, (m, w) => { ids.add(w); return m; });
const declared = new Set();
stripped.replace(/\b(?:const|let|var)\s+([A-Za-z_$][\w$]*)/g, (m, w) => { declared.add(w); return m; });
const KEYWORDS = new Set(["const","let","var","if","else","return","typeof","true","false","null",
  "void","function","new","String","Number","Math","Boolean","window","document","Array","Object",
  "undefined","for","of","in","while","break","continue","push","join","length","slice","replace"]);
const externals = [...ids].filter((w) => !declared.has(w) && !KEYWORDS.has(w));
out.push("区间内声明 %d 个；外部引用：%s", declared.size, externals.join(", ") || "无");

let css = null;
try {
  const stubs = externals.map((n) => "const " + n + ' = "";').join("\n");
  css = new Function(stubs + "\n" + region + '\nreturn LAYOUT_CSS_PARTS.join("");')();
  out.push("真实求值：成功，装配后 CSS 长度 %d", css.length);
} catch (e) { fail.push("真实求值失败：" + e.message); }

if (css) {
  let d = 0, minD = 0;
  for (const ch of css) { if (ch === "{") d++; else if (ch === "}") { d--; if (d < minD) minD = d; } }
  out.push("花括号终值深度 = %d（应为 0），历史最小 = %d（不应 <0）", d, minD);
  if (d !== 0) fail.push("花括号不配平 " + d);
  if (minD < 0) fail.push("存在提前闭合的 }");
  const pollute = (css.match(/\\n/g) || []).length;
  out.push("字面 反斜杠n 污染 = %d（应为 0）", pollute);
  if (pollute !== 0) fail.push("\\n 双转义污染 " + pollute + " 处");
  out.push("真实换行 = %d", (css.match(/\n/g) || []).length);

  // ---------- 2a. 级联顺序 ----------
  out.push("");
  out.push("级联顺序（新块必须晚于旧块，后者胜出）：");
  const last = (s) => css.lastIndexOf(s);
  const order = [
    ["好感度面板：晚于 0.4.8 玻璃化块",
      ".main-page .setting-fav-field{",
      ".main-page .el-card::before{content:'';position:absolute;inset:-16px;"],
    ["好感度面板：晚于 0.4.7 液态玻璃块",
      ".main-page .setting-fav-field{",
      "/* ==== v0.4.9 liquid glass ==== */"],
    ["好感度面板：晚于「本次运行时长」胶囊",
      ".main-page .fav-bar>i{",
      ".main-page .usage-uptime{"],
    ["好感度分节注释在最后一块",
      "/* ==== v0.4.9 : 好感度面板",
      "/* ==== v0.4.9-d : 可见光带"],
  ];
  for (const [label, newer, older] of order) {
    const a = last(newer), b = last(older);
    const ok = a > b && a >= 0 && b >= 0;
    out.push("  [%s] %s (新@%d > 旧@%d)", ok ? "OK" : "NG", label, a, b);
    if (!ok) fail.push("级联顺序错：" + label);
  }

  // ---------- 2b. 规则存在性 ----------
  const rules = [
    // —— 0.4.9 本轮 ——
    ["/* ==== v0.4.9 : 好感度面板", "0.4.9 分节注释"],
    [".main-page .setting-fav-field{margin:2px 0 8px;", "好感度卡片容器"],
    ["backdrop-filter:blur(11px) saturate(140%)", "好感度卡玻璃底"],
    [".main-page .fav-head{display:flex", "好感度标题行"],
    [".main-page .fav-lv{", "等级胶囊"],
    [".main-page .fav-info{", "ⓘ 信息按钮"],
    [".main-page .fav-info:hover{", "ⓘ 悬停发光"],
    [".main-page .fav-bar{", "进度条轨道"],
    [".main-page .fav-bar>i{display:block;height:100%;width:0;", "进度条填充"],
    ["transition:width .5s cubic-bezier(.22,1,.36,1)", "进度条过渡"],
    [".main-page .fav-meta{display:flex", "累计/还差 文案行"],
    [".main-page .fav-note{display:none;", "说明默认收起"],
    [".main-page .setting-fav-field.is-open .fav-note{display:block", "点 ⓘ 展开说明"],
    ["@keyframes favNoteIn{", "说明入场关键帧"],
    [".main-page .fav-note .fav-tiers li>span:first-child{flex:0 0 62px", "等级清单两列"],
    // —— 0.4.8 回归 ——
    ["@keyframes hxBgSweep{", "背景扫掠关键帧"],
    ["@keyframes hxBgBreathe{", "背景呼吸关键帧"],
    [".main-page .el-card::before{content:'';position:absolute;inset:-16px;", "光带搬到卡片上"],
    [".main-page .el-card__body::after{content:'';position:absolute;inset:0;", "卡片内扫掠层"],
    [".main-page .usage-uptime{", "本次运行时长"],
    [".main-page .setting>div.setting-ai .el-form-item.setting-pet-field", "小名字段样式"],
    // —— 0.4.7 回归 ——
    [".main-page{isolation:isolate}", "主面板隔离层"],
    ["@keyframes hxHeroGlowA{", "鲸娘青光团关键帧"],
    ["@keyframes hxWhaleAura{", "头像随相光晕关键帧"],
    ["@keyframes hxLineIn{", "空闲文案入场关键帧"],
    // —— 0.4.6 / 0.4.5 / 更早回归 ——
    [".main-page .demo-tabs .el-tabs__item:active{transform:none!important}", "标签位移归零"],
    ["@keyframes hxDotPulse{", "状态灯脉冲关键帧"],
    [".hx-status-dot[data-hx-status='run']{color:#4ade80", "状态灯-绿"],
    [".hx-status-dot[data-hx-status='busy']{color:#ffc857", "状态灯-黄"],
    [".hx-status-dot[data-hx-status='stop']{color:#ff6b6b", "状态灯-红"],
    [".main-page .whale-hero__avatar{flex:0 0 auto}", "头像禁止收缩"],
    [".main-page .demo-tabs .el-tabs__nav{display:flex!important;width:100%!important;", "标签行铺满无 dock"],
    ["@keyframes hxMiniGlow{", "最小化发光关键帧"],
    [".main-page{--lg-rim:", "液态玻璃变量集"],
    [".main-page .card-header__logo{", "标题栏徽标"],
    [".main-page .usage-session{display:inline-flex", "「本次」用量胶囊"],
    [".main-page .hero-balance{display:inline-flex", "英雄区余额胶囊"],
    [".main-page .el-card:has(.card_content[style*='display: none']),.main-page .el-card:has(.card_content[style*='display:none']){height:auto", "最小化高度解锁"]
  ];
  out.push("");
  out.push("CSS 规则存在性：");
  for (const [needle, label] of rules) {
    const ok = css.includes(needle);
    out.push("  [%s] %s", ok ? "有" : "缺", label);
    if (!ok) fail.push("缺少 CSS 规则：" + label);
  }
}

// ---------- 3. JS 标识符 ----------
const decls = {
  build: [/const HX_BUILD = "0\.4\.9";/],
  favTiers: [/const HX_FAV_TIERS = \[/],
  favCost: [/const hxFavCost = \(\) => \{/, /const c = Number\(usageStore\.cost\);/],
  favFallback: [/const rawStats = _GM_getValue\("hx_usage_stats_v1"\);/, /const c2 = Number\(parsedStats && parsedStats\.cost\);/],
  favMoney: [/const hxFavMoney = \(value\) => \{/, /hxFavMoney\(cost\)/, /hxFavMoney\(Math\.max\(next\.at - cost, 0\)\)/],
  paintGuarded: [/try \{ paintFavCard\(el\); \} catch \(error\) \{ \/\* 忽略 \*\/ \}/],
  favLevel: [/const hxFavLevelIdx = \(\) => \{/],
  favTotal: [/const hxFavTotalLines = \(\) => \{/],
  unlocked: [/const hxUnlockedLines = \(\) => \{/],
  lineCount: [/const hxLineCount = \(\) => hxUnlockedLines\(\)\.length;/],
  lineText: [/const hxLineText = \(idx\) => \{/, /String\(raw\)\.split\("\{n\}"\)\.join\(hxPetName\(\)\)/],
  petName: [/const hxPetName = \(\) => \{/, /parsed\.ai\.petName/],
  paintFav: [/const paintFavCard = \(el\) => \{/, /barEl\.style\.width = wv;/],
  mountFav: [/const mountFavCard = \(\) => \{/, /root\.querySelector\('\.setting-ai \.setting-pet-field'\)/, /root\.querySelector\('\.setting-ai \.setting-fav-field'\)/],
  bindFav: [/const bindFavCard = \(\) => \{/, /if \(hxFavTimer === null\) hxFavTimer = setInterval\(ensure, 1500\);/],
  favState: [/let hxFavOpen = false;/, /let hxFavTimer = null;/],
  favNote: [/const hxFavNoteHtml = \(\) => '<div class="fav-note">'/, /const hxFavTierRows = \(\) => HX_FAV_TIERS\.map/],
  favProbe: [/w\.__HX_FAV__ = \(\) => \{/],
  favCalled: [/try \{ bindFavCard\(\); \} catch \(error2\) \{ \/\* 忽略 \*\/ \}/],
  rollPool: [/if \(hxLineCount\(\) > 1\) \{/, /next = Math\.floor\(Math\.random\(\) \* hxLineCount\(\)\);/],
  idleLine: [/let hxIdleLine = hxLineText\(hxIdleLineIdx\);/, /const line = hxLineText\(hxIdleLineIdx\);/],
  schedRoll: [/const scheduleIdleRoll = \(\) => \{/, /4200 \+ Math\.floor\(Math\.random\(\) \* 3600\)/],
  lineProbe: [/w\.__HX_LINE__ = \(\) => hxIdleLine;/],
  nameProbe: [/w\.__HX_NAME__ = \(\) => hxPetName\(\);/],
  tabProbe: [/w\.__HX_TAB__ = \(\) => \(\{ active: hxActiveTabIndex\(\)/],
  statusProbe: [/w\.__HX_STATUS__ = \(\) => readPanelStatus\(\);/],
  diagFav: [/fav: \{ cost: hxFavCost\(\), level: hxFavLevelIdx\(\) \+ 1,/],
  bindLiquidGlass: [/const bindLiquidGlass = \(\) => \{/, /bindLiquidGlass\(\)/],
  bindStatusDot: [/const bindStatusDot = \(\) => \{/, /bindStatusDot\(\);/],
  bindIdle: [/const bindIdleLines = \(\) => \{/, /bindIdleLines\(\);/],
  bindTabRouter: [/const bindTabRouter = \(\) => \{/, /bindTabRouter\(\);/],
  minHeightVar: [/root\.host\.style\.setProperty\("--hx-min-h", measuredH \+ 3 \+ "px"\);/],
  renameOnly: [/"仅仅作答"/, /const VIDEO_QUIZ_SETTING = "弹题作答";/],
  panelMark: [/shadowHost\.setAttribute\(PANEL_MARK_ATTR, HX_RUN_ID\);/]
};
out.push("");
out.push("JS 标识符：");
for (const k of Object.keys(decls)) {
  const hits = decls[k].map((re) => (src.match(new RegExp(re.source, "g")) || []).length);
  const ok = hits.every((n) => n >= 1);
  out.push("  [%s] %s 命中 %s", ok ? "OK" : "NG", k, hits.join("/"));
  if (!ok) fail.push("标识符不完整：" + k);
}

// ---------- 4. 结构不变量 ----------
out.push("");
out.push("结构不变量：");
const nGet = (s) => src.split(s).length - 1;
const inv = [
  ["0.4.8 残留", nGet("0.4.8"), 0],
  ["HX_IDLE_LINES 残留（旧扁平池）", nGet("HX_IDLE_LINES"), 0],
  ["{n} 占位总数 = 50 条语录 + 2 处代码", nGet("{n}"), 52],
  ["门槛字面量 at: 0", nGet("at: 0,"), 1],
  ["门槛字面量 at: 1", nGet("at: 1,"), 1],
  ["门槛字面量 at: 2", nGet("at: 2,"), 1],
  ["门槛字面量 at: 5", nGet("at: 5,"), 1],
  ["门槛字面量 at: 10", nGet("at: 10,"), 1],
  ["fav-note 节点构造", nGet('class="fav-note"'), 1],
  ["fav-tiers 清单", nGet('class="fav-tiers"'), 1],
  ["fav-info 按钮", nGet('class="fav-info"'), 1],
  ["小名字段（render）", nGet("setting-ai-field setting-pet-field"), 1],
  ["配置默认 ai.petName", nGet("petName: \"小鲸娘\""), 1],
  ["sanitize petName", nGet("if (typeof ai.petName !== \"string\")"), 1],
  ["标签名「状态」保留", nGet('label: "状态"'), 1],
  ["标签名「通知」未回退", nGet('label: "通知"'), 0],
  ["whale-page 根", nGet('class: "whale-page"'), 1],
  ["ElEmpty 残留", nGet('resolveComponent("el-empty")'), 0],
  ["usage-build 残留", nGet("usage-build"), 0],
  ["autoAnswer 路由块", nGet("const hxActiveTabIndex = "), 1]
];
for (const [label, actual, expect] of inv) {
  const ok = actual === expect;
  out.push("  [%s] %s 实际 %d / 期望 %d", ok ? "OK" : "NG", label, actual, expect);
  if (!ok) fail.push("不变量不符：" + label);
}
out.push("  [--] LAYOUT_CSS_PARTS.push 次数 = %d（信息）", nGet("LAYOUT_CSS_PARTS.push("));

out.push("");
out.push(fail.length ? "==== 失败 " + fail.length + " 项 ====" : "==== 全部通过 ====");
fail.forEach((f) => out.push("  ! " + f));

fs.writeFileSync(OUT, out.join("\n"), "utf8");
process.exit(fail.length ? 1 : 0);
