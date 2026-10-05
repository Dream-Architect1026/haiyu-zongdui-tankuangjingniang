# -*- coding: utf-8 -*-
"""工作区整理与留底（修正版）

设计目标：**任何时刻崩溃或重复执行，都不会造成不可追溯的丢失。**

五条硬规则（规则 1-4 对应第四轮覆盖事故；规则 5 对应本轮"清理孤儿依赖"事故）：
  1. 留底包名带唯一时间戳后缀，永不原地覆盖
  2. 清单先落盘、再删文件
  3. 删除逐项记账（journal），支持断点续跑
  4. 幂等：**只认 journal.deleted**（确实已归档且已删除），不认 ledger（归档尝试）
  5. 删前查依赖：扫描仓库确认没有脚本/文档引用待删文件名，命中即**拒绝删除**

规则 5 为什么必要：删除散件时，散件承载的"凭据"不会一起消失——
`_bak_0411.user.js` 曾是验收脚本的对照基线，删掉它脚本立刻 ENOENT，
回归能力凭空消失，而且要到下一次跑验收才会暴露。

用法：
  python _housekeeping.py --ws <工作区> --archive <归档目录>                     # 干跑
  python _housekeeping.py --ws <工作区> --archive <归档目录> --apply             # 执行
  python _housekeeping.py --ws <工作区> --archive <归档目录> --refscan <仓库根>   # 带依赖扫描
  python _housekeeping.py ... --refscan <仓库根> --allow a.txt,b.txt            # 显式放行拦截项
  python _housekeeping.py --ws <工作区> --archive <归档目录> --finish --apply    # 补删中断残留

退出码：0 = 正常；2 = 有需人工处置的项（被依赖文件 / 补删时核对不通过）
"""
import argparse, hashlib, io, json, os, sys, time, zipfile

SKIP_DIRS = {".git", "node_modules", "__pycache__", ".workbuddy"}
MAX_SCAN_BYTES = 8 << 20


def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def sha256_bytes(b):
    return hashlib.sha256(b).hexdigest()


def zip_index(archive_dir):
    """扫描归档目录，返回 文件名 -> [含该条目的 zip 路径, ...]"""
    idx = {}
    for fn in sorted(os.listdir(archive_dir)):
        if not fn.lower().endswith(".zip"):
            continue
        p = os.path.join(archive_dir, fn)
        try:
            with zipfile.ZipFile(p) as z:
                for e in z.infolist():
                    idx.setdefault(e.filename, []).append(p)
        except (zipfile.BadZipFile, OSError):
            continue
    return idx


def load_json(p, default):
    if os.path.exists(p):
        with io.open(p, encoding="utf-8") as f:
            return json.load(f)
    return default


