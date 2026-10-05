# -*- coding: utf-8 -*-
"""
0.4.7 -> 0.4.8
A. 背景光带真正可见（原 .main-page 是 0 尺寸 fixed 盒，伪元素 inset:0 等于没画）
   + 卡片整体玻璃化（透明底 + 大高斯模糊 + 模糊化的原图色层）
B. 空闲语录用可自定义的小名
C. 配置页 AI 卡片内新增「小名」输入（模型下面，不单独开卡）
D. 用量栏补「本次运行时长」，填掉中间空白
E. 日志（状态页通知）全部萌化
F. 默认停在鲸娘页；状态页有新动静跳过去，安静 10s 回鲸娘
"""
import io
import re
import sys
import os

P = r"C:\Users\D_A\DoubaoWork\chats\2026-10-05\new-chat-4\海底小纵队·探矿鲸娘.user.js"
OUT = r"C:\Users\D_A\WorkBuddy\2026-10-05-13-53-42\_f47out.txt"
DRY = "--dry" in sys.argv
OLD_VER = "0.4.7"
NEW_VER = "0.4.8"

log = []
def w(s):
    log.append(str(s))

raw_bytes = open(P, "rb").read()
raw = raw_bytes.decode("utf-8")
s = raw.replace("\r\n", "\n")
orig_len = len(s)

# ── 0. 版本号替换（白名单闸门）─────────────────────────────
hits = list(re.finditer(re.escape(OLD_VER), s))
w("=== 版本号 %s 出现 %d 处 ===" % (OLD_VER, len(hits)))
bad = []
for m in hits:
    ctx = s[max(0, m.start() - 46): m.end() + 46].replace("\n", "\\n")
    ok = bool(re.search(r"(@version|HX_BUILD|v0\.|/\\*|// ----|License|面板|已加载|液态玻璃|背景脉动光|标签|hero)", ctx))
    w("  [%s] %s" % ("OK" if ok else "??", ctx))
    if not ok:
        bad.append(ctx)
if bad:
    w("!! 有非版本字面量的 0.4.7，已中止")
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    open(OUT, "w", encoding="utf-8").write("\n".join(log))
    sys.exit(1)
s = s.replace(OLD_VER, NEW_VER)

# ── 1. 分节注释去歧义（全部同名 0.4.8 会让后续 grep 混乱）──
D = [
    ("/* ==== v" + NEW_VER + " : 标签只发光不上浮", "/* ==== v" + NEW_VER + "-b : 标签只发光不上浮", 1),
    ("/* ==== v" + NEW_VER + " : 背景脉动光", "/* ==== v" + NEW_VER + "-c : 背景脉动光", 1),
]

# ── 2. 背景：把伪元素从 .main-page 搬到卡片上 ─────────────
CSS_GLASS_A = (
    ".main-page .el-card{background:transparent!important;backdrop-filter:blur(20px) saturate(156%)!important;"
    "-webkit-backdrop-filter:blur(20px) saturate(156%)!important}"
    "\\n.main-page .el-card::before{content:'';position:absolute;inset:-16px;z-index:0;pointer-events:none;"
    "background-image:var(--hx-bg);background-position:center;background-size:310px 500px;background-repeat:no-repeat;"
    "filter:blur(16px) saturate(142%);animation:hxBgBreathe 13s ease-in-out infinite}"
    "\\n.main-page .el-card__body::after{content:'';position:absolute;inset:0;z-index:0;pointer-events:none;"
    "border-radius:inherit;background-image:linear-gradient(180deg,rgba(56,226,255,0) 0%,"
    "rgba(56,226,255,.58) 13%,rgba(155,107,255,.52) 25%,rgba(56,226,255,0) 43%);background-size:100% 260%;"
    "background-repeat:no-repeat;background-position:50% 50%;animation:hxBgSweep 11s cubic-bezier(.45,0,.55,1) infinite}"
)
OLD_BG_SWEEP = (".main-page::before{content:'';position:absolute;inset:0;z-index:-1;pointer-events:none;"
                "background-image:linear-gradient(180deg,rgba(56,226,255,0) 0%,rgba(56,226,255,.22) 15%,"
                "rgba(155,107,255,.20) 26%,rgba(56,226,255,0) 40%);background-size:100% 240%;background-repeat:no-repeat;"
                "background-position:50% 50%;animation:hxBgSweep 9.6s cubic-bezier(.45,0,.55,1) infinite}")
NEW_BG_SWEEP = CSS_GLASS_A

OLD_KF_SWEEP = ("@keyframes hxBgSweep{0%{background-position:50% 50%;opacity:0}12%{opacity:.85}45%{opacity:.95}"
                "100%{background-position:50% -50%;opacity:0}}")
