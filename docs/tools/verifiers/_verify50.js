// _verify50.js —— 0.4.10 回归验收
// 语法 + CSS 真实求值 + 级联顺序 + 状态灯判定逻辑真实求值 + 路由抑制 + 旧功能不回归
const fs = require("fs");
const vm = require("vm");
const util = require("util");
const P = "C:\\Users\\D_A\\DoubaoWork\\chats\\2026-10-05\\new-chat-4\\海底小纵队·探矿鲸娘.user.js";
const OUT = "C:\\Users\\D_A\\WorkBuddy\\2026-10-05-13-53-42\\_v50out.txt";
const buf = fs.readFileSync(P);
const src = buf.toString("utf8");
const lines = [];
const out = [];
function w() { out.push(util.format.apply(null, arguments)); }
const fail = [];

// ---------- 0. 字节 / 行尾 / 语法 ----------
const crlf = (buf.toString("latin1").match(/\r\n/g) || []).length;
const bareLF = (buf.toString("latin1").replace(/\r\n/g, "").match(/\n/g) || []).length;
w("字节数 = %d", buf.length);
w("CRLF = %d", crlf);
w("裸 LF = %d（应为 0）", bareLF);
if (bareLF !== 0) fail.push("存在裸 LF " + bareLF + " 个");
if (crlf === 0) fail.push("未检测到 CRLF");

try { new vm.Script(src, { filename: "whale.user.js" }); w("语法解析：通过（vm.Script）"); }
catch (e) { fail.push("语法解析失败：" + e.message); }

// ---------- 1. CSS 装配区间 + 真实求值 ----------
const MARK = 'const layoutCss = LAYOUT_CSS_PARTS.join("")';
const i0 = src.indexOf("const LAYOUT_CSS_PARTS = [");
const jt = src.indexOf(MARK, i0);
if (i0 < 0 || jt < 0) fail.push("找不到 LAYOUT_CSS_PARTS 区间");
const region = src.slice(i0, jt + MARK.length);
w("");
w("CSS 装配区间长度 %d", region.length);

