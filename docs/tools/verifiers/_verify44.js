// _verify44.js —— 0.4.6 回归验收：语法 + CSS 真实求值 + 级联顺序 + "标签零位移"专项 + 不变量
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

  // ---------- 2b. 级联顺序：新规则必须晚于旧规则 ----------
  out.push("");
  out.push("级联顺序（新块必须晚于旧块，后者胜出）：");
  const last = (s) => css.lastIndexOf(s);
  const order = [
    ["标签零位移：transform:none 分组规则晚于 0.4.4 的 -1px 悬停",
      ".main-page .demo-tabs .el-tabs__item:active{transform:none!important}",
      ".main-page .demo-tabs .el-tabs__item:hover{color:var(--hx-ink)!important;background:rgba(255,255,255,.07)!important;transform:translateY(-1px);"],
    ["标签零位移：晚于 0.4.5 的 -2px 悬停",
      ".main-page .demo-tabs .el-tabs__item:active{transform:none!important}",
      "background:linear-gradient(150deg,rgba(255,255,255,.14),rgba(255,255,255,.04) 46%,rgba(8,18,38,.30))!important;transform:translateY(-2px);"],
    ["标签零位移：晚于 0.4.5 的 -2px 激活",
      ".main-page .demo-tabs .el-tabs__item:active{transform:none!important}",
      "rgba(155,107,255,.22))!important;transform:translateY(-2px);"],
    ["叠层：标签行 z-index:2 晚于 0.4.5 的胶囊行定义",
      ".main-page .demo-tabs>.el-tabs__header{position:relative;z-index:2;isolation:isolate}",
      ".main-page .demo-tabs>.el-tabs__header{overflow:visible!important;margin:0 0 9px!important}"],
    ["悬停发光覆盖：新悬停发光晚于 0.4.5 的悬停发光",
      ".main-page .demo-tabs .el-tabs__item:hover{border-color:rgba(56,226,255,.40)!important;box-shadow:0 0 14px rgba(56,226,255,.30)",
      "border-color:rgba(140,200,255,.34)!important;background:linear-gradient(150deg,rgba(255,255,255,.14)"],
    ["hero 余额零宽（0.4.5 修复）晚于旧规则",
      ".main-page .whale-hero.is-busy .whale-hero__balance{flex:0 0 0px;width:0;min-width:0;",
      ".main-page .whale-hero.is-busy .whale-hero__balance{opacity:0;"],
    ["标签等宽（0.4.5）晚于旧 height:28px",
      ".main-page .demo-tabs .el-tabs__item{flex:1 1 0!important;",
      ".main-page .demo-tabs .el-tabs__item{position:relative;height:28px!important;"]
  ];
  for (const [label, newer, older] of order) {
    const a = last(newer), b = last(older);
    const ok = a > b && a >= 0 && b >= 0;
    out.push("  [%s] %s (新@%d > 旧@%d)", ok ? "OK" : "NG", label, a, b);
    if (!ok) fail.push("级联顺序错：" + label);
  }

  // ---------- 2c. 专项：标签规则里不得残留任何位移 ----------
  out.push("");
  out.push("专项：标签类规则中不得有位移（transform/translate/top/margin-top 位移）：");
  const tabRules = css.match(/[^{}]*\.el-tabs__item[^{}]*\{[^}]*\}/g) || [];
  out.push("  命中标签规则 %d 条", tabRules.length);
  const offenders = [];
  for (const r of tabRules) {
    const sel = r.slice(0, r.indexOf("{"));
    const body = r.slice(r.indexOf("{") + 1, r.lastIndexOf("}"));
    // 允许 transform:none；不允许 translateX/Y/scale 之外的位移量
    const mv = body.match(/transform\s*:\s*(?!none)[^;}]+/gi) || [];
    for (const m of mv) {
      if (/translate|scale|rotate|skew|matrix/i.test(m)) offenders.push(sel.trim() + " => " + m.trim());
    }
    const top = body.match(/(?:^|;)\s*(?:top|margin-top)\s*:\s*(-?\d)/gi) || [];
    for (const m of top) offenders.push(sel.trim() + " => " + m.trim());
  }
  if (offenders.length) {
    fail.push("标签规则仍含位移 " + offenders.length + " 处");
    offenders.forEach((o) => out.push("  [NG] " + o));
  } else {
    out.push("  [OK] 无任何位移声明残留");
  }
  // 反向确认：新块确实写了 transform:none
  const hasNone = /\.el-tabs__item:(?:hover|active)[^{]*,\s*\.main-page[^{]*is-active[^{]*,\s*\.main-page[^{]*:active\s*\{\s*transform\s*:\s*none\s*!important\s*\}/.test(
    css.replace(/\n/g, " ")
  );
  out.push("  [%s] 分组 transform:none!important 规则存在", hasNone ? "OK" : "NG");
  if (!hasNone) fail.push("未找到分组的 transform:none 覆写规则");

  // ---------- 2d. 规则存在性 ----------
  const rules = [
    // —— 0.4.6 本轮 ——
    ["/* ==== v0.4.6 : 标签只发光不上浮", "0.4.6 分节注释"],
    [".main-page .demo-tabs .el-tabs__item:active{transform:none!important}", "标签位移归零"],
    ["will-change:box-shadow,background-color,border-color", "发光改为合成层优化"],
    [".main-page .demo-tabs>.el-tabs__header{position:relative;z-index:2;isolation:isolate}", "标签行独立叠层"],
    [".main-page .demo-tabs .el-tabs__nav{position:relative;z-index:1}", "nav 独立层"],
    [".main-page .demo-tabs .el-tabs__item:hover{border-color:rgba(56,226,255,.40)!important;box-shadow:0 0 14px rgba(56,226,255,.30)", "悬停改纯发光"],
    [".main-page .demo-tabs .el-tabs__item.is-active{box-shadow:0 0 20px rgba(56,226,255,.42)", "激活光晕加强"],
    // —— 0.4.5 回归 ——
    ["/* ==== v0.4.6 : hero", "0.4.5 分节注释（随版本号上移）"],
    [".main-page .whale-hero__avatar{flex:0 0 auto}", "头像禁止收缩"],
    [".main-page .whale-hero.is-busy .whale-hero__balance{flex:0 0 0px;width:0;", "作答态余额块退出布局"],
    [".main-page .demo-tabs .el-tabs__nav{display:flex!important;width:100%!important;", "标签行铺满且无 dock"],
    ["animation:hxTabGlow 2.8s ease-in-out infinite", "激活呼吸发光"],
    ["@keyframes hxTabGlow{", "发光关键帧"],
    [".main-page .card-header .zoom-icon{display:inline-flex!important;", "按钮独立胶囊"],
    ["@keyframes hxMiniGlow{", "最小化发光关键帧"],
    [".main-page .minus .compact-divider{display:none!important}", "去掉最小化虚线"],
    // —— 更早回归 ——
    ["/* ==== v0.4.6 liquid glass ==== */", "液态玻璃分节注释"],
    [".main-page{--lg-rim:", "液态玻璃变量集"],
    [".main-page .demo-tabs .el-tabs__active-bar{display:none", "去掉标签下划条"],
    [".main-page .demo-tabs .el-tabs__item+.el-tabs__item{border-left:none", "去掉标签竖分隔线"],
    [".main-page .card-header__logo{", "标题栏鲸娘徽标"],
    [".main-page.is-scrolled .card-header{", "滚动触发态"],
    [".main-page .usage-session{display:inline-flex", "「本次」用量胶囊"],
    [".main-page .hero-balance{display:inline-flex", "英雄区余额胶囊"],
    ["@keyframes hxBalPulse{", "余额脉冲关键帧"],
    [".main-page .setting>div.setting-ai{--lg-blur:20px", "AI 卡片高模糊"],
    [".main-page .question-card{--lg-blur:15px", "题目卡模糊"],
    [".main-page .whale-page>.usage-bar{", "吸底用量栏"],
    [".main-page .whale-hero.is-idle .whale-hero__avatar{width:132px", "空闲态 132px"],
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
  HX_BUILD: [/const HX_BUILD = "0\.4\.6";/],
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
  ["0.4.4 残留", src.split("0.4.4").length - 1, 0],
  ["0.4.5 残留", src.split("0.4.5").length - 1, 0],
  ["0.4.6 出现", src.split("0.4.6").length - 1, 10],
  ["usage-build 残留", src.split("usage-build").length - 1, 0],
  ["usage-session 类", src.split('class="usage-session"').length - 1, 1],
  ["hero-balance 节点", src.split('class: "whale-hero__balance"').length - 1, 1],
  ["whale-hero 头像节点", src.split('class: "whale-hero__avatar"').length - 1, 1],
  ["card-header__logo 节点", src.split('class: "card-header__logo"').length - 1, 1],
  ["zoom-icon 按钮", src.split('class: "zoom-icon').length - 1, 2],
  ["ElEmpty 残留", src.split("resolveComponent(\"el-empty\")").length - 1, 0],
  ["标签名「状态」保留", src.split('label: "状态"').length - 1, 1],
  ["标签名「通知」未回退", src.split('label: "通知"').length - 1, 0],
  ["whale-page 根", src.split('class: "whale-page"').length - 1, 1],
  ["面板宿主标记", src.split("shadowHost.setAttribute(PANEL_MARK_ATTR, HX_RUN_ID)").length - 1, 1],
  ["LAYOUT_CSS_PARTS.push", src.split("LAYOUT_CSS_PARTS.push(").length - 1, 6]
];
for (const [label, actual, expect] of inv) {
  const ok = actual === expect;
  out.push("  [%s] %s 实际 %d / 期望 %d", ok ? "OK" : "NG", label, actual, expect);
  if (!ok) fail.push("不变量不符：" + label);
}

out.push("");
out.push(fail.length ? "==== 失败 " + fail.length + " 项 ====" : "==== 全部通过 ====");
fail.forEach((f) => out.push("  ! " + f));

fs.writeFileSync("C:\\Users\\D_A\\WorkBuddy\\2026-10-05-13-53-42\\_v44out.txt", out.join("\n"), "utf8");
process.exit(fail.length ? 1 : 0);
