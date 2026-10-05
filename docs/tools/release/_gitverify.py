# -*- coding: utf-8 -*-
"""验证 git 仓库内的 .user.js 仍是逐字节 CRLF：对象层 + git archive 导出层"""
import hashlib, io, os, subprocess, zipfile

REPO = r"C:\Users\D_A\WorkBuddy\2026-10-05-13-53-42\repo\haiyu-zongdui-tankuangjingniang"
NAME = "海底小纵队·探矿鲸娘.user.js"
OUT = r"C:\Users\D_A\WorkBuddy\2026-10-05-23-01-21\_gitverify.txt"
ARCH = r"C:\Users\D_A\WorkBuddy\2026-10-05-23-01-21\_gitarc.zip"

EXPECT = "db08cb4244cfc7d14762f20f932d47d380eb3a4fdc80b42429fcc263b56098ee"
EXPECT_BYTES = 639440
EXPECT_CRLF = 8965

lines = []
def w(s): lines.append(s)
fails = 0
def ck(label, got, exp):
    global fails
    ok = got == exp
    if not ok: fails += 1
    w(("  [OK] " if ok else "  [NG] ") + label + "   got=" + str(got) + " exp=" + str(exp))

def stats(b):
    s = b.decode("utf-8")
    crlf = s.count("\r\n")
    return len(b), crlf, s.count("\n") - crlf, hashlib.sha256(b).hexdigest()

def run(args):
    return subprocess.run(args, cwd=REPO, capture_output=True).stdout

w("================ git 内 CRLF 一致性验证 ================")
w("")

# ---- 1. 工作区文件（基准）----
wb = open(os.path.join(REPO, NAME), "rb").read()
n, crlf, bare, sha = stats(wb)
w("---- 1. 工作区文件（基准）----")
ck("字节", n, EXPECT_BYTES); ck("CRLF", crlf, EXPECT_CRLF); ck("裸 LF", bare, 0); ck("SHA256", sha, EXPECT)
w("")

# ---- 2. git 对象层（blob）----
w("---- 2. git 对象层：cat-file blob HEAD:<file> ----")
blob = run(["git", "cat-file", "blob", "HEAD:" + NAME])
n2, crlf2, bare2, sha2 = stats(blob)
ck("字节", n2, EXPECT_BYTES); ck("CRLF", crlf2, EXPECT_CRLF); ck("裸 LF", bare2, 0); ck("SHA256", sha2, EXPECT)
w("")

# ---- 3. git archive 导出层（等价于平台"下载 zip"）----
w("---- 3. git archive 导出层：git archive --format=zip ----")
if os.path.exists(ARCH):
    os.remove(ARCH)
subprocess.run(["git", "archive", "--format=zip", "-o", ARCH, "HEAD"], cwd=REPO, capture_output=True)
if os.path.exists(ARCH):
    with zipfile.ZipFile(ARCH) as z:
        names = z.namelist()
        # 精确匹配仓库根目录那一份（docs/repro 与 docs/versions 下另有同名/近名副本）
        hit = [x for x in names if x == NAME]
        if hit:
            inner = z.read(hit[0])
            n3, crlf3, bare3, sha3 = stats(inner)
            w("  导出包内条目：" + hit[0])
            ck("字节", n3, EXPECT_BYTES); ck("CRLF", crlf3, EXPECT_CRLF); ck("裸 LF", bare3, 0); ck("SHA256", sha3, EXPECT)
        else:
            w("  [NG] 导出包内未找到根目录脚本条目（候选 " + str([x for x in names if x.endswith('.user.js')]) + "）")
            fails += 1
    w("  导出包字节 = " + str(os.path.getsize(ARCH)))
else:
    w("  [NG] git archive 未产出文件"); fails += 1
w("")

# ---- 3b. 仓库内全部 .user.js 的行尾普查 ----
#      约束适用范围（本报告予以精确界定）：
#        · 发布件 = 仓库根 + docs/versions/  -> 必须 CRLF、裸 LF 为 0（硬校验）
#        · 工装件 = docs/bisect/ + docs/repro/ -> 当年二分定位与复现用的本地候选，
#          按"不篡改历史证据"原则保留原貌，其 LF 不计入失败
w("---- 3b. 仓库内全部 .user.js 行尾普查 ----")
HARD = ("海底小纵队·探矿鲸娘.user.js", "docs/versions/")
def is_release(rel):
    return rel in HARD or rel.startswith("docs/versions/")
n_rel = n_fix = 0
for root, dirs, fs in os.walk(REPO):
    if ".git" in root.split(os.sep):
        continue
    for fn in sorted(fs):
        if not fn.endswith(".user.js"):
            continue
        p = os.path.join(root, fn)
        rel = os.path.relpath(p, REPO).replace(os.sep, "/")
        b = open(p, "rb").read()
        nn, cc, bb, ss = stats(b)
        rel_flag = is_release(rel)
        kind = "发布件（必须 CRLF）" if rel_flag else "工装件（保留原貌）"
        w("  " + ("● " if rel_flag else "○ ") + rel.ljust(50) + " bytes=" + str(nn).rjust(7)
          + " CRLF=" + str(cc).rjust(5) + " 裸LF=" + str(bb).rjust(5) + "  " + kind)
        if rel_flag:
            n_rel += 1
            if bb != 0:
                fails += 1
                w("     !! 发布件存在裸 LF")
        else:
            n_fix += 1
w("  小计：发布件 " + str(n_rel) + " 个（全部硬校验），工装件 " + str(n_fix) + " 个（保留原貌）")
w("")

# ---- 4. 九个历史快照在对象层是否也是 CRLF ----
w("---- 4. 历史版本快照（对象层逐字节）----")
for v in sorted(os.listdir(os.path.join(REPO, "docs", "versions"))):
    p = "docs/versions/" + v
    b = run(["git", "cat-file", "blob", "HEAD:" + p])
    on_disk = open(os.path.join(REPO, "docs", "versions", v), "rb").read()
    ck(v + " 与工作区逐字节一致且无裸 LF", (b == on_disk, stats(b)[2]), (True, 0))
w("")
w("======================================================")
w("结论：" + ("仓库内脚本为逐字节 CRLF，可安全分发（fail=0）" if fails == 0 else "存在失败项 fail=" + str(fails)))
with io.open(OUT, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))
print("ok fails=" + str(fails))
