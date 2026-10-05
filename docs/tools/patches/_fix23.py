# -*- coding: utf-8 -*-
"""fix23:
  1) 首页滚动区绝对定位撑满 —— 彻底消灭下方空白
  2) 滚动条彻底隐藏（全局 * 覆盖，保留滚动能力）
  3) 设置页文案重写 + 章节标题胶囊化（不再突兀）
  4) 答题页 el-empty 换成鲸娘图标 + 文案改「小鲸娘正在吃白饭」
  5) 版本号 0.4.0 -> 0.4.1（便于确认浏览器里装的是哪一版）
"""
import io, os, re, shutil, sys

P = r"C:\Users\D_A\DoubaoWork\chats\2026-10-05\new-chat-4\海底小纵队·探矿鲸娘.user.js"
OUT = r"C:\Users\D_A\WorkBuddy\2026-10-05-13-53-42"
NL = "\r\n"
LOG = []

# newline="" 读写 —— 原样保留 CRLF（上一轮踩过：默认模式会把 CRLF 全变成 LF）
src = io.open(P, encoding="utf-8", newline="").read()
orig_len = len(src)

def sub_once(name, old, new, must=1):
    global src
    n = src.count(old)
    if n != must:
        LOG.append("!! %s: 命中 %d 次（期望 %d）" % (name, n, must))
        LOG.append("   anchor=%r" % old[:90])
        return False
    src = src.replace(old, new, 1)
    LOG.append("ok %s" % name)
    return True

# ---------- 0. 提取 @icon data URI ----------
m = re.search(r"^// @icon\s+(data:image/[A-Za-z0-9.+_-]+;base64,[A-Za-z0-9+/=]+)\s*$", src, re.M)
if not m:
    LOG.append("!! 无法从 @icon 提取图标 data URI")
    print(NL.join(LOG)); sys.exit(1)
ICON = m.group(1)
LOG.append("icon data URI: %d 字节" % len(ICON))

# ---------- 1. 版本号 ----------
sub_once("版本 @version", "// @version      0.4.0", "// @version      0.4.1")
sub_once("footer 版本", "v0.4.0 · MIT License", "v0.4.1 · MIT License")

# ---------- 2. 图标常量 + VIDEO_QUIZ_SETTING ----------
sub_once(
    "插入 HX_LOGO_SRC / 视频弹题文案",
    '  const VIDEO_QUIZ_SETTING = "视频弹题自动处理";',
    '  const HX_LOGO_SRC = "' + ICON + '";' + NL +
    '  const VIDEO_QUIZ_SETTING = "视频弹题自动作答";'
)

# ---------- 3. 设置页文案 ----------
sub_once("章节标题 章节设置->课程任务", '                name: "章节设置",', '                name: "课程任务",')
sub_once("章节标题 考试设置->考试模式", '                name: "考试设置",', '                name: "考试模式",')
sub_once("其他参数->进阶调节", '          name: "其他参数",', '          name: "进阶调节",')
sub_once("选项 章节作业自动提交",
         '{ name: "章节作业自动提交", value: true, type: "boolean" },',
         '{ name: "作业自动提交", value: true, type: "boolean" },')
sub_once("选项 是否自动下一章节",
         '{ name: "是否自动下一章节", value: true, type: "boolean" },',
         '{ name: "自动进入下一节", value: true, type: "boolean" },')
sub_once("选项 只答题不做其他",
         '{ name: "只答题，不做其他", value: false, type: "boolean" },',
         '{ name: "只答题不刷课", value: false, type: "boolean" },')
sub_once("选项 视频倍速",
         '{ name: "视频倍速（1-2）", value: 2, type: "number", min: 1, max: 2, step: 0.5 }',
         '{ name: "倍速播放（1~2）", value: 2, type: "number", min: 1, max: 2, step: 0.5 }')
sub_once("选项 考试是否自动切换",
         '                params: [{ name: "是否自动切换", value: true, type: "boolean" }]',
         '                params: [{ name: "自动翻到下一题", value: true, type: "boolean" }]')
sub_once("选项 切换答题间隔",
         '{ name: "切换、答题间隔，单位秒", value: 3, type: "number", min: 1 },',
         '{ name: "操作间隔（秒）", value: 3, type: "number", min: 1 },')
sub_once("选项 正确率阈值",
         '{ name: "正确率达到多少自动提交", value: 85, type: "number" },',
         '{ name: "自动提交的正确率（%）", value: 85, type: "number" },')
sub_once("选项 相似度阈值",
         '{ name: "答案相似度超过多少选择", value: 85, type: "number", min: 0, max: 100, step: 1 }',
         '{ name: "答案相似度阈值（%）", value: 85, type: "number", min: 0, max: 100, step: 1 }')

