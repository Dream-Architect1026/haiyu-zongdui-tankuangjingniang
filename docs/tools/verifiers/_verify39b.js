// 真实求值：整段提取 CSS 装配代码并运行
const fs = require("fs");
const P = "C:\\Users\\D_A\\DoubaoWork\\chats\\2026-10-05\\new-chat-4\\海底小纵队·探矿鲸娘.user.js";
const src = fs.readFileSync(P, "utf8");

const startTag = "const LAYOUT_CSS_PARTS = [";
const endTag = "const layoutCss = LAYOUT_CSS_PARTS.join(\"\");";
const i = src.indexOf(startTag);
const j = src.indexOf(endTag);
if (i < 0 || j < 0) { console.log("BOUND_FAIL i=" + i + " j=" + j); process.exit(1); }

const region = src.slice(i, j);
const out = [];
out.push("region length = " + region.length);

// 逐个补齐外部常量（已知的两个 + 运行期发现的）
const KNOWN_VARS = { DEFAULT_CARD_WIDTH: "'310px'", PANEL_HEIGHT: "500", MINIMIZED_PANEL_HEIGHT: "35" };
let stubs = Object.keys(KNOWN_VARS).map((n) => "const " + n + " = " + KNOWN_VARS[n] + ";").join("\n");
let css = null, err = null;
for (let attempt = 0; attempt < 8; attempt++) {
  const code = stubs + "\n" + region + "\nreturn LAYOUT_CSS_PARTS.join('');";
  try {
    css = new Function(code)();
    err = null;
    break;
  } catch (e) {
    err = e.message;
    const m = /^([A-Za-z_$][\w$]*) is not defined$/.exec(e.message);
    if (!m) break;
    stubs += "\nconst " + m[1] + " = 0;";
    out.push("补充桩常量: " + m[1]);
  }
}
if (css === null) {
  console.log(out.join("\n") + "\nEVAL_FAIL: " + err);
  process.exit(1);
}
out.splice(1, 0, "region length = " + region.length);

out.push("assembled CSS length = " + css.length);

const polluted = css.match(/(^|[;}\s])n\.[a-zA-Z-]+\{/g);
out.push("n.污染 命中 = " + (polluted ? polluted.length : 0));
out.push("字面 反斜杠n 残留 = " + (css.match(/\\n/g) || []).length);

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
const miss = must.filter((m) => css.indexOf(m) < 0);
out.push("新增规则缺失 = " + (miss.length ? miss.join(" | ") : "无（全部落地）"));

const checks = {
  "空闲头像 132px": /\.whale-hero\.is-idle \.whale-hero__avatar\{width:132px;height:132px/.test(css),
  "作答头像 44px": /\.whale-hero__avatar\{[^}]*width:44px/.test(css),
  "idle flex 撑满": /\.whale-hero\.is-idle\{flex:1 1 auto/.test(css),
  "busy flex 0 0": /\.whale-hero\{flex:0 0 auto/.test(css),
  "列表唯一滚动": /\.whale-page>\.question_table\{[^}]*overflow-y:auto/.test(css),
  "用量吸底": /\.whale-page>\.usage-bar\{margin-top:0/.test(css),
  "AI卡片描边": /\.setting>div\.setting-ai\{border-color:/.test(css)
};
Object.keys(checks).forEach((k) => out.push("  " + k + " = " + checks[k]));

const gtRules = (css.match(/[^{};]*>[^{};]*\{/g) || []).map((s) => s.trim());
out.push("直接子选择器总数 = " + gtRules.length);
gtRules.filter((r) => r.includes("whale")).forEach((r) => out.push("   whale子选择器: " + r.replace(/\{.*/, "")));

console.log(out.join("\n"));
