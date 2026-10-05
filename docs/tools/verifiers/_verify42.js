// _verify42.js —— 0.4.4 回归验收：语法解析 + CSS 装配真实求值 + 新增标识符 + 结构不变量
const fs = require("fs");
const vm = require("vm");
const util = require("util");
const P = "C:\\Users\\D_A\\DoubaoWork\\chats\\2026-10-05\\new-chat-4\\海底小纵队·探矿鲸娘.user.js";
const buf = fs.readFileSync(P);
const src = buf.toString("utf8");
const out = {
  lines: [],
  push() { this.lines.push(util.format.apply(null, arguments)); },
  join(s) { return this.lines.join(s); }
};
const fail = [];

// ---------------- 0. 行尾/字节（一律 Node 逐字节，不信 PowerShell）----------------
const crlf = (buf.toString("latin1").match(/\r\n/g) || []).length;
const bareLF = (buf.toString("latin1").replace(/\r\n/g, "").match(/\n/g) || []).length;
out.push("字节数 = %d", buf.length);
out.push("CRLF = %d", crlf);
out.push("裸 LF = %d（应为 0）", bareLF);
if (bareLF !== 0) fail.push("存在裸 LF " + bareLF + " 个");
if (crlf === 0) fail.push("未检测到 CRLF");

// ---------------- 0b. 语法解析 ----------------
try {
  new vm.Script(src, { filename: "whale.user.js" });
  out.push("语法解析：通过（vm.Script）");
} catch (e) {
  fail.push("语法解析失败：" + e.message);
}

// ---------------- 1. 提取 CSS 装配区间 ----------------
const MARK = 'const layoutCss = LAYOUT_CSS_PARTS.join("")';
const i0 = src.indexOf("const LAYOUT_CSS_PARTS = [");
const jt = src.indexOf(MARK, i0);
if (i0 < 0 || jt < 0) fail.push("找不到 LAYOUT_CSS_PARTS 区间");
const region = src.slice(i0, jt + MARK.length);
out.push("CSS 装配区间：%d..%d 长度 %d", i0, jt, region.length);

// ---------------- 2. 外部标识符打桩求值 ----------------
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
out.push("区间内声明标识符 %d 个；外部引用：%s", declared.size, externals.join(", ") || "无");

let css = null;
try {
  const stubs = externals.map((n) => "const " + n + ' = "";').join("\n");
  css = new Function(stubs + "\n" + region + '\nreturn LAYOUT_CSS_PARTS.join("");')();
  out.push("真实求值：成功，装配后 CSS 长度 %d", css.length);
} catch (e) {
  fail.push("真实求值失败：" + e.message);
}

if (css) {
  let d = 0, minD = 0;
  for (const ch of css) { if (ch === "{") d++; else if (ch === "}") { d--; if (d < minD) minD = d; } }
  out.push("花括号终值深度 = %d（应为 0），历史最小 = %d（不应 <0）", d, minD);
  if (d !== 0) fail.push("花括号不配平 " + d);
  if (minD < 0) fail.push("存在提前闭合的 }");

  const pollute = (css.match(/\\n/g) || []).length;
  out.push("字面 '\\\\n' 污染 = %d（应为 0）", pollute);
  if (pollute !== 0) fail.push("\\n 双转义污染 " + pollute + " 处");
  out.push("真实换行 = %d", (css.match(/\n/g) || []).length);

  const rules = [
    // —— 本轮新增：液态玻璃 ——
    ["/* ==== v0.4.4 liquid glass ==== */", "液态玻璃分节注释"],
    [".main-page{--lg-rim:", "液态玻璃变量集"],
    [".main-page .demo-tabs .el-tabs__nav{display:flex", "标签条改玻璃胶囊行"],
    [".main-page .demo-tabs .el-tabs__active-bar{display:none", "去掉标签下划条"],
    [".main-page .demo-tabs .el-tabs__nav-wrap::after{display:none", "去掉导航横条"],
    [".main-page .demo-tabs .el-tabs__item:hover{color:var(--hx-ink)!important", "标签悬停浮起"],
    [".main-page .demo-tabs .el-tabs__item:hover", "标签悬停规则"],
    ["transform:translateY(-1px)", "悬停位移"],
    [".main-page .demo-tabs .el-tabs__item.is-active{color:#fff", "标签激活态"],
    [".main-page .demo-tabs .el-tabs__item+.el-tabs__item{border-left:none", "去掉标签间竖分隔线"],
    [".main-page .demo-tabs .el-tabs__nav-wrap::before{content:none", "去掉导航伪元素竖线"],
    [".main-page .card-header__logo{", "标题栏鲸娘徽标"],
    [".main-page.is-scrolled .card-header{", "滚动触发态（标题栏）"],
    [".main-page.is-scrolled .demo-tabs .el-tabs__nav{", "滚动触发态（标签条）"],
    [".main-page .usage-session{display:inline-flex", "「本次」用量胶囊"],
    [".main-page .hero-balance{display:inline-flex", "英雄区余额胶囊"],
    [".main-page .hero-balance.is-loading .hero-balance__v{animation:hxBalPulse", "余额加载动画"],
    ["@keyframes hxBalPulse{", "余额脉冲关键帧"],
    [".main-page .setting>div.setting-ai{--lg-blur:20px", "AI 卡片高模糊"],
    [".main-page .guide-card{--lg-blur:12px", "教程卡中模糊"],
    [".main-page .question-card{--lg-blur:15px", "题目卡模糊"],
    ["@media (prefers-reduced-motion:reduce){.main-page .card-header", "减弱动效媒体查询"],
    // —— 上轮回归（不能被破坏）——
    [".main-page .whale-page>.usage-bar{", "吸底用量栏"],
    [".main-page .whale-hero.is-idle .whale-hero__avatar{width:132px", "空闲态 132px"],
    [".main-page .whale-hero.is-busy{flex-direction:row", "作答态横排"],
    ["@keyframes hxWhaleBreath{", "呼吸动画"],
    [".main-page .setting>div.setting-ai{border-color", "AI 卡片描边"]
  ];
  out.push("");
  out.push("CSS 规则存在性：");
  for (const [needle, label] of rules) {
    const ok = css.includes(needle);
    out.push("  [%s] %s", ok ? "有" : "缺", label);
    if (!ok) fail.push("缺少 CSS 规则：" + label);
  }
}