# ---------- 4. 空状态：换图标 + 换文案 ----------
sub_once("el-empty 图标与文案",
         'vue.createVNode(ElEmpty, { description: "该页面无需答题" })',
         'vue.createVNode(ElEmpty, { image: HX_LOGO_SRC, imageSize: 108, description: "小鲸娘正在吃白饭" })')

# ---------- 5. 追加 CSS ----------
CSS = [
    r'    + "\n/* ===== 首页：绝对定位撑满，消灭下方空白 ===== */"',
    r'    + "\n.main-page .el-tab-pane>.script-home{position:relative!important;flex:1 1 auto!important;min-height:0!important;display:block!important;height:auto!important;padding:0!important}"',
    r'    + "\n.main-page .script-home>.el-scrollbar{position:absolute!important;top:0!important;left:0!important;right:0!important;bottom:0!important;height:auto!important;max-height:none!important;width:auto!important;margin:0!important}"',
    r'    + "\n.main-page .script-home .el-scrollbar__wrap{height:100%!important;max-height:none!important;overflow-y:auto!important;overflow-x:hidden!important;box-sizing:border-box}"',
    r'    + "\n.main-page .script-home .el-scrollbar__view{min-height:100%;box-sizing:border-box;padding:0 2px 8px 0}"',
    r'    + "\n/* ===== 彻底隐藏滚动条（保留滚动能力）===== */"',
    r'    + "\n.main-page *{scrollbar-width:none!important;-ms-overflow-style:none!important}"',
    r'    + "\n.main-page *::-webkit-scrollbar{width:0!important;height:0!important;display:none!important;background:transparent!important}"',
    r'    + "\n.main-page *::-webkit-scrollbar-thumb,.main-page *::-webkit-scrollbar-track,.main-page *::-webkit-scrollbar-corner{display:none!important;background:transparent!important;border:none!important}"',
    r'    + "\n/* ===== 设置页：章节标题胶囊化 ===== */"',
    r'    + "\n.main-page .setting .el-divider--horizontal{height:auto!important;min-height:0!important;border-top:none!important;background:transparent!important;display:flex!important;align-items:center;margin:0!important;padding:1px 0 2px}"',
    r'    + "\n.main-page .setting .el-divider__text{position:static!important;left:auto!important;transform:none!important;background-color:transparent!important;background:transparent!important;padding:0!important;display:inline-flex!important}"',
    r'    + "\n.main-page .setting-section-title{display:inline-flex;align-items:center;gap:6px;padding:3px 11px 3px 8px;border:1px solid rgba(56,226,255,.30);border-radius:20px;background:rgba(56,226,255,.09);font-size:12px;font-weight:700;color:var(--hx-cyan)!important;letter-spacing:.6px;line-height:1.5;white-space:nowrap}"',
    r'    + "\n.main-page .setting>div>.el-divider--horizontal+.el-checkbox,.main-page .setting>div>.el-divider--horizontal+.el-form-item{margin-top:2px!important}"',
    r'    + "\n/* ===== 空状态：鲸娘图标 ===== */"',
    r'    + "\n.main-page .el-empty{padding:16px 0 12px!important}"',
    r'    + "\n.main-page .el-empty__image{width:108px!important;height:108px!important;opacity:.96;filter:drop-shadow(0 10px 24px rgba(56,226,255,.30))}"',
    r'    + "\n.main-page .el-empty__image img{width:100%!important;height:100%!important;object-fit:contain;border-radius:20px}"',
    r'    + "\n.main-page .el-empty__description{margin-top:10px!important}"',
    r'    + "\n.main-page .el-empty__description p{color:var(--hx-ink-dim)!important;font-size:12px;letter-spacing:.5px}"',
]
anchor = r'    + "\n.main-page .el-tab-pane,.main-page .guide-page,.main-page .setting{-webkit-overflow-scrolling:touch}"'
sub_once("CSS 追加", anchor, anchor + NL + NL.join(CSS))

# ---------- 写回 ----------
bad = [x for x in LOG if x.startswith("!!")]
if bad:
    print(NL.join(LOG)); print("ABORT: 有未命中项，未写盘"); sys.exit(1)

shutil.copy2(P, P + ".bak-fix23")
io.open(P, "w", encoding="utf-8", newline="").write(src)

LOG.append("bytes: %d -> %d" % (orig_len, len(src)))
LOG.append("CRLF=%d  bareLF=%d" % (src.count("\r\n"), src.count("\n") - src.count("\r\n")))
LOG.append("backup: .bak-fix23")
io.open(os.path.join(OUT, "_fix23.txt"), "w", encoding="utf-8").write(NL.join(LOG))
print("done")
