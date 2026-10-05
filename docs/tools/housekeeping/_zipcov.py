# -*- coding: utf-8 -*-
"""留底包覆盖核对：证明"删除的每一个文件都确实躺在归档包里，且字节未变"

这是删除动作的**前置证据**。清理事故的两种形态——
  ① 删了但没留底（数据真丢）
  ② 留底了但没删（垃圾堆积，还欺骗台账）
——只有靠"逐名 + 逐字节"核对才能分别排除。

用法：python docs/tools/housekeeping/_zipcov.py [归档目录]
产出：docs/reports/_zipcov.txt
"""
import hashlib, io, json, os, sys, zipfile

def _repo_root():
    """本文件位于 <repo>/docs/tools/housekeeping/ ⇒ 上溯 4 级才是仓库根。
    层级数算错是这类脚本最常见的静默 bug（会生成 docs/docs/reports/... 这种鬼路径），
    所以这里直接断言，让错路径在启动瞬间就炸掉而不是跑到写文件才报错。"""
    here = os.path.abspath(__file__)
    root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(here))))
    if not (os.path.isdir(os.path.join(root, "docs")) and os.path.isfile(os.path.join(root, "README.md"))):
        raise RuntimeError("推导出的仓库根不对：" + root)
    return root


REPO = _repo_root()
OUT = os.path.join(REPO, "docs", "reports", "_zipcov.txt")
ARC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(REPO, "archive")
os.makedirs(os.path.dirname(OUT), exist_ok=True)

L = []
def w(s): L.append(str(s))

w("归档目录 " + ARC)
w("")

ledger_p = os.path.join(ARC, "ledger.json")
if not os.path.exists(ledger_p):
    w("[NG] 找不到 ledger.json，无法核对")
    io.open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n")
    sys.exit(1)

with io.open(ledger_p, encoding="utf-8") as f:
    ledger = json.load(f)
want = {}
for e in ledger["entries"]:
    want[e["name"]] = e["sha256"]

# 全量扫描归档目录：名字 -> [(zip, 解出字节)]
found = {}
zips = sorted(x for x in os.listdir(ARC) if x.lower().endswith(".zip"))
w("=== 归档包清单 ===")
for z in zips:
    p = os.path.join(ARC, z)
    try:
        with zipfile.ZipFile(p) as zf:
            infos = zf.infolist()
            w("  " + z + "  " + str(os.path.getsize(p)) + " 字节  " + str(len(infos)) + " 条目")
            for e in infos:
                found.setdefault(e.filename, []).append((z, zf.read(e.filename)))
    except zipfile.BadZipFile:
        w("  [NG] " + z + "  不是有效 zip")
w("")

fails = 0

w("=== 覆盖与哈希核对（ledger " + str(len(want)) + " 条）===")
miss, bad = [], []
for n, h in sorted(want.items()):
    if n not in found:
        miss.append(n)
        continue
    oks = [z for z, b in found[n] if hashlib.sha256(b).hexdigest() == h]
    if not oks:
        bad.append(n)
    else:
        w("  [OK] " + n.ljust(24) + " sha256=" + h[:16] + "  在 " + oks[0])
if miss:
    fails += len(miss)
    w("")
    w("  [NG] 未进包 " + str(len(miss)) + " 个：" + ", ".join(miss))
if bad:
    fails += len(bad)
    w("")
    w("  [NG] 包内哈希不符 " + str(len(bad)) + " 个：" + ", ".join(bad))
if not miss and not bad:
    w("")
    w("  [OK] ledger 全部条目都能在归档包内找到，且 sha256 逐字节一致")
w("")

w("======================================================")
w("结论：" + ("留底完整，删除有据（fail=0）" if fails == 0 else "存在问题 fail=" + str(fails)))

with io.open(OUT, "w", encoding="utf-8") as f:
    f.write("\n".join(L) + "\n")
print("ok fails=" + str(fails))
sys.exit(0 if fails == 0 else 1)