const stripped = region
  .replace(/"(?:[^"\\]|\\.)*"/gs, '""')
  .replace(/'(?:[^'\\]|\\.)*'/gs, "''")
  .replace(/\/\*(?:[\s\S]*?)\*\//g, "")
  .replace(/\/\/[^\n]*/g, "");
const ids = new Set();
stripped.replace(/\b([A-Za-z_$][\w$]*)\b/g, function (m, x) { ids.add(x); return m; });
const declared = new Set();
stripped.replace(/\b(?:const|let|var)\s+([A-Za-z_$][\w$]*)/g, function (m, x) { declared.add(x); return m; });
const KEYWORDS = new Set(["const", "let", "var", "if", "else", "return", "typeof", "true", "false", "null",
  "void", "function", "new", "String", "Number", "Math", "Boolean", "window", "document", "Array", "Object",
  "undefined", "for", "of", "in", "while", "break", "continue", "push", "join", "length", "slice", "replace"]);
const externals = [...ids].filter(function (x) { return !declared.has(x) && !KEYWORDS.has(x); });
w("区间内声明 %d 个；外部引用：%s", declared.size, externals.join(", ") || "无");

let css = null;
try {
  const stubs = externals.map(function (n) { return "const " + n + ' = "";'; }).join("\n");
  css = new Function(stubs + "\n" + region + '\nreturn LAYOUT_CSS_PARTS.join("");')();
  w("真实求值：成功，装配后 CSS 长度 %d", css.length);
} catch (e) { fail.push("真实求值失败：" + e.message); }

if (css) {
  let d = 0, minD = 0;
  for (const ch of css) { if (ch === "{") d++; else if (ch === "}") { d--; if (d < minD) minD = d; } }
  w("花括号终值深度 = %d（应为 0），历史最小 = %d（不应 <0）", d, minD);
  if (d !== 0) fail.push("花括号不配平 " + d);
  if (minD < 0) fail.push("存在提前闭合的 }");
  const pollute = (css.match(/\\n/g) || []).length;
  w("字面 反斜杠n 污染 = %d（应为 0）", pollute);
  if (pollute !== 0) fail.push("\\n 双转义污染 " + pollute + " 处");
  w("真实换行 = %d", (css.match(/\n/g) || []).length);

  // ---------- 1a. 级联顺序 ----------
  w("");
  w("级联顺序（新规则必须晚于被它覆盖的旧规则）：");
  const last = function (x) { return css.lastIndexOf(x); };
  const NEWBLK = "/* ==== v0.4.10 · 本轮 :";
  const order = [
    ["新块 晚于 好感度面板块", NEWBLK, "/* ==== v0.4.10 : 好感度面板"],
    ["新块 晚于 0.4.8 可见光带块", NEWBLK, "/* ==== v0.4.10-d : 可见光带"],
    ["新块 晚于 0.4.7 背景脉动块", NEWBLK, "/* ==== v0.4.10-c : 背景脉动光"],
    ["新块 晚于 液态玻璃块", NEWBLK, "/* ==== v0.4.10 liquid glass ==== */"],
    ["卡座 position 晚于 旧 .el-card 底色", ".main-page .el-card{position:relative}", ".main-page .el-card{background:transparent"],
    ["必填胶囊 晚于 表单标签基样式", ".el-form-item.is-required>.el-form-item__label{flex", ".main-page .setting .el-form-item__label{"],
    ["AI字段胶囊 晚于 表单标签基样式", ".setting-ai-field>.el-form-item__label{flex", ".main-page .setting .el-form-item__label{"],
    ["好感度胶囊 晚于 旧「本次」胶囊", ".main-page .usage-fav{", ".main-page .usage-session{display:inline-flex"],
    ["状态灯过渡 晚于 状态灯三色", ".main-page .hx-status-dot{transition:color", ".hx-status-dot[data-hx-status='stop']"],
    ["光晕A 61.8% 晚于 原光晕A", "@keyframes hxHeroGlowA{0%,100%{opacity:.185;", "@keyframes hxHeroGlowA{0%,100%{opacity:.30;"],
    ["光晕B 61.8% 晚于 原光晕B", "@keyframes hxHeroGlowB{0%,100%{opacity:0;transform:scale(.84)}48%{opacity:.544;", "@keyframes hxHeroGlowB{0%,100%{opacity:0;transform:scale(.84)}48%{opacity:.88;"]
  ];
  for (const pair of order) {
    const a = last(pair[1]), b = last(pair[2]);
    const ok = a > b && a >= 0 && b >= 0;
    w("  [%s] %s (新@%d > 旧@%d)", ok ? "OK" : "NG", pair[0], a, b);
    if (!ok) fail.push("级联顺序错：" + pair[0]);
  }

  // ---------- 1b. 61.8% 换算正确性 ----------
  w("");
  w("光晕 61.8% 换算核对（原文 × 0.618，保留 3 位）：");
  const scale = [
    [".30", ".185"], [".95", ".587"], ["0", "0"], [".88", ".544"], [".45", ".278"], [".70", ".433"]
  ];
  for (const p of scale) {
    const v = Number(p[0]) * 0.618;
    const ok = Math.abs(Number(v.toFixed(3)) - Number(p[1])) < 0.0005;
    w("  [%s] %s × 0.618 = %s（源码写 %s）", ok ? "OK" : "NG", p[0], v.toFixed(3), p[1]);
    if (!ok) fail.push("61.8% 换算不符：" + p[0]);
  }
  const haloHits = (css.match(/opacity:\.185|opacity:\.587|opacity:\.544|rgba\(56,226,255,\.278\)/g) || []).length;
  w("  61.8% 取值在 CSS 中出现 %d 处", haloHits);
  if (haloHits < 4) fail.push("61.8% 取值未全部落地");

  // ---------- 1c. 规则存在性 ----------
  const rules = [
    // —— 0.4.10 本轮 ——
    [NEWBLK, "本轮分节注释"],
    [".main-page .el-card{position:relative}", "卡座定位（伪元素挂对盒）"],
    ["border:1px solid rgba(152,206,255,.30)!important", "卡片液态玻璃边框"],
    [".main-page .el-card::after{content:'';position:absolute;inset:0;border-radius:inherit;pointer-events:none;z-index:4", "边框内高光层"],
    ["inset 0 1px 0 rgba(255,255,255,.20),inset 0 -1px 0 rgba(120,190,255,.12)", "上亮下冷内描边"],
    [".hx-status-dot{transition:color .3s ease,box-shadow .3s ease}", "状态灯平滑过渡"],
    [".setting .el-form-item.is-required>.el-form-item__label{flex:0 0 auto", "必填红星标签胶囊"],
    [".setting-ai-field>.el-form-item__label{flex:0 0 auto", "AI 三字段标签胶囊"],
    [".main-page .usage-fav{display:inline-flex", "用量栏好感度胶囊"],
    [".main-page .usage-fav__k{", "好感度键名"],
    [".main-page .usage-fav__v{", "好感度等级值"],
    ["@keyframes hxHeroGlowA{0%,100%{opacity:.185;", "光晕A 61.8%"],
    ["@keyframes hxHeroGlowB{0%,100%{opacity:0;transform:scale(.84)}48%{opacity:.544;", "光晕B 61.8%"],
    ["rgba(56,226,255,.278)", "鲸娘随相光晕 61.8%"],
    // —— 旧功能回归 ——
    ["/* ==== v0.4.10 : 好感度面板", "好感度分节注释"],
    [".main-page .setting-fav-field{margin:2px 0 8px;", "好感度卡片容器"],
    [".main-page .fav-info{", "ⓘ 信息按钮"],
    [".main-page .setting-fav-field.is-open .fav-note{display:block", "点 ⓘ 展开说明"],
    ["@keyframes hxBgSweep{", "背景扫掠关键帧"],
    [".main-page .el-card::before{content:'';position:absolute;inset:-16px;", "光带在卡片上"],
    [".main-page .el-card__body::after{content:'';position:absolute;inset:0;", "卡内扫掠层"],
    [".main-page .usage-uptime{", "本次运行时长"],
    [".main-page .setting>div.setting-ai .el-form-item.setting-pet-field", "小名字段样式"],
    ["@keyframes hxWhaleAura{", "头像随相光晕关键帧"],
    ["@keyframes hxLineIn{", "空闲文案入场关键帧"],
    [".main-page .demo-tabs .el-tabs__item:active{transform:none!important}", "标签位移归零"],
    ["@keyframes hxDotPulse{", "状态灯脉冲关键帧"],
    [".hx-status-dot[data-hx-status='run']{color:#4ade80", "状态灯-绿"],
    [".hx-status-dot[data-hx-status='busy']{color:#ffc857", "状态灯-黄"],
    [".hx-status-dot[data-hx-status='stop']{color:#ff6b6b", "状态灯-红"],
    [".main-page .whale-hero__avatar{flex:0 0 auto}", "头像禁止收缩"],
    [".main-page .demo-tabs .el-tabs__nav{display:flex!important;width:100%!important;", "标签行铺满无 dock"],
    ["@keyframes hxMiniGlow{", "最小化发光关键帧"],
    [".main-page{--lg-rim:", "液态玻璃变量集"],
    [".main-page .card-header__logo{", "标题栏徽标"]
  ];
  w("");
  w("CSS 规则存在性：");
  for (const r of rules) {
    const ok = css.includes(r[0]);
    w("  [%s] %s", ok ? "有" : "缺", r[1]);
    if (!ok) fail.push("缺少 CSS 规则：" + r[1]);
  }
}

// ---------- 2. 状态灯判定逻辑：真实求值 ----------
w("");
w("状态灯判定逻辑（把 HX_FATAL_RE / HX_RESUME_RE 字面量抠出来，用真实日志跑一遍）：");
let FATAL = null, RESUME = null;
{
  const grab = function (name) {
    const k = src.indexOf("const " + name + " = ");
    if (k < 0) return null;
    let a = src.indexOf("/", k + name.length + 4);
    let b = -1, esc = false;
    for (let i = a + 1; i < src.length; i++) {
      const c = src[i];
      if (esc) { esc = false; continue; }
      if (c === "\\") { esc = true; continue; }
      if (c === "\n") break;
      if (c === "/") { b = i; break; }
    }
    if (b < 0) return null;
    return src.slice(a, b + 1);
  };
  const lf = grab("HX_FATAL_RE"), lr = grab("HX_RESUME_RE");
  w("  FATAL  字面量 = %s", lf || "(未找到)");
  w("  RESUME 字面量 = %s", lr || "(未找到)");
  if (!lf || !lr) fail.push("找不到 HX_FATAL_RE / HX_RESUME_RE");
  else {
    FATAL = new Function("return " + lf + ";")();
    RESUME = new Function("return " + lr + ";")();
    w("  [OK] 两个正则真实求值成功（FATAL.flags=%s RESUME.flags=%s）", FATAL.flags, RESUME.flags);
  }
}

// 复刻 readPanelStatus 的扫描语义：busy(黄) > 最新优先扫描(遇 resume 判绿 / 遇 fatal 判红) > 默认绿
function readStatus(logs, busy) {
  if (busy) return "busy";
  const from = Math.max(logs.length - 24, 0);
  for (let i = logs.length - 1; i >= from; i -= 1) {
    const msg = String(logs[i].message || "");
    if (RESUME.test(msg)) return "run";
    if (FATAL.test(msg)) return "stop";
  }
  return "run";
}

if (FATAL && RESUME) {
  // 2a. 取源码里全部 danger / error 级日志文案（这些正是当初误判成"已终止"的元凶）
  const dangerMsgs = [];
  const reD = /addLog\(\s*"((?:[^"\\]|\\.)*)"\s*,\s*"(danger|error)"\s*\)/g;
  let m;
  while ((m = reD.exec(src))) dangerMsgs.push({ message: m[1].replace(/\\"/g, '"'), type: m[2] });
  w("");
  w("  源码里 danger/error 级日志共 %d 条：", dangerMsgs.length);
  dangerMsgs.forEach(function (x) { w("    · %s", x.message); });

  const noiseLogs = dangerMsgs.map(function (x) { return { message: x.message, type: x.type }; });
  if (noiseLogs.length === 0) fail.push("没取到任何 danger/error 日志，本项测试无意义");
  const noiseStatus = readStatus(noiseLogs, false);
  w("");
  w("  【核心回归】把「全部 danger/error 日常噪音」当作最近日志：判定 = %s", noiseStatus);
  w("  [%s] 日常噪音不得判红（这正是用户看到的假「已终止」）", noiseStatus === "run" ? "OK" : "NG");
  if (noiseStatus !== "run") fail.push("日常 danger/error 噪音仍被判成 stop —— 假红灯未修复");

  // 2b. 真实运行中的启动日志
  const boot = [
    { message: "面板 0.4.10 已就位，鲸娘开工～", type: "success" },
    { message: "嗅到 8 道题，开动啦～", type: "success" },
    { message: "自动翻到下一题～", type: "success" },
    { message: "这页没活儿，歇会儿～", type: "warning" },
    { message: "正确率不达标，先攒着～", type: "danger" }
  ];
  const bootStatus = readStatus(boot, false);
  w("  运行中（启动+翻题+噪音）：判定 = %s", bootStatus);
  w("  [%s] 运行中应为绿", bootStatus === "run" ? "OK" : "NG");
  if (bootStatus !== "run") fail.push("运行中未判绿");

  // 2c. 真终止
  const stopped = boot.concat([{ message: "脚本已停止", type: "danger" }]);
  const stopStatus = readStatus(stopped, false);
  w("  真终止（最新一条=脚本已停止）：判定 = %s", stopStatus);
  w("  [%s] 真终止应为红", stopStatus === "stop" ? "OK" : "NG");
  if (stopStatus !== "stop") fail.push("真终止未判红");

  // 2d. 答题中优先黄
  const busyStatus = readStatus(boot, true);
  w("  答题中（有题目在答）：判定 = %s", busyStatus);
  w("  [%s] 答题中应为黄", busyStatus === "busy" ? "OK" : "NG");
  if (busyStatus !== "busy") fail.push("答题中未判黄");

  // 2e. 终止后恢复
  const resumed = stopped.concat([{ message: "鲸娘重新潜入，开始干活～", type: "success" }]);
  const rs = readStatus(resumed, false);
  w("  终止后恢复（最新一条=重新潜入）：判定 = %s", rs);
  w("  [%s] 恢复后应为绿", rs === "run" ? "OK" : "NG");
  if (rs !== "run") fail.push("恢复后未判绿");

  // 2f. 旧逻辑对照：证明旧规则必然误红
  const oldRuleRed = noiseLogs.slice(-6).some(function (x) { return x.type === "danger" || x.type === "error"; });
  w("");
  w("  对照：旧规则（最近 6 条里有 danger/error 就判红）对同一批噪音 → %s", oldRuleRed ? "红（误判）" : "绿（不误判）");
  w("  [%s] 旧规则确实会误红（说明本次改动有实际作用）", oldRuleRed ? "OK" : "NG");
  if (!oldRuleRed) fail.push("旧规则并未误红，本次改动的必要性需要重新论证");
}

// ---------- 3. 路由：答题中不得跳走 ----------
w("");
w("智能路由（答题中留在鲸娘页，答完才回状态页）：");
const routeChecks = [
  ["hxIsBusy 定义", /const hxIsBusy = \(\) => \{/, 1],
  ["hxJumpToLog 定义", /const hxJumpToLog = \(\) => \{/, 1],
  ["hxWasBusy 声明", /let hxWasBusy = false;/, 1],
  ["答题中提前 return", /if \(busy\) \{\s*\n\s*hxWasBusy = true;/, 1],
  ["答题结束才跳", /if \(hxWasBusy\) \{\s*\n\s*hxWasBusy = false;/, 1],
  ["启动时记录 busy", /hxWasBusy = hxIsBusy\(\);\s*\n\s*return;/, 1],
  ["跳转函数被复用", /hxJumpToLog\(\);/g, 2],
  ["探针补 busy", /busy: hxIsBusy\(\), wasBusy: hxWasBusy/, 1]
];
for (const c of routeChecks) {
  const n = (src.match(c[1]) || []).length;
  const ok = n === c[2];
  w("  [%s] %s  got=%d exp=%d", ok ? "OK" : "NG", c[0], n, c[2]);
  if (!ok) fail.push("路由检查失败：" + c[0]);
}

// ---------- 4. JS 标识符 ----------
w("");
w("JS 标识符：");
const decls = [
  ["HX_BUILD = 0.4.10", /const HX_BUILD = "0\.4\.10";/, 1],
  ["HX_FATAL_RE 声明", /const HX_FATAL_RE = \//, 1],
  ["HX_RESUME_RE 声明", /const HX_RESUME_RE = \//, 1],
  ["readPanelStatus 定义", /const readPanelStatus = \(\) => \{/, 1],
  ["readPanelStatus 引用", /readPanelStatus/g, 3],
  ["用量栏: 本次 = 请求数", /\["本次", String\(sess\.requests\)/, 1],
  ["用量栏: 总花费", /\["总花费", formatCost\(store\.cost\)/, 1],
  ["用量栏: 好感度胶囊", /class="usage-fav"/, 1],
  ["用量栏: 运行时长保留", /class="usage-uptime"/, 1],
  ["用量栏: build 属性", /data-hx-build="' \+ HX_BUILD/, 1],
  ["好感度锚点选取", /const hxFavAnchorPick = \(root\) => \{/, 1],
  ["好感度观察器定义", /const hxFavObserve = \(host\) => \{/, 1],
  ["MutationObserver 抗重渲染", /new MutationObserver\(\(\) => \{/, 1],
  ["迁移: 考试 -> 测试", /"考试": "测试"/, 1],
  ["参数组名: 测试", /name: "测试"/, 1]
];
for (const d of decls) {
  const n = (src.match(d[1]) || []).length;
  const ok = n === d[2];
  w("  [%s] %s  got=%d exp=%d", ok ? "OK" : "NG", d[0], n, d[2]);
  if (!ok) fail.push("标识符检查失败：" + d[0]);
}

// ---------- 5. 旧物清除 ----------
w("");
w("旧物清除（改版后不应再出现的旧出参/旧判定）：");
const gone = [
  ["旧版号残留 0.4.9", /0\.4\.9/g],
  ["旧「请求」用量键", /usage-tag__k">请求/],
  ["旧 tok/s 速率（含死函数 formatRate）", /formatRate|tok\/s/],
  ["旧用量栏出参 class=\"usage-tag ", /class="usage-tag /g],
  ["旧用量栏出参 class=\"usage-rate\"", /class="usage-rate"/g],
  ["旧用量栏出参 class=\"usage-session\"", /class="usage-session"/g],
  ["旧状态灯逻辑 logs.slice(-6).some", /logs\.slice\(-6\)\.some/g],
  ["旧状态灯逻辑 let dead = false;", /let dead = false;/g]
];
for (const g of gone) {
  const n = (src.match(g[1]) || []).length;
  const ok = n === 0;
  w("  [%s] %s  got=%d exp=0", ok ? "OK" : "NG", g[0], n);
  if (!ok) fail.push("旧物未清除：" + g[0]);
}
// 用量栏构建函数体内部单独校验（旧类名可能仅作为历史 CSS 残留存在，不算出参）
const bStart = src.indexOf("const buildUsageBarHtml = (store, peak) => {");
const bEnd = src.indexOf("\n  };", bStart);
const builder = (bStart >= 0 && bEnd > bStart) ? src.slice(bStart, bEnd) : "";
w("  用量栏构建函数体长度 = %d", builder.length);
if (!builder) fail.push("找不到 buildUsageBarHtml 函数体");
else {
  const bchk = [
    ["函数体内无 usage-tag 出参", /class="usage-tag/, 0],
    ["函数体内无 usage-rate 出参", /class="usage-rate/, 0],
    ["函数体内无 usage-session 出参", /class="usage-session/, 0],
    ["无旧单元格标签 「请求」", /\["请求"/, 0],
    ["无旧单元格标签 「花费」", /\["花费"/, 0],
    ["新单元格标签 「本次」= 本次请求数", /\["本次", String\(sess\.requests\)/, 1],
    ["新单元格标签 「总花费」= 累计花费", /\["总花费", formatCost\(store\.cost\)/, 1],
    ["顶级标签 = 好感度胶囊", /class="usage-fav"/, 1],
    ["保留运行时长胶囊", /class="usage-uptime"/, 1]
  ];
  for (const c of bchk) {
    const n = (builder.match(c[1]) || []).length;
    const ok = n === c[2];
    w("  [%s] %s  got=%d exp=%d", ok ? "OK" : "NG", c[0], n, c[2]);
    if (!ok) fail.push("用量栏函数体检查失败：" + c[0]);
  }
  w("  （说明）「请求」「空闲/高峰」仍出现在 title 提示文案里，这是有意保留的说明文字，非出参标签");
}
w("  （参考）usage-tag 全文 %d 处、usage-rate %d 处、usage-session %d 处 —— 允许作为历史 CSS 残留",
  (src.match(/usage-tag/g) || []).length, (src.match(/usage-rate/g) || []).length, (src.match(/usage-session/g) || []).length);

// ---------- 汇总 ----------
w("");
w("====================== 汇总 ======================");
w("失败项 = %d", fail.length);
fail.forEach(function (f, i) { w("  %d) %s", i + 1, f); });
w(fail.length === 0 ? "★ 全部通过" : "✗ 存在失败项，需修复");

fs.writeFileSync(OUT, out.join("\r\n"), "utf8");
console.log(out.join("\r\n"));
process.exit(fail.length === 0 ? 0 : 1);
