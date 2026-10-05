# -*- coding: utf-8 -*-
"""收尾：重写归档清单（含未及压缩即被删的 46 项）+ 清掉剩余散件

事故说明：本轮的整理脚本被重复执行了两次，第一次执行在"压缩留底"之后、
"删散件"中途崩溃，且第二次执行把第一次的留底包与清单**原地覆盖**，
导致那 46 个散件只剩清单可查、包体已丢。此脚本把这段事实写进清单，不留假象。
"""
import io, os, json, zipfile, hashlib, shutil

WS2 = r"C:\Users\D_A\WorkBuddy\2026-10-05-23-01-21"
REPO = r"C:\Users\D_A\WorkBuddy\2026-10-05-13-53-42\repo\haiyu-zongdui-tankuangjingniang"
ARCHIVE = os.path.join(REPO, "archive")
JUNK_ZIP = os.path.join(ARCHIVE, "_junk-round4-2026-10-05.zip")
MANIFEST = os.path.join(ARCHIVE, "_manifest-round4.json")
OUT = os.path.join(WS2, "_fin54.txt")
APPLY = "--apply" in os.sys.argv

# 已压缩留底的 41 项（在留底包内）
# 未及压缩即被删的 46 项：名称 + 当时的字节数
LOST = {
    "A": [
        ("_bak_0411.user.js", 640151, "与 docs/versions/v0.4.11.user.js 逐字节相同，另有权威副本"),
        ("_chain54.js", 1147, "已镜像 -> docs/tools/release/_chain54.js"),
        ("_chain54.txt", 1395, "已镜像 -> docs/reports/_chain54.txt"),
        ("_dbg54.js", 2132, "验收脚本抽块调试"),
        ("_dbg54.txt", 607, ""),
        ("_f54out.txt", 3040, "已镜像 -> docs/reports/_f54out.txt"),
        ("_find040.mjs", 2004, "定位 0.4.0 快照"),
        ("_find040.txt", 37733, ""),
        ("_ls_now.txt", 1154, ""),
        ("_ocr2235.py", 2373, "截图 OCR"),
        ("_ocr2235.txt", 2314, ""),
        ("_pack3.mjs", 6313, "上一轮仓库重建脚本"),
        ("_pack3.txt", 3666, ""),
        ("_pack3_stdout.txt", 105, ""),
        ("_recent_img.txt", 1061, ""),
        ("_recentimg.mjs", 1521, ""),
        ("_sess.mjs", 1180, "会话记录提取"),
        ("_sess.txt", 8256, ""),
        ("_sess2.mjs", 1119, ""),
        ("_sess2.txt", 6717, ""),
        ("_sess3.mjs", 1416, ""),
        ("_sess3.txt", 5852, ""),
        ("_ubarcss2.mjs", 1291, "面板 CSS 提取"),
        ("_ubarcss2.txt", 10949, ""),
        ("_ubarcss3.mjs", 755, ""),
        ("_ubarcss3.txt", 5335, ""),
        ("_v54out.txt", 4512, "已镜像 -> docs/reports/_v54out.txt"),
    ],
    "B": [
        ("_big.txt", 100200, "大文件写入探针"),
        ("_big2.txt", 70888, ""),
        ("_bigout.txt", 304, ""),
        ("_bigtest.py", 458, ""),
        ("_chainrun.txt", 15, ""),
        ("_cnt.txt", 194, "目录计数"),
        ("_db.py", 2380, "workbuddy.db 读取探针"),
        ("_db.txt", 2604, ""),
        ("_db2.py", 814, ""),
        ("_db2.txt", 27703, ""),
        ("_diag.py", 2525, "会话诊断导出"),
        ("_diag.txt", 63, ""),
        ("_diag2.txt", 86999, ""),
        ("_find_zip.txt", 1921, "查找历史发布包"),
        ("_gitchk.txt", 176, "git/归档状态检查"),
        ("_hash54.txt", 367, "四副本哈希比对（其结论已并入 docs/reports/_chain54.txt）"),
        ("_msgs.py", 2714, "会话消息提取"),
        ("_msgs.txt", 95259, ""),
        ("_msgs_end.txt", 54537, ""),
    ],
}

lines = []
def w(s): lines.append(s)
fails = 0

w("================ 第四轮收尾 ================")
w("模式：" + ("APPLY（写入）" if APPLY else "DRY-RUN（不写入）"))
w("")

