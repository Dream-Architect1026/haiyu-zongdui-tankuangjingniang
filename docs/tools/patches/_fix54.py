# -*- coding: utf-8 -*-
"""
fix54 -> 0.4.12 ：「本次」用量永不归零的修复

用户实测：本次 = 20，「重新启用脚本之后它还是 20」。

两处根因（均已在源码里钉死）：
  A. 基线落在 sessionStorage["hx_session_base_v1"]。
     sessionStorage 在同一标签页内跨「刷新 / 关掉脚本再打开」存活，
     于是重新启用时 readSessionBase() 读到的是上一条基线 ⇒ 本次 = 累计 − 旧基线，
     永远不归零。改法：基线改为**内存变量**，只活在本页脚本实例里，
     启动即从当前累计值起算 ⇒ 重新启用必定归零（与「运行时长」同源同界）。
  B. 手动归零点失效。0.4.10 用量栏改版时 .usage-session 胶囊被移除，
     而点击绑定仍是 target.closest(".usage-session") ⇒ 死代码，
     用户连「点一下归零」这条退路也没有。
     改法：本次格补 data-hx-cell="session"，绑定改指它，并补 cursor/悬停反馈。

顺带清理：4 条已成死代码的 .usage-session CSS 规则 + reduced-motion 名单里的死项。

用法：
  python _fix54.py --dry    # 只校验锚点唯一性与结构不变量，不落盘
  python _fix54.py          # 校验通过后落盘（CRLF）
"""
import io
import os
import shutil
import subprocess
import sys

P = r"C:\Users\D_A\DoubaoWork\chats\2026-10-05\new-chat-4\海底小纵队·探矿鲸娘.user.js"
OUT = r"C:\Users\D_A\WorkBuddy\2026-10-05-13-53-42\_f54out.txt"
BAK = r"C:\Users\D_A\WorkBuddy\2026-10-05-13-53-42\_bak_0411.user.js"
DRY = "--dry" in sys.argv

log = []


def w(s):
    log.append(str(s))


def flush(code=0):
    io.open(OUT, "w", encoding="utf-8").write("\n".join(log))
    sys.exit(code)


raw = io.open(P, "rb").read().decode("utf-8")
was_crlf = "\r\n" in raw
s = raw.replace("\r\n", "\n")
lines = s.split("\n")
w("输入 " + P)
w("  字节=" + str(len(raw.encode("utf-8"))) + "  CRLF=" + str(was_crlf) + "  行=" + str(len(lines)))
w("")

# ── 0. 前置：确认 sessionStorage 只出现在待删块内 ────────────────────────
pre_ss = s.count("sessionStorage")
w("前置 sessionStorage 命中 = " + str(pre_ss) + "（期望 4：1 处注释 + 3 处代码，全在待删块内）")
if pre_ss != 4:
    w("!! 前置不符，中止")
    flush(1)
pre_011 = s.count("0.4.11")
w("前置 0.4.11 命中 = " + str(pre_011) + "（含历史分节注释，本次只改其中 4 处语义位置）")
if pre_011 < 4:
    w("!! 前置不符，中止")
    flush(1)


def must(label, text, old, new, expected=1):
    n = text.count(old)
    if n != expected:
        w("!! [" + label + "] 期望 " + str(expected) + " 处，实际 " + str(n) + " 处 —— 未写入")
        flush(1)
    w("  [OK] " + label + "  (" + str(n) + " 处)")
    return text.replace(old, new)


w("=== P1 删死代码：.usage-session CSS 规则 ===")
dead_marker = r"\n.main-page .usage-session"
dead_idx = set(i for i, l in enumerate(lines) if dead_marker in l)
if len(dead_idx) != 4:
    w("!! 死规则期望 4 行，实际 " + str(len(dead_idx)) + " 行：" + str(sorted(dead_idx)))
    flush(1)
for i in sorted(dead_idx):
    w("  [删] L" + str(i + 1) + " " + lines[i].strip()[:96] + " ...")
