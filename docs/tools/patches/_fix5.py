# -*- coding: utf-8 -*-
import io, shutil, re

P = r"C:\Users\D_A\DoubaoWork\chats\2026-10-05\new-chat-4\海底小纵队·探矿鲸娘.user.js"
shutil.copyfile(P, P + ".bak7")
src = io.open(P, encoding="utf-8").read()
log = []

def sub1(old, new, tag, expect=1):
    global src
    n = src.count(old)
    assert n == expect, "[%s] 命中 %d 次，应为 %d" % (tag, n, expect)
    src = src.replace(old, new)
    log.append("OK  %-26s %d 处" % (tag, n))

# ── FIX 1: 模型迁移必须在 persistConfig 之前 ─────────────
old_state = """      let globalConfig = defaultConfig;
      const storedConfig = getStoredConfigText();
      if (storedConfig) {
        try {
          const parsedStoredConfig = JSON.parse(storedConfig);
          globalConfig = migrateConfig(parsedStoredConfig, defaultConfig);
        } catch (error) {
          console.error(error);
        }
      }
      persistConfig(globalConfig);
      return globalConfig;"""
new_state = """      let globalConfig = defaultConfig;
      const storedConfig = getStoredConfigText();
      if (storedConfig) {
        try {
          const parsedStoredConfig = JSON.parse(storedConfig);
          globalConfig = migrateConfig(parsedStoredConfig, defaultConfig);
        } catch (error) {
          console.error(error);
        }
      }
      sanitizeAiConfig(globalConfig);
      persistConfig(globalConfig);
      return globalConfig;"""
sub1(old_state, new_state, "FIX1 模型迁移前置")

# ── FIX 2: question_table 硬编码 625px → 自适应 ──────────
sub1(".main-page .question_table{width:625px}",
     ".main-page .question_table{width:100%;max-width:100%}",
     "FIX2 question_table 自适应")

# ── FIX 3: card_content 去掉 overflow:hidden（会裁切内容）──
sub1(".main-page .card_content{max-width:100%;overflow:hidden}",
     ".main-page .card_content{max-width:100%}",
     "FIX3 去掉裁切")

# ── FIX 4: 自诊断输出堆栈，定位 Promise 异常 ─────────────
old_rej = """  window.addEventListener("unhandledrejection", (e) => {
    box("Promise 未捕获异常", e.reason && e.reason.message ? e.reason.message : e.reason);
  });"""
new_rej = """  window.addEventListener("unhandledrejection", (e) => {
    const r = e.reason;
    const msg = r && r.message ? r.message : String(r);
    const st = r && r.stack ? "\\n" + String(r.stack).split("\\n").slice(0, 7).join("\\n") : "";
    box("Promise 未捕获异常", msg + st);
  });"""
sub1(old_rej, new_rej, "FIX4 Promise 堆栈")

old_err = """  window.addEventListener("error", (e) => {
    const where = e.filename ? " @ " + String(e.filename).split("/").pop() + ":" + e.lineno : "";
    box("脚本运行错误", (e.message || "未知错误") + where);
  });"""
new_err = """  window.addEventListener("error", (e) => {
    const where = e.filename ? " @ " + String(e.filename).split("/").pop() + ":" + e.lineno : "";
    const st = e.error && e.error.stack ? "\\n" + String(e.error.stack).split("\\n").slice(0, 7).join("\\n") : "";
    box("脚本运行错误", (e.message || "未知错误") + where + st);
  });"""
sub1(old_err, new_err, "FIX5 error 堆栈")

io.open(P, "w", encoding="utf-8", newline="").write(src)

# ── 报告 ────────────────────────────────────────────────
s = io.open(P, encoding="utf-8").read()
log.append("")
log.append("=== 核对 ===")
log.append("  sanitizeAiConfig 前置: %s" % ("OK" if "sanitizeAiConfig(globalConfig);\n      persistConfig(globalConfig);" in s else "FAIL"))
log.append("  question_table 625px 残留: %d (应 0)" % s.count("question_table{width:625px}"))
log.append("  question_table 100%%: %d" % s.count("question_table{width:100%;max-width:100%}"))
log.append("  card_content overflow:hidden 残留: %d (应 0)" % s.count("card_content{max-width:100%;overflow:hidden}"))
log.append("  堆栈上报 slice(0, 7): %d (应 2)" % s.count("slice(0, 7)"))
log.append("")

log.append("=== 面板标题来源 ===")
i = s.find('const _hoisted_2 = { class: "title" };')
log.append(s[max(0, i-300):i+200] if i != -1 else "未找到 _hoisted_2")
for m in re.finditer(r"scriptInfo\.\w+", s):
    j = m.start()
    log.append("  line %d: %s" % (s[:j].count("\n")+1, s[j-90:j+60].replace("\n", " | ")))

log.append("")
log.append("=== getScriptInfo 定义 ===")
i = s.find("const getScriptInfo")
log.append(s[i:i+400] if i != -1 else "未找到")

io.open(r"C:\Users\D_A\WorkBuddy\2026-10-05-13-53-42\_fix5.txt", "w", encoding="utf-8").write("\n".join(log))
print("ALL DONE")
