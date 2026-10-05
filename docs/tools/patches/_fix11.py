# -*- coding: utf-8 -*-
"""
一次性迁移：让历史配置里的模型也落到 deepseek-flash 默认。
用 GM 存储做独立标记，只生效一次，之后用户手动选 v4-pro 不会被覆盖。
"""
import io, os, shutil, re

P = r"C:\Users\D_A\DoubaoWork\chats\2026-10-05\new-chat-4\海底小纵队·探矿鲸娘.user.js"
OUT = r"C:\Users\D_A\WorkBuddy\2026-10-05-13-53-42\_fix11.txt"
LOG = []
def w(s=""):
    LOG.append(str(s)); print(s)

src = io.open(P, "r", encoding="utf-8", newline="").read()
orig_len = len(src)

# 探测脚本里 GM 存储 API 的实际别名
g = "_GM_getValue" if "_GM_getValue(" in src else "GM_getValue"
s = "_GM_setValue" if "_GM_setValue(" in src else "GM_setValue"
w("GM API 别名: get=%s  set=%s" % (g, s))
w("")

old = ('    if (!ALLOWED_AI_MODELS.includes(ai.deepseek.model)) '
       'ai.deepseek.model = DEFAULT_AI_MODEL;\n  };')

new = ('    if (!ALLOWED_AI_MODELS.includes(ai.deepseek.model)) '
       'ai.deepseek.model = DEFAULT_AI_MODEL;\n'
       '    if (!%s("hx_ai_model_default_migrated_v1", false)) {\n'
       '      ai.deepseek.model = DEFAULT_AI_MODEL;\n'
       '      %s("hx_ai_model_default_migrated_v1", true);\n'
       '    }\n'
       '  };') % (g, s)

n = src.count(old)
if n == 1:
    src = src.replace(old, new)
    w("[OK ] ① 插入一次性迁移（首启落到 Flash，之后尊重手动选择）  命中 1")
else:
    w("[!! ] ① 目标段未唯一命中，实际 %d  << 未写回" % n)

if n == 1:
    bak = P + ".bak12"
    shutil.copy2(P, bak)
    w("备份 -> %s" % os.path.basename(bak))
    with io.open(P, "w", encoding="utf-8", newline="") as f:
        f.write(src)
    w("写回完成: %d -> %d" % (orig_len, len(src)))

# ---- 复核 ----
w("")
w("=== 复核：sanitizeAiConfig 全文 ===")
m = re.search(r'const sanitizeAiConfig = \(store\) => \{[\s\S]*?\n  \};', src)
w(m.group(0) if m else "!! 未匹配")

w("")
w("=== 复核：默认模型三处 ===")
for pat, name in [
    (r'const DEFAULT_AI_MODEL = "(.*?)";', "DEFAULT_AI_MODEL"),
    (r'const ALLOWED_AI_MODELS = (\[.*?\]);', "ALLOWED_AI_MODELS"),
    (r'const jsonModeModels = (\[.*?\]);', "jsonModeModels"),
]:
    mm = re.search(pat, src)
    w("  %-18s %s" % (name, mm.group(1) if mm else "!! 未找到"))

w("")
w("OK = %s" % (n == 1))
with io.open(OUT, "w", encoding="utf-8") as f:
    f.write("\n".join(LOG))
