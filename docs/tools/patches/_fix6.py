# -*- coding: utf-8 -*-
import io, os, shutil, re

P = r"C:\Users\D_A\DoubaoWork\chats\2026-10-05\new-chat-4\海底小纵队·探矿鲸娘.user.js"
BAK = P + ".bak8"
shutil.copyfile(P, BAK)

src = io.open(P, encoding="utf-8").read()
log = []
log.append("备份: %s (%d B)" % (os.path.basename(BAK), os.path.getsize(BAK)))
log.append("修改前: %d B" % len(src))
log.append("")

def rep(old, new, tag, expect=1):
    global src
    n = src.count(old)
    if n != expect:
        log.append("[!! 跳过] %s —— 命中 %d 次（期望 %d）" % (tag, n, expect))
        return False
    src = src.replace(old, new, expect)
    log.append("[OK ] %s" % tag)
    return True

# ---------- 1. 答题页宽度还原 630px ----------
rep(
    '  const ANSWER_CARD_WIDTH = DEFAULT_CARD_WIDTH;',
    '  const ANSWER_CARD_WIDTH = "630px";',
    "① ANSWER_CARD_WIDTH 还原为 630px"
)

# ---------- 2. 表格容器宽度还原 625px ----------
rep(
    '.main-page .token-label{border-radius:0}.main-page .question_table{width:100%;max-width:100%}',
    '.main-page .token-label{border-radius:0}.main-page .question_table{width:625px}',
    "② .question_table 还原为 width:625px"
)

# ---------- 3. 去掉我自己加的宽度/滚动干预（还原正式版布局） ----------
OLD_PUSH = ('  LAYOUT_CSS_PARTS.push("\\n/* 答题页自适应：面板固定宽度，表格内部横向滚动 */'
            '.main-page .card_content{max-width:100%}'
            '.main-page .question-list{max-width:100%;overflow-x:auto;border-radius:10px}'
            '.main-page .question-list::-webkit-scrollbar{height:6px}'
            '.main-page .question-list::-webkit-scrollbar-thumb{background:linear-gradient(90deg,var(--hx-cyan),var(--hx-violet));border-radius:3px}'
            '.main-page .ai-config{display:grid;gap:8px;margin:0 0 10px}'
            '.main-page .ai-config .el-select,.main-page .ai-config .el-input{width:100%}'
            '.main-page .answer-result{word-break:break-word}");')
NEW_PUSH = ('  LAYOUT_CSS_PARTS.push("\\n/* 答题页增强（不改变面板宽度） */'
            '.main-page .ai-config{display:grid;gap:8px;margin:0 0 10px}'
            '.main-page .ai-config .el-select,.main-page .ai-config .el-input{width:100%}'
            '.main-page .answer-result{word-break:break-word}");')
rep(OLD_PUSH, NEW_PUSH, "③ 移除 card_content/question-list 宽度干预")

# ---------- 4. 表格三列宽度还原 40 / 370 / 215 ----------
rep(
    'vue.createVNode(ElTableColumn, { type: "index", width: "34" }),',
    'vue.createVNode(ElTableColumn, { type: "index", width: "40" }),',
    "④ 序号列 34 -> 40"
)
rep(
    '''                vue.createVNode(ElTableColumn, {
                  prop: "title",
                  label: "题目",
                  minWidth: "136",
                  showOverflowTooltip: true
                }, {''',
    '''                vue.createVNode(ElTableColumn, {
                  prop: "title",
                  label: "题目",
                  width: "370"
                }, {''',
    "⑤ 题目列 minWidth136 -> width370"
)
rep(
    '''                vue.createVNode(ElTableColumn, {
                  prop: "answer",
                  label: "答案",
                  minWidth: "100"
                }, {''',
    '''                vue.createVNode(ElTableColumn, {
                  prop: "answer",
                  label: "答案",
                  width: "215"
                }, {''',
    "⑥ 答案列 minWidth100 -> width215"
)

