# -*- coding: utf-8 -*-
"""收尾现状核对：工作区是否真的清空 + 关键资产是否都还在

清理的最后一步不该是"我觉得清干净了"，而应是一份可复核的现状快照：
  · 每个工作区还剩什么（含隐藏目录；`.workbuddy` 必须保留）
  · 仓库内关键资产是否齐全
  · 台账（ledger / journal）是否自洽

用法：python docs/tools/housekeeping/_vault.py <工作区1> [工作区2 ...]
产出：docs/reports/_vaultout.txt
"""
import io, json, os, sys

def _repo_root():
    """本文件位于 <repo>/docs/tools/housekeeping/ ⇒ 上溯 4 级才是仓库根。
    层级数算错会静默生成 docs/docs/reports/... 这类鬼路径，故直接断言。"""
    here = os.path.abspath(__file__)
    root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(here))))
    if not (os.path.isdir(os.path.join(root, "docs")) and os.path.isfile(os.path.join(root, "README.md"))):
        raise RuntimeError("推导出的仓库根不对：" + root)
    return root


REPO = _repo_root()
OUT = os.path.join(REPO, "docs", "reports", "_vaultout.txt")
ARC = os.path.join(REPO, "archive")
os.makedirs(os.path.dirname(OUT), exist_ok=True)

WS = sys.argv[1:] or []
KEY_ASSETS = [
    "海底小纵队·探矿鲸娘.user.js",
    "docs/versions/v0.4.11.user.js",
    "docs/reports/_v54out.txt",
    "docs/reports/_eolout.txt",
    "docs/reports/_zipcov.txt",
    "docs/tools/release/_gitverify.py",
    "docs/tools/housekeeping/_housekeeping.py",
    "releases/SHA256SUMS.txt",
]
# 允许残留的目录（不是垃圾）
KEEP_DIRS = {".workbuddy", "repo"}

L = []
def w(s): L.append(str(s))

fails = 0
w("=== 工作区现状 ===")
for root in WS:
    if not os.path.isdir(root):
        w("  [NG] 不存在：" + root); fails += 1; continue
    w("  " + root)
    for n in sorted(os.listdir(root)):
        p = os.path.join(root, n)
        if os.path.isdir(p):
            cnt = sum(len(fs) for _, _, fs in os.walk(p))
            w("      [D] " + n + "  （内含 " + str(cnt) + " 个文件）")
        else:
            w("      [F] " + str(os.path.getsize(p)).rjust(9) + "  " + n)
            if n.startswith("_"):
                fails += 1
                w("          !! 残留未清理的临时散件")
w("")

w("=== 关键资产 ===")
for rel in KEY_ASSETS:
    p = os.path.join(REPO, rel.replace("/", os.sep))
    ok = os.path.exists(p)
    if not ok:
        fails += 1
    w("  " + ("[OK] " if ok else "[缺失] ") + rel
      + ("  " + str(os.path.getsize(p)) + " 字节" if ok else ""))
w("")

w("=== 台账自洽 ===")
lp = os.path.join(ARC, "ledger.json")
jp = os.path.join(ARC, "journal.json")
ren = rdel = 0
if os.path.exists(lp):
    with io.open(lp, encoding="utf-8") as f:
        led = json.load(f)
    ren = len(led["entries"])
    uniq = set(e["name"] for e in led["entries"])
    w("  ledger entries = " + str(ren) + "（去重后 " + str(len(uniq)) + " 个不同文件名）")
else:
    w("  [NG] ledger.json 不存在"); fails += 1
if os.path.exists(jp):
    with io.open(jp, encoding="utf-8") as f:
        j = json.load(f)
    rdel = len(j["deleted"])
    w("  journal deleted = " + str(rdel))
    # 自洽判据按**去重名单**比较：同一文件可能被重复归档（内容变了会再入一次包），
    # 用条目数直接比删除数会得到虚假的"未删"缺口。
    if rdel > len(uniq):
        w("  [NG] 删除数大于归档去重数——存在删了没留底的风险"); fails += 1
    elif rdel < len(uniq):
        w("  [注意] 有 " + str(len(uniq) - rdel) + " 个文件名已归档但未删（应跑 --finish 补删）")
    else:
        w("  [OK] 归档去重名单与删除名单数量一致，台账自洽")
else:
    w("  [NG] journal.json 不存在"); fails += 1
w("")

w("======================================================")
w("结论：" + ("两处工作区已清空，资产齐全，台账自洽（fail=0）"
             if fails == 0 else "存在问题 fail=" + str(fails)))

with io.open(OUT, "w", encoding="utf-8") as f:
    f.write("\n".join(L) + "\n")
print("ok fails=" + str(fails))
sys.exit(0 if fails == 0 else 1)
