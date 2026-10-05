/* _verify54.js —— 0.4.12 验收（Node 逐字节 + 真实求值 + 旧逻辑对照）
 *
 * 与既有四类手段一脉相承，本轮把「本次用量」的判定逻辑做真值表 + 旧逻辑对照：
 * 光断言「sessionStorage 没了」等于没验 —— 必须证明
 *   ① 旧逻辑在同一输入上确实给错答案（本次=20 不归零）
 *   ② 新逻辑在同一输入上给出正确答案（本次=0）
 *
 * 用法：node docs/tools/verifiers/_verify54.js
 * 产出：docs/reports/_v54out.txt
 *
 * 可复现性（0.4.12 修订）：所有路径由 __dirname 推导，不再依赖工作区散件；
 * 对照基线锁定仓库内权威快照 docs/versions/v0.4.11.user.js 并以 SHA256 钉死，
 * 防止「随手拿一个旧文件当基线」这种静默失效。
 */
const fs = require("fs");
const path = require("path");
const vm = require("vm");
const crypto = require("crypto");

const REPO = path.resolve(__dirname, "..", "..", "..");
const NEWF = path.join(REPO, "海底小纵队·探矿鲸娘.user.js");
const OUT = path.join(REPO, "docs", "reports", "_v54out.txt");

// 对照基线（0.4.11）：优先仓库内权威快照，兼容历史工作区备份
const BASE_CANDIDATES = [
  path.join(REPO, "docs", "versions", "v0.4.11.user.js"),
  path.resolve(REPO, "..", "_bak_0411.user.js"),
];
const BASE_SHA = "9c290a8346fce5e7bf158111a21f834b4ac6142ed8f83f0cef47bf4fbbf81a97";
const OLDF = BASE_CANDIDATES.find(function (p) { return fs.existsSync(p); }) || BASE_CANDIDATES[0];
const sha256 = function (b) { return crypto.createHash("sha256").update(b).digest("hex"); };

const L = [];
const w = (s) => L.push(String(s));
let fails = 0;
function ck(name, got, exp, extra) {
  const ok = String(got) === String(exp);
  if (!ok) fails++;
  w("  [" + (ok ? "OK" : "NG") + "] " + String(name).padEnd(38) + " got=" + got + " exp=" + exp
    + (extra === undefined ? "" : "  " + extra));
}
function ckT(name, cond, extra) {
  if (!cond) fails++;
  w("  [" + (cond ? "OK" : "NG") + "] " + String(name).padEnd(38) + (extra === undefined ? "" : "  " + extra));
}
function flush() {
  w("");
  w("================================");
  w(fails === 0 ? "结论：全部通过（fail=0）" : "结论：存在失败项 fail=" + fails);
  fs.writeFileSync(OUT, L.join("\n"), "utf8");
  process.exit(fails === 0 ? 0 : 1);
}
// 崩溃兜底：任何意外异常也要把报告落盘，否则等于没有凭据
process.on("uncaughtException", (e) => {
  fails++;
  w("");
  w("[NG] 验收脚本未捕获异常：" + e.message);
  w("     " + String(e.stack || "").split("\n").slice(1, 4).join(" | "));
  flush();
});

// ─────────────────────────────────────────────────────────────
const buf = fs.readFileSync(NEWF);
const src = buf.toString("utf8");
const oldBuf = fs.readFileSync(OLDF);
const oldSrc = oldBuf.toString("utf8");

w("=========== 0.4.12 验收 ===========");
w("文件 " + NEWF);
w("基线 " + path.relative(REPO, OLDF).replace(/\\/g, "/") + "  （候选命中 = "
  + BASE_CANDIDATES.findIndex(function (p) { return p === OLDF; }) + "）");
w("");

// ── 1. 语法可解析 ─────────────────────────────────────────────
w("=== 1. 语法（vm.Script 解析，等价 node --check）===");
try {
  new vm.Script(src, { filename: "whale.user.js" });
  w("  [OK] 整文件解析通过");
} catch (e) {
  w("  [NG] 解析失败：" + e.message);
  fails++;
}
// 旧文件同法解析（对照基线可读）
try { new vm.Script(oldSrc); w("  [OK] 对照基线（0.4.11）亦可解析"); }
catch (e) { w("  [NG] 备份解析失败：" + e.message); fails++; }
// 基线身份钉死：必须等于版本链记录的 v0.4.11 哈希，否则对照无意义
ck("对照基线 SHA256 = v0.4.11 官方值", sha256(oldBuf), BASE_SHA);

