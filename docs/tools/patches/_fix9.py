# -*- coding: utf-8 -*-
"""
把 TEST 版里不存在的模型名 deepseek-v4.1-flash 全部收敛到服务端真实存在的模型。
服务端真实支持: deepseek-flash, deepseek-v4-pro
"""
import io, os, shutil, re

P = r"C:\Users\D_A\DoubaoWork\chats\2026-10-05\new-chat-4\海底小纵队·探矿鲸娘.user.js"
OUT = r"C:\Users\D_A\WorkBuddy\2026-10-05-13-53-42\_fix9.txt"
LOG = []
def w(s=""):
    LOG.append(str(s))
    print(s)

src = io.open(P, "r", encoding="utf-8", newline="").read()
orig_len = len(src)
w("原始字符数: %d" % orig_len)

# ---------- 替换表 ----------
# (说明, 旧文本, 新文本, 期望命中次数)
RULES = [
    (
        "① 默认模型 v4.1-flash -> v4-pro（服务端最强）",
        'const DEFAULT_AI_MODEL = "deepseek-v4.1-flash";',
        'const DEFAULT_AI_MODEL = "deepseek-v4-pro";',
        1,
    ),
    (
        "② 白名单收敛为服务端真实存在的 2 个模型",
        'const ALLOWED_AI_MODELS = ["deepseek-v4.1-flash", "deepseek-v4-pro", "deepseek-flash"];',
        'const ALLOWED_AI_MODELS = ["deepseek-v4-pro", "deepseek-flash"];',
        1,
    ),
    (
        "③ jsonMode 名单去掉不存在的模型（v4-pro 按 PROD 逻辑不走 json mode）",
        'const jsonModeModels = ["deepseek-v4.1-flash", "deepseek-flash"];',
        'const jsonModeModels = ["deepseek-flash"];',
        1,
    ),
    (
        "④ 下拉选项：v4.1-flash -> v4-pro，并标注为默认推荐",
        'vue.createVNode(ElOption, { value: "deepseek-v4.1-flash", label: "DeepSeek V4.1 Flash（默认·推荐·最强）" })',
        'vue.createVNode(ElOption, { value: "deepseek-v4-pro", label: "DeepSeek V4 Pro（默认·推荐·最强）" })',
        1,
    ),
    (
        "⑤ 脚本描述文案",
        'V4.1 Flash 驱动智能答题',
        'V4 Pro 驱动智能答题',
        1,
    ),
    (
        "⑥ 使用引导文案",
        '填入后模型已默认选中 <strong>V4.1 Flash</strong>，无需修改',
        '填入后模型已默认选中 <strong>V4 Pro（推荐·最强）</strong>，无需修改',
        1,
    ),
]

ok_all = True
for desc, old, new, expect in RULES:
    n = src.count(old)
    if n == expect:
        src = src.replace(old, new)
        w("[OK ] %s  命中 %d" % (desc, n))
    else:
        ok_all = False
        w("[!! ] %s  期望 %d 实际 %d  << 未替换" % (desc, expect, n))

# ---------- 兜底：清剿所有残留 ----------
leftover = src.count("deepseek-v4.1-flash")
leftover_txt = src.count("V4.1 Flash")
w("")
w("残留 deepseek-v4.1-flash: %d" % leftover)
w("残留 V4.1 Flash 文案: %d" % leftover_txt)

if leftover or leftover_txt:
    ok_all = False
    w("!! 仍有残留，未写回磁盘")
else:
    # 备份
    bak = P + ".bak10"
    shutil.copy2(P, bak)
    w("备份 -> %s" % os.path.basename(bak))
    with io.open(P, "w", encoding="utf-8", newline="") as f:
        f.write(src)
    w("写回完成: %d -> %d" % (orig_len, len(src)))

# ---------- 复核清单 ----------
w("")
w("=== 复核：模型相关字面量计数 ===")
for tok in ["deepseek-v4-pro", "deepseek-flash", "deepseek-v4.1-flash",
            "deepseek-chat", "DEFAULT_AI_MODEL", "ALLOWED_AI_MODELS"]:
    w("  %-22s x%d" % (tok, src.count(tok)))

w("")
w("=== 复核：关键行原文 ===")
for pat in [r'const DEFAULT_AI_MODEL = .*?;',
            r'const ALLOWED_AI_MODELS = .*?;',
            r'const jsonModeModels = .*?;']:
    m = re.search(pat, src)
    w("  " + (m.group(0) if m else "!! 未找到 " + pat))
for m in re.finditer(r'ElOption, \{ value: "deepseek[^"]*", label: "[^"]*" \}', src):
    w("  " + m.group(0))
for m in re.finditer(r'const model = ALLOWED_AI_MODELS[^;]*;', src):
    w("  " + m.group(0))

w("")
w("ALL_RULES_OK = %s" % ok_all)

with io.open(OUT, "w", encoding="utf-8") as f:
    f.write("\n".join(LOG))
