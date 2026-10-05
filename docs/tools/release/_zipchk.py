# -*- coding: utf-8 -*-
"""校验发布 zip：条目名、内嵌 .user.js 字节/行尾哈希是否与源文件逐字节一致"""
import io, os, zipfile, hashlib

REPO = r"C:\Users\D_A\WorkBuddy\2026-10-05-13-53-42\repo\haiyu-zongdui-tankuangjingniang"
ZIP = os.path.join(REPO, "releases", "haiyu-zongdui-tankuangjingniang-0.4.12.zip")
OUT = r"C:\Users\D_A\WorkBuddy\2026-10-05-23-01-21\_zipchk.txt"

lines = []
w = lines.append
w("================ 发布包校验 ================")
w("包体 = " + ZIP)
w("")

fails = 0

def ck(label, got, exp):
    global fails
    ok = (got == exp)
    if not ok:
        fails += 1
    w(("  [OK] " if ok else "  [NG] ") + label + "   got=" + str(got) + " exp=" + str(exp))

with zipfile.ZipFile(ZIP) as z:
    names = z.namelist()
    w("---- 条目（" + str(len(names)) + " 个）----")
    for n in names:
        w("  " + str(z.getinfo(n).file_size).rjust(9) + "  " + n)
    w("")

    # 1. UTF-8 文件名标志位（flag_bits & 0x800）—— 中文名不能靠 codepage 猜
    zh = [n for n in names if "探矿鲸娘" in n]
    ck("中文条目名按 UTF-8 编码存储（flag 0x800）", all(z.getinfo(n).flag_bits & 0x800 for n in zh), True)
    ck("脚本条目名唯一且无乱码副本", len([n for n in names if n.endswith(".user.js")]), 1)

    # 2. 内嵌 .user.js 与源文件逐字节一致
    inner = z.read(names[0]) if names[0].endswith(".user.js") else z.read([n for n in names if n.endswith(".user.js")][0])
    src_p = os.path.join(REPO, "海底小纵队·探矿鲸娘.user.js")
    src = open(src_p, "rb").read()
    ck("内嵌脚本 字节数 = 源文件", len(inner), len(src))
    ck("内嵌脚本 SHA256 = 源文件",
       hashlib.sha256(inner).hexdigest(), hashlib.sha256(src).hexdigest())
    s = inner.decode("utf-8")
    ck("内嵌脚本 裸 LF = 0", s.count("\n") - s.count("\r\n"), 0)
    ck("内嵌脚本 @version 为 0.4.12", ("// @version      0.4.12" in s) or ("@version" in s and "0.4.12" in s.split("@version")[1][:40]), True)

    # 3. 顶层目录名规范（zip 根只有一个文件夹）
    tops = set(n.split("/")[0] for n in names)
    ck("zip 根目录唯一", len(tops), 1)
    ck("zip 根目录名 = haiyu-zongdui-tankuangjingniang", list(tops)[0], "haiyu-zongdui-tankuangjingniang")

    # 4. 与源文件逐项字节一致（全部条目）
    import posixpath
    bad = []
    for n in names:
        rel = n.split("/", 1)[1] if "/" in n else n
        sp = os.path.join(REPO, rel.replace("/", os.sep))
        if not os.path.exists(sp):
            bad.append(n + "(源缺失)")
        elif z.read(n) != open(sp, "rb").read():
            bad.append(n + "(字节不符)")
    ck("全部条目与源文件逐字节一致", bad, [])

w("")
w("==========================================")
w("结论：" + ("全部通过（fail=0）" if fails == 0 else "存在失败项 fail=" + str(fails)))
with io.open(OUT, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))
print("ok fails=" + str(fails))
