// _verify41.js —— 0.4.3 回归验收：CSS 装配真实求值 + 新增标识符声明检查
const fs = require("fs");
const P = "C:\\Users\\D_A\\DoubaoWork\\chats\\2026-10-05\\new-chat-4\\海底小纵队·探矿鲸娘.user.js";
const src = fs.readFileSync(P, "utf8");
const out = [];
const fail = [];

// ---------------- 1. 提取 CSS 装配区间 ----------------
const i0 = src.indexOf("const LAYOUT_CSS_PARTS = [");
const jt = src.indexOf('const layoutCss = LAYOUT_CSS_PARTS.join("")', i0);
if (i0 < 0 || jt < 0) { fail.push("找不到 LAYOUT_CSS_PARTS 区间"); }
const region = src.slice(i0, jt + 'const layoutCss = LAYOUT_CSS_PARTS.join("")'.length);
out.push("CSS 装配区间：起点 %d 终点 %d 长度 %d", i0, jt, region.length);

// ---------------- 2. 找出外部标识符并打桩求值 ----------------
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
const externals = [...ids].filter((w) => !declared.has(w) && !KEYWORDS.has(w) && /^[A-Za-z_$][\w$]*$/.test(w));
out.push("区间内声明的标识符 %d 个；疑似外部引用：%s", declared.size, externals.join(", ") || "无");

const stubs = externals.map((n) => "const " + n + ' = "";').join("\n");
let css = null;
try {
  css = new Function(stubs + "\n" + region + '\nreturn LAYOUT_CSS_PARTS.join("");')();
  out.push("真实求值：成功，装配后 CSS 长度 %d", css.length);
} catch (e) {
  fail.push("真实求值失败：" + e.message);
}

if (css) {
  // 花括号配平
  let d = 0, minD = 0;
  for (const ch of css) { if (ch === "{") d++; else if (ch === "}") { d--; if (d < minD) minD = d; } }
  out.push("花括号终值深度 = %d（应为 0），历史最小深度 = %d（不应 < 0）", d, minD);
  if (d !== 0) fail.push("花括号不配平，深度 " + d);
  if (minD < 0) fail.push("存在提前闭合的 }");

  // \n 污染：装配结果里不应出现「字面反斜杠 + n」
  const pollute = (css.match(/\\n/g) || []).length;
  out.push("装配结果中字面 '\\\\n' 出现 %d 次（应为 0）", pollute);
  if (pollute !== 0) fail.push("存在 \\n 双转义污染 " + pollute + " 处");

  // 真实换行数
  out.push("装配结果中真实换行 %d 个", (css.match(/\n/g) || []).length);

  // 关键规则存在性
  const rules = [
    [".main-page .whale-page{", "鲸娘页根容器"],
    [".main-page .whale-page>.question_table{", "唯一滚动列表"],
    [".main-page .whale-page>.usage-bar{", "吸底用量栏"],
    [".main-page .whale-hero{", "鲸娘 hero 基础"],
    [".main-page .whale-hero.is-idle .whale-hero__avatar{width:132px", "空闲态 132px"],
    [".main-page .whale-hero.is-busy{flex-direction:row", "作答态横排"],
    ["@keyframes hxWhaleBreath{", "呼吸动画"],
    [".main-page .setting .el-form-item.setting-ai-field{", "AI 卡片表单对齐"],
    [".main-page .setting>div.setting-ai{border-color", "AI 卡片描边"],
    [".main-page .usage-sub{display:flex;align-items:center;justify-content:flex-start", "用量副行改 flex-start"],
    [".main-page .usage-build{margin-left:auto", "版本角标样式"]
  ];
  for (const [needle, label] of rules) {
    const ok = css.includes(needle);
    out.push("  [%s] %s", ok ? "有" : "缺", label);
    if (!ok) fail.push("缺少 CSS 规则：" + label);
  }
}

// ---------------- 3. 新增标识符声明检查 ----------------
const decls = {
  HX_BUILD: [/const HX_BUILD = "0\.4\.3";/],
  HX_RUN_ID: [/const HX_RUN_ID = /],
  hxShadow: [/let hxShadow = null;/, /hxShadow = shadowRoot;/, /const sr = hxShadow;/],
  ownPanelHost: [/const ownPanelHost = /],
  sweepOtherPanels: [/const sweepOtherPanels = /, /sweepOtherPanels\(\)/],
  hostsShadowTree: [/const hostsShadowTree = /, /hostsShadowTree\(el\)/],
  exposeDiagnostics: [/const exposeDiagnostics = /, /exposeDiagnostics\(\)/],
  HX_SWEEP_DELAYS: [/const HX_SWEEP_DELAYS = \[/, /HX_SWEEP_DELAYS\.forEach/]
};
out.push("");
out.push("新增标识符声明/引用：");
for (const k of Object.keys(decls)) {
  const hits = decls[k].map((re) => (src.match(new RegExp(re.source, "g")) || []).length);
  const ok = hits.every((n) => n >= 1);
  out.push("  [%s] %-18s 命中 %s", ok ? "OK" : "NG", k, hits.join("/"));
  if (!ok) fail.push("标识符不完整：" + k);
}

// ---------------- 4. 关键结构不变量 ----------------
out.push("");
out.push("结构不变量：");
const inv = [
  ["0.4.2 残留", src.split("0.4.2").length - 1, 0],
  ["0.4.3 出现", src.split("0.4.3").length - 1, 4],
  ["setting-ai 卡片", src.split('class: "setting-ai"').length - 1, 1],
  ["whale-page 根", src.split('class: "whale-page"').length - 1, 1],
  ["ElEmpty 残留", src.split("vue.createVNode(ElEmpty").length - 1, 0],
  ["面板宿主标记", src.split('shadowHost.setAttribute(PANEL_MARK_ATTR, HX_RUN_ID)').length - 1, 1],
  ["usage-build 角标", src.split('class="usage-build"').length - 1, 1]
];
for (const [label, actual, expect] of inv) {
  const ok = actual === expect;
  out.push("  [%s] %-16s 实际 %d / 期望 %d", ok ? "OK" : "NG", label, actual, expect);
  if (!ok) fail.push("不变量不符：" + label);
}

out.push("");
out.push(fail.length ? "==== 失败 " + fail.length + " 项 ====" : "==== 全部通过 ====");
fail.forEach((f) => out.push("  ! " + f));
console.log(out.join("\n"));
process.exit(fail.length ? 1 : 0);
