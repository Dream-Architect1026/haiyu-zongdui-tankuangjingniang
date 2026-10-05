// _verify46.js —— 0.4.7 回归验收：语法 + CSS 真实求值 + 级联顺序 + 伪元素不越界/不占 flex + 文案改名 + 不变量
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

  // ---------- 2a. 专项：背景扫掠不得越界 ----------
  out.push("");
  out.push("专项：背景脉动光必须在面板内完成扫掠（不得靠 transform 溢出屏幕）：");
  const ruleOf = (sel) => {
    const i = css.indexOf(sel + "{");
    if (i < 0) return null;
    return css.slice(i + sel.length + 1, css.indexOf("}", i));
  };
  const bgBody = ruleOf(".main-page::before");
  if (!bgBody) fail.push("找不到 .main-page::before 规则");
  else {
    const okSize = /background-size:100% 240%/.test(bgBody);
    const okPos = /background-position:50% 50%/.test(bgBody);
    const noTr = !/transform\s*:/.test(bgBody);
    const okZ = /z-index:-1/.test(bgBody);
    const okPe = /pointer-events:none/.test(bgBody);
    const freqM = bgBody.match(/animation:hxBgSweep (\d+(?:\.\d+)?)s/);
    out.push("  [%s] 用 background-size/position 扫掠（非 transform 位移）", okSize && okPos ? "OK" : "NG");
    out.push("  [%s] 无 transform 位移（不会溢出面板）", noTr ? "OK" : "NG");
    out.push("  [%s] z-index:-1 置于内容之下", okZ ? "OK" : "NG");
    out.push("  [%s] pointer-events:none 不吃点击", okPe ? "OK" : "NG");
    out.push("  [%s] 扫掠周期 = %ss（低频，>=8s 为佳）", freqM && parseFloat(freqM[1]) >= 8 ? "OK" : "NG", freqM ? freqM[1] : "?");
    if (!(okSize && okPos)) fail.push("背景扫掠未使用 background-position 方案");
    if (!noTr) fail.push("背景扫掠含 transform 位移，可能越界");
    if (!okZ) fail.push("背景扫掠未置于内容之下");
    if (!okPe) fail.push("背景扫掠未禁用指针事件");
    if (!freqM || parseFloat(freqM[1]) < 8) fail.push("背景扫掠周期不是低频(>=8s)");
  }
  const kfBody = (name) => {
    const start = css.indexOf("@keyframes " + name + "{");
    if (start < 0) return null;
    const i = css.indexOf("{", start);
    let depth = 0;
    for (let j = i; j < css.length; j++) {
      if (css[j] === "{") depth++;
      else if (css[j] === "}") { depth--; if (depth === 0) return css.slice(i + 1, j); }
    }
    return null;
  };
  const sweep = kfBody("hxBgSweep");
  if (!sweep) fail.push("找不到 hxBgSweep 关键帧体");
  else {
    const body = sweep;
    const moves = /background-position:50% 50%/.test(body) && /background-position:50% -50%/.test(body);
    out.push("  [%s] 关键帧从 50% 50% 扫到 50% -50%（自上而下）", moves ? "OK" : "NG");
    if (!moves) fail.push("背景扫掠方向/端点不正确");
    const freq = (body.match(/\d+(?:\.\d+)?s(?![a-z])/g) || []);
    out.push("  关键帧体内时间字面量 = %s（周期见上方规则）", freq.join(",") || "无");
    const noTr = !/transform\s*:/.test(body);
    out.push("  [%s] 关键帧内无 transform（只用 background-position）", noTr ? "OK" : "NG");
    if (!noTr) fail.push("关键帧内含 transform 位移");
  }

  // ---------- 2b. 专项：hero 双伪元素不得成为 flex 项 ----------
  out.push("");
  out.push("专项：.whale-hero 是 flex 容器，其 ::before/::after 必须绝对定位（否则会成为 flex 项撑破布局）：");
  for (const sel of [".main-page .whale-hero::before", ".main-page .whale-hero::after"]) {
    const b = ruleOf(sel);
    if (!b) { fail.push("找不到 " + sel); out.push("  [NG] %s 缺失", sel); continue; }
    const abs = /position:absolute/.test(b);
    const z = /z-index:-1/.test(b);
    const pe = /pointer-events:none/.test(b);
    out.push("  [%s] %s 绝对定位/负层/不吃点击 = %s/%s/%s", abs && z && pe ? "OK" : "NG", sel, abs, z, pe);
    if (!abs) fail.push(sel + " 未绝对定位，会变成 flex 项");
    if (!z) fail.push(sel + " 未置于负层");
    if (!pe) fail.push(sel + " 未禁用指针事件");
  }

  // ---------- 2c. 级联顺序 ----------
  out.push("");
  out.push("级联顺序（新块必须晚于旧块，后者胜出）：");
  const last = (s) => css.lastIndexOf(s);
  const NEWTAB = ".main-page .demo-tabs .el-tabs__item:active{transform:none!important}";
  const order = [
    ["标签零位移：晚于 0.4.4 的 -1px 悬停", NEWTAB,
      ".main-page .demo-tabs .el-tabs__item:hover{color:var(--hx-ink)!important;background:rgba(255,255,255,.07)!important;transform:translateY(-1px);"],
    ["标签零位移：晚于 0.4.5 的 -2px 悬停", NEWTAB,
      "background:linear-gradient(150deg,rgba(255,255,255,.14),rgba(255,255,255,.04) 46%,rgba(8,18,38,.30))!important;transform:translateY(-2px);"],
    ["标签零位移：晚于 0.4.5 的 -2px 激活", NEWTAB,
      "rgba(155,107,255,.22))!important;transform:translateY(-2px);"],
    ["标签行叠层：晚于 0.4.5 的胶囊行定义",
      ".main-page .demo-tabs>.el-tabs__header{position:relative;z-index:2;isolation:isolate}",
      ".main-page .demo-tabs>.el-tabs__header{overflow:visible!important;margin:0 0 9px!important}"],
    ["页面渐隐渐入：晚于最小化高度解锁", "@keyframes hxPaneIn{",
      ".main-page .el-card:has(.card_content[style*='display:none']){height:auto"],
    ["最小化实测高度：晚于旧 height:auto 解锁",
      ".main-page .el-card:has(.card_content[style*='display: none']){height:var(--hx-min-h,52px);",
      ".main-page .el-card:has(.card_content[style*='display:none']){height:auto"],
    ["状态灯显示：晚于状态灯基础隐藏",
      ".main-page .el-card:has(.card_content[style*='display: none']) .hx-status-dot{display:block;",
      ".main-page .hx-status-dot{display:none;"],
    ["空闲浮动+光晕：晚于 0.4.6 的单一浮动规则",
      ".main-page .whale-hero.is-idle .whale-hero__avatar{animation:hxIdleFloat 5.2s ease-in-out infinite,hxWhaleAura",
      ".main-page .whale-hero.is-idle .whale-hero__avatar{animation:hxIdleFloat 4.6s ease-in-out infinite}"],
    ["作答呼吸+光晕：晚于 0.4.4 的单一呼吸规则",
      ".main-page .whale-hero.is-busy .whale-hero__avatar{animation:hxWhaleBreath 2.4s ease-in-out infinite,hxWhaleAura",
      ".main-page .whale-hero.is-busy .whale-hero__avatar{animation:hxWhaleBreath 2.4s ease-in-out infinite}"],
    ["hero 负层光团：晚于 0.4.5 的 position:relative",
      ".main-page .whale-hero{isolation:isolate}",
      ".main-page .whale-hero{position:relative}"],
    ["新静音块最后", "@media (prefers-reduced-motion:reduce){.main-page::before",
      ".main-page .hx-status-dot[data-hx-status='stop']{"]
  ];
  for (const [label, newer, older] of order) {
    const a = last(newer), b = last(older);
    const ok = a > b && a >= 0 && b >= 0;
    out.push("  [%s] %s (新@%d > 旧@%d)", ok ? "OK" : "NG", label, a, b);
    if (!ok) fail.push("级联顺序错：" + label);
  }

  // ---------- 2d. 规则存在性 ----------
  const rules = [
    // —— 0.4.7 本轮 ——
    ["/* ==== v0.4.7 : 背景脉动光", "0.4.7 分节注释"],
    [".main-page{isolation:isolate}", "主面板隔离层"],
    ["@keyframes hxBgSweep{", "背景扫掠关键帧"],
    ["@keyframes hxBgBreathe{", "背景呼吸关键帧"],
    ["radial-gradient(130% 62% at 50% -8%", "顶部柔光"],
    ["@keyframes hxHeroGlowA{", "鲸娘青光团关键帧"],
    ["@keyframes hxHeroGlowB{", "鲸娘紫光团关键帧"],
    ["@keyframes hxWhaleAura{", "头像随相光晕关键帧"],
    ["filter:drop-shadow(0 3px 9px rgba(56,226,255,.45))", "光晕起始色（青）"],
    ["filter:drop-shadow(0 7px 18px rgba(155,107,255,.70))", "光晕峰值色（紫）"],
    ["will-change:transform,filter", "头像合成层优化"],
    ["@keyframes hxLineIn{", "空闲文案入场关键帧"],
    // —— 0.4.6 回归 ——
    [".main-page .demo-tabs .el-tabs__item:active{transform:none!important}", "标签位移归零"],
    [".main-page .demo-tabs>.el-tabs__header{position:relative;z-index:2;isolation:isolate}", "标签行独立叠层"],
    ["box-shadow:0 3px 14px rgba(56,226,255,.32)", "悬停纯发光"],
    ["@keyframes hxPaneIn{", "页面切换关键帧"],
    ["@keyframes hxCardIn{", "卡片入场关键帧"],
    ["@keyframes hxLogIn{", "日志入场关键帧"],
    ["@keyframes hxIdleFloat{", "空闲浮动关键帧"],
    [".main-page .el-card{transition:height .32s cubic-bezier(.22,1,.36,1)}", "最小化高度过渡"],
    ["height:var(--hx-min-h,52px);overflow:hidden", "最小化实测高度"],
    [".main-page .minus{display:none!important}", "最小化只留标题栏"],
    ["@keyframes hxDotPulse{", "状态灯脉冲关键帧"],
    ["@keyframes hxDotHalo{", "状态灯光晕关键帧"],
    [".hx-status-dot[data-hx-status='run']{color:#4ade80", "状态灯-绿/运行中"],
    [".hx-status-dot[data-hx-status='busy']{color:#ffc857", "状态灯-黄/答题中"],
    [".hx-status-dot[data-hx-status='stop']{color:#ff6b6b", "状态灯-红/终止"],
    // —— 0.4.5 回归 ——
    [".main-page .whale-hero__avatar{flex:0 0 auto}", "头像禁止收缩"],
    [".main-page .whale-hero.is-busy .whale-hero__balance{flex:0 0 0px;width:0;", "作答态余额块退出布局"],
    [".main-page .demo-tabs .el-tabs__nav{display:flex!important;width:100%!important;", "标签行铺满且无 dock"],
    ["animation:hxTabGlow 2.8s ease-in-out infinite", "激活呼吸发光"],
    [".main-page .card-header .zoom-icon{display:inline-flex!important;", "按钮独立胶囊"],
    ["@keyframes hxMiniGlow{", "最小化发光关键帧"],
    // —— 更早回归 ——
    ["/* ==== v0.4.7 liquid glass ==== */", "液态玻璃分节注释"],
    [".main-page{--lg-rim:", "液态玻璃变量集"],
    [".main-page .demo-tabs .el-tabs__active-bar{display:none", "去掉标签下划条"],
    [".main-page .demo-tabs .el-tabs__item+.el-tabs__item{border-left:none", "去掉标签竖分隔线"],
    [".main-page .card-header__logo{", "标题栏鲸娘徽标"],
    [".main-page.is-scrolled .card-header{", "滚动触发态"],
    [".main-page .usage-session{display:inline-flex", "「本次」用量胶囊"],
    [".main-page .hero-balance{display:inline-flex", "英雄区余额胶囊"],
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
  HX_BUILD: [/const HX_BUILD = "0\.4\.7";/],
  idleLines: [/const HX_IDLE_LINES = \["小鲸娘正在吃白饭"/, /hxIdleLine = HX_IDLE_LINES\[hxIdleLineIdx\];/],
  paintIdle: [/const paintIdleLine = \(animate\) => \{/, /paintIdleLine\(true\)/, /paintIdleLine\(false\)/],
  rollIdle: [/const rollIdleLine = \(\) => \{/, /rollIdleLine\(\);/],
  schedRoll: [/const scheduleIdleRoll = \(\) => \{/, /4200 \+ Math\.floor\(Math\.random\(\) \* 3600\)/],
  bindIdle: [/const bindIdleLines = \(\) => \{/, /bindIdleLines\(\);/],
  lineTimer: [/let hxLineTimer = null;/],
  lineProbe: [/w\.__HX_LINE__ = \(\) => hxIdleLine;/],
  renameOnly: [/"仅仅作答"/, /const VIDEO_QUIZ_SETTING = "弹题作答";/],
  statusText: [/const HX_STATUS_TEXT = \{ run: "运行中", busy: "答题中", stop: "已终止" \};/],
  readPanelStatus: [/const readPanelStatus = \(\) => \{/, /const state = readPanelStatus\(\);/],
  syncStatusDot: [/const syncStatusDot = \(\) => \{/, /try \{ syncStatusDot\(\); \} catch/],
  bindStatusDot: [/const bindStatusDot = \(\) => \{/, /bindStatusDot\(\);/],
  minHeightVar: [/root\.host\.style\.setProperty\("--hx-min-h", measuredH \+ 3 \+ "px"\);/],
  dotProbe: [/w\.__HX_STATUS__ = \(\) => readPanelStatus\(\);/],
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

// ---------- 4. 文案改名（含迁移，防丢配置） ----------
out.push("");
out.push("文案改名与配置迁移：");
const migBlock = src.slice(src.indexOf("const CONFIG_NAME_MIGRATIONS = {"), src.indexOf("const PREFIX_NAME_MIGRATIONS"));
const ren = [
  ['仅作答 -> 旧名只应作为迁移键出现 1 次', src.split('"仅作答"').length - 1, 1],
  ['仅仅作答 出现 4 次（参数名 + 3 处映射值）', src.split('"仅仅作答"').length - 1, 4],
  ['弹题自动作答 -> 旧名只应作为迁移键出现 1 次', src.split('"弹题自动作答"').length - 1, 1],
  ['弹题作答 出现 3 次（常量 + 2 处映射值）', src.split('"弹题作答"').length - 1, 3],
  ['迁移键 "仅作答" 在映射表内', migBlock.split('"仅作答":').length - 1, 1],
  ['迁移键 "弹题自动作答" 在映射表内', migBlock.split('"弹题自动作答":').length - 1, 1],
  ['旧-旧名 "只答题不刷课" 仍在（历史键不删）', migBlock.split('"只答题不刷课"').length - 1, 1],
  ['旧-旧名 "视频弹题自动作答" 仍在（历史键不删）', migBlock.split('"视频弹题自动作答"').length - 1, 1]
];
for (const [label, actual, expect] of ren) {
  const ok = actual === expect;
  out.push("  [%s] %s 实际 %d / 期望 %d", ok ? "OK" : "NG", label, actual, expect);
  if (!ok) fail.push("改名/迁移不符：" + label);
}

// ---------- 5. 结构不变量 ----------
out.push("");
out.push("结构不变量：");
const inv = [
  ["0.4.5 残留", src.split("0.4.5").length - 1, 0],
  ["0.4.6 残留", src.split("0.4.6").length - 1, 0],
  ["0.4.7 出现", src.split("0.4.7").length - 1, 12],
  ["HX_MINIMIZED_HEIGHT 残留", src.split("HX_MINIMIZED_HEIGHT").length - 1, 0],
  ["usage-build 残留", src.split("usage-build").length - 1, 0],
  ["usage-session 类", src.split('class="usage-session"').length - 1, 1],
  ["hero-balance 节点", src.split('class: "whale-hero__balance"').length - 1, 1],
  ["whale-hero 头像节点", src.split('class: "whale-hero__avatar"').length - 1, 1],
  ["whale-hero__text 节点", src.split('class: "whale-hero__text"').length - 1, 1],
  ["card-header__logo 节点", src.split('class: "card-header__logo"').length - 1, 1],
  ["zoom-icon 按钮", src.split('class: "zoom-icon').length - 1, 2],
  ["ElEmpty 残留", src.split("resolveComponent(\"el-empty\")").length - 1, 0],
  ["标签名「状态」保留", src.split('label: "状态"').length - 1, 1],
  ["标签名「通知」未回退", src.split('label: "通知"').length - 1, 0],
  ["whale-page 根", src.split('class: "whale-page"').length - 1, 1],
  ["面板宿主标记", src.split("shadowHost.setAttribute(PANEL_MARK_ATTR, HX_RUN_ID)").length - 1, 1],
  ["LAYOUT_CSS_PARTS.push", src.split("LAYOUT_CSS_PARTS.push(").length - 1, 7],
  ["hx-status-dot 类名出现", src.split("hx-status-dot").length - 1, 10]
];
for (const [label, actual, expect] of inv) {
  const ok = actual === expect;
  out.push("  [%s] %s 实际 %d / 期望 %d", ok ? "OK" : "NG", label, actual, expect);
  if (!ok) fail.push("不变量不符：" + label);
}

out.push("");
out.push(fail.length ? "==== 失败 " + fail.length + " 项 ====" : "==== 全部通过 ====");
fail.forEach((f) => out.push("  ! " + f));

fs.writeFileSync("C:\\Users\\D_A\\WorkBuddy\\2026-10-05-13-53-42\\_v46out.txt", out.join("\n"), "utf8");
process.exit(fail.length ? 1 : 0);
