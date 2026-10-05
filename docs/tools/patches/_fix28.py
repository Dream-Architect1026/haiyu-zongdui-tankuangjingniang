# -*- coding: utf-8 -*-
"""fix28（按用户 4 条反馈）:
  1) 删除首页通知里的两段文案：
       「脚本加载成功，正在解析网页」/「请不要多个脚本同时使用，会有脚本冲突问题」
  2) 协议页署名：移除「（星虹）」；取消吸底/悬浮，改回正常文段放在最后
  3) 答题页状态标识（legend）改为两个字：已答 / 查询 / 等待 / 失败
  4) 答题页：废掉 el-table 表格，改为卡片列表——第一行「题号 + 题目」，第二行「答案」
"""
import io, os, shutil, sys

P = r"C:\Users\D_A\DoubaoWork\chats\2026-10-05\new-chat-4\海底小纵队·探矿鲸娘.user.js"
OUT = r"C:\Users\D_A\WorkBuddy\2026-10-05-13-53-42"
NL = "\r\n"
LOG = []

src = io.open(P, encoding="utf-8", newline="").read()
orig_len = len(src)

def sub_once(name, old, new, must=1):
    global src
    n = src.count(old)
    if n != must:
        LOG.append("!! %s: 命中 %d 次（期望 %d）" % (name, n, must))
        return False
    src = src.replace(old, new, 1)
    LOG.append("ok %s" % name)
    return True

def slice_replace(name, start_marker, end_marker, new_block):
    """按唯一首尾标记切片替换（避开中间空白字符精确匹配问题）"""
    global src
    if src.count(start_marker) != 1:
        LOG.append("!! %s: start 命中 %d" % (name, src.count(start_marker))); return False
    if src.count(end_marker) != 1:
        LOG.append("!! %s: end 命中 %d" % (name, src.count(end_marker))); return False
    a = src.index(start_marker)
    b = src.index(end_marker, a) + len(end_marker)
    src = src[:a] + new_block + src[b:]
    LOG.append("ok %s（替换 %d 字符 -> %d 字符）" % (name, b - a, len(new_block)))
    return True

# ---------------- 1) 删除两段日志文案 ----------------
sub_once(
    "删除日志:脚本加载成功 / 脚本冲突",
    '      logStore.addLog("脚本加载成功，正在解析网页", "primary");' + NL
    + '      logStore.addLog("请不要多个脚本同时使用，会有脚本冲突问题", "warning");' + NL,
    ''
)

# ---------------- 2) 署名：去掉「（星虹）」 ----------------
sub_once(
    "署名去掉（星虹）",
    "Developed by <strong>X.H</strong>（星虹）",
    "Developed by <strong>X.H</strong>"
)

# 取消吸底/悬浮 -> 正常文段
sub_once(
    "署名取消吸底(sticky->static)",
    '    + "\\n.main-page .guide-footer{position:sticky!important;bottom:0!important;z-index:6;flex:0 0 auto;margin:8px 0 0!important;padding:9px 12px;border:1px solid var(--hx-line);border-radius:12px;background:linear-gradient(120deg,rgba(20,36,68,.95),rgba(28,20,60,.95));text-align:center;box-shadow:0 -8px 22px rgba(2,8,24,.5);backdrop-filter:blur(14px) saturate(150%);-webkit-backdrop-filter:blur(14px) saturate(150%)}"',
    '    + "\\n.main-page .guide-footer{position:static!important;flex:0 0 auto;margin:10px 0 0!important;padding:9px 12px;border:1px solid var(--hx-line);border-radius:12px;background:linear-gradient(120deg,rgba(20,36,68,.62),rgba(28,20,60,.58));text-align:center;box-shadow:0 6px 18px rgba(2,8,24,.24);backdrop-filter:blur(12px) saturate(140%);-webkit-backdrop-filter:blur(12px) saturate(140%)}"'
)

# ---------------- 3) legend 改两个字 ----------------
sub_once(
    "legend 改两个字",
    '<span class="answer-result--success">有答案</span><span class="answer-result--searching">查询中</span><span class="answer-result--pending">等待中</span><span class="answer-result--error">未找到 / 失败</span>',
    '<span class="answer-result--success">已答</span><span class="answer-result--searching">查询</span><span class="answer-result--pending">等待</span><span class="answer-result--error">失败</span>'
)

# ---------------- 4) 表格 -> 卡片列表 ----------------
NEW_BLOCK = NL.join([
    '          vue.withDirectives(vue.createElementVNode("div", _hoisted_1$3, [',
    '            _hoisted_2$3,',
    '            vue.createElementVNode("div", { class: "question-list" }, [',
    '              (vue.openBlock(true), vue.createElementBlock(vue.Fragment, null, vue.renderList(_ctx.questionList, (row, idx) => {',
    '                return vue.openBlock(), vue.createElementBlock("div", {',
    '                  key: idx,',
    '                  class: "question-card"',
    '                }, [',
    '                  vue.createElementVNode("span", { class: "question-index" }, vue.toDisplayString(idx + 1), 1),',
    '                  vue.createElementVNode("span", { class: "question-title", innerHTML: getDisplayTitle(row) }, null, 8, _hoisted_3$1),',
    '                  vue.createElementVNode("div", {',
    '                    class: vue.normalizeClass(["answer-result", `answer-result--${getAnswerStatus(row)}`])',
    '                  }, [',
    '                    getAnswerStatus(row) === "pending" ? (vue.openBlock(), vue.createElementBlock("span", _hoisted_4$2, "等待")) : getAnswerStatus(row) === "searching" ? (vue.openBlock(), vue.createElementBlock("span", _hoisted_5, "查询")) : (vue.openBlock(), vue.createElementBlock("div", {',
    '                      key: 2,',
    '                      innerHTML: row.answer.join()',
    '                    }, null, 8, _hoisted_6))',
    '                  ], 2)',
    '                ]);',
    '              }), 128))',
    '            ])',
    '          ], 512), [',
    '            [vue.vShow, _ctx.questionList.length]',
])

