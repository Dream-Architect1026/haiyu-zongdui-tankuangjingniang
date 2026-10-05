# -*- coding: utf-8 -*-
"""
最终收敛：
  - 默认模型 = deepseek-flash（用户明确要求）
  - 白名单 = 服务端真实存在的 [deepseek-flash, deepseek-v4-pro]
  - 删除重复的 deepseek-v4-pro 选项
  - label / 文案 与"默认 Flash"一致
"""
import io, os, shutil, re

P = r"C:\Users\D_A\DoubaoWork\chats\2026-10-05\new-chat-4\海底小纵队·探矿鲸娘.user.js"
OUT = r"C:\Users\D_A\WorkBuddy\2026-10-05-13-53-42\_fix10.txt"
LOG = []
def w(s=""):
    LOG.append(str(s)); print(s)

src = io.open(P, "r", encoding="utf-8", newline="").read()
orig_len = len(src)
w("原始字符数: %d" % orig_len)
w("")

# ---------- 替换表：(说明, 旧, 新, 期望次数) ----------
RULES = [
    ("① 默认模型 -> deepseek-flash（用户指定）",
     'const DEFAULT_AI_MODEL = "deepseek-v4-pro";',
     'const DEFAULT_AI_MODEL = "deepseek-flash";', 1),

    ("② 白名单顺序：flash 置首",
     'const ALLOWED_AI_MODELS = ["deepseek-v4-pro", "deepseek-flash"];',
     'const ALLOWED_AI_MODELS = ["deepseek-flash", "deepseek-v4-pro"];', 1),

    ("③ 删除重复的 v4-pro 选项行",
     ',\n                vue.createVNode(ElOption, { value: "deepseek-v4-pro", label: "DeepSeek V4 Pro" })',
     '', 1),

    ("④ v4-pro label 去掉「默认」字样",
     'vue.createVNode(ElOption, { value: "deepseek-v4-pro", label: "DeepSeek V4 Pro（默认·推荐·最强）" })',
     'vue.createVNode(ElOption, { value: "deepseek-v4-pro", label: "DeepSeek V4 Pro（最强）" })', 1),

    ("⑤ flash label 标为默认推荐 + 去掉不存在的 V4 档位暗示",
     'vue.createVNode(ElOption, { value: "deepseek-flash", label: "DeepSeek V4 Flash（快）" })',
     'vue.createVNode(ElOption, { value: "deepseek-flash", label: "DeepSeek Flash（默认·推荐）" })', 1),

    ("⑥ 脚本描述文案",
     'V4 Pro 驱动智能答题',
     'Flash 驱动智能答题', 1),

    ("⑦ 使用引导文案",
     '填入后模型已默认选中 <strong>V4 Pro（推荐·最强）</strong>，无需修改',
     '填入后模型已默认选中 <strong>Flash（默认·推荐）</strong>，无需修改', 1),
]

ok = True
for desc, old, new, expect in RULES:
    n = src.count(old)
    if n == expect:
        src = src.replace(old, new)
        w("[OK ] %s  命中 %d" % (desc, n))
    else:
        ok = False
        w("[!! ] %s  期望 %d 实际 %d  << 未替换" % (desc, expect, n))

# ---------- 兜底检查 ----------
w("")
for tok in ["deepseek-v4.1-flash", "deepseek-chat", "V4.1", "V4 Flash"]:
    w("  残留 %-20s x%d" % (tok, src.count(tok)))

opts = re.findall(r'ElOption, \{ value: "([^"]*)", label: "([^"]*)" \}', src)
vals = [v for v, _ in opts]
dup_ok = len(vals) == len(set(vals))
w("  选项唯一性: %s" % ("OK" if dup_ok else "!! 重复"))

if not ok or not dup_ok:
    w("")
    w("!! 存在问题，未写回磁盘")
else:
    bak = P + ".bak11"
    shutil.copy2(P, bak)
    w("")
    w("备份 -> %s" % os.path.basename(bak))
    with io.open(P, "w", encoding="utf-8", newline="") as f:
        f.write(src)
    w("写回完成: %d -> %d" % (orig_len, len(src)))

# ---------- 复核 ----------
w("")
w("=== 复核：ElOption 清单 ===")
for v, l in opts:
    w("  value=%-18s label=%s" % (v, l))

w("")
w("=== 复核：模型常量 ===")
for pat in [r'const DEFAULT_AI_MODEL = .*?;',
            r'const ALLOWED_AI_MODELS = .*?;',
            r'const jsonModeModels = .*?;',
            r'const model = ALLOWED_AI_MODELS[^;]*;']:
    m = re.search(pat, src)
    w("  " + (m.group(0) if m else "!! " + pat))

w("")
w("=== 复核：三处默认值一致性 ===")
w("  DEFAULT_AI_MODEL        : %s" % re.search(r'const DEFAULT_AI_MODEL = "(.*?)";', src).group(1))
m2 = re.search(r'ai: \{\s*deepseek: \{ apiKey: "", model: "([^"]*)"', src)
w("  defaultConfig 内硬编码   : %s" % (m2.group(1) if m2 else "(无硬编码，走 DEFAULT_AI_MODEL)"))

w("")
w("ALL_OK = %s" % (ok and dup_ok))
with io.open(OUT, "w", encoding="utf-8") as f:
    f.write("\n".join(LOG))