lines = [l for i, l in enumerate(lines) if i not in dead_idx]
s = "\n".join(lines)

w("")
w("=== P2 替换「本次」用量块：sessionStorage 基线 -> 内存基线 ===")
KEY = 'const HX_SESSION_KEY = "hx_session_base_v1";'
if s.count(KEY) != 1:
    w("!! 锚点 " + KEY + " 命中 " + str(s.count(KEY)))
    flush(1)
i0 = next(i for i, l in enumerate(lines) if KEY in l)
a = None
for j in range(i0, max(-1, i0 - 6), -1):
    if "「本次」用量" in lines[j]:
        a = j
        break
if a is None:
    w("!! 找不到「本次」用量 块注释起始行")
    flush(1)
RESET = "  const resetSessionUsage = () => {"
j0 = next(i for i, l in enumerate(lines) if l == RESET)
b = None
for j in range(j0, min(len(lines), j0 + 14)):
    if lines[j] == "  };":
        b = j
        break
if b is None:
    w("!! 找不到 resetSessionUsage 结束行")
    flush(1)
w("  替换区间 L" + str(a + 1) + " - L" + str(b + 1) + "（共 " + str(b - a + 1) + " 行）")
w("  起始注释行：" + lines[a].strip()[:70])
w("  结束行     ：" + lines[b].strip())

NEW_BLOCK = r'''  /* ── 「本次」用量：以「本次启用脚本」为界 ───────────────────────────
     0.4.12 修复：基线由会话级存储（sessionStorage）改为**内存变量**。
     旧实现把基线写进会话级存储，而它会在同一标签页里跨「刷新 / 关掉脚本再打开」存活，
     于是重新启用时读回的是上一条基线 ⇒ 本次 = 累计 − 旧基线，永远不归零
     （用户实测：重新启用之后它还是 20）。
     现在基线只活在本页内存里：脚本每次启动都从当前累计值起算，
     所以「本次」= 本次启用脚本后的用量，重新启用必定归零；
     与「运行时长」同源同界，语义一致。
     另：旧版「点本次格归零」绑在一个已于 0.4.10 改版时被移除的旧胶囊元素上，
     属死代码；现在改绑到本次格自身的 data-hx-cell 标记。 */
  let sessionBase = {
    cost: usageStore.cost, totalTokens: usageStore.totalTokens, requests: usageStore.requests, at: Date.now()
  };
  const sessionUsage = () => ({
    requests: Math.max(usageStore.requests - sessionBase.requests, 0),
    totalTokens: Math.max(usageStore.totalTokens - sessionBase.totalTokens, 0),
    cost: Math.max(usageStore.cost - sessionBase.cost, 0)
  });
  const resetSessionUsage = () => {
    sessionBase = { cost: usageStore.cost, totalTokens: usageStore.totalTokens, requests: usageStore.requests, at: Date.now() };
    try { usageTick.value += 1; } catch (error) {}
    return sessionUsage();
  };'''.split("\n")
lines = lines[:a] + NEW_BLOCK + lines[b + 1:]
s = "\n".join(lines)
w("  已替换为 " + str(len(NEW_BLOCK)) + " 行内存基线实现")
w("")
w("=== P3 其余锚点替换 ===")

s = must("P3.1 @version", s, "// @version      0.4.11", "// @version      0.4.12")
s = must("P3.2 HX_BUILD", s, 'const HX_BUILD = "0.4.11";', 'const HX_BUILD = "0.4.12";')
s = must("P3.3 通知页日志", s,
         'logStore.addLog("\u9762\u677f 0.4.11 \u5df2\u5c31\u4f4d\uff0c\u9cb8\u5a18\u5f00\u5de5\uff5e", "success");',
         'logStore.addLog("\u9762\u677f 0.4.12 \u5df2\u5c31\u4f4d\uff0c\u9cb8\u5a18\u5f00\u5de5\uff5e", "success");')