# ---------- 5. 模型下拉补回 PRO ----------
rep(
    '  const ALLOWED_AI_MODELS = ["deepseek-v4.1-flash", "deepseek-flash"];',
    '  const ALLOWED_AI_MODELS = ["deepseek-v4.1-flash", "deepseek-v4-pro", "deepseek-flash"];',
    "⑦ 白名单补回 deepseek-v4-pro"
)
rep(
    '                vue.createVNode(ElOption, { value: "deepseek-v4.1-flash", label: "DeepSeek V4.1 Flash（默认·推荐）" }),\n'
    '                vue.createVNode(ElOption, { value: "deepseek-flash", label: "DeepSeek V4 Flash" })',
    '                vue.createVNode(ElOption, { value: "deepseek-v4.1-flash", label: "DeepSeek V4.1 Flash（默认·推荐·最强）" }),\n'
    '                vue.createVNode(ElOption, { value: "deepseek-v4-pro", label: "DeepSeek V4 Pro" }),\n'
    '                vue.createVNode(ElOption, { value: "deepseek-flash", label: "DeepSeek V4 Flash（快）" })',
    "⑧ 下拉补回 Pro 选项（默认仍是 V4.1 Flash）"
)

# ---------- 6. 过滤无害报错（ResizeObserver 等） ----------
rep(
    '  const box = (title, detail) => {',
    '''  // 无害噪音：ResizeObserver 通知循环、跨域 "Script error."、非 Error 的 Promise 拒绝
  const BENIGN = /ResizeObserver loop|Script error\\.?\\s*$|Non-Error promise rejection|^undefined$|^null$/;
  const isBenign = (m) => BENIGN.test(String(m || "").trim());
  const box = (title, detail) => {''',
    "⑨ 新增无害报错过滤器"
)
rep(
    '''  window.addEventListener("error", (e) => {
    const where = e.filename ? " @ " + String(e.filename).split("/").pop() + ":" + e.lineno : "";
    const st = e.error && e.error.stack ? "\\n" + String(e.error.stack).split("\\n").slice(0, 7).join("\\n") : "";
    box("脚本运行错误", (e.message || "未知错误") + where + st);
  });''',
    '''  window.addEventListener("error", (e) => {
    if (isBenign(e.message)) return;      // 忽略 ResizeObserver 等无害噪音
    if (String(e.message || "").startsWith("ResizeObserver")) return;
    const where = e.filename ? " @ " + String(e.filename).split("/").pop() + ":" + e.lineno : "";
    const st = e.error && e.error.stack ? "\\n" + String(e.error.stack).split("\\n").slice(0, 7).join("\\n") : "";
    box("脚本运行错误", (e.message || "未知错误") + where + st);
  });''',
    "⑩ error 处理器忽略无害报错"
)
rep(
    '''  window.addEventListener("unhandledrejection", (e) => {
    const r = e.reason;
    const msg = r && r.message ? r.message : String(r);
    const st = r && r.stack ? "\\n" + String(r.stack).split("\\n").slice(0, 7).join("\\n") : "";
    box("Promise 未捕获异常", msg + st);
  });''',
    '''  window.addEventListener("unhandledrejection", (e) => {
    const r = e.reason;
    const msg = r && r.message ? r.message : String(r);
    if (isBenign(msg)) return;            // 忽略无害噪音
    const st = r && r.stack ? "\\n" + String(r.stack).split("\\n").slice(0, 7).join("\\n") : "";
    box("Promise 未捕获异常", msg + st);
  });''',
    "⑪ unhandledrejection 忽略无害报错"
)

io.open(P, "w", encoding="utf-8", newline="").write(src)
log.append("")
log.append("修改后: %d B" % len(src))
log.append("")
log.append("=== 复核 ===")
for pat in ['ANSWER_CARD_WIDTH = "630px"', '.question_table{width:625px}',
            'const DEFAULT_CARD_WIDTH = "310px"', 'width: "40"', 'width: "370"', 'width: "215"',
            'deepseek-v4-pro", label: "DeepSeek V4 Pro"', 'deepseek-v4.1-flash", label',
            'const BENIGN = ', 'minWidth: "136"', 'minWidth: "100"', 'question_table{width:100%',
            '.card_content{max-width:100%}']:
    log.append("  %-58s x%d" % (pat, src.count(pat)))

io.open(r"C:\Users\D_A\WorkBuddy\2026-10-05-13-53-42\_fix6.txt", "w", encoding="utf-8").write("\n".join(log))
print("ok")