// ── 2. 行尾逐字节 ─────────────────────────────────────────────
w("");
w("=== 2. 行尾（Node 逐字节）===");
function eol(b) {
  let crlf = 0, lf = 0;
  for (let i = 0; i < b.length; i++) {
    if (b[i] === 10) { if (i > 0 && b[i - 1] === 13) crlf++; else lf++; }
  }
  return { crlf, lf };
}
const e1 = eol(buf);
w("  现行版 bytes=" + buf.length + "  CRLF=" + e1.crlf + "  裸LF=" + e1.lf);
ck("现行版 裸 LF = 0", e1.lf, 0);
ck("现行版 字节 = 639440", buf.length, 639440);
const e0 = eol(oldBuf);
w("  基线   bytes=" + oldBuf.length + "  CRLF=" + e0.crlf + "  裸LF=" + e0.lf);
ck("基线   裸 LF = 0", e0.lf, 0);
ck("基线   字节 = 640151（v0.4.11 官方值）", oldBuf.length, 640151);

// ── 3. CSS 装配真实求值 ───────────────────────────────────────
w("");
w("=== 3. CSS 装配：真跑一遍，不信字符串存在 ===");
// 沿用 0.4.10 起的做法：取整个装配区间 -> 剥掉字符串/注释 -> 找出区间外引用的标识符并桩掉 -> 真跑
let css = null;
try {
  const MARK = 'const layoutCss = LAYOUT_CSS_PARTS.join("")';
  const i0 = src.indexOf("const LAYOUT_CSS_PARTS = [");
  const jt = src.indexOf(MARK, i0);
  if (i0 < 0 || jt < 0) throw new Error("找不到 LAYOUT_CSS_PARTS 区间（i0=" + i0 + " jt=" + jt + "）");
  const region = src.slice(i0, jt + MARK.length);
  w("  装配区间长度 = " + region.length);
  const stripped = region
    .replace(/"(?:[^"\\]|\\.)*"/gs, '""')
    .replace(/'(?:[^'\\]|\\.)*'/gs, "''")
    .replace(/\/\*(?:[\s\S]*?)\*\//g, "")
    .replace(/\/\/[^\n]*/g, "");
  const ids = new Set();
  stripped.replace(/\b([A-Za-z_$][\w$]*)\b/g, (m, x) => { ids.add(x); return m; });
  const declared = new Set();
  stripped.replace(/\b(?:const|let|var)\s+([A-Za-z_$][\w$]*)/g, (m, x) => { declared.add(x); return m; });
  const KEYWORDS = new Set(["const", "let", "var", "if", "else", "return", "typeof", "true", "false", "null",
    "void", "function", "new", "String", "Number", "Math", "Boolean", "window", "document", "Array", "Object",
    "undefined", "for", "of", "in", "while", "break", "continue", "push", "join", "length", "slice", "replace"]);
  const externals = [...ids].filter((x) => !declared.has(x) && !KEYWORDS.has(x));
  w("  区间内声明 " + declared.size + " 个；外部引用：" + (externals.join(", ") || "无"));
  const stubs = externals.map((n) => 'const ' + n + ' = "";').join("\n");
  css = new Function(stubs + "\n" + region + '\nreturn LAYOUT_CSS_PARTS.join("");')();
  w("  [OK] 真实求值成功，装配后 CSS 长度 = " + css.length);
} catch (e) {
  w("  [NG] 装配区真实求值失败：" + e.message);
  fails++;
}
if (css !== null) {
  // 花括号深度
  let depth = 0, min = 0, bad = 0;
  for (const c of css) { if (c === "{") depth++; else if (c === "}") { depth--; if (depth < min) min = depth; if (depth < 0) bad++; } }
  ck("花括号终值深度", depth, 0);
  ck("花括号最小深度 < 0 次数", bad, 0);
  w("    最小深度 = " + min);
  // 字面 \n 污染（两个字符的 backslash-n）应为 0
  let lit = 0;
  for (let i = 0; i + 1 < css.length; i++) if (css[i] === "\\" && css[i + 1] === "n") lit++;
  ck("字面 \\n 污染", lit, 0);
  w("    真实换行数 = " + (css.match(/\n/g) || []).length);

  // ── 4. 规则存在性 ───────────────────────────────────────────
  w("");
  w("=== 4. CSS 规则存在性（0.4.12 新增 + 死代码清除）===");
  const mustHave = [
    [".main-page .usage-cell[data-hx-cell='session']{cursor:pointer}", "本次格 cursor:pointer"],
    [".main-page .usage-cell[data-hx-cell='session']:hover{", "本次格悬停反馈"],
    [".main-page .usage-cell[data-hx-cell='session']:active{transform:none}", "本次格按下不位移"],
    ["v0.4.12", "本轮分节注释"],
  ];
  for (const [n, label] of mustHave) ck("含 " + label, css.includes(n), true);
  const mustNot = [
    ["usage-session", "旧用量胶囊规则"],
  ];
  for (const [n, label] of mustNot) ck("不含 " + label, css.includes(n), false);

  // ── 5. 级联顺序 ─────────────────────────────────────────────
  w("");
  w("=== 5. 级联顺序断言（新规则必须写在被覆盖的旧规则之后）===");
  const older = css.indexOf(".main-page .usage-cell{border:none!important;");
  const olderHover = css.indexOf(".main-page .usage-cell:hover{background:var(--lg-tint-hi)");
  const newer = css.indexOf(".main-page .usage-cell[data-hx-cell='session']{cursor:pointer}");
  ckT("旧 .usage-cell 规则存在（被覆盖方）", older >= 0, "offset=" + older);
  ckT("旧 .usage-cell:hover 存在（被覆盖方）", olderHover >= 0, "offset=" + olderHover);
  ckT("新本次格规则 offset > 旧规则 offset", newer > older, newer + " > " + older);
  ckT("新本次格规则 offset > 旧 hover offset", newer > olderHover, newer + " > " + olderHover);
  // 分节注释顺序：v0.4.12 块必须在 v0.4.11 本轮块之后
  const c11 = css.indexOf("v0.4.11 · 本轮");
  const c12 = css.indexOf("v0.4.12 · 本轮");
  ckT("v0.4.12 块排在 v0.4.11 本轮块之后", c12 > c11 && c11 >= 0, c11 + " -> " + c12);
} else {
  w("  !! 装配求值失败，跳过后继 CSS 断言");
}

