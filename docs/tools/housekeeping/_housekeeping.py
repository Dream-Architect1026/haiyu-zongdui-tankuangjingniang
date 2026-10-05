# -*- coding: utf-8 -*-
"""工作区整理与留底（修正版）

设计目标：**任何时刻崩溃或重复执行，都不会造成不可追溯的丢失。**

四条硬规则（对应第四轮事故）：
  1. 留底包名带唯一时间戳后缀，永不原地覆盖
  2. 清单先落盘、再删文件
  3. 删除逐项记账（journal），支持断点续跑
  4. 幂等：已归档过的文件不会二次入包，重跑只处理"新出现的"

用法：
  python _housekeeping.py --ws <工作区目录> --archive <归档目录>            # 干跑
  python _housekeeping.py --ws <工作区目录> --archive <归档目录> --apply    # 执行
"""
import argparse, hashlib, io, json, os, sys, time, zipfile

def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()

def load_json(p, default):
    if os.path.exists(p):
        with io.open(p, encoding="utf-8") as f:
            return json.load(f)
    return default

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ws", required=True, help="工作区目录")
    ap.add_argument("--archive", required=True, help="归档目录（留底包与清单的存放处）")
    ap.add_argument("--prefix", default="_", help="待清理文件的名称前缀，默认 _")
    ap.add_argument("--keep", default="", help="不参与清理的文件名，逗号分隔")
    ap.add_argument("--apply", action="store_true", help="真正写入（默认干跑）")
    a = ap.parse_args()

    keep = set(x for x in a.keep.split(",") if x)
    os.makedirs(a.archive, exist_ok=True)

    journal_p = os.path.join(a.archive, "journal.json")
    ledger_p = os.path.join(a.archive, "ledger.json")
    journal = load_json(journal_p, {"archived": [], "deleted": []})
    ledger = load_json(ledger_p, {"entries": []})
    done_names = set(e["name"] for e in ledger["entries"])   # 已归档过（含已删）
    archived_names = set(journal["archived"])
    deleted_names = set(journal["deleted"])

    # 规则 4：重跑只处理"新出现的"
    targets = []
    for n in sorted(os.listdir(a.ws)):
        p = os.path.join(a.ws, n)
        if not os.path.isfile(p) or not n.startswith(a.prefix):
            continue
        if n in keep or n in done_names:
            continue
        targets.append(p)

    print("工作区 " + a.ws)
    print("  待处理 " + str(len(targets)) + " 个（已归档过而跳过 " + str(len(done_names)) + " 个）")
    for p in targets:
        print("    " + str(os.path.getsize(p)).rjust(9) + "  " + os.path.basename(p))
    if not a.apply:
        print("（干跑：未改动磁盘）")
        return

    # 规则 1：唯一后缀
    stamp = time.strftime("%Y%m%d-%H%M%S")
    zip_p = os.path.join(a.archive, a.prefix + "junk-" + stamp + ".zip")
    n = 1
    while os.path.exists(zip_p):                       # 同秒重跑也不覆盖
        zip_p = os.path.join(a.archive, a.prefix + "junk-" + stamp + "-" + str(n) + ".zip")
        n += 1

    # 规则 2：先把清单落盘
    new_entries = []
    for p in targets:
        new_entries.append({"name": os.path.basename(p), "bytes": os.path.getsize(p), "sha256": sha256(p)})
    ledger["entries"].extend(new_entries)
    ledger["last_run"] = {"stamp": stamp, "zip": os.path.basename(zip_p), "count": len(new_entries)}
    with io.open(ledger_p, "w", encoding="utf-8") as f:
        json.dump(ledger, f, ensure_ascii=False, indent=2)
    print("  清单已落盘：" + os.path.basename(ledger_p))

    # 打包
    with zipfile.ZipFile(zip_p, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for p in targets:
            z.write(p, os.path.basename(p))
    print("  留底包：" + os.path.basename(zip_p) + "  " + str(os.path.getsize(zip_p)) + " 字节")

    # 规则 3：删除并逐项记账（每删一项即刷盘，崩溃可续）
    archived_names |= set(os.path.basename(p) for p in targets)
    for p in targets:
        name = os.path.basename(p)
        try:
            os.remove(p)
            deleted_names.add(name)
        except OSError as e:
            print("  [跳过] " + name + "：" + e)
        journal["archived"] = sorted(archived_names)
        journal["deleted"] = sorted(deleted_names)
        with io.open(journal_p, "w", encoding="utf-8") as f:
            json.dump(journal, f, ensure_ascii=False, indent=2)
    print("  已删除 " + str(len(deleted_names)) + " 个")
    print("（可随时中断；重跑只会处理尚未归档的新文件）")

if __name__ == "__main__":
    main()