NEW_KF_SWEEP = ("@keyframes hxBgSweep{0%{background-position:50% 58%;opacity:0}9%{opacity:.92}50%{opacity:1}"
                "100%{background-position:50% -58%;opacity:0}}")

OLD_BG_BREATHE = (".main-page::after{content:'';position:absolute;inset:0;z-index:-1;pointer-events:none;"
                  "background:radial-gradient(130% 62% at 50% -8%,rgba(56,226,255,.17),rgba(56,226,255,0) 62%);"
                  "opacity:.4;animation:hxBgBreathe 13s ease-in-out infinite}")
NEW_BG_BREATHE = (".main-page .el-card__body::before{background:linear-gradient(180deg,rgba(8,16,36,.28) 0%,"
                  "rgba(10,20,44,.44) 45%,rgba(8,16,36,.56) 100%)!important}")

OLD_KF_BREATHE = "@keyframes hxBgBreathe{0%,100%{opacity:.30}50%{opacity:.72}}"
NEW_KF_BREATHE = "@keyframes hxBgBreathe{0%,100%{opacity:.54}50%{opacity:.80}}"

OLD_RM = ".main-page::before,.main-page::after,"
NEW_RM = ".main-page .el-card::before,.main-page .el-card__body::after,"

# ── 3. 用量栏：本次运行时长 ───────────────────────────────
UP_FN = (
    '  const formatUptime = (ms) => {\n'
    '    const total = Math.floor(ms / 1000);\n'
    '    if (total < 60) return total + " \\u79d2";\n'
    '    const mins = Math.floor(total / 60);\n'
    '    if (mins < 60) return mins + " \\u5206\\u949f";\n'
    '    const hours = Math.floor(mins / 60);\n'
    '    return hours + " \\u5c0f\\u65f6 " + (mins % 60) + " \\u5206";\n'
    '  };\n'
)

# ── 4. 空闲文案 + 小名 ─────────────────────────────────────
OLD_IDLE = (
    '  const HX_IDLE_LINES = ["\u5c0f\u9cb8\u5a18\u6b63\u5728\u5403\u767d\u996d", '
    '"\u5c0f\u9cb8\u5a18\u5728\u7b49\u4e3b\u4eba\u6295\u5582", '
    '"\u5c0f\u9cb8\u5a18\u5728\u5543\u6570\u636e\u6d77\u8349", '
    '"\u5c0f\u9cb8\u5a18\u5728\u6570\u5c0f\u91d1\u5e93", '
    '"\u5c0f\u9cb8\u5a18\u5728\u78e8\u9cb8\u987b", '
    '"\u5c0f\u9cb8\u5a18\u5077\u5077\u6253\u4e86\u4e2a\u54c8\u6b20"];\n'
    '  let hxIdleLineIdx = Math.floor(Math.random() * HX_IDLE_LINES.length);\n'
    '  let hxIdleLine = HX_IDLE_LINES[hxIdleLineIdx];'
)
NEW_IDLE = (
    '  const HX_IDLE_LINES = ["{n}\u6b63\u5728\u5403\u767d\u996d", "{n}\u5728\u7b49\u4e3b\u4eba\u6295\u5582", '
    '"{n}\u5728\u5543\u6570\u636e\u6d77\u8349", "{n}\u5728\u6570\u5c0f\u91d1\u5e93", '
    '"{n}\u5728\u78e8\u9cb8\u987b", "{n}\u5077\u5077\u6253\u4e86\u4e2a\u54c8\u6b20", '
    '"{n}\u5728\u6253\u635e\u6d77\u5e95\u7684\u7b97\u529b", "{n}\u5728\u64e6\u4eae\u5c0f\u94dc\u94c3", '
    '"{n}\u5728\u6570\u4eca\u5929\u7684\u661f\u661f"];\n'
    '  const hxPetName = () => {\n'
    '    try {\n'
    '      const text = getStoredConfigText();\n'
    '      if (!text) return HX_DEFAULT_PET;\n'
    '      const parsed = JSON.parse(text);\n'
    '      const name = parsed && parsed.ai && parsed.ai.petName;\n'
    '      const trimmed = typeof name === "string" ? name.trim() : "";\n'
    '      return trimmed || HX_DEFAULT_PET;\n'
    '    } catch (error) { return HX_DEFAULT_PET; }\n'
    '  };\n'
    '  const hxLineText = (idx) => HX_IDLE_LINES[idx].split("{n}").join(hxPetName());\n'
    '  let hxIdleLineIdx = Math.floor(Math.random() * HX_IDLE_LINES.length);\n'
    '  let hxIdleLine = hxLineText(hxIdleLineIdx);'
)