// ---------------- 3. JS 标识符 / 引用 ----------------
const decls = {
  HX_BUILD: [/const HX_BUILD = "0\.4\.4";/],
  sessionKey: [/const HX_SESSION_KEY = "hx_session_base_v1";/],
  sessionBase: [/let sessionBase = readSessionBase\(\);/, /sessionBase = readSessionBase\(\);/],
  sessionUsage: [/const sessionUsage = \(\) => \(\{/, /const sess = sessionUsage\(\);/],
  resetSessionUsage: [/const resetSessionUsage = \(\) => \{/, /resetSessionUsage\(\)/],
  writeSessionBase: [/const writeSessionBase = /],
  balanceUrl: [/const DEEPSEEK_BALANCE_URL = "https:\/\/api\.deepseek\.com\/user\/balance";/],
  readStoredApiKey: [/const readStoredApiKey = \(\) => \{/, /readStoredApiKey\(\)/],
  balanceStore: [/const balanceStore = vue\.reactive\(\{/],
  fetchBalance: [/const fetchBalance = \(\) => \{/, /fetchBalance\(\)/],
  formatMoney: [/const formatMoney = \(value, currency\) => \{/],
  heroBalanceHtml: [/const heroBalanceHtml = vue\.computed\(\(\) => \{/, /heroBalanceHtml\.value/],
  bindLiquidGlass: [/const bindLiquidGlass = \(\) => \{/, /bindLiquidGlass\(\)/],
  diagHooks: [/w\.__HX_SESSION_RESET__ = /, /w\.__HX_BALANCE__ = /]
};
out.push("");
out.push("JS 新增标识符：");
for (const k of Object.keys(decls)) {
  const hits = decls[k].map((re) => (src.match(new RegExp(re.source, "g")) || []).length);
  const ok = hits.every((n) => n >= 1);
  out.push("  [%s] %s 命中 %s", ok ? "OK" : "NG", k, hits.join("/"));
  if (!ok) fail.push("标识符不完整：" + k);
}

// ---------------- 4. 结构不变量 ----------------
out.push("");
out.push("结构不变量：");
const inv = [
  ["0.4.3 残留", src.split("0.4.3").length - 1, 0],
  ["0.4.4 出现", src.split("0.4.4").length - 1, 6],
  ["usage-build 残留", src.split("usage-build").length - 1, 0],
  ["usage-session 类", src.split('class="usage-session"').length - 1, 1],
  ["hero-balance 节点", src.split('class: "whale-hero__balance"').length - 1, 1],
  ["card-header__logo 节点", src.split('class: "card-header__logo"').length - 1, 1],
  ["ElEmpty 残留", src.split("resolveComponent(\"el-empty\")").length - 1, 0],
  ["whale-page 根", src.split('class: "whale-page"').length - 1, 1],
  ["面板宿主标记", src.split("shadowHost.setAttribute(PANEL_MARK_ATTR, HX_RUN_ID)").length - 1, 1]
];
for (const [label, actual, expect] of inv) {
  const ok = actual === expect;
  out.push("  [%s] %s 实际 %d / 期望 %d", ok ? "OK" : "NG", label, actual, expect);
  if (!ok) fail.push("不变量不符：" + label);
}

out.push("");
out.push(fail.length ? "==== 失败 " + fail.length + " 项 ====" : "==== 全部通过 ====");
fail.forEach((f) => out.push("  ! " + f));

fs.writeFileSync("C:\\Users\\D_A\\WorkBuddy\\2026-10-05-13-53-42\\_v42out.txt", out.join("\n"), "utf8");
process.exit(fail.length ? 1 : 0);
