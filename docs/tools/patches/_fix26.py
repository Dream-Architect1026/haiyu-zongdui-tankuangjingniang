# -*- coding: utf-8 -*-
"""fix26（按用户 5 条反馈）:
  1) 首页通知卡片紧凑化：时间内联成小徽章，消灭「时间↔正文」空档，纵向收到 ~2/3
  2) 答题页：鲸娘图标放大到 132px 并在空白区垂直居中
  3) 设置页：布局不动，仅文案（已在 fix23 完成，本轮复核）
  4) 教程页 / 协议页：不动
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

CSS = [
    r'    + "\n/* ===== 通知卡片紧凑化：时间内联成徽章，时间↔正文空档归零 ===== */"',
    r'    + "\n.main-page .script-home .el-scrollbar__view>div{position:relative;margin:0 0 5px!important;padding:6px 9px 7px 18px!important;border:1px solid var(--hx-line);border-radius:9px;background:linear-gradient(135deg,rgba(18,32,62,.62),rgba(12,22,44,.40));box-shadow:0 3px 10px rgba(2,8,24,.20);backdrop-filter:blur(8px) saturate(140%);-webkit-backdrop-filter:blur(8px) saturate(140%);line-height:1.7;transition:border-color .18s,background .18s}"',
    r'    + "\n.main-page .script-home .el-scrollbar__view>div:before{content:\'\';position:absolute;left:7px;top:7px;bottom:7px;width:3px;border-radius:2px;background:var(--hx-blue);box-shadow:0 0 8px rgba(74,140,255,.5)}"',
    r'    + "\n.main-page .script-home .el-scrollbar__view>div:has(>.el-text--primary:not(.log-time)):before{background:var(--hx-cyan);box-shadow:0 0 8px rgba(56,226,255,.55)}"',
    r'    + "\n.main-page .script-home .el-scrollbar__view>div:has(>.el-text--success:not(.log-time)):before{background:#4ade80;box-shadow:0 0 8px rgba(74,222,128,.55)}"',
    r'    + "\n.main-page .script-home .el-scrollbar__view>div:has(>.el-text--warning:not(.log-time)):before{background:#ffc46b;box-shadow:0 0 8px rgba(255,196,107,.55)}"',
    r'    + "\n.main-page .script-home .el-scrollbar__view>div:has(>.el-text--danger:not(.log-time)):before{background:#ff7a7a;box-shadow:0 0 8px rgba(255,138,138,.55)}"',
    r'    + "\n.main-page .script-home .el-scrollbar__view>div:has(>.el-text--info:not(.log-time)):before{background:#7f96b8;box-shadow:none}"',
    r'    + "\n.main-page .script-home .log-time{display:inline!important;margin:0 5px 0 0!important;padding:1px 5px;border-radius:5px;background:rgba(120,190,255,.10);font-size:9.5px!important;line-height:1.5!important;letter-spacing:.3px;color:#7f9ab8!important;font-variant-numeric:tabular-nums;vertical-align:1px;white-space:nowrap}"',
    r'    + "\n.main-page .script-home .el-scrollbar__view>div>.el-text:not(.log-time){display:inline!important;padding:0!important;border:none!important;font-size:12px;line-height:1.7;letter-spacing:.1px;overflow-wrap:anywhere;word-break:break-word;vertical-align:baseline}"',
    r'    + "\n.main-page .script-home .el-scrollbar__view>div>.el-text[class=\"el-text\"]{display:none!important}"',
    r'    + "\n/* ===== 答题页空状态：图标放大 + 空白区垂直居中 ===== */"',
    r'    + "\n.main-page .el-tab-pane>div:has(>.el-empty){flex:1 1 auto!important;min-height:0!important;display:flex!important;flex-direction:column;align-items:center;justify-content:center;width:100%!important}"',
    r'    + "\n.main-page .el-empty{display:flex!important;flex-direction:column;align-items:center;justify-content:center;width:100%!important;padding:0!important;margin:0!important;box-sizing:border-box!important}"',
    r'    + "\n.main-page .el-empty__image{width:132px!important;height:132px!important;margin:0 auto!important}"',
    r'    + "\n.main-page .el-empty__description{margin-top:12px!important;width:100%!important;text-align:center!important}"',
    r'    + "\n.main-page .el-empty__description p{text-align:center!important;font-size:12.5px!important}"',
]

anchor = r'    + "\n.main-page .el-card__body,.main-page .card_content,.main-page .demo-tabs,.main-page .demo-tabs>.el-tabs__content{box-sizing:border-box!important;max-width:100%!important}"'
sub_once("CSS（通知紧凑化 + 空状态居中）", anchor, anchor + NL + NL.join(CSS))

# ---------- 6) 标签页改名（只动 label，name 是路由键不可动）----------
sub_once("标签 首页->通知", '          label: "首页",', '          label: "通知",')
sub_once("标签 答题->AI", '          label: "答题",', '          label: "AI",')
sub_once("标签 设置->配置", '          label: "设置",', '          label: "配置",')

bad = [x for x in LOG if x.startswith("!!")]
if bad:
    print(NL.join(LOG)); print("ABORT"); sys.exit(1)

shutil.copy2(P, P + ".bak-fix26")
io.open(P, "w", encoding="utf-8", newline="").write(src)
LOG.append("bytes: %d -> %d" % (orig_len, len(src)))
LOG.append("CRLF=%d bareLF=%d" % (src.count("\r\n"), src.count("\n") - src.count("\r\n")))
io.open(os.path.join(OUT, "_fix26.txt"), "w", encoding="utf-8").write(NL.join(LOG))
print("done")
