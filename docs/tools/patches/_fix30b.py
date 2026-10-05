# -*- coding: utf-8 -*-
"""fix30b：补插配置项改名迁移（fix30 的 C 步因 CRLF 锚点未命中）。

修正：删除 fix30 里误加的 ["操作间隔","操作间隔"] 占位映射——default 里该项仍是
「操作间隔（秒）」，若把老值迁成「操作间隔」反而对不上、导致该项回默认。
"""
import io, os, re

P = r"C:\Users\D_A\DoubaoWork\chats\2026-10-05\new-chat-4\海底小纵队·探矿鲸娘.user.js"
L = []

src = io.open(P, encoding="utf-8", newline="").read()

ANCHOR = re.compile(
    u"  const migrateConfig = \\(storedConfig, defaultConfig\\) => \\{\r?\n"
    u"    storedConfig = cloneLatestValue\\(storedConfig\\);"
)

MIG = u"""  const CONFIG_NAME_MIGRATIONS = {
    "\u89c6\u9891\u5f39\u9898\u81ea\u52a8\u4f5c\u7b54": "\u5f39\u9898\u81ea\u52a8\u4f5c\u7b54",
    "\u4f5c\u4e1a\u81ea\u52a8\u63d0\u4ea4": "\u81ea\u52a8\u63d0\u4ea4",
    "\u81ea\u52a8\u8fdb\u5165\u4e0b\u4e00\u8282": "\u81ea\u52a8\u5207\u6362",
    "\u81ea\u52a8\u7ffb\u5230\u4e0b\u4e00\u9898": "\u81ea\u52a8\u5207\u9898",
    "\u8bfe\u7a0b\u4efb\u52a1": "\u4efb\u52a1",
    "\u8003\u8bd5\u6a21\u5f0f": "\u8003\u8bd5",
    "\u8fdb\u9636\u8c03\u8282": "\u5176\u4ed6"
  };
  const PREFIX_NAME_MIGRATIONS = [
    ["\u500d\u901f\u64ad\u653e", "\u500d\u901f"],
    ["\u81ea\u52a8\u63d0\u4ea4\u7684\u6b63\u786e\u7387", "\u6b63\u786e\u7387\u9608\u503c"],
    ["\u7b54\u6848\u76f8\u4f3c\u5ea6\u9608\u503c", "\u76f8\u4f3c\u5ea6\u9608\u503c"]
  ];
  const renameConfigItemName = (node) => {
    if (!node || typeof node !== "object") return;
    if (Array.isArray(node)) {
      node.forEach(renameConfigItemName);
      return;
    }
    if (typeof node.name === "string") {
      const currentName = node.name;
      if (CONFIG_NAME_MIGRATIONS[currentName]) {
        node.name = CONFIG_NAME_MIGRATIONS[currentName];
      } else {
        const hit = PREFIX_NAME_MIGRATIONS.find((item) => currentName.indexOf(item[0]) === 0);
        if (hit)
          node.name = hit[1];
      }
    }
    Object.values(node).forEach(renameConfigItemName);
  };
  const migrateConfig = (storedConfig, defaultConfig) => {
    renameConfigItemName(storedConfig);
    storedConfig = cloneLatestValue(storedConfig);""".replace(u"\n", u"\r\n")

m = ANCHOR.search(src)
if not m:
    L.append(u"!! C 锚点仍未命中")
else:
    src = src[:m.start()] + MIG + src[m.end():]
    L.append(u"ok C 迁移已插入 (+%d chars)" % (len(MIG) - (m.end() - m.start())))

bad = [x for x in L if x.startswith("!!")]
io.open(P, "w", encoding="utf-8", newline="").write(src)
crlf = src.count(u"\r\n")
bare = src.count(u"\n") - crlf
L.append(u"chars=%d CRLF=%d bareLF=%d" % (len(src), crlf, bare))
io.open(r"C:\Users\D_A\WorkBuddy\2026-10-05-13-53-42\_fix30b.txt", "w", encoding="utf-8").write(u"\n".join(L))
print(u"\n".join(L))
if bad:
    print("HAS_FAIL")
