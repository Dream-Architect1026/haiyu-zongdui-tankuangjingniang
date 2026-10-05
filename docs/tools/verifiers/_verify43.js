// _verify43.js —— 0.4.5 回归验收：语法 + CSS 真实求值 + 级联顺序 + 规则存在性 + 不变量
const fs = require("fs");
const vm = require("vm");
const util = require("util");
const P = "C:\\Users\\D_A\\DoubaoWork\\chats\\2026-10-05\\new-chat-4\\海底小纵队·探矿鲸娘.user.js";
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

// ---------- 1. CSS 装配区间 ----------
const MARK = 'const layoutCss = LAYOUT_CSS_PARTS.join("")';
const i0 = src.indexOf("const LAYOUT_CSS_PARTS = [");
const jt = src.indexOf(MARK, i0);
if (i0 < 0 || jt < 0) fail.push("找不到 LAYOUT_CSS_PARTS 区间");
const region = src.slice(i0, jt + MARK.length);
out.push("CSS 装配区间长度 %d", region.length);

// ---------- 2. 打桩真实求值 ----------
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

  // ---------- 2b. 级联顺序（本轮修复生效的关键凭据）----------
  out.push("");
  out.push("级联顺序（新块必须晚于旧块，后者胜出）：");
  const last = (s) => css.lastIndexOf(s);
  const first = (s) => css.indexOf(s);
  const order = [
    ["hero 余额：归零规则晚于旧的 opacity:0 规则",
      ".main-page .whale-hero.is-busy .whale-hero__balance{flex:0 0 0px;width:0;min-width:0;",
      ".main-page .whale-hero.is-busy .whale-hero__balance{opacity:0;"],
    ["hero 余额：width:0 晚于 width:100%",
      ".main-page .whale-hero.is-busy .whale-hero__balance{flex:0 0 0px;width:0;",
      ".main-page .whale-hero__balance{flex:0 0 auto;display:flex;align-items:center;justify-content:center;width:100%;"],
    ["标签：flex:1 1 0 晚于旧 height:28px 规则",
      ".main-page .demo-tabs .el-tabs__item{flex:1 1 0!important;",
      ".main-page .demo-tabs .el-tabs__item{position:relative;height:28px!important;"],
    ["标签行：width:100% 晚于旧的玻璃 dock",
      ".main-page .demo-tabs .el-tabs__nav{display:flex!important;width:100%!important;",
      ".main-page .demo-tabs .el-tabs__nav{display:flex!important;align-items:center;gap:4px;padding:3px;"],
    ["按钮：胶囊规则晚于旧的 color-only 规则",
      ".main-page .card-header .zoom-icon{display:inline-flex!important;",
      ".main-page .card-header .zoom-icon{color:var(--hx-ink-dim)!important;"]
  ];
  for (const [label, newer, older] of order) {
    const a = last(newer), b = last(older);
    const ok = a > b && b >= 0 && a >= 0;
    out.push("  [%s] %s (新@%d > 旧@%d)", ok ? "OK" : "NG", label, a, b);
    if (!ok) fail.push("级联顺序错：" + label);
  }

  // ---------- 2c. 规则存在性 ----------
  const rules = [
    // —— 0.4.5 A：作答态修复 ——
    ["/* ==== v0.4.5 : hero", "0.4.5 分节注释"],
    [".main-page .whale-hero__avatar{flex:0 0 auto}", "头像禁止收缩"],
    [".main-page .whale-hero__bubble{flex:0 1 auto;min-width:0}", "气泡可收缩"],
    [".main-page .whale-hero.is-busy .whale-hero__balance{flex:0 0 0px;width:0;", "作答态余额块退出布局"],
    ["width .28s ease}", "余额宽度过渡"],
    // —— 0.4.5 B：标签独立胶囊 ——
    [".main-page .demo-tabs .el-tabs__nav{display:flex!important;width:100%!important;", "标签行铺满且无 dock"],
    ["background:none!important;box-shadow:none!important;backdrop-filter:none!important", "去掉外层 dock 材质"],
    [".main-page .demo-tabs .el-tabs__item{flex:1 1 0!important;", "标签等宽均分"],
    ["border-radius:11px!important", "标签独立胶囊圆角"],
    [".main-page .demo-tabs .el-tabs__item.is-active{color:#fff!important;", "激活发光"],
    ["animation:hxTabGlow 2.8s ease-in-out infinite", "激活呼吸发光"],
    ["@keyframes hxTabGlow{", "发光关键帧"],
    [".main-page .demo-tabs .el-tabs__item::before{display:none!important}", "去掉旧光泽伪元素"],
    [".main-page .demo-tabs .el-tabs__nav-prev,.main-page .demo-tabs .el-tabs__nav-next{display:none!important}", "隐藏滚动箭头"],
    // —— 0.4.5 C：标题栏按钮胶囊 ——
    [".main-page .card-header .zoom-icon{display:inline-flex!important;", "按钮独立胶囊"],
    [".main-page .card-header .zoom-icon+.zoom-icon{margin-left:7px}", "按钮间距"],
    [".main-page .card-header .zoom-icon:hover{color:var(--hx-cyan)!important;", "按钮悬停发光"],
    // —— 0.4.5 D：最小化美化 ——
    [".main-page .el-card:has(.card_content[style*='display: none']) .card-header{padding:7px 9px!important;", "最小化条胶囊化"],
    ["animation:hxMiniGlow 3.2s ease-in-out infinite", "最小化呼吸发光"],
    ["@keyframes hxMiniGlow{", "最小化发光关键帧"],
    [".main-page .el-card:has(.card_content[style*='display: none']) .card-header .title{flex:1 1 auto;justify-content:center}", "最小化标题居中"],
    [".main-page .minus .compact-divider{display:none!important}", "去掉最小化虚线"],
    // —— 上轮回归（不得破坏）——
    ["/* ==== v0.4.5 liquid glass ==== */", "0.4.4 液态玻璃分节注释（随版本号上移）"],
    [".main-page{--lg-rim:", "液态玻璃变量集"],
    [".main-page .demo-tabs .el-tabs__active-bar{display:none", "去掉标签下划条"],
    [".main-page .demo-tabs .el-tabs__nav-wrap::after{display:none", "去掉导航横条"],
    [".main-page .demo-tabs .el-tabs__item+.el-tabs__item{border-left:none", "去掉标签竖分隔线"],
    [".main-page .card-header__logo{", "标题栏鲸娘徽标"],
    [".main-page.is-scrolled .card-header{", "滚动触发态"],
    [".main-page .usage-session{display:inline-flex", "「本次」用量胶囊"],
    [".main-page .hero-balance{display:inline-flex", "英雄区余额胶囊"],
    ["@keyframes hxBalPulse{", "余额脉冲关键帧"],
    [".main-page .setting>div.setting-ai{--lg-blur:20px", "AI 卡片高模糊"],
    [".main-page .guide-card{--lg-blur:12px", "教程卡中模糊"],
    [".main-page .question-card{--lg-blur:15px", "题目卡模糊"],
    [".main-page .whale-page>.usage-bar{", "吸底用量栏"],
    [".main-page .whale-hero.is-idle .whale-hero__avatar{width:132px", "空闲态 132px"],
    [".main-page .whale-hero.is-busy{flex-direction:row", "作答态横排"],
    ["@keyframes hxWhaleBreath{", "呼吸动画"],
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
  HX_BUILD: [/const HX_BUILD = "0\.4\.5";/],
  sessionKey: [/const HX_SESSION_KEY = "hx_session_base_v1";/],
  balanceUrl: [/const DEEPSEEK_BALANCE_URL = "https:\/\/api\.deepseek\.com\/user\/balance";/],
  balanceStore: [/const balanceStore = vue\.reactive\(\{/],
  fetchBalance: [/const fetchBalance = \(\) => \{/, /fetchBalance\(\)/],
  heroBalanceHtml: [/const heroBalanceHtml = vue\.computed\(\(\) => \{/, /heroBalanceHtml\.value/],
  bindLiquidGlass: [/const bindLiquidGlass = \(\) => \{/, /bindLiquidGlass\(\)/],
  diagHooks: [/w\.__HX_SESSION_RESET__ = /, /w\.__HX_BALANCE__ = /]
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
const inv = [
  ["0.4.3 残留", src.split("0.4.3").length - 1, 0],
  ["0.4.4 残留", src.split("0.4.4").length - 1, 0],
  ["0.4.5 出现", src.split("0.4.5").length - 1, 8],
  ["usage-build 残留", src.split("usage-build").length - 1, 0],
  ["usage-session 类", src.split('class="usage-session"').length - 1, 1],
  ["hero-balance 节点", src.split('class: "whale-hero__balance"').length - 1, 1],
  ["whale-hero 节点", src.split('class: "whale-hero__avatar"').length - 1, 1],
  ["card-header__logo 节点", src.split('class: "card-header__logo"').length - 1, 1],
  ["zoom-icon 按钮", src.split('class: "zoom-icon').length - 1, 2],
  ["ElEmpty 残留", src.split("resolveComponent(\"el-empty\")").length - 1, 0],
  ["标签名「状态」保留", src.split('label: "状态"').length - 1, 1],
  ["标签名「通知」未回退", src.split('label: "通知"').length - 1, 0],
  ["whale-page 根", src.split('class: "whale-page"').length - 1, 1],
  ["面板宿主标记", src.split("shadowHost.setAttribute(PANEL_MARK_ATTR, HX_RUN_ID)").length - 1, 1],
  ["LAYOUT_CSS_PARTS.push", src.split("LAYOUT_CSS_PARTS.push(").length - 1, 5]
];
for (const [label, actual, expect] of inv) {
  const ok = actual === expect;
  out.push("  [%s] %s 实际 %d / 期望 %d", ok ? "OK" : "NG", label, actual, expect);
  if (!ok) fail.push("不变量不符：" + label);
}

out.push("");
out.push(fail.length ? "==== 失败 " + fail.length + " 项 ====" : "==== 全部通过 ====");
fail.forEach((f) => out.push("  ! " + f));

fs.writeFileSync("C:\\Users\\D_A\\WorkBuddy\\2026-10-05-13-53-42\\_v43out.txt", out.join("\n"), "utf8");
process.exit(fail.length ? 1 : 0);