# ── 5. 自动页面路由 ────────────────────────────────────────
TAB_ROUTER = (
    '  /* ── 页面路由：默认停在鲸娘页；状态页有新动静就跳过去，安静 10s 回鲸娘 ── */\n'
    '  const HX_TAB_MAIN = "1";\n'
    '  const HX_TAB_LOG = "0";\n'
    '  const HX_TAB_LABELS = { "0": "\u72b6\u6001", "1": "\u9cb8\u5a18" };\n'
    '  const HX_TAB_RETURN_MS = 10000;\n'
    '  let hxTabTimer = null;\n'
    '  let hxAutoTabTimer = null;\n'
    '  let hxAutoJumped = false;\n'
    '  let hxDefaultTabApplied = false;\n'
    '  let hxLastLogSig = "\\u0000";\n'
    '  let hxRouteReadyAt = 0;\n'
    '  const hxTabItems = () => {\n'
    '    const root = hxShadow;\n'
    '    if (!root) return [];\n'
    '    return Array.from(root.querySelectorAll(".demo-tabs>.el-tabs__header .el-tabs__item"));\n'
    '  };\n'
    '  const hxActiveTabIndex = () => hxTabItems().findIndex((el) => el.classList.contains("is-active"));\n'
    '  const hxTabIdIndex = (id) => {\n'
    '    const items = hxTabItems();\n'
    '    let idx = items.findIndex((el) => String(el.id || "") === "tab-" + id);\n'
    '    if (idx < 0) {\n'
    '      const want = HX_TAB_LABELS[id] || "";\n'
    '      idx = items.findIndex((el) => (el.textContent || "").trim() === want);\n'
    '    }\n'
    '    return idx;\n'
    '  };\n'
    '  const hxSwitchTab = (idx) => {\n'
    '    const items = hxTabItems();\n'
    '    const el = idx >= 0 ? items[idx] : null;\n'
    '    if (!el || el.classList.contains("is-active")) return false;\n'
    '    el.click();\n'
    '    return true;\n'
    '  };\n'
    '  const hxLogSignature = () => {\n'
    '    try {\n'
    '      const store = useLogStore();\n'
    '      const list = store && Array.isArray(store.logList) ? store.logList : [];\n'
    '      const last = list[list.length - 1];\n'
    '      return list.length + "|" + (last ? String(last.message || "") + "@" + String(last.time || "") : "");\n'
    '    } catch (error) { return ""; }\n'
    '  };\n'
    '  const hxReturnToMain = () => {\n'
    '    hxAutoJumped = false;\n'
    '    hxSwitchTab(hxTabIdIndex(HX_TAB_MAIN));\n'
    '  };\n'
    '  const hxRouteTick = () => {\n'
    '    const items = hxTabItems();\n'
    '    if (items.length === 0) return;\n'
    '    if (!hxDefaultTabApplied) {\n'
    '      hxDefaultTabApplied = true;\n'
    '      if (hxActiveTabIndex() === hxTabIdIndex(HX_TAB_LOG)) hxSwitchTab(hxTabIdIndex(HX_TAB_MAIN));\n'
    '      hxLastLogSig = hxLogSignature();\n'
    '      return;\n'
    '    }\n'
    '    const sig = hxLogSignature();\n'
    '    if (sig === hxLastLogSig) return;\n'
    '    hxLastLogSig = sig;\n'
    '    if (Date.now() < hxRouteReadyAt) return;\n'
    '    const active = hxActiveTabIndex();\n'
    '    const logIdx = hxTabIdIndex(HX_TAB_LOG);\n'
    '    if (active === logIdx || active === hxTabIdIndex(HX_TAB_MAIN)) {\n'
    '      if (hxSwitchTab(logIdx)) hxAutoJumped = true;\n'
    '    }\n'
    '    if (!hxAutoJumped) return;\n'
    '    if (hxAutoTabTimer) clearTimeout(hxAutoTabTimer);\n'
    '    hxAutoTabTimer = setTimeout(() => { try { hxReturnToMain(); } catch (error) { /* 忽略 */ } }, HX_TAB_RETURN_MS);\n'
    '  };\n'
    '  const bindTabRouter = () => {\n'
    '    const root = hxShadow;\n'
    '    if (!root) return false;\n'
    '    hxLastLogSig = hxLogSignature();\n'
    '    hxRouteReadyAt = Date.now() + 3000;\n'
    '    hxDefaultTabApplied = false;\n'
    '    if (hxTabTimer === null)\n'
    '      hxTabTimer = setInterval(() => { try { hxRouteTick(); } catch (error) { /* 忽略 */ } }, 1200);\n'
    '    try { hxRouteTick(); } catch (error) { /* 忽略 */ }\n'
    '    return true;\n'
    '  };\n'
    '\n'
)

