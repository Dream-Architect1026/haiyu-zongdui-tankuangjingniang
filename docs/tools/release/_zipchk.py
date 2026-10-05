# -*- coding: utf-8 -*-
"""校验发布 zip：条目名、内嵌 .user.js 字节/行尾/哈希是否与源文件逐字节一致。

设计要点（都是前几轮踩出来的）：
  · 路径全部由 __file__ 推导并断言 —— 本文件位于 <repo>/docs/tools/release/，
    上溯 4 级才是仓库根；层级算错立刻报错，不静默跑在错目录
  · 报告写回仓库 docs/reports/，不落在临时工作区（否则散件一清理，凭据就丢）
  · 期望版本号从**发布包文件名**推出，不写死 —— 换版本时无需改脚本
  · 全局崩溃兜底：任何异常也先把已收集的结果落盘再退出

用法：
    python _zipchk.py                        # 自动选 releases/ 下最新版本包
    python _zipchk.py <某个发布包.zip>

产出：docs/reports/_zipchk.txt
退出码：0 = 全部通过；1 = 有失败项
"""
import hashlib
import io
import os
import re
import sys
import zipfile

SELF = os.path.abspath(__file__)
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(SELF))))
NAME = "海底小纵队·探矿鲸娘.user.js"
REL_DIR = os.path.join(REPO, "releases")
OUT = os.path.join(REPO, "docs", "reports", "_zipchk.txt")

assert os.path.isfile(os.path.join(REPO, NAME)), \
    "仓库根解析错误：未在 " + REPO + " 找到 " + NAME

L = []
fails = 0


def w(s=""):
    L.append(str(s))


def dash(v):
    return "".join(c for c in v if c.isdigit() or c == ".")


def pick_zip():
    """选最新版本的发布包：从文件名里的版本号按数值排序"""
    if len(sys.argv) > 1:
        return sys.argv[1]
    if not os.path.isdir(REL_DIR):
        return ""
    cands = [f for f in os.listdir(REL_DIR) if f.endswith(".zip")]

    def vkey(fn):
        m = re.findall(r"(\d+\.\d+(?:\.\d+)?)", fn)
        if not m:
            return (0,)
        parts = [int(x) for x in dash(m[-1]).rstrip(".").split(".") if x != ""]
        return tuple(parts) or (0,)

    if not cands:
        return ""
    cands.sort(key=vkey)
    return os.path.join(REL_DIR, cands[-1])


def main():
    global fails
    zip_p = pick_zip()

    w("================ 发布包校验 ================")
    w("包体 = " + (zip_p or "(未找到)"))
    w("")

    if not zip_p or not os.path.isfile(zip_p):
        w("[NG] 发布包不存在")
        fails += 1
        end()
        return 1

    # 期望版本号由包名推出 —— 换版本不用改脚本
    m = re.findall(r"(\d+\.\d+(?:\.\d+)?)", os.path.basename(zip_p))
    exp_ver = m[-1] if m else ""
    w("包名推出的版本号 = " + (exp_ver or "(无)"))
    w("")

    def ck(label, got, exp):
        global fails
        ok = (got == exp)
        if not ok:
            fails += 1
        w(("  [OK] " if ok else "  [NG] ") + label
          + "   got=" + str(got) + " exp=" + str(exp))

    try:
        zf = zipfile.ZipFile(zip_p)
    except zipfile.BadZipFile as e:
        w("[NG] 无法作为 zip 打开：" + str(e))
        fails += 1
        end()
        return 1

    with zf as z:
        names = z.namelist()
        w("---- 条目（" + str(len(names)) + " 个）----")
        for n in names:
            w("  " + str(z.getinfo(n).file_size).rjust(9) + "  " + n)
        w("")

        # 1. UTF-8 文件名标志位（flag_bits & 0x800）—— 中文名不能靠 codepage 猜
        zh = [n for n in names if "探矿鲸娘" in n]
        ck("中文条目名非空", len(zh) > 0, True)
        ck("中文条目名按 UTF-8 编码存储（flag 0x800）",
           all(z.getinfo(n).flag_bits & 0x800 for n in zh) if zh else False, True)
        scripts = [n for n in names if n.endswith(".user.js")]
        ck("脚本条目数 = 1（唯一且无乱码副本）", len(scripts), 1)

        # 2. 内嵌 .user.js 与源文件逐字节一致
        if not scripts:
            w("[NG] 包内没有 .user.js，后续校验跳过")
            fails += 1
            end()
            return 1
        inner = z.read(scripts[0])
        src_p = os.path.join(REPO, NAME)
        src = open(src_p, "rb").read()
        ck("内嵌脚本 字节数 = 源文件", len(inner), len(src))
        ck("内嵌脚本 SHA256 = 源文件",
           hashlib.sha256(inner).hexdigest(), hashlib.sha256(src).hexdigest())
        s = inner.decode("utf-8")
        ck("内嵌脚本 裸 LF = 0", s.count("\n") - s.count("\r\n"), 0)
        if exp_ver:
            ck("内嵌脚本 @version = " + exp_ver, exp_ver in s[:400], True)
        else:
            w("  [注意] 未能从包名推出版本号，跳过 @version 断言")

        # 3. 顶层目录名规范（zip 根只有一个文件夹）
        tops = sorted(set(n.split("/")[0] for n in names))
        ck("zip 根目录唯一", len(tops), 1)
        if len(tops) == 1:
            ck("zip 根目录名 = haiyu-zongdui-tankuangjingniang",
               tops[0], "haiyu-zongdui-tankuangjingniang")

        # 4. 全部条目与源文件逐字节一致
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
    end()
    return 0 if fails == 0 else 1


def end():
    w("==========================================")
    w("结论：" + ("全部通过（fail=0）" if fails == 0 else "存在失败项 fail=" + str(fails)))
    try:
        os.makedirs(os.path.dirname(OUT), exist_ok=True)
        with io.open(OUT, "w", encoding="utf-8", newline="\n") as f:
            f.write("\n".join(L) + "\n")
    except OSError as e:
        sys.stderr.write("报告写入失败：" + str(e) + "\n")
    print("ok fails=" + str(fails))
    print("[报告] " + OUT)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:      # 崩溃兜底：报告也要落地，否则等于没跑
        import traceback
        w("")
        w("[NG] 脚本异常：" + str(e))
        w(traceback.format_exc())
        fails += 1
        end()
        sys.exit(1)
