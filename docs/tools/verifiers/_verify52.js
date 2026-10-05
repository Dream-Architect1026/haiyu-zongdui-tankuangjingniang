// _verify52.js —— 0.4.11 回归验收
// 语法 + CSS 真实求值 + 【真实级联求解：证明 4 个数值参数行的调节控件落在行右侧】+ 路由 3s + 旧功能不回归
const fs = require("fs");
const vm = require("vm");
const util = require("util");
const P = "C:\\Users\\D_A\\DoubaoWork\\chats\\2026-10-05\\new-chat-4\\海底小纵队·探矿鲸娘.user.js";
const OUT = "C:\\Users\\D_A\\WorkBuddy\\2026-10-05-13-53-42\\_v52out.txt";
const buf = fs.readFileSync(P);
const src = buf.toString("utf8");
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

  // ══════════════════════════════════════════════════════════
  // 2. 【核心】真实级联求解：4 个数值参数行的排布与胶囊外观
  // ══════════════════════════════════════════════════════════
  w("");
  w("=== 2. 数值参数行（倍速/操作间隔/正确阈值/相似阈值）真实级联求解 ===");

  // 解析所有规则（含 @media 内部规则；跳过 keyframes 的百分比/from/to 停止点）
  const rules = [];
  {
    const re = /([^{}]+)\{([^{}]*)\}/g;
    let m;
    while ((m = re.exec(css))) {
      const sel = m[1].trim().replace(/\s+/g, " ");
      if (!sel) continue;
      if (sel.charAt(0) === "@") continue;
      if (/^(\d|from\b|to\b)/.test(sel)) continue;
      if (sel.indexOf("%") >= 0 && !/\./.test(sel)) continue;
      rules.push({ sel: sel, body: m[2] });
    }
  }
  w("解析出规则 %d 条", rules.length);

  const SRC = { idx: src, };
  // 用 src 顺序算偏移（规则在 css 中的次序即装配次序）
  function compounds(sel) { return sel.replace(/\s*[>+~]\s*/g, " ").trim().split(/\s+/); }
  function classesOf(part) { return (part.match(/\.[A-Za-z_][\w-]*/g) || []).map(function (x) { return x.slice(1); }); }
  function spec(sel) {
    let a = 0, b = 0, c = 0;
    compounds(sel).forEach(function (part) {
      a += (part.match(/#[A-Za-z_][\w-]*/g) || []).length;
      b += (part.match(/\.[A-Za-z_][\w-]*|\[[^\]]*\]|::?[A-Za-z-]+(\([^)]*\))?/g) || []).length;
      const t = part.replace(/[#.\[:].*$/, "");
      if (/^[A-Za-z][\w-]*/.test(t)) c += 1;
    });
    return [a, b, c];
  }
  function specStr(sp) { return sp.join("-"); }

  // 目标：div.main-page > div.setting > div.el-form-item.is-required > (label|content)
  const UNION = ["main-page", "setting", "el-form-item", "is-required", "el-form-item__label", "el-form-item__content"];
  function matches(sel, tailClass, mustInclude) {
    if (!mustInclude) {
      // 元素本体探针：伪元素规则（::before）与状态伪类（:hover）在当前稳态下不生效，必须排除，
      // 否则 ::before 的 margin:0 会冒充标签本体的 margin（本轮真吃过一次这个误报）
      if (sel.indexOf("::") >= 0) return false;
      if (/:(hover|active|focus|focus-visible|focus-within|visited|target)\b/.test(sel)) return false;
    } else if (sel.indexOf(mustInclude) < 0) return false;
    const cs = compounds(sel);
    if (!cs.length) return false;
    const lc = classesOf(cs[cs.length - 1]);
    if (lc.indexOf(tailClass) < 0) return false;
    for (const part of cs) {
      for (const c of classesOf(part)) {
        if (UNION.indexOf(c) < 0) return false;
      }
    }
    return true;
  }
  function effective(prop, tailClass, mustInclude) {
    let best = null;
    rules.forEach(function (r, i) {
      if (!matches(r.sel, tailClass, mustInclude)) return;
      r.body.split(";").forEach(function (d) {
        const k = d.indexOf(":");
        if (k < 0) return;
        const p = d.slice(0, k).trim();
        if (p !== prop) return;
        let raw = d.slice(k + 1).trim();
        const imp = /!important\s*$/.test(raw);
        const val = raw.replace(/!important\s*$/, "").trim();
        const sp = spec(r.sel);
        if (val === "") return;
        const cand = { imp: imp, sp: sp, order: i, val: val, sel: r.sel };
        if (!best) { best = cand; return; }
        let better = false;
        if (cand.imp !== best.imp) better = cand.imp;
        else {
          for (let z = 0; z < 3; z++) {
            if (cand.sp[z] !== best.sp[z]) { better = cand.sp[z] > best.sp[z]; break; }
          }
          if (cand.sp.join() === best.sp.join()) better = cand.order > best.order;
        }
        if (better) best = cand;
      });
    });
    return best;
  }
  function show(prop, tailClass, mustInclude) {
    const b = effective(prop, tailClass, mustInclude);
    if (!b) return "（无匹配声明）";
    return b.val + "    <= " + b.sel + "  [spec " + specStr(b.sp) + (b.imp ? ", !important" : "") + "]";
  }

  const probes = [
    ["label", ".is-required 行 标签 flex", "flex", "el-form-item__label", ""],
    ["label", ".is-required 行 标签 border", "border", "el-form-item__label", ""],
    ["label", ".is-required 行 标签 border-radius", "border-radius", "el-form-item__label", ""],
    ["label", ".is-required 行 标签 padding", "padding", "el-form-item__label", ""],
    ["label", ".is-required 行 标签 margin", "margin", "el-form-item__label", ""],
    ["content", ".is-required 行 控件 flex", "flex", "el-form-item__content", ""],
    ["content", ".is-required 行 控件 margin-left", "margin-left", "el-form-item__content", ""],
    ["content", ".is-required 行 控件 justify-content", "justify-content", "el-form-item__content", ""],
    ["before", ".is-required 行 星号 display", "display", "el-form-item__label", "::before"]
  ];
  const eff = {};
  for (const p of probes) {
    const b = effective(p[2], p[3], p[4]);
    eff[p[0] + "." + p[2]] = b ? b.val : null;
    w("  %s = %s", p[1], show(p[2], p[3], p[4]));
  }

  w("");
  w("  断言：");
  function assertEq(label, got, want) {
    const ok = got === want;
    w("    [%s] %s  got=%s  want=%s", ok ? "OK" : "NG", label, JSON.stringify(got), JSON.stringify(want));
    if (!ok) fail.push("级联断言失败：" + label);
  }
  function assertHas(label, got, needle) {
    const ok = typeof got === "string" && got.indexOf(needle) >= 0;
    w("    [%s] %s  含 %s", ok ? "OK" : "NG", label, needle);
    if (!ok) fail.push("级联断言失败：" + label);
  }
  function assertNotHas(label, got, needle) {
    const ok = !(typeof got === "string" && got.indexOf(needle) >= 0);
    w("    [%s] %s  不含 %s", ok ? "OK" : "NG", label, needle);
    if (!ok) fail.push("级联断言失败：" + label);
  }

  // 标签 = 收缩的小胶囊（不再 flex:1 1 auto 撑满整行）
  assertEq("标签 flex 收缩为胶囊（不撑满行）", eff["label.flex"], "0 0 auto");
  assertHas("标签圆角 8px（小胶囊）", eff["label.border-radius"], "8px");
  assertHas("标签描边为常规玻璃冷蓝", eff["label.border"], "140,200,255");
  assertNotHas("标签描边已无粉红", eff["label.border"], "255,152,152");
  // 控件被显式推到行右侧
  assertEq("控件 margin-left:auto（推到行右侧）", eff["content.margin-left"], "auto");
  assertEq("控件 flex:0 0 auto（不被拉伸）", eff["content.flex"], "0 0 auto");
  assertEq("控件靠右对齐", eff["content.justify-content"], "flex-end");
  // 星号隐藏
  assertEq("必填星号已隐藏", eff["before.display"], "none");

  // 反向对照：模拟"没有 B3 规则"时的结果应当不是 auto —— 证明该规则确实在起作用
  w("");
  w("  反向对照（剔除 B3 规则后重算 margin-left，应回落到 8px）：");
  {
    const idxB3 = rules.findIndex(function (r) {
      return r.sel.indexOf("is-required") >= 0 && classesOf(compounds(r.sel).pop()).indexOf("el-form-item__content") >= 0;
    });
    if (idxB3 < 0) fail.push("找不到 B3 控件推右规则");
    const keep = rules[idxB3];
    rules[idxB3] = { sel: ".__hx_disabled__", body: keep.body };
    const before = effective("margin-left", "el-form-item__content", "");
    rules[idxB3] = keep;
    const v = before ? before.val : null;
    const ok = v !== "auto";
    w("    [%s] 无 B3 时 margin-left = %s（≠auto 才能证明 B3 有效）", ok ? "OK" : "NG", JSON.stringify(v));
    if (!ok) fail.push("反向对照失败：B3 规则似乎无效");
  }

  // ---------- 2b. 级联顺序 ----------
  w("");
  w("级联顺序（新规则必须晚于被它覆盖的旧规则）：");
  const last = function (x) { return css.lastIndexOf(x); };
  const NEWBLK = "/* ==== v0.4.11 · 本轮 :";
  const order = [
    ["新块 晚于 好感度面板块", NEWBLK, "/* ==== v0.4.11 : 好感度面板"],
    ["新块 晚于 液态玻璃块", NEWBLK, "/* ==== v0.4.11 liquid glass ==== */"],
    ["必填胶囊 晚于 表单标签基样式", ".el-form-item.is-required>.el-form-item__label{flex", ".main-page .setting .el-form-item__label{"],
    ["控件推右 晚于 控件基样式", ".el-form-item.is-required>.el-form-item__content{margin-left:auto", ".main-page .setting .el-form-item__content{flex:0 0 auto;margin-left:8px"]
  ];
  for (const pair of order) {
    const a = last(pair[1]), b = last(pair[2]);
    const ok = a > b && a >= 0 && b >= 0;
    w("  [%s] %s (新@%d > 旧@%d)", ok ? "OK" : "NG", pair[0], a, b);
    if (!ok) fail.push("级联顺序错：" + pair[0]);
  }
}

// ---------- 3. 智能路由 3s ----------
w("");
w("=== 3. 智能路由：状态页停留 3s ===");
const routeChk = [
  ["HX_TAB_RETURN_MS = 3000", /const HX_TAB_RETURN_MS = 3000;/, 1],
  ["旧值 10000 已无", /HX_TAB_RETURN_MS = 10000/, 0],
  ["定时器引用该常量", /\}, HX_TAB_RETURN_MS\)/, 1],
  ["无写死 10000 的定时器", /\}, 10000\)/, 0],
  ["答题中不跳（busy 早返回）", /if \(busy\) \{\s*hxWasBusy = true;/, 1],
  ["答题结束必跳一次", /if \(hxWasBusy\) \{\s*hxWasBusy = false;/, 1],
  ["注释已同步 3s", /安静 3s 回鲸娘/, 1]
];
for (const c of routeChk) {
  const n = (src.match(c[1]) || []).length;
  const ok = n === c[2];
  w("  [%s] %s  got=%d exp=%d", ok ? "OK" : "NG", c[0], n, c[2]);
  if (!ok) fail.push("路由检查失败：" + c[0]);
}

// ---------- 4. 模板结构（胶囊选择器依赖 required 属性） ----------
w("");
w("=== 4. 模板结构 ===");
const tpl = [
  ["required 属性保留（胶囊选择器依赖）", (src.match(/required: ""/g) || []).length, 2],
  ["is-required 胶囊规则仍唯一", (src.match(/\.el-form-item\.is-required>\.el-form-item__label\{flex:0 0 auto/g) || []).length, 1],
  ["B3 推右规则唯一", (src.match(/is-required>\.el-form-item__content\{margin-left:auto/g) || []).length, 1],
  ["行基础 flex 排布仍在", (src.match(/\.main-page \.setting \.el-form-item\{display:flex;align-items:center;margin:0!important\}/g) || []).length, 1],
  ["AI 卡字段胶囊未误伤", (src.match(/\.setting-ai-field>\.el-form-item__label\{flex:0 0 auto/g) || []).length, 1],
  ["旧粉星号色已清零", (src.match(/#ff9a9a/g) || []).length, 0],
  ["旧粉描边已清零", (src.match(/rgba\(255,152,152,\.30\)/g) || []).length, 0],
  ["版本 0.4.11", (src.match(/0\.4\.11/g) || []).length, 18]
];
for (const c of tpl) {
  const ok = c[1] === c[2];
  w("  [%s] %s  got=%d exp=%d", ok ? "OK" : "NG", c[0], c[1], c[2]);
  if (!ok) fail.push("模板检查失败：" + c[0]);
}

// ---------- 5. 旧功能不回归 ----------
w("");
w("=== 5. 旧功能回归点 ===");
const reg = [
  ["鲸娘双态文案", /小鲸娘正在吃白饭/, 1],
  ["作答态文案", /主人别急，马上就好/, 1],
  ["好感度卡片挂载", /bindFavCard\(\);/, 1],
  ["状态灯三色", /hx-status-dot\[data-hx-status='stop'\]/, 1],
  ["状态灯读日志（新版判定）", /const readPanelStatus = \(\) => \{/, 1],
  ["用量栏：本次", /usage-uptime/, 1],
  ["用量栏：好感度胶囊", /usage-fav/, 1],
  ["tok\/s 已清除", /formatRate|tok\/s/, 0],
  ["探针 __HX_FAV__", /w\.__HX_FAV__ = /, 1],
  ["探针 __HX_TAB__", /w\.__HX_TAB__ = /, 1]
];
for (const c of reg) {
  const n = (src.match(c[1]) || []).length;
  const ok = n >= c[2] && (c[2] === 0 ? n === 0 : true);
  w("  [%s] %s  got=%d min=%d", ok ? "OK" : "NG", c[0], n, c[2]);
  if (!ok) fail.push("回归点失败：" + c[0]);
}

// ---------- 汇总 ----------
w("");
if (fail.length === 0) {
  w("===== 全部通过（fail=0）=====");
} else {
  w("===== 失败 %d 项 =====", fail.length);
  fail.forEach(function (x) { w("  !! " + x); });
}
fs.writeFileSync(OUT, out.join("\n"), "utf8");
process.exit(fail.length === 0 ? 0 : 1);
