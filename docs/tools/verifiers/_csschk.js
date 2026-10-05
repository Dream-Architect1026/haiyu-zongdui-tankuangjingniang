// 校验装配后的 layoutCss 是否语法可解析（花括号配平 + 可疑构造）
const fs = require("fs");
const P = "C:\\Users\\D_A\\DoubaoWork\\chats\\2026-10-05\\new-chat-4\\海底小纵队·探矿鲸娘.user.js";
const src = fs.readFileSync(P, "utf8");

const startTag = "const LAYOUT_CSS_PARTS = [";
const endTag = "const layoutCss = LAYOUT_CSS_PARTS.join(\"\");";
const i = src.indexOf(startTag), j = src.indexOf(endTag);
const region = src.slice(i, j);

const KNOWN = { DEFAULT_CARD_WIDTH: "'310px'", PANEL_HEIGHT: "500", MINIMIZED_PANEL_HEIGHT: "35" };
let stubs = Object.keys(KNOWN).map((n) => "const " + n + " = " + KNOWN[n] + ";").join("\n");
let css = null;
for (let a = 0; a < 8; a++) {
  try { css = new Function(stubs + "\n" + region + "\nreturn LAYOUT_CSS_PARTS.join('');")(); break; }
  catch (e) {
    const m = /^([A-Za-z_$][\w$]*) is not defined$/.exec(e.message);
    if (!m) { console.log("EVAL_FAIL " + e.message); process.exit(1); }
    stubs += "\nconst " + m[1] + " = 0;";
  }
}

const out = [];
out.push("layoutCss 长度 = " + css.length);

// 括号配平（CSS 里字符串与注释先剥掉）
const clean = css.replace(/\/\*[\s\S]*?\*\//g, "").replace(/"(?:[^"\\]|\\.)*"/g, '""').replace(/'(?:[^'\\]|\\.)*'/g, "''");
let depth = 0, minDepth = 0, badAt = -1;
for (let p = 0; p < clean.length; p++) {
  if (clean[p] === "{") depth++;
  else if (clean[p] === "}") { depth--; if (depth < minDepth) { minDepth = depth; badAt = p; } }
}
out.push("最终花括号深度 = " + depth + "  (必须 0)");
out.push("最浅深度 = " + minDepth + " (负值说明提前闭合)" + (badAt >= 0 ? " @ " + badAt : ""));
if (badAt >= 0) out.push("  上下文: " + JSON.stringify(clean.slice(Math.max(0, badAt - 160), badAt + 60)));

// 无效属性名扫描（CSS 语法错误主要来源）
const suspicious = [];
const propRe = /([a-z-]+)\s*:\s*([^;{}]*)/g;
const validPrefixes = /^(--|color|background|border|margin|padding|font|text|line-height|letter|display|position|top|left|right|bottom|width|height|min-|max-|flex|grid|gap|row-|column-|align|justify|overflow|box-|z-index|opacity|visibility|transform|transition|animation|cursor|pointer|white-space|word-|vertical-align|content|scrollbar|backdrop|object-|inset|fill|stroke|list-|outline|clip|float|clear|order|aspect|isolation|filter|mask|will-change|contain|overscroll|table-|caption|empty-cells|direction|unicode|writing|user-select|appearance|resize|touch-action|counter|quotes|tab-size|hyphens|src|unicode-range|d|r|cx|cy|x|y|rx|ry|stroke-|fill-|stop-|baseline|dominant|paint-order|shape-|marker)/;
for (const m of clean.matchAll(propRe)) {
  const p = m[1];
  if (/^[0-9]/.test(p)) continue;
  if (!validPrefixes.test(p)) suspicious.push(p);
}
const uniq = [...new Set(suspicious)];
out.push("可疑属性名 = " + (uniq.length ? uniq.slice(0, 20).join(", ") : "无 ✓"));

// 我本次新增的那一段单独复查
const mine = css.slice(css.indexOf(".main-page .whale-page{"), css.indexOf(".main-page .guide-page{max-height:none"));
out.push("");
out.push("--- 本次新增段 ---");
out.push("长度 = " + mine.length);
let d2 = 0, min2 = 0;
for (const ch of mine) { if (ch === "{") d2++; else if (ch === "}") { d2--; min2 = Math.min(min2, d2); } }
out.push("花括号深度 = " + d2 + " ; 最浅 = " + min2);
out.push("含 __avatar 规则数 = " + (mine.match(/__avatar/g) || []).length);
out.push("含 setting-ai 规则数 = " + (mine.match(/setting-ai/g) || []).length);

console.log(out.join("\n"));