def scan_refs(roots, names, self_paths=(), skip_abs=()):
    """在 roots 下扫描，找出哪些文件提到了 names 里的文件名。

    返回 {name: [(相对路径, 行号, 该行摘要), ...]}
    只扫文本文件；二进制（rar/zip/png/字体等）解码失败即跳过。

    skip_abs：绝对路径黑名单（归档目录必须排除——ledger/journal/留底清单里
    天然写满了被归档的文件名，不排除就会自己引用自己，导致永远拦截）。
    """
    want = set(names)
    hits = {}
    skip = set(os.path.abspath(x) for x in skip_abs)
    for root in roots:
        if not os.path.isdir(root):
            continue
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
            for fn in filenames:
                fp = os.path.join(dirpath, fn)
                if os.path.abspath(fp) in skip or os.path.abspath(dirpath) in skip:
                    continue
                try:
                    if os.path.getsize(fp) > MAX_SCAN_BYTES:
                        continue
                    with io.open(fp, "rb") as f:
                        raw = f.read()
                    text = raw.decode("utf-8")
                except (OSError, UnicodeDecodeError):
                    continue
                if not any(n in text for n in want):
                    continue
                rel = os.path.relpath(fp, root).replace(os.sep, "/")
                for i, line in enumerate(text.splitlines(), 1):
                    for n in want:
                        if n in line:
                            hits.setdefault(n, []).append(
                                (rel, i, line.strip()[:110]))
    return hits


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ws", required=True, help="工作区目录")
    ap.add_argument("--archive", required=True, help="归档目录（留底包与清单的存放处）")
    ap.add_argument("--prefix", default="_", help="待清理文件的名称前缀，默认 _")
    ap.add_argument("--keep", default="", help="不参与清理的文件名，逗号分隔")
    ap.add_argument("--refscan", default="", help="依赖扫描根目录（建议传仓库根），逗号分隔")
    ap.add_argument("--allow", default="", help="显式放行的文件名（覆盖规则 5 拦截），逗号分隔；会被记入清单")
    ap.add_argument("--finish", action="store_true",
                    help="补删模式：只处理「台账已记但文件仍在盘」的条目，先在归档包内核对 sha256 再删，不重新打包")
    ap.add_argument("--apply", action="store_true", help="真正写入（默认干跑）")
    a = ap.parse_args()

    keep = set(x for x in a.keep.split(",") if x)
    allow = set(x for x in a.allow.split(",") if x)
    os.makedirs(a.archive, exist_ok=True)

    journal_p = os.path.join(a.archive, "journal.json")
    ledger_p = os.path.join(a.archive, "ledger.json")
    journal = load_json(journal_p, {"archived": [], "deleted": []})
    ledger = load_json(ledger_p, {"entries": []})
    done_names = set(journal["deleted"])   # 已归档**且已删除**
    archived_names = set(journal["archived"])
    deleted_names = set(journal["deleted"])
    ledger_sha = {e["name"]: e["sha256"] for e in ledger["entries"]}

    # 规则 4（0.4.12 修正）：幂等判据必须是 journal.deleted，不是 ledger.entries。
    # ledger 只证明"曾经尝试归档"，它在打包**之前**落盘；若进程在"写台账"与
    # "删文件"之间中断，文件会留在盘上却被 ledger 判为已完成 ⇒ 永远清不掉。
    # 用 journal.deleted（逐项确认）才与真实状态一致。
    stuck = []
    for n in sorted(os.listdir(a.ws)):
        p = os.path.join(a.ws, n)
        if os.path.isfile(p) and n.startswith(a.prefix) and n in ledger_sha and n not in deleted_names:
            stuck.append(p)

    # 补删模式：台账已记、文件仍在盘 —— 先在归档包里按名找到并核对 sha256，
    # 一致才删（不重新打包，避免 8MB 级重复留底）。
    if a.finish:
        idx = zip_index(a.archive)
        print("工作区 " + a.ws)
        print("  待补删 " + str(len(stuck)) + " 个（台账已记但文件仍在盘）")
        okd, skipd = 0, 0
        for p in stuck:
            n = os.path.basename(p)
            want = ledger_sha.get(n)
            found = False
            for zp in idx.get(n, []):
                with zipfile.ZipFile(zp) as z:
                    if sha256_bytes(z.read(n)) == want:
                        found = True
                        break
            if not found:
                print("    [保留] " + n + " —— 归档包内未找到同名同哈希副本，不敢删")
                skipd += 1
                continue
            if a.apply:
                try:
                    os.remove(p)
                    deleted_names.add(n)
                    journal["deleted"] = sorted(deleted_names)
                    with io.open(journal_p, "w", encoding="utf-8") as f:
                        json.dump(journal, f, ensure_ascii=False, indent=2)
                except OSError as e:
                    print("    [跳过] " + n + "：" + str(e))
                    skipd += 1
                    continue
            print("    [" + ("已补删" if a.apply else "将补删") + "] " + n
                  + "  sha256=" + str(want)[:12] + " 已核对入包")
            okd += 1
        print("  补删 " + str(okd) + " 个，保留 " + str(skipd) + " 个")
        return 0 if skipd == 0 else 2

    # 规则 4：重跑只处理"新出现的"。判重键是 (文件名, sha256) 而非仅文件名——
    # 否则"删掉之后又被重新创建（内容不同）"的同名文件会被永久跳过，
    # 悄悄堆在工作区里（本轮收尾日志就撞上了这个坑）。
    candidates = []
    for n in sorted(os.listdir(a.ws)):
        p = os.path.join(a.ws, n)
        if not os.path.isfile(p) or not n.startswith(a.prefix):
            continue
        if n in keep:
            continue
        if n in done_names and n in ledger_sha and sha256(p) == ledger_sha[n]:
            continue          # 确实归档过、删过，且内容未变
        candidates.append(p)

    if stuck:
        print("注意：有 " + str(len(stuck)) + " 个文件台账已记但仍在盘（上次中断在删除前）。"
              + "加 --finish 可只补删不重打包。")

    # 规则 5：删前查依赖
    blocked = {}
    overridden = {}
    targets = list(candidates)
    if a.refscan:
        roots = [x for x in a.refscan.split(",") if x]
        refs = scan_refs(roots, [os.path.basename(p) for p in candidates],
                         skip_abs=[os.path.abspath(__file__), os.path.abspath(a.archive)])
        real = {n: v for n, v in refs.items() if v}
        # --allow 显式放行：不静默通过，命中数记入清单备查
        for n in sorted(real):
            if n in allow:
                overridden[n] = len(real[n])
            else:
                blocked[n] = real[n]
        targets = [p for p in candidates if os.path.basename(p) not in blocked]

    print("工作区 " + a.ws)
    print("  候选 " + str(len(candidates)) + " 个（已归档过而跳过 " + str(len(done_names)) + " 个）"
          + "，其中被引用而拦截 " + str(len(blocked)) + " 个"
          + "，显式放行 " + str(len(overridden)) + " 个")
    for p in targets:
        tag = "[放行]" if os.path.basename(p) in overridden else "[可删]"
        print("    " + tag + " " + str(os.path.getsize(p)).rjust(9) + "  " + os.path.basename(p))
    for n in sorted(blocked):
        print("    [拦截] " + n + " —— 被以下位置引用，拒绝删除：")
        for rel, ln, s in blocked[n][:5]:
            print("             " + rel + ":" + str(ln) + "  " + s)
        if len(blocked[n]) > 5:
            print("             …（另有 " + str(len(blocked[n]) - 5) + " 处）")
    if blocked:
        print("  提示：把该文件**升格为仓库正式资产**（迁入 docs/ 并纳入版本控制），")
        print("        或改掉引用方的路径。二者必居其一，不要靠「反正还在某个角落」蒙过去。")

    if not a.apply:
        print("（干跑：未改动磁盘）")
        return 2 if blocked else 0

    if not targets:
        print("  无可删文件，结束")
        return 2 if blocked else 0

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
    ledger["last_run"] = {"stamp": stamp, "zip": os.path.basename(zip_p),
                          "count": len(new_entries), "blocked": sorted(blocked),
                          "overridden": overridden}
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
    return 2 if blocked else 0


if __name__ == "__main__":
    sys.exit(main())