# ── 6. 日志萌化 ────────────────────────────────────────────
MOE = [
    ("`\u89e3\u6790\u5230${this.questions.length}\u9053\u9898`", "`\u55c5\u5230 ${this.questions.length} \u9053\u9898\uff0c\u5f00\u52a8\u5566\uff5e`", 1),
    ("`\u7b2c${index + 1}\u9898\u6210\u529f`", "`\u7b2c ${index + 1} \u9898\u62ff\u4e0b\u5566\uff5e`", 1),
    ("`\u7b2c${index + 1}\u9898\u5931\u8d25 ", "`\u7b2c ${index + 1} \u9898\u7eca\u4e86\u4e00\u8de4\u2026 ", 1),
    ("show-answer-tab\">\u67e5\u770b\u539f\u56e0</a>", "show-answer-tab\">\u770b\u770b\u4e3a\u5565</a>", 1),
    ('"\u672a\u89e3\u6790\u5230\u9898\u76ee"', '"\u54e6\uff1f\u8fd9\u9875\u6ca1\u635e\u5230\u9898\u76ee\u55b9"', 1),
    ("`\u5df2\u8fdb\u5165\u7ae0\u8282\u9875`", "`\u6f5c\u5165\u7ae0\u8282\u9875\u5566\uff5e`", 1),
    ("`\u6b63\u5728\u89e3\u6790\u4efb\u52a1\u70b9`", "`\u6b63\u5728\u7ffb\u4efb\u52a1\u70b9\u7684\u8d1d\u58f3\u2026`", 1),
    ("`\u672c\u9875\u5b8c\u6210\uff0c\u524d\u5f80\u4e0b\u4e00\u7ae0`", "`\u672c\u9875\u5543\u5b8c\uff0c\u6e38\u5411\u4e0b\u4e00\u7ae0\uff01`", 1),
    ("`\u5df2\u5230\u6700\u540e\u4e00\u7ae0`", "`\u5230\u6700\u540e\u4e00\u7ae0\u5566\uff0c\u524d\u9762\u6ca1\u8def\u4e86`", 1),
    ("`\u81ea\u52a8\u4e0b\u4e00\u7ae0\u5df2\u5173\u95ed`", "`\u81ea\u52a8\u7ffb\u7ae0\u5173\u6389\u4e86\u54e6`", 1),
    ("`\u4efb\u52a1\u5904\u7406\u5931\u8d25`", "`\u4efb\u52a1\u5361\u4f4f\u4e86\uff0c\u545c\u2026`", 1),
    ("`\u53d1\u73b0${mediaType}\uff0c\u89e3\u6790\u4e2d`", "`\u6361\u5230${mediaType}\uff0c\u6b63\u5728\u62c6\u89e3\uff5e`", 1),
    ("`\u6b63\u5728\u64ad\u653e${mediaType}`", "`\u6b63\u5728\u653e${mediaType}\uff0c\u5c0f\u58f0\u70b9\uff5e`", 1),
    ("`${mediaType}\u64ad\u653e\u5b8c\u6210`", "`${mediaType}\u653e\u5b8c\u5566\uff5e`", 1),
    ("`${mediaType}\u5df2\u5b8c\u6210\uff0c\u8df3\u8fc7`", "`${mediaType}\u65e9\u770b\u8fc7\u4e86\uff0c\u8df3\u8fc7\uff5e`", 1),
    ('"\u64ad\u653e\u6210\u529f"', '"\u653e\u5f97\u5f88\u987a\uff0c\u641e\u5b9a\uff5e"', 1),
    ('"\u53d1\u73b0\u4f5c\u4e1a\uff0c\u89e3\u6790\u4e2d"', '"\u53d1\u73b0\u4f5c\u4e1a\uff0c\u9cb8\u5a18\u53bb\u7784\u4e00\u773c\uff5e"', 1),
    ('logStore.addLog("\u4f5c\u4e1a\u5df2\u5b8c\u6210\uff0c\u8df3\u8fc7", "success");',
     'logStore.addLog("\u4f5c\u4e1a\u65e9\u5c31\u5199\u5b8c\u5566\uff0c\u8df3\u8fc7\uff5e", "success");', 1),
    ("`\u9898\u76ee\u83b7\u53d6\u6210\u529f`", "`\u9898\u76ee\u5230\u624b\u5566\uff5e`", 1),
    ('"\u5c1d\u8bd5\u81ea\u52a8\u63d0\u4ea4"', '"\u51c6\u5907\u4ea4\u5377\u5490\u2026"', 1),
    ("`\u6b63\u786e\u7387\u4e0d\u8db3", "`\u6b63\u786e\u7387\u624d", 1),
    ("%\uff0c\u6682\u5b58`", "%\uff0c\u5148\u6512\u7740\uff5e`", 1),
    ("`\u6b63\u786e\u7387\u8fbe\u6807\uff0c\u63d0\u4ea4`", "`\u6b63\u786e\u7387\u8fbe\u6807\uff0c\u4ea4\u5377\uff01`", 1),
    ('"\u63d0\u4ea4\u6210\u529f"', '"\u4ea4\u5377\u6210\u529f\uff0c\u8036\uff5e"', 1),
    ('"\u672a\u5f00\u542f\u63d0\u4ea4\uff0c\u6682\u5b58"', '"\u6ca1\u5f00\u81ea\u52a8\u4ea4\u5377\uff0c\u5148\u5b58\u7740\uff5e"', 1),
    ('logStore.addLog("\u4f5c\u4e1a\u5df2\u5b8c\u6210", "success");',
     'logStore.addLog("\u4f5c\u4e1a\u641e\u5b9a\u5566\uff5e", "success");', 1),
    ('"\u53d1\u73b0\u6587\u6863\uff0c\u89e3\u6790\u4e2d"', '"\u53d1\u73b0\u6587\u6863\uff0c\u6b63\u5728\u5543\uff5e"', 1),
    ('"\u9605\u8bfb\u5b8c\u6210"', '"\u8bfb\u5b8c\u5566\uff5e"', 2),
    ('"\u53d1\u73b0\u7535\u5b50\u4e66\uff0c\u89e3\u6790\u4e2d"', '"\u53d1\u73b0\u7535\u5b50\u4e66\uff0c\u55c5\u55c5\uff5e"', 1),
    ('"\u4efb\u52a1\u70b9\u5df2\u5b8c\u6210"', '"\u4efb\u52a1\u70b9\u6e05\u7a7a\u5566\uff5e"', 1),
    ('"\u53ea\u7b54\u9898\u6a21\u5f0f\u5df2\u5f00\u542f"', '"\u4ec5\u4ec5\u4f5c\u7b54\u6a21\u5f0f\u5f00\u542f\uff5e"', 1),
    ("`\u8fdb\u5165\u4f5c\u4e1a\u9875\uff0c\u51c6\u5907\u7b54\u9898`", "`\u6e38\u8fdb\u4f5c\u4e1a\u9875\uff0c\u51c6\u5907\u7b54\u9898\uff5e`", 1),
    ("`\u6b63\u5728\u89e3\u6790\u9898\u76ee`", "`\u6b63\u5728\u8bfb\u9898\u2026`", 1),
    ('"\u8fdb\u5165\u8003\u8bd5\u9875\uff0c\u51c6\u5907\u7b54\u9898"', '"\u8fdb\u8003\u573a\u5566\uff0c\u52a0\u6cb9\uff5e"', 1),
    ('logStore.addLog("\u81ea\u52a8\u5207\u9898", "success");', 'logStore.addLog("\u81ea\u52a8\u7ffb\u5230\u4e0b\u4e00\u9898\uff5e", "success");', 1),
    ('"\u5df2\u5230\u6700\u540e\u4e00\u9898"', '"\u8fd9\u662f\u6700\u540e\u4e00\u9898\u5490\uff5e"', 1),
    ('"\u81ea\u52a8\u5207\u6362\u5df2\u5173\u95ed"', '"\u81ea\u52a8\u7ffb\u9898\u5173\u6389\u4e86\u54e6"', 1),
    ('"\u5df2\u540c\u610f\u7528\u6237\u534f\u8bae"', '"\u534f\u8bae\u6309\u8fc7\u722a\u5370\u5566\uff5e"', 1),
    ('"\u5f02\u5e38\u8bf7\u6539\u7528 Edge \u6d4f\u89c8\u5668"', '"\u602a\u602a\u7684\u2026\u6362\u4e2a Edge \u6d4f\u89c8\u5668\u8bd5\u8bd5\uff1f"', 1),
    ('"\u6b64\u9875\u65e0\u4efb\u52a1"', '"\u8fd9\u9875\u6ca1\u6d3b\u513f\uff0c\u9cb8\u5a18\u6b47\u4f1a\u513f\uff5e"', 1),
    ('"\u672c\u6b21\u7528\u91cf\u7edf\u8ba1\u5df2\u91cd\u7f6e"', '"\u672c\u6b21\u7528\u91cf\u5f52\u96f6\uff0c\u91cd\u65b0\u6570\u94b1\uff5e"', 1),
]