// ── 6. 「本次」判定真值表 + 旧逻辑对照 ────────────────────────
w("");
w("=== 6. 「本次」用量：真值表（新逻辑） + 旧逻辑对照 ===");
function sliceBlock(text, startNeedle) {
  const i = text.indexOf(startNeedle);
  if (i < 0) return null;
  const endNeedle = "const resetSessionUsage = () => {";
  const j = text.indexOf(endNeedle, i);
  if (j < 0) return null;
  const k = text.indexOf("\n  };", j);
  if (k < 0) return null;
  return text.slice(i, k + 5);
}
const newBlock = sliceBlock(src, "let sessionBase = {");
const oldBlock = sliceBlock(oldSrc, "const HX_SESSION_KEY = ");
ckT("新块已抠出", !!newBlock, newBlock ? newBlock.length + " 字符" : "");
ckT("旧块已抠出（对照）", !!oldBlock, oldBlock ? oldBlock.length + " 字符" : "");

// 假 sessionStorage：模拟「同一标签页内跨刷新存活」
function fakeSessionStorage() {
  const m = new Map();
  return {
    getItem: (k) => (m.has(k) ? m.get(k) : null),
    setItem: (k, v) => { m.set(k, String(v)); },
    removeItem: (k) => { m.delete(k); },
    _dump: () => Array.from(m.entries()),
  };
}
function loader(blockSrc, store) {
  return function load(usageStore) {
    const usageTick = { value: 0 };
    const fn = new Function(
      "usageStore", "usageTick", "sessionStorage", "unsafeWindow",
      blockSrc + "\nreturn { sessionUsage: sessionUsage, resetSessionUsage: resetSessionUsage };"
    );
    return fn(usageStore, usageTick, store, undefined);
  };
}
function runScenario(blockSrc, label) {
  const store = fakeSessionStorage();
  const load = loader(blockSrc, store);
  const usage = { cost: 0, totalTokens: 0, requests: 0 };
  const steps = [];
  // L1 首次加载（累计 0）
  let api = load(usage);
  steps.push(["L1 首次加载（累计 0）", api.sessionUsage().requests]);
  // L1 答题后（累计 20）
  usage.requests = 20; usage.totalTokens = 29000; usage.cost = 10.08;
  steps.push(["L1 答题后（累计 20）", api.sessionUsage().requests]);
  // L2 重新启用（累计仍是 20）—— 用户报的场景
  api = load(usage);
  steps.push(["L2 重新启用（累计 20）", api.sessionUsage().requests]);
  // L2 再答一题（累计 26）
  usage.requests = 26; usage.totalTokens = 34000; usage.cost = 11.2;
  steps.push(["L2 再答一题（累计 26）", api.sessionUsage().requests]);
  // L2 手动归零
  api.resetSessionUsage();
  steps.push(["L2 点击归零（累计 26）", api.sessionUsage().requests]);
  w("");
  w("  ── " + label + " ──");
  for (const [k, v] of steps) w("     " + k.padEnd(28) + " 本次 = " + v);
  return Object.fromEntries(steps);
}
const gotNew = runScenario(newBlock, "新逻辑（0.4.12 内存基线）");
const gotOld = runScenario(oldBlock, "旧逻辑（0.4.11 会话级存储 · 对照）");

