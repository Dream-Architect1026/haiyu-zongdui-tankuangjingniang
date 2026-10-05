# -*- coding: utf-8 -*-
"""一站式核对 releases/SHA256SUMS.txt：逐项重算哈希并与清单比对。

不依赖 `sha256sum`（Windows 上不一定有），路径与输出目录均由 __file__ 推导。
同时把每个 `.user.js` 的字节数与裸 LF 数一并列出——**字节数漂移几乎总意味着
行尾被改**（CRLF→LF 会让文件瘦一圈），这是光比对哈希之外的第二道保险。

用法：
    python _verify_sums.py

退出码：0 = 全部一致；1 = 有缺失或不一致
"""
import hashlib
import io
import os
import sys

SELF = os.path.abspath(__file__)
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(SELF))))
SUMS = os.path.join(REPO, "releases", "SHA256SUMS.txt")
OUT = os.path.join(REPO, "docs", "reports", "_sumsout.txt")

assert os.path.isdir(os.path.join(REPO, "docs")), \
    "仓库根解析错误：未在 " + REPO + " 找到 docs/"

L = []
fails = 0


def w(s=""):
    L.append(s)


def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def eol(b):
    crlf = b.count(b"\r\n")
    lf = b.count(b"\n") - crlf
    return crlf, lf


def main():
    global fails
    w("================ SHA256SUMS 核对 ================")
    w("清单 = " + SUMS)
    w("仓库根 = " + REPO)

    if not os.path.isfile(SUMS):
        w("[NG] 清单不存在")
        flush(1)
        return 1

    with io.open(SUMS, encoding="utf-8") as f:
        lines = f.read().splitlines()

    entries = []
    for idx, ln in enumerate(lines, 1):
        if not ln.strip() or ln.lstrip().startswith("#"):
            continue
        parts = ln.split("  ", 1)
        if len(parts) != 2:
            w("[NG] 第 " + str(idx) + " 行格式非法：" + ln)
            fails += 1
            continue
        entries.append((parts[0].strip(), parts[1].strip()))

    w("条目数 = " + str(len(entries)))
    w("")
    w("---- 逐项核对 ----")

    n_userjs = 0
    for want, rel in entries:
        p = os.path.join(REPO, rel.replace("/", os.sep))
        if not os.path.isfile(p):
            w("  [NG] 缺失  " + rel)
            fails += 1
            continue
        got = sha256(p)
        size = os.path.getsize(p)
        ok = (got == want)
        if not ok:
            fails += 1
        mark = "[OK]" if ok else "[NG]"
        extra = ""
        if rel.endswith(".user.js"):
            n_userjs += 1
            b = open(p, "rb").read()
            crlf, lf = eol(b)
            extra = "  bytes=" + str(size) + " CRLF=" + str(crlf) + " 裸LF=" + str(lf)
            if lf != 0:
                extra += "  !! 存在裸 LF"
                fails += 1
        w("  " + mark + "  " + rel.ljust(46) + " " + got[:16] + "…" + extra)
        if not ok:
            w("        清单期望 = " + want)

    w("")
    w("---- 统计 ----")
    w("  核对条目 = " + str(len(entries)) + "（其中 .user.js = " + str(n_userjs) + "）")
    w("  失败项   = " + str(fails))
    w("")
    w("================================================")
    w("结论：" + ("全部一致（fail=0）" if fails == 0 else "存在不一致 fail=" + str(fails)))
    flush(fails == 0)
    return 0 if fails == 0 else 1


def flush(ok):
    try:
        os.makedirs(os.path.dirname(OUT), exist_ok=True)
        with io.open(OUT, "w", encoding="utf-8", newline="\n") as f:
            f.write("\n".join(L) + "\n")
    except OSError as e:
        sys.stderr.write("报告写入失败：" + str(e) + "\n")
    print("\n".join(L))
    print("[报告] " + OUT)


if __name__ == "__main__":
    sys.exit(main())