# 状态灯「终止」判定要跟上新文案
OLD_STATUS_RE = "\u5b8c\u6210|\u6700\u540e\u4e00\u7ae0|\u6700\u540e\u4e00\u9898|\u5df2\u5230\u6700\u540e\u4e00"
NEW_STATUS_RE = "\u5b8c\u6210|\u6700\u540e|\u5543\u5b8c|\u641e\u5b9a|\u6e05\u7a7a|\u8bfb\u5b8c|\u653e\u5b8c|\u8df3\u8fc7"

# ── 7. 新增 CSS（最后一个 push，一定赢）────────────────────
NEW_CSS_BLOCK = (
    "\n  // ---- v0.4.8 ----\n"
    "  LAYOUT_CSS_PARTS.push(\n"
    '    "\\n/* ==== v0.4.8-d : \u53ef\u89c1\u5149\u5e26 + \u73bb\u7483\u5316 + \u5c0f\u540d + \u8fd0\u884c\u65f6\u957f + \u81ea\u52a8\u8def\u7531 ==== */"\n'
    '    + "\\n.main-page .usage-uptime{margin-left:auto;flex:0 0 auto;padding:1px 8px;border:1px solid var(--hx-line);border-radius:20px;background:rgba(255,255,255,.05);font-size:10.5px;line-height:15px;color:var(--hx-ink-dim);white-space:nowrap;font-variant-numeric:tabular-nums}"\n'
    '    + "\\n.main-page .setting>div.setting-ai .el-form-item.setting-pet-field>.el-form-item__label{flex:0 0 54px}"\n'
    '    + "\\n.main-page .el-card{box-shadow:0 18px 48px rgba(2,8,24,.42),0 0 0 1px rgba(140,200,255,.14) inset!important}"\n'
    "  );\n"
)

