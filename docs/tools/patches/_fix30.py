# -*- coding: utf-8 -*-
"""fix30：配置页文案精简（分组名 / 选项名），并加旧名->新名迁移避免老配置丢值。

改动清单（用户口述）：
  分组：课程任务 -> 任务 ；考试模式 -> 考试 ；进阶调节(=其他参数) -> 其他
  选项：视频弹题自动作答 -> 弹题自动作答
        作业自动提交 -> 自动提交
        自动进入下一节 -> 自动切换
        倍速播放（1~2） -> 倍速          （去括号）
        自动翻到下一题 -> 自动切题
        自动提交的正确率（%） -> 正确率阈值
        答案相似度阈值（%） -> 相似度阈值
  日志：自动切换到下一题 -> 自动切题
  保留：操作间隔（秒） 不动（用户未提及，去掉单位会丢信息）
"""
import io, os, re, sys

P = r"C:\Users\D_A\DoubaoWork\chats\2026-10-05\new-chat-4\海底小纵队·探矿鲸娘.user.js"
L = []

src = io.open(P, encoding="utf-8", newline="").read()
orig_len = len(src)

# ---------- A) 精确字符串替换 ----------
PAIRS = [
    # 常量（配置项 name 的来源）
    (u'const VIDEO_QUIZ_SETTING = "\u89c6\u9891\u5f39\u9898\u81ea\u52a8\u4f5c\u7b54";',
     u'const VIDEO_QUIZ_SETTING = "\u5f39\u9898\u81ea\u52a8\u4f5c\u7b54";'),
    # 分组名
    (u'name: "\u8bfe\u7a0b\u4efb\u52a1"', u'name: "\u4efb\u52a1"'),
    (u'name: "\u8003\u8bd5\u6a21\u5f0f"', u'name: "\u8003\u8bd5"'),
    (u'name: "\u8fdb\u9636\u8c03\u8282"', u'name: "\u5176\u4ed6"'),
    # 选项名
    (u'name: "\u4f5c\u4e1a\u81ea\u52a8\u63d0\u4ea4"', u'name: "\u81ea\u52a8\u63d0\u4ea4"'),
    (u'name: "\u81ea\u52a8\u8fdb\u5165\u4e0b\u4e00\u8282"', u'name: "\u81ea\u52a8\u5207\u6362"'),
    (u'name: "\u81ea\u52a8\u7ffb\u5230\u4e0b\u4e00\u9898"', u'name: "\u81ea\u52a8\u5207\u9898"'),
    # 通知日志
    (u'logStore.addLog("\u81ea\u52a8\u5207\u6362\u5230\u4e0b\u4e00\u9898", "success")',
     u'logStore.addLog("\u81ea\u52a8\u5207\u9898", "success")'),
]

for old, new in PAIRS:
    n = src.count(old)
    if n != 1:
        L.append(u"!! A 命中 %d : %s" % (n, old[:48]))
    else:
        src = src.replace(old, new, 1)
        L.append(u"ok A -> %s" % new.split('"')[1] if '"' in new else "ok A")

# ---------- B) 正则替换（值里含全角括号 / 波浪线，字符码点不好硬编码） ----------
REGEX = [
    (u'name: "\u500d\u901f\u64ad\u653e[^"]*"', u'name: "\u500d\u901f"'),                                  # 倍速播放（1~2） -> 倍速
    (u'name: "\u81ea\u52a8\u63d0\u4ea4\u7684\u6b63\u786e\u7387[^"]*"', u'name: "\u6b63\u786e\u7387\u9608\u503c"'),   # 自动提交的正确率（%） -> 正确率阈值
    (u'name: "\u7b54\u6848\u76f8\u4f3c\u5ea6\u9608\u503c[^"]*"', u'name: "\u76f8\u4f3c\u5ea6\u9608\u503c"'),        # 答案相似度阈值（%） -> 相似度阈值
]
for pat, rep in REGEX:
    hits = re.findall(pat, src)
    if len(hits) != 1:
        L.append(u"!! B 命中 %d : %s" % (len(hits), pat))
    else:
        L.append(u"ok B %s -> %s" % (hits[0], rep))
        src = re.sub(pat, rep, src, count=1)

# ---------- C) 插入配置项改名迁移 ----------
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
    ["\u7b54\u6848\u76f8\u4f3c\u5ea6\u9608\u503c", "\u76f8\u4f3c\u5ea6\u9608\u503c"],
    ["\u64cd\u4f5c\u95f4\u9694", "\u64cd\u4f5c\u95f4\u9694"]
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
        const hit = PREFIX_NAME_MIGRATIONS.find(([prefix]) => currentName.indexOf(prefix) === 0);
        if (hit)
          node.name = hit[1];
      }
    }
    Object.values(node).forEach(renameConfigItemName);
  };
  const migrateConfig = (storedConfig, defaultConfig) => {
    renameConfigItemName(storedConfig);
    storedConfig = cloneLatestValue(storedConfig);"""

OLD_MIG = u"""  const migrateConfig = (storedConfig, defaultConfig) => {
    storedConfig = cloneLatestValue(storedConfig);"""

if src.count(OLD_MIG) != 1:
    L.append(u"!! C migrateConfig 锚点命中 %d" % src.count(OLD_MIG))
else:
    src = src.replace(OLD_MIG, MIG, 1)
    L.append(u"ok C 迁移已插入")

# ---------- 写回 ----------
bad = [x for x in L if x.startswith("!!")]
io.open(P, "w", encoding="utf-8", newline="").write(src)

crlf = src.count(u"\r\n")
bare = src.count(u"\n") - crlf
L.append(u"bytes: %d -> %d chars" % (orig_len, len(src)))
L.append(u"CRLF=%d bareLF=%d" % (crlf, bare))
io.open(r"C:\Users\D_A\WorkBuddy\2026-10-05-13-53-42\_fix30.txt", "w", encoding="utf-8").write(u"\n".join(L))
print(u"\n".join(L))
if bad:
    print("HAS_FAIL")