s = must("P3.4 \u6559\u7a0b\u9875\u9875\u811a", s,
         "\u6d77\u5e95\u5c0f\u7eb5\u961f \u00b7 \u63a2\u77ff\u9cb8\u5a18 \u00b7 v0.4.11 \u00b7 MIT License",
         "\u6d77\u5e95\u5c0f\u7eb5\u961f \u00b7 \u63a2\u77ff\u9cb8\u5a18 \u00b7 v0.4.12 \u00b7 MIT License")
s = must("P3.5 本次格 title 补归零提示", s,
         '+ " token \u00b7 " + formatCost(sess.cost);',
         '+ " token \u00b7 " + formatCost(sess.cost) + " \uff5c \u70b9\u8fd9\u4e00\u683c\u5f52\u96f6";')

OLD_CELLS = '''    const cells = [
      ["\u672c\u6b21", String(sess.requests), sessTitle],
      ["Token", formatTokenCount(store.totalTokens), "\u811a\u672c\u7edf\u8ba1\u7684\u7d2f\u8ba1 token \u7528\u91cf"],
      ["\u603b\u82b1\u8d39", formatCost(store.cost), "\u811a\u672c\u7edf\u8ba1\u7684\u7d2f\u8ba1\u82b1\u8d39"]
    ].map(([label, value, tip]) => '<div class="usage-cell" title="' + tip + '"><span class="usage-cell__k">' + label'''
NEW_CELLS = '''    const cells = [
      ["\u672c\u6b21", String(sess.requests), sessTitle, ' data-hx-cell="session"'],
      ["Token", formatTokenCount(store.totalTokens), "\u811a\u672c\u7edf\u8ba1\u7684\u7d2f\u8ba1 token \u7528\u91cf", ""],
      ["\u603b\u82b1\u8d39", formatCost(store.cost), "\u811a\u672c\u7edf\u8ba1\u7684\u7d2f\u8ba1\u82b1\u8d39", ""]
    ].map(([label, value, tip, attr]) => '<div class="usage-cell"' + attr + ' title="' + tip + '"><span class="usage-cell__k">' + label'''
s = must("P3.6 本次格补 data-hx-cell", s, OLD_CELLS, NEW_CELLS)

s = must("P3.7 点击绑定改指本次格", s,
         'if (target.closest(".usage-session")) {',
         'if (target.closest(\'[data-hx-cell="session"]\')) {')

s = must("P3.8 reduced-motion 去掉死项", s,
         ".main-page .usage-cell,.main-page .usage-session,.main-page .hero-balance",
         ".main-page .usage-cell,.main-page .hero-balance")

NEW_CSS = [
    "",
    "// ---- v0.4.12 ----",
    "LAYOUT_CSS_PARTS.push(",
    r'  "\n/* ==== v0.4.12 · 本轮 : 「本次」用量归零修复（基线改内存） + 本次格可点击归零 ==== */"',
    r'  + "\n/* --- A. 本次格是唯一可点的用量格。旧版把重置绑在一个已于 0.4.10 改版时被移除的旧用量胶囊上 ⇒ 点击成了死代码；这里补回可点的手感 --- */"',
    r"""  + "\n.main-page .usage-cell[data-hx-cell='session']{cursor:pointer}" """.rstrip(),
    r"""  + "\n.main-page .usage-cell[data-hx-cell='session']:hover{border-color:rgba(56,226,255,.46)!important;box-shadow:0 5px 14px rgba(2,8,24,.28),inset 0 1px 0 rgba(255,255,255,.30)!important}" """.rstrip(),
    r"""  + "\n.main-page .usage-cell[data-hx-cell='session']:active{transform:none}" """.rstrip(),
    ");",
]
ANCHOR_LINE = 'const layoutCss = LAYOUT_CSS_PARTS.join("");'
if s.count(ANCHOR_LINE) != 1:
    w("!! 锚点 " + ANCHOR_LINE + " 命中 " + str(s.count(ANCHOR_LINE)))
    flush(1)