# ── 应用 ───────────────────────────────────────────────────
patches = [
    ("分节注释-b", D[0][0], D[0][1], 1),
    ("分节注释-c", D[1][0], D[1][1], 1),
    ("背景光带迁到卡片", OLD_BG_SWEEP, NEW_BG_SWEEP, 1),
    ("关键帧 hxBgSweep", OLD_KF_SWEEP, NEW_KF_SWEEP, 1),
    ("背景呼吸层", OLD_BG_BREATHE, NEW_BG_BREATHE, 1),
    ("关键帧 hxBgBreathe", OLD_KF_BREATHE, NEW_KF_BREATHE, 1),
    ("降级选择器", OLD_RM, NEW_RM, 1),
    ("formatUptime 定义", "  const buildUsageBarHtml = (store, peak) => {",
     UP_FN + "  const buildUsageBarHtml = (store, peak) => {", 1),
    ("session 基线 at(读)", "      return { cost, totalTokens: tokens, requests: reqs };",
     "      const at = Number(obj.at);\n      return { cost, totalTokens: tokens, requests: reqs, at: isFinite(at) && at > 0 ? at : Date.now() };", 1),
    ("session 基线 at(建)",
     "  if (!sessionBase) {\n    sessionBase = { cost: usageStore.cost, totalTokens: usageStore.totalTokens, requests: usageStore.requests };",
     "  if (!sessionBase) {\n    sessionBase = { cost: usageStore.cost, totalTokens: usageStore.totalTokens, requests: usageStore.requests, at: Date.now() };", 1),
    ("session 基线 at(重置)",
     "  const resetSessionUsage = () => {\n    sessionBase = { cost: usageStore.cost, totalTokens: usageStore.totalTokens, requests: usageStore.requests };",
     "  const resetSessionUsage = () => {\n    sessionBase = { cost: usageStore.cost, totalTokens: usageStore.totalTokens, requests: usageStore.requests, at: Date.now() };", 1),
    ("时长入 HTML", "    const sess = sessionUsage();",
     "    const sess = sessionUsage();\n    const upMs = Math.max(Date.now() - (sessionBase.at || Date.now()), 0);", 1),
    ("时长 span",
     "      + '<span class=\"usage-session__k\">\u672c\u6b21</span>'\n"
     "      + '<span class=\"usage-session__v\">' + formatCost(sess.cost) + \"</span>\"\n"
     "      + \"</span>\"\n"
     "      + \"</div>\";",
     "      + '<span class=\"usage-session__k\">\u672c\u6b21</span>'\n"
     "      + '<span class=\"usage-session__v\">' + formatCost(sess.cost) + \"</span>\"\n"
     "      + \"</span>\"\n"
     "      + '<span class=\"usage-uptime\" title=\"\u672c\u6b21\u542f\u7528\u811a\u672c\u540e\u7684\u8fd0\u884c\u65f6\u957f\">\u8fd0\u884c ' + formatUptime(upMs) + \"</span>\"\n"
     "      + \"</div>\";", 1),
    ("tick 改 20s", "  setInterval(() => {\n    usageTick.value += 1;\n  }, 6e4);",
     "  setInterval(() => {\n    usageTick.value += 1;\n  }, 2e4);", 1),
    ("HX_DEFAULT_PET", '  const HX_BUILD = "0.4.8";',
     '  const HX_BUILD = "0.4.8";\n  const HX_DEFAULT_PET = "\u5c0f\u9cb8\u5a18";', 1),
    ("空闲文案池", OLD_IDLE, NEW_IDLE, 1),
    ("paintIdleLine 取当前小名",
     "    if (!animate && text.textContent === hxIdleLine)\n      return true;\n    text.textContent = hxIdleLine;",
     "    const line = hxLineText(hxIdleLineIdx);\n    hxIdleLine = line;\n    if (!animate && text.textContent === line)\n      return true;\n    text.textContent = line;", 1),
    ("rollIdleLine 取当前小名",
     "    hxIdleLine = HX_IDLE_LINES[hxIdleLineIdx];\n    try { paintIdleLine(true); }",
     "    hxIdleLine = hxLineText(hxIdleLineIdx);\n    try { paintIdleLine(true); }", 1),
    ("路由块注入", "  const CAN_USE_ADOPTED_SHEETS = (() => {", TAB_ROUTER + "  const CAN_USE_ADOPTED_SHEETS = (() => {", 1),
    ("路由绑定调用", "      try { bindIdleLines(); } catch (error2) { /* \u5ffd\u7565 */ }",
     "      try { bindIdleLines(); } catch (error2) { /* \u5ffd\u7565 */ }\n      try { bindTabRouter(); } catch (error2) { /* \u5ffd\u7565 */ }", 1),
    ("探针补 NAME/TAB", "      w.__HX_LINE__ = () => hxIdleLine;",
     "      w.__HX_LINE__ = () => hxIdleLine;\n"
     "      w.__HX_NAME__ = () => hxPetName();\n"
     "      w.__HX_TAB__ = () => ({ active: hxActiveTabIndex(), labels: hxTabItems().map((el) => (el.textContent || \"\").trim()), autoJumped: hxAutoJumped, applied: hxDefaultTabApplied });", 1),
    ("DIAG 补字段",
     "          session: sessionUsage(),\n          sessionBase: { requests: sessionBase.requests, totalTokens: sessionBase.totalTokens, cost: sessionBase.cost },",
     "          session: sessionUsage(),\n          sessionBase: { requests: sessionBase.requests, totalTokens: sessionBase.totalTokens, cost: sessionBase.cost, at: sessionBase.at || 0 },\n"
     "          uptimeMs: Math.max(Date.now() - (sessionBase.at || Date.now()), 0),\n"
     "          petName: hxPetName(),\n"
     "          route: { active: hxActiveTabIndex(), autoJumped: hxAutoJumped, applied: hxDefaultTabApplied, sig: hxLastLogSig },", 1),
    ("DIAG configTab 补小名",
     "            model: q(\".setting-ai .el-select\")\n          },",
     "            model: q(\".setting-ai .el-select\"),\n            pet: q(\".setting-pet-field\")\n          },", 1),
    ("DIAG 补背景",
     "          tabs: sr ? Array.from(sr.querySelectorAll(\".el-tabs__item\")).map((el) => (el.textContent || \"\").trim()) : []",
     "          background: (() => {\n"
     "            try {\n"
     "              const card = sr && sr.querySelector(\".el-card\");\n"
     "              if (!card) return null;\n"
     "              const cs = getComputedStyle(card);\n"
     "              const body = sr.querySelector(\".el-card__body\");\n"
     "              const bs = body ? getComputedStyle(body, \"::after\") : null;\n"
     "              return { cardBg: (cs.backgroundImage || \"\").slice(0, 24), cardBlur: cs.backdropFilter || cs.webkitBackdropFilter || \"\", sweepAnim: bs ? String(bs.animationName || \"\") : \"\" };\n"
     "            } catch (error) { return null; }\n"
     "          })(),\n"
     "          tabs: sr ? Array.from(sr.querySelectorAll(\".el-tabs__item\")).map((el) => (el.textContent || \"\").trim()) : []", 1),
    ("AI 卡片加小名字段",
     "                    vue.createVNode(_component_el_option, { value: \"deepseek-flash\", label: \"DeepSeek Flash\" })\n"
     "                  ]),\n"
     "                  _: 1\n"
     "                }, 8, [\"modelValue\"])\n"
     "              ]),\n"
     "              _: 2\n"
     "            }, 1032, [\"label\"])\n"
     "          ]),",
     "                    vue.createVNode(_component_el_option, { value: \"deepseek-flash\", label: \"DeepSeek Flash\" })\n"
     "                  ]),\n"
     "                  _: 1\n"
     "                }, 8, [\"modelValue\"])\n"
     "              ]),\n"
     "              _: 2\n"
     "            }, 1032, [\"label\"]),\n"
     "            vue.createVNode(_component_el_form_item, { class: \"setting-ai-field setting-pet-field\", label: \"\u5c0f\u540d\" }, {\n"
     "              default: vue.withCtx(() => [\n"
     "                vue.createVNode(_component_el_input, {\n"
     "                  modelValue: _ctx.globalConfig.ai.petName,\n"
     "                  \"onUpdate:modelValue\": (v) => _ctx.globalConfig.ai.petName = v,\n"
     "                  placeholder: \"\u7ed9\u9cb8\u5a18\u53d6\u4e2a\u5c0f\u540d\",\n"
     "                  clearable: true,\n"
     "                  maxlength: \"12\",\n"
     "                  size: \"small\"\n"
     "                }, null, 8, [\"modelValue\"])\n"
     "              ]),\n"
     "              _: 2\n"
     "            }, 1032, [\"label\"])\n"
     "          ]),", 1),
    ("sanitize 小名",
     "    if (!ai.deepseek) ai.deepseek = { apiKey: \"\", model: DEFAULT_AI_MODEL };",
     "    if (!ai.deepseek) ai.deepseek = { apiKey: \"\", model: DEFAULT_AI_MODEL };\n    if (typeof ai.petName !== \"string\") ai.petName = \"\u5c0f\u9cb8\u5a18\";", 1),
    ("默认配置 小名",
     "        ai: {\n          deepseek: { apiKey: \"\", model: DEFAULT_AI_MODEL }\n        },",
     "        ai: {\n          deepseek: { apiKey: \"\", model: DEFAULT_AI_MODEL },\n          petName: \"\u5c0f\u9cb8\u5a18\"\n        },", 1),
    ("状态灯判据", OLD_STATUS_RE, NEW_STATUS_RE, 1),
    ("新 CSS 块", "const layoutCss = LAYOUT_CSS_PARTS.join(\"\");",
     NEW_CSS_BLOCK + "\nconst layoutCss = LAYOUT_CSS_PARTS.join(\"\");", 1),
]
for i, (old, new, exp) in enumerate(MOE):
    patches.append(("\u840c\u5316 %02d" % (i + 1), old, new, exp))

