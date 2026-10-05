# -*- coding: utf-8 -*-
"""0.4.12 发布打包：生成 dist zip + SHA256SUMS.txt（可重复构建：固定 zip 时间戳）"""
import io, os, zipfile, hashlib, shutil

REPO = r"C:\Users\D_A\WorkBuddy\2026-10-05-13-53-42\repo\haiyu-zongdui-tankuangjingniang"
REPO_PARENT = r"C:\Users\D_A\WorkBuddy\2026-10-05-13-53-42\repo"
REL = os.path.join(REPO, "releases")
OUT = r"C:\Users\D_A\WorkBuddy\2026-10-05-23-01-21\_rel54.txt"
APPLY = "--apply" in os.sys.argv

NAME = "haiyu-zongdui-tankuangjingniang"
VER = "0.4.12"
ZIP_NAME = NAME + "-" + VER + ".zip"

# 打包内容：与 0.4.0 交付包同构（脚本 + 三份文档 + LICENSE + assets）
ITEMS = [
    ("海底小纵队·探矿鲸娘.user.js", "海底小纵队·探矿鲸娘.user.js"),
    ("README.md", "README.md"),
    ("CHANGELOG.md", "CHANGELOG.md"),
    ("LICENSE", "LICENSE"),
    ("assets/bg_hero.jpg", "assets/bg_hero.jpg"),
    ("assets/bg_main.jpg", "assets/bg_main.jpg"),
    ("assets/donate-alipay.jpg", "assets/donate-alipay.jpg"),
    ("assets/icon.png", "assets/icon.png"),
    ("assets/README.md", "assets/README.md"),
]

lines = []
w = lines.append

w("================ 0.4.12 发布打包 ================")
w("模式：" + ("APPLY（写入）" if APPLY else "DRY-RUN（不写入）"))
w("")

# ---- 1. 预检：所有待打包文件存在 ----
missing = 0
total_in = 0
for src_rel, _ in ITEMS:
    p = os.path.join(REPO, src_rel.replace("/", os.sep))
    if not os.path.exists(p):
        w("  [缺失] " + src_rel)
        missing += 1
    else:
        sz = os.path.getsize(p)
        total_in += sz
        w("  [OK] " + str(sz).rjust(9) + "  " + src_rel)
w("  待打包合计 " + str(total_in) + " 字节，缺失 " + str(missing))
w("")

if missing:
    w("!! 有缺失项，中止")
    with io.open(OUT, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    raise SystemExit(1)

# ---- 2. 组装 zip（固定时间戳 => 可重复构建）----
FIXED = (2026, 10, 5, 12, 0, 0)
zip_path = os.path.join(REL, ZIP_NAME)
top = NAME + "/"

if APPLY:
    os.makedirs(REL, exist_ok=True)
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for src_rel, dst_rel in ITEMS:
            src = os.path.join(REPO, src_rel.replace("/", os.sep))
            zi = zipfile.ZipInfo(top + dst_rel, date_time=FIXED)
            zi.compress_type = zipfile.ZIP_DEFLATED
            zi.external_attr = 0o644 << 16
            with open(src, "rb") as fh:
                z.writestr(zi, fh.read())
    w("  [写入] " + ZIP_NAME + "  " + str(os.path.getsize(zip_path)) + " 字节")
else:
    w("  [计划] 将写入 " + zip_path)

# ---- 3. 归档原始 0.4.0 交付包到 releases/（幂等：已在位则跳过）----
src040 = os.path.join(REPO_PARENT, NAME + "-0.4.0.zip")
dst040 = os.path.join(REL, NAME + "-0.4.0.zip")
if os.path.exists(src040):
    sz040 = os.path.getsize(src040)          # 先取大小，再搬
    if APPLY:
        os.makedirs(REL, exist_ok=True)
        shutil.move(src040, dst040)
    w("  [归位] " + NAME + "-0.4.0.zip  ->  releases/  (" + str(sz040) + " 字节)")
elif os.path.exists(dst040):
    w("  [已在位] releases/" + NAME + "-0.4.0.zip  (" + str(os.path.getsize(dst040)) + " 字节)")
else:
    w("  [跳过] 未找到 " + NAME + "-0.4.0.zip（repo 根与 releases/ 都没有）")

# ---- 4. SHA256SUMS ----
def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()

sums_path = os.path.join(REL, "SHA256SUMS.txt")
entries = []
for n in sorted(os.listdir(REL)) if os.path.isdir(REL) else []:
    if n.endswith(".zip"):
        p = os.path.join(REL, n)
        entries.append(sha(p) + "  " + n)
if APPLY:
    with io.open(sums_path, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(entries) + "\n")
w("")
w("---- releases/SHA256SUMS.txt ----")
for e in entries:
    w("  " + e)

# ---- 5. 清掉 repo 根上被取代的旧 SHA256SUMS ----
old_sums = os.path.join(REPO_PARENT, "SHA256SUMS.txt")
if os.path.exists(old_sums):
    if APPLY:
        os.remove(old_sums)
    w("")
    w("  [清理] repo/SHA256SUMS.txt（已被 releases/SHA256SUMS.txt 取代）")

w("")
w("================ 汇总 ================")
if os.path.isdir(REL):
    for n in sorted(os.listdir(REL)):
        w("  " + str(os.path.getsize(os.path.join(REL, n))).rjust(9) + "  releases/" + n)

with io.open(OUT, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))
print("ok")
