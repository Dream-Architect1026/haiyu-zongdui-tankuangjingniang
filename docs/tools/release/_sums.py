# -*- coding: utf-8 -*-
"""生成 releases/SHA256SUMS.txt：版本链快照 + 现行版 + 发布包，全量 64 位 SHA256。

路径一律相对于**仓库根**，便于在仓库根执行 `sha256sum -c releases/SHA256SUMS.txt`
（Windows 下：`Get-FileHash` 逐项核对，或用 git bash 的 sha256sum）。

用法：
    python _sums.py            # 干跑，只打印将要写入的内容
    python _sums.py --apply    # 真正写入

退出码：0 = 正常；1 = 有文件缺失（不会写出不完整的清单）
"""
import hashlib
import io
import os
import sys

SELF = os.path.abspath(__file__)
# docs/tools/release/_sums.py → 上溯 4 级到仓库根
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(SELF))))
NAME = "海底小纵队·探矿鲸娘.user.js"

# 自检断言：层级算错时立刻报错，绝不静默跑在错目录
assert os.path.isfile(os.path.join(REPO, NAME)), \
    "仓库根解析错误：未在 " + REPO + " 找到 " + NAME

VERSIONS_DIR = os.path.join(REPO, "docs", "versions")
RELEASES_DIR = os.path.join(REPO, "releases")
OUT = os.path.join(RELEASES_DIR, "SHA256SUMS.txt")


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def collect():
    """返回 [(相对路径, 绝对路径, 分组标题)] 与缺失项列表"""
    groups = []
    missing = []

    # 1) 版本链快照（按版本号数值排序，别用字符串排序）
    def vkey(p):
        base = os.path.basename(p)          # v0.4.10.user.js
        nums = base.lstrip("v").split(".")[:3]
        out = []
        for x in nums:
            d = "".join(c for c in x if c.isdigit())
            out.append(int(d) if d else 0)
        return tuple(out)

    snap = []
    if os.path.isdir(VERSIONS_DIR):
        for fn in os.listdir(VERSIONS_DIR):
            if fn.endswith(".user.js"):
                snap.append(os.path.join(VERSIONS_DIR, fn))
    snap.sort(key=vkey)
    if not snap:
        missing.append("docs/versions/*.user.js（版本链为空）")
    groups.append(("历史版本快照（docs/versions/）", snap))

    # 2) 现行版
    cur = os.path.join(REPO, NAME)
    groups.append(("现行版（仓库根）", [cur] if os.path.isfile(cur) else []))

    # 3) 发布包
    zips = []
    if os.path.isdir(RELEASES_DIR):
        for fn in sorted(os.listdir(RELEASES_DIR)):
            if fn.endswith(".zip"):
                zips.append(os.path.join(RELEASES_DIR, fn))
    groups.append(("发布包（releases/）", zips))

    for title, paths in groups:
        for p in paths:
            if not os.path.isfile(p):
                missing.append(os.path.relpath(p, REPO).replace(os.sep, "/"))

    return groups, missing


def build():
    groups, missing = collect()
    L = []
    L.append("# SHA-256 校验清单 —— haiyu-zongdui-tankuangjingniang")
    L.append("#")
    L.append("# 路径相对于仓库根。核对方式：")
    L.append("#   git bash      : sha256sum -c releases/SHA256SUMS.txt")
    L.append("#   PowerShell    : Get-FileHash 逐项比对（见下）")
    L.append("#   Python 一站式 : python docs/tools/release/_verify_sums.py")
    L.append("# 详细说明见 docs/VERIFICATION.md「五、复现方式」。")
    L.append("#")
    L.append("# 全部文件行尾为 CRLF、裸 LF 为 0（校验字节数即可发现行尾被改动）。")
    L.append("")
    for title, paths in groups:
        if not paths:
            continue
        L.append("# ---- " + title + " ----")
        for p in paths:
            rel = os.path.relpath(p, REPO).replace(os.sep, "/")
            L.append(sha256(p) + "  " + rel)
        L.append("")
    return "\n".join(L).rstrip("\n") + "\n", missing


def main():
    apply = "--apply" in sys.argv
    text, missing = build()

    if missing:
        print("!! 有 " + str(len(missing)) + " 个文件缺失，拒绝写出不完整清单：")
        for m in missing:
            print("   - " + m)
        return 1

    n_lines = len([x for x in text.splitlines() if x and not x.startswith("#")])
    print("条目数 = " + str(n_lines) + "  字符数 = " + str(len(text)))
    print("")
    print(text)

    if apply:
        # 统一 LF：本文件是纯清单，不参与 .user.js 的 CRLF 约束
        with io.open(OUT, "w", encoding="utf-8", newline="\n") as f:
            f.write(text)
        print("[已写入] " + OUT)
    else:
        print("[干跑] 未写盘；加 --apply 生效")
    return 0


if __name__ == "__main__":
    sys.exit(main())