w("")
w("=== 补丁预检（共 %d 项）===" % len(patches))
fails = []
for name, old, new, exp in patches:
    cnt = s.count(old)
    flag = "OK" if cnt == exp else "NG"
    w("  [%s] %-22s 期望=%d 实际=%d" % (flag, name, exp, cnt))
    if cnt != exp:
        fails.append((name, exp, cnt, old[:70]))

PANEL_LOG_RE = re.compile(r'logStore\.addLog\(".*?0\.4\.8.*?", "success"\);')
PANEL_LOG_NEW = 'logStore.addLog("\u9762\u677f 0.4.8 \u5df2\u5c31\u4f4d\uff0c\u9cb8\u5a18\u5f00\u5de5\uff5e", "success");'
w("")
w("=== 面板启动日志（正则定位，规避 \\uXXXX 转义歧义）===")
_panel_hits = PANEL_LOG_RE.findall(s)
w("  matches=%d" % len(_panel_hits))
for _one in _panel_hits:
    w("  -> " + _one[:120])
if len(_panel_hits) != 1:
    fails.append(("面板启动日志", 1, len(_panel_hits), "regex"))

if fails:
    w("")
    w("!! 预检失败，未写入任何改动：")
    for name, exp, cnt, head in fails:
        w("   - %s: 期望 %d 实际 %d  << %s" % (name, exp, cnt, head))
    with open(OUT, "w", encoding="utf-8") as f:
        f.write("\n".join(log))
    w("")
    print("PRECHECK_FAIL")
    sys.exit(1)

w("")
w("全部匹配，开始写入…")
for name, old, new, exp in patches:
    s = s.replace(old, new)
s = PANEL_LOG_RE.sub(PANEL_LOG_NEW, s, count=1)

# ── 写回 CRLF ──────────────────────────────────────────────
out_bytes = s.replace("\n", "\r\n").encode("utf-8")
crlf = out_bytes.count(b"\r\n")
bare = len(re.findall(rb"(?<!\r)\n", out_bytes))
w("")
w("orig_chars=%d  new_chars=%d" % (orig_len, len(s)))
w("bytes=%d  crlf=%d  bare_lf=%d" % (len(out_bytes), crlf, bare))

if DRY:
    w("")
    w("DRY RUN —— 未写入文件")
else:
    if bare != 0:
        w("!! 裸 LF 非 0，拒绝写入")
        with open(OUT, "w", encoding="utf-8") as f:
            f.write("\n".join(log))
        sys.exit(1)
    with open(P, "wb") as f:
        f.write(out_bytes)
    w("")
    w("已写入：%s" % P)

with open(OUT, "w", encoding="utf-8") as f:
    f.write("\n".join(log))
print("DONE dry=%s" % DRY)
