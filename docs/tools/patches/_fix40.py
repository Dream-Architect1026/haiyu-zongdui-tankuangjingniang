# -*- coding: utf-8 -*-
# fix40: 让「更新」真正生效
#  A) @version 0.4.1 -> 0.4.2   ← 核心：版本号不变，脚本管理器会拒绝更新
#  B) whale-page 根节点 patchFlag 64(STABLE_FRAGMENT) -> 0（Fragment 标志误留在 element 上）
#  C) 启动日志加可见版本标记，便于一眼确认装的是哪一版
import io, sys

P = r"C:\Users\D_A\DoubaoWork\chats\2026-10-05\new-chat-4\海底小纵队·探矿鲸娘.user.js"
CRLF = "\r\n"

with io.open(P, "r", encoding="utf-8", newline="") as f:
    t = f.read()

orig_len = len(t)
log = []


def sub_once(old, new, tag):
    global t
    old = old.replace("\n", CRLF)
    new = new.replace("\n", CRLF)
    n = t.count(old)
    assert n == 1, "[%s] 锚点命中 %d 次" % (tag, n)
    t = t.replace(old, new, 1)
    log.append("ok " + tag)


# ---------- A: 版本号（头部 + 教程页页脚硬编码） ----------
sub_once("// @version      0.4.1", "// @version      0.4.2", "A @version 0.4.1 -> 0.4.2")
assert t.count("v0.4.1") == 1, "教程页页脚 v0.4.1 命中 %d 次" % t.count("v0.4.1")
t = t.replace("v0.4.1", "v0.4.2", 1)
log.append("ok A2 教程页页脚 v0.4.1 -> v0.4.2")

# ---------- B: 根节点 patchFlag ----------
sub_once(
    '''          vue.createElementVNode("div", { class: "usage-bar", innerHTML: usageBarHtml.value }, null, 8, ["innerHTML"])
        ], 64);''',
    '''          vue.createElementVNode("div", { class: "usage-bar", innerHTML: usageBarHtml.value }, null, 8, ["innerHTML"])
        ], 0);''',
    "B whale-page 根 patchFlag 64 -> 0",
)

# ---------- C: 可见版本标记 ----------
sub_once(
    '''      logStore.addLog("已同意用户协议", "success");''',
    '''      logStore.addLog("已同意用户协议", "success");
      logStore.addLog("面板 0.4.2 \\u00b7 \\u65b0\\u7248\\u5e03\\u5c40\\u5df2\\u52a0\\u8f7d", "success");''',
    "C 启动日志加版本标记",
)

# ---------- 复核 ----------
ver = t.split("// @version")[1].split("\n")[0].strip()
log.append("version now = " + ver)
assert ver == "0.4.2", "版本号未更新"

assert t.count("], 0);" + CRLF + "      };") >= 1, "patchFlag 未改"
assert t.count("\\u65b0\\u7248\\u5e03\\u5c40\\u5df2\\u52a0\\u8f7d") == 1, "版本标记未注入"
assert t.count("0.4.1") == 0, "仍有 0.4.1 残留: %d" % t.count("0.4.1")

crlf = t.count(CRLF)
bare = t.count("\n") - crlf
log.append("chars: %d -> %d ; CRLF=%d bareLF=%d" % (orig_len, len(t), crlf, bare))
assert bare == 0, "出现裸 LF"

with io.open(P, "w", encoding="utf-8", newline="") as f:
    f.write(t)

sys.stdout.write("\n".join(log) + "\n")