lines = s.split("\n")
k = next(i for i, l in enumerate(lines) if l == ANCHOR_LINE)
lines = lines[:k] + NEW_CSS + [""] + lines[k:]
s = "\n".join(lines)
w("  [OK] P3.9 追加 v0.4.12 CSS 块（5 条规则）于 L" + str(k + 1) + " 之前")

w("")
w("=== P4 结构不变量 ===")
checks = [
    ("unsafeWindow.sessionStorage 归零", s.count("unsafeWindow.sessionStorage"), 0),
    ("代码里 sessionStorage 归零", s.count(": sessionStorage"), 0),
    ("选择器 \".usage-session\" 归零", s.count('".usage-session"'), 0),
    ("CSS .main-page .usage-session 归零", s.count(".main-page .usage-session"), 0),
    ("usage-session 全清（含注释）", s.count("usage-session"), 0),
    ("HX_SESSION_KEY 归零", s.count("HX_SESSION_KEY"), 0),
    ("hxSessionStore 归零", s.count("hxSessionStore"), 0),
    ("readSessionBase 归零", s.count("readSessionBase"), 0),
    ("writeSessionBase 归零", s.count("writeSessionBase"), 0),
    ("内存基线声明 1 处", s.count("let sessionBase = {"), 1),
    ("sessionUsage 定义 1 处", s.count("const sessionUsage = () => ({"), 1),
    ("resetSessionUsage 定义 1 处", s.count("const resetSessionUsage = () => {"), 1),
    ("本次格标记 2 处（模板+绑定）", s.count('data-hx-cell="session"'), 2),
    ("点击绑定新锚点 1 处", s.count("[data-hx-cell=\"session\"]')) {"), 1),
    ("旧点击锚点归零", s.count('closest(".usage-session")'), 0),
    ("语义 0.4.11 全清", s.count("0.4.11"), pre_011 - 4),
    ("0.4.12 版本串 7 处（4 语义 + 3 注释）", s.count("0.4.12"), 7),
    ("CRLF 文档属性保持", 1 if was_crlf else 0, 1),
]
fails = []
for name, got, exp in checks:
    ok = got == exp
    w("  [" + ("OK" if ok else "NG") + "] " + name.ljust(26) + " got=" + str(got) + " exp=" + str(exp))
    if not ok:
        fails.append(name)
if fails:
    w("!! 未写入：" + ", ".join(fails))
    flush(1)

crlf = s.replace("\n", "\r\n")
payload = crlf.encode("utf-8")
w("")
w("=== P5 落盘前语法预检（node --check）===")
NODE = r"C:\Users\D_A\.workbuddy\binaries\node\versions\22.22.2-3\node.exe"
if os.path.exists(NODE):
    tmp = P + ".chk.user.js"
    io.open(tmp, "wb").write(payload)
    r = subprocess.run([NODE, "--check", tmp], capture_output=True)
    try:
        os.remove(tmp)
    except OSError:
        pass
    if r.returncode != 0:
        w("  [NG] node --check 失败，拒绝写盘：")
        for ln in r.stderr.decode("utf-8", "replace").splitlines()[:6]:
            w("       " + ln)
        flush(1)
    w("  [OK] node --check 通过（exit 0）")
else:
    w("  [WARN] 未找到 node，跳过语法预检：" + NODE)
w("")
w("=== P6 落盘 ===")
w("  预览 bytes=" + str(len(payload)) + "  crlf=" + str(s.count("\n")) + "  bareLF=0")
w("  dry=" + str(DRY))
if DRY:
    w("  [DRY] 未写盘")
    flush(0)

if not os.path.exists(BAK):
    shutil.copyfile(P, BAK)
    w("  已备份 0.4.11 -> " + BAK)
else:
    w("  备份已存在，跳过：" + BAK)
io.open(P, "wb").write(payload)
w("  已写盘 " + P)
flush(0)