w("");
w("  判据表：");
ck("新 · L1 首次加载 = 0", gotNew["L1 首次加载（累计 0）"], 0);
ck("新 · L1 答题后 = 20", gotNew["L1 答题后（累计 20）"], 20);
ck("新 · L2 重新启用 = 0（已修复）", gotNew["L2 重新启用（累计 20）"], 0);
ck("新 · L2 再答一题 = 6", gotNew["L2 再答一题（累计 26）"], 6);
ck("新 · L2 点击归零 = 0", gotNew["L2 点击归零（累计 26）"], 0);
ck("旧 · L2 重新启用 = 20（复现原 bug）", gotOld["L2 重新启用（累计 20）"], 20);
ckT("对照成立：旧逻辑确实不归零（20 ≠ 0）", gotOld["L2 重新启用（累计 20）"] !== gotNew["L2 重新启用（累计 20）"],
  "旧=" + gotOld["L2 重新启用（累计 20）"] + " 新=" + gotNew["L2 重新启用（累计 20）"]);

// ── 7. 结构性不变量（源码级） ─────────────────────────────────
w("");
w("=== 7. 结构性不变量（源码）===");
const cnt = (n) => src.split(n).length - 1;
ck("unsafeWindow.sessionStorage 归零", cnt("unsafeWindow.sessionStorage"), 0);
ck("readSessionBase 归零", cnt("readSessionBase"), 0);
ck("usage-session 全清", cnt("usage-session"), 0);
ck("data-hx-cell 标记数", cnt('data-hx-cell="session"'), 2);
ck("closest('[data-hx-cell=\"session\"]') 调用 1 处", cnt("closest('[data-hx-cell=\"session\"]')"), 1);
ck("let sessionBase 声明 1 处", cnt("let sessionBase = {"), 1);
ck("resetSessionUsage 定义 1 处", cnt("const resetSessionUsage = () => {"), 1);
ck("resetSessionUsage 调用点 2 处（点击处理 + 探针）", cnt("resetSessionUsage();"), 2);
ck("HX_BUILD = 0.4.12", cnt('const HX_BUILD = "0.4.12";'), 1);
ck("@version 0.4.12", cnt("// @version      0.4.12"), 1);
ck("通知页日志 0.4.12", cnt("面板 0.4.12 已就位"), 1);
ck("教程页页脚 v0.4.12", cnt("· v0.4.12 · MIT License"), 1);
ck("__HX_SESSION_RESET__ 探针保留", cnt("__HX_SESSION_RESET__"), 1);

flush();
