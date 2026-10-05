// 真实求值：把 LAYOUT_CSS_PARTS 三段拼接起来，验收新增规则
const fs = require("fs");
const P = "C:\\Users\\D_A\\DoubaoWork\\chats\\2026-10-05\\new-chat-4\\海底小纵队·探矿鲸娘.user.js";
const src = fs.readFileSync(P, "utf8");
const lines = src.split("\r\n");

// 定位三段 push 的起止（用行号区间，源码已知）
function slice(a, b) { return lines.slice(a - 1, b).join("\r\n"); }

const seg1 = slice(7507, 7644);   // 第一段数组内容
const seg2 = slice(7648, 7655);   // push 段 A（基础皮肤）
const seg3 = slice(7656, 7831);   // push 段 B（皮肤续 + 我们新增的）

// 组装并求值
const code = "const DEFAULT_CARD_WIDTH='310px',PANEL_HEIGHT=500;"
  + "const LAYOUT_CSS_PARTS=[\n" + seg1.replace(/^\s*const LAYOUT_CSS_PARTS = \[\r?\n?/, "") + "\n];"
  + "\nLAYOUT_CSS_PARTS.push(\n" + seg2.replace(/^\s*LAYOUT_CSS_PARTS\.push\(/, "") + "\n);"
  + "\nLAYOUT_CSS_PARTS.push(\n" + seg3.replace(/^\s*LAYOUT_CSS_PARTS\.push\(/, "") + "\n);"
  + "\nreturn LAYOUT_CSS_PARTS.join('');";

let css;
try {
  css = new Function(code)();
} catch (e) {
  console.log("EVAL_FAIL: " + e.message);
  process.exit(1);
}

const out = [];
out.push("assembled CSS length = " + css.length);

// 1) \n 污染检查：不应出现 "n.xxx{" 形态（选择器被 \n 字面量污染）
const polluted = css.match(/(^|[;}\s])n\.[a-zA-Z-]+\{/g);
out.push("n.污染 命中 = " + (polluted ? polluted.length : 0) + (polluted ? " -> " + polluted.slice(0, 5).join(" | ") : ""));

// 2) 字面反斜杠 n 残留
out.push("字面 \\\\n 残留 = " + (css.match(/\\n/g) || []).length);

// 3) 新增规则是否全部落地
const must = [
  ".main-page .whale-page{",
  ".main-page .whale-page>.question_table{",
  ".main-page .whale-page>.usage-bar{",
  ".main-page .whale-hero{",
  ".main-page .whale-hero__avatar{",
  ".main-page .whale-hero__bubble{",
  ".main-page .whale-hero__text{",
  ".main-page .whale-hero.is-idle{",
  ".main-page .whale-hero.is-idle .whale-hero__avatar{",
  ".main-page .whale-hero.is-busy{",
  ".main-page .whale-hero.is-busy .whale-hero__avatar{",
  "@keyframes hxWhaleBreath{",
  "@keyframes hxWhaleDots{",
  ".main-page .setting .el-form-item.setting-ai-field{",
  ".main-page .setting>div.setting-ai{"
];
let miss = [];
must.forEach((m) => { if (css.indexOf(m) < 0) miss.push(m); });
out.push("新增规则缺失 = " + (miss.length ? miss.join(" | ") : "无（全部落地）"));

// 4) 关键数值核对
const checks = {
  "空闲头像 132px": /\.whale-hero\.is-idle \.whale-hero__avatar\{width:132px;height:132px/.test(css),
  "作答头像 44px": /\.whale-hero__avatar\{[^}]*width:44px/.test(css),
  "idle flex 撑满": /\.whale-hero\.is-idle\{flex:1 1 auto/.test(css),
  "busy 0 0 auto": /\.whale-hero\{flex:0 0 auto/.test(css),
  "列表唯一滚动": /\.whale-page>\.question_table\{[^}]*overflow-y:auto/.test(css),
  "用量吸底": /\.whale-page>\.usage-bar\{margin-top:0/.test(css)
};
Object.keys(checks).forEach((k) => out.push("  " + k + " = " + checks[k]));

// 5) 直接子选择器失配排查：找出所有 X>Y 且 Y 在源里已改父的场景
const gtRules = (css.match(/[^{};]*>[^{};]*\{/g) || []).map((s) => s.trim());
out.push("直接子选择器总数 = " + gtRules.length);
const staleTabs = gtRules.filter((r) => r.includes(".el-tab-pane>.question_table"));
out.push("仍指向 .el-tab-pane>.question_table 的规则 = " + staleTabs.length + "（旧规则保留无害，新规则已补）");

console.log(out.join("\n"));