slice_replace(
    "答题页表格->卡片列表",
    '          vue.withDirectives(vue.createElementVNode("div", _hoisted_1$3, [',
    '            [vue.vShow, _ctx.questionList.length]',
    NEW_BLOCK
)

# ---------------- 5) 新增卡片 CSS ----------------
CSS = [
    r'    + "\n/* ===== 答题页：表格改卡片列表（题号+题目一行 / 答案下一行） ===== */"',
    r'    + "\n.main-page .question_table{overflow-x:hidden!important;overflow-y:auto!important;border:none!important;background:transparent!important;padding:0 1px 2px!important}"',
    r'    + "\n.main-page .answer-legend{position:sticky!important;top:0;z-index:4;backdrop-filter:blur(10px);-webkit-backdrop-filter:blur(10px)}"',
    r'    + "\n.main-page .question-list{width:auto!important;max-width:100%!important;border:none!important;background:transparent!important;overflow:visible!important;padding:0}"',
    r'    + "\n.main-page .question-card{position:relative;display:flex!important;flex-wrap:wrap!important;align-items:flex-start;margin:0 0 7px!important;padding:8px 10px 9px 12px!important;border:1px solid var(--hx-line);border-radius:11px;background:linear-gradient(135deg,rgba(18,32,62,.58),rgba(12,22,44,.38));box-shadow:0 3px 10px rgba(2,8,24,.20);backdrop-filter:blur(8px) saturate(140%);-webkit-backdrop-filter:blur(8px) saturate(140%);transition:border-color .18s,background .18s}"',
    r'    + "\n.main-page .question-card:last-child{margin-bottom:0!important}"',
    r'    + "\n.main-page .question-card:hover{border-color:rgba(56,226,255,.40);background:linear-gradient(135deg,rgba(22,40,74,.62),rgba(14,26,52,.44))}"',
    r'    + "\n.main-page .question-card:before{content:\'\';position:absolute;left:5px;top:8px;bottom:8px;width:3px;border-radius:2px;background:var(--hx-blue);opacity:.8}"',
    r'    + "\n.main-page .question-index{flex:0 0 auto;display:inline-flex;align-items:center;justify-content:center;min-width:19px;height:19px;margin-right:7px;padding:0 5px;border-radius:10px;background:linear-gradient(135deg,rgba(56,226,255,.24),rgba(155,107,255,.24));border:1px solid rgba(120,190,255,.22);color:#cfe9ff;font-size:10px;font-weight:700;line-height:1;font-variant-numeric:tabular-nums}"',
    r'    + "\n.main-page .question-title{flex:1 1 0;min-width:0;font-size:11.5px;line-height:1.62;color:var(--hx-ink)!important;overflow-wrap:anywhere;word-break:break-word}"',
    r'    + "\n.main-page .question-title img{max-width:100%!important;height:auto!important;border-radius:6px}"',
    r'    + "\n.main-page .question-card>.answer-result{flex:0 0 100%;width:100%;margin-top:6px!important;padding-top:6px!important;border-top:1px dashed rgba(120,190,255,.16);font-size:11.5px;line-height:1.65;overflow-wrap:anywhere;word-break:break-word}"',
    r'    + "\n.main-page .question-card>.answer-result:before{content:\'答案\';display:inline-block;margin-right:6px;padding:0 5px;border-radius:5px;background:rgba(56,226,255,.12);border:1px solid rgba(56,226,255,.26);color:var(--hx-cyan);font-size:10px;line-height:15px;vertical-align:1px}"',
]

anchor_css = r'    + "\n.main-page .guide-meta{margin:5px 0 0;font-size:10px;line-height:1.6;letter-spacing:.4px;color:var(--hx-ink-dim)!important;opacity:.9}"'
sub_once("CSS（答题页卡片列表）", anchor_css, anchor_css + NL + NL.join(CSS))

bad = [x for x in LOG if x.startswith("!!")]
if bad:
    print(NL.join(LOG)); print("ABORT"); sys.exit(1)

shutil.copy2(P, P + ".bak-fix28")
io.open(P, "w", encoding="utf-8", newline="").write(src)
LOG.append("bytes: %d -> %d" % (orig_len, len(src)))
LOG.append("CRLF=%d bareLF=%d" % (src.count("\r\n"), src.count("\n") - src.count("\r\n")))
io.open(os.path.join(OUT, "_fix28.txt"), "w", encoding="utf-8").write(NL.join(LOG))
print("done")