# ---- 1. 从留底包重建"已归档"部分 ----
w("---- 1. 留底包内的条目（逐个复算 SHA256）----")
archived = []
if os.path.exists(JUNK_ZIP):
    with zipfile.ZipFile(JUNK_ZIP) as z:
        ok = z.testzip()
        if ok:
            w("  [NG] 包内坏项：" + str(ok)); fails += 1
        for n in z.namelist():
            data = z.read(n)
            archived.append({
                "arcname": n,
                "name": n.split("/", 1)[-1],
                "bytes": len(data),
                "sha256": hashlib.sha256(data).hexdigest(),
            })
    w("  留底包 " + os.path.basename(JUNK_ZIP) + "：" + str(len(archived)) + " 项，" + str(os.path.getsize(JUNK_ZIP)) + " 字节")
else:
    w("  [缺失] 留底包不存在：" + JUNK_ZIP); fails += 1
w("")

# ---- 2. 重写清单 ----
n_lost = sum(len(v) for v in LOST.values())
manifest = {
    "generated": "2026-10-05",
    "round": 4,
    "purpose": "第四轮（0.4.12）整理留底。散件均为一次性脚手架/中间输出，不含交付物。",
    "workspaces": {"A": r"C:\Users\D_A\WorkBuddy\2026-10-05-13-53-42",
                   "B": WS2},
    "archived_zip": os.path.basename(JUNK_ZIP),
    "archived_count": len(archived),
    "archived_entries": archived,
    "lost_count": n_lost,
    "lost_entries": [
        {"ws": ws, "name": n, "bytes": sz, "note": note}
        for ws, items in LOST.items() for (n, sz, note) in items
    ],
    "incident": {
        "what": "整理脚本被重复执行两次；第一次在删除阶段中途崩溃，第二次把留底包与清单原地覆盖。",
        "impact": "46 个散件（A 区 27 + B 区 19）未及压缩即被删除；包体与其 SHA256 不可再得，仅存本清单中的名称与字节数。",
        "loss_assessment": "无交付物损失：其中 4 份关键凭据（_v54out / _f54out / _chain54 / _bak_0411）在别处已有权威副本；其余为一次性诊断脚本与中间输出。",
        "fix_for_next_round": [
            "留底包名带唯一后缀（时间/序号），永不原地覆盖",
            "清单先落盘，再执行删除",
            "删除循环逐项记录已完成/待完成，支持断点续跑",
            "一次运行只允许执行一次；重跑前先检查目标是否已存在"
        ]
    },
    "carried_over_archives": ["_junk-removed-2026-10-05.zip"],
}
w("---- 2. 重写清单 ----")
w("  已归档 " + str(len(archived)) + " 项 + 未及归档 " + str(n_lost) + " 项 = " + str(len(archived) + n_lost) + " 项")
if APPLY:
    with io.open(MANIFEST, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
    w("  [写入] " + os.path.basename(MANIFEST) + "  " + str(os.path.getsize(MANIFEST)) + " 字节")
w("")

# ---- 3. 清掉剩余散件（含 _dbtmp 与本轮脚本）----
w("---- 3. 清理剩余散件 ----")
KEEP = {"_fin54.py", "_fin54.txt", "_fin54_run.txt"}
targets = []
for n in sorted(os.listdir(WS2)):
    p = os.path.join(WS2, n)
    if os.path.isfile(p) and n.startswith("_") and n not in KEEP:
        targets.append(p)
dirs = [os.path.join(WS2, "_dbtmp")]

w("  待删文件 " + str(len(targets)) + " 个，待删目录 " + str(len(dirs)) + " 个")
if APPLY and fails == 0:
    done = 0
    for p in targets:
        try:
            os.remove(p); done += 1
        except OSError as e:
            w("  [跳过] " + os.path.basename(p) + "：" + str(e)); fails += 1
    for d in dirs:
        if os.path.isdir(d):
            shutil.rmtree(d); w("  已删目录 " + os.path.basename(d))
    w("  已删除文件 " + str(done) + " 个")
else:
    w("  （未执行）")
w("")

w("---- 4. 清理后现状 ----")
for label, root in (("A 工作区", r"C:\Users\D_A\WorkBuddy\2026-10-05-13-53-42"), ("B 工作区", WS2)):
    w("  " + label + "：")
    for n in sorted(os.listdir(root)):
        p = os.path.join(root, n)
        w("    " + ("[D] " if os.path.isdir(p) else str(os.path.getsize(p)).rjust(9) + " ") + n)
w("  repo/archive/：")
for n in sorted(os.listdir(ARCHIVE)):
    w("    " + str(os.path.getsize(os.path.join(ARCHIVE, n))).rjust(9) + "  " + n)
w("")
w("==========================================")
w("结论：" + ("完成（fail=0）" if fails == 0 else "有失败项 fail=" + str(fails)))

with io.open(OUT, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))
print("ok fails=" + str(fails))
