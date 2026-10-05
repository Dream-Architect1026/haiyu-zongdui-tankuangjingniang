// 静态符号验证：检出 render 函数里的「自由变量」（未声明就使用 → 运行时 ReferenceError）
// ReferenceError 会让整个组件不渲染，症状恰好是"更新了但没效果"
const fs = require("fs");
const P = "C:\\Users\\D_A\\DoubaoWork\\chats\\2026-10-05\\new-chat-4\\海底小纵队·探矿鲸娘.user.js";
const src = fs.readFileSync(P, "utf8");
const out = [];

// 模块级声明（顶层 const/let/var/function/class）
const moduleDecls = new Set();
for (const m of src.matchAll(/^  (?:const|let|var|function|class)\s+([A-Za-z_$][\w$]*)/gm)) moduleDecls.add(m[1]);
out.push("模块级声明数 = " + moduleDecls.size);

// 剥掉字符串与注释后统计标识符
function strip(code) {
  return code
    .replace(/"(?:[^"\\]|\\.)*"/gs, '""')
    .replace(/'(?:[^'\\]|\\.)*'/gs, "''")
    .replace(/`(?:[^`\\]|\\.)*`/gs, "``")
    .replace(/\/\*[\s\S]*?\*\//g, "")
    .replace(/(^|[^:])\/\/[^\n]*/g, "$1");
}

// 定位每个组件的 setup 返回的 render 函数区域
function findRender(componentName) {
  const i = src.indexOf('__name: "' + componentName + '"');
  if (i < 0) return null;
  // 从组件定义起点，向后找 return (_ctx, _cache) => {
  const j = src.indexOf("return (_ctx, _cache) => {", i);
  if (j < 0) return null;
  // 花括号配对找函数结束
  let k = src.indexOf("{", j);
  let depth = 0, end = k;
  for (let p = k; p < src.length; p++) {
    if (src[p] === "{") depth++;
    else if (src[p] === "}") { depth--; if (depth === 0) { end = p; break; } }
  }
  return { start: i, renderStart: j, renderEnd: end, code: src.slice(j, end + 1), setup: src.slice(i, j) };
}

const targets = ["index", "QuestionTable"];
const skip = new Set([
  "vue", "_ctx", "_cache", "const", "let", "var", "function", "return", "if", "else", "for", "of", "in",
  "new", "void", "typeof", "true", "false", "null", "undefined", "this", "key", "default", "class", "src",
  "label", "value", "modelValue", "placeholder", "size", "min", "max", "step", "type", "name", "props",
  "children", "onClick", "innerHTML", "clearable", "controlsPosition", "borderStyle", "always", "required",
  "image", "imageSize", "description", "style", "width", "height", "id", "role", "aria", "data"
]);

for (const name of targets) {
  const r = findRender(name);
  if (!r) { out.push("[" + name + "] 未找到 render"); continue; }
  const code = strip(r.code);
  const setupCode = strip(r.setup);

  // 函数内声明
  const local = new Set();
  for (const m of code.matchAll(/\b(?:const|let|var|function)\s+([A-Za-z_$][\w$]*)/g)) local.add(m[1]);
  for (const m of code.matchAll(/\(([^)]*)\)\s*=>/g)) {
    m[1].split(",").forEach((s) => { const w = s.trim().split(/[=\s]/)[0]; if (/^[A-Za-z_$][\w$]*$/.test(w)) local.add(w); });
  }
  // setup 内声明
  for (const m of setupCode.matchAll(/\b(?:const|let|var|function)\s+([A-Za-z_$][\w$]*)/g)) local.add(m[1]);

  // 取所有「非属性访问」的标识符：前面不是 . 且后面不是 :
  const free = new Map();
  for (const m of code.matchAll(/(^|[^.\w$])([A-Za-z_$][\w$]*)\s*(?!\s*:)/g)) {
    const w = m[2];
    if (skip.has(w) || local.has(w) || moduleDecls.has(w)) continue;
    if (/^\d/.test(w)) continue;
    free.set(w, (free.get(w) || 0) + 1);
  }
  const arr = [...free.entries()].sort((a, b) => b[1] - a[1]);
  out.push("[" + name + "] 未解析标识符 = " + (arr.length ? arr.map((x) => x[0] + "x" + x[1]).join(", ") : "无 ✓"));
}

// 专项：鲸娘页 root 与 hero 的 patchFlag 检查
const whale = findRender("QuestionTable");
if (whale) {
  const c = whale.code;
  const heroIdx = c.indexOf('"whale-hero"');
  out.push("");
  out.push("--- 鲸娘页关键节点 patchFlag ---");
  out.push("hero 用 normalizeClass + patchFlag 2 : " + /class: vue\.normalizeClass\(\["whale-hero"[\s\S]{0,400}?\], 2\)/.test(c));
  out.push("whale-page 根节点存在             : " + c.includes('class: "whale-page"'));
  out.push("usage-bar 带 patchFlag 8          : " + c.includes('class: "usage-bar", innerHTML: usageBarHtml.value }, null, 8, ["innerHTML"])'));
  out.push("question_table 带 vShow           : " + c.includes("[vue.vShow, _ctx.questionList.length]"));
  out.push("根节点收尾 patchFlag              : " + (c.match(/\], (\d+)\);\s*\n\s*\};\s*\n\s*\}\s*\n\s*\}\);/) || [])[1]);
}

console.log(out.join("\n"));
