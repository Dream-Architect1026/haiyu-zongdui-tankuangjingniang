# -*- coding: utf-8 -*-
"""fix35：根治「存量配置压住新文案」。

根因：mergeByLatestFields 对叶子字段是「stored 优先」——
  return storedValue === void 0 ? clone : stored;
所以 otherParams.name 这种纯 UI 标签，一旦用户存过旧值，就永远显示旧文案，
重装脚本也没用（与「模型下拉一直显示 V3」同源）。

两道修：
 A) 扩展 CONFIG_NAME_MIGRATIONS，补齐更老世代的名字（章节设置/考试设置/其他参数/…）
    —— 让 merge 能按 name 找到存储项，**保住用户的开关值**。
 B) 新增 alignConfigLabels(merged, default)，合并后把 name 标签按默认值强制对齐
    —— 标签永远跟随脚本，不再受存量配置影响。
"""
import io, os, re

P = r"C:\Users\D_A\DoubaoWork\chats\2026-10-05\new-chat-4\海底小纵队·探矿鲸娘.user.js"
L = []
src = io.open(P, encoding="utf-8", newline="").read()
orig_len = len(src)

# ---------- A) 扩展迁移表 ----------
OLD_TABLE = (
u'''  const CONFIG_NAME_MIGRATIONS = {
    "\u89c6\u9891\u5f39\u9898\u81ea\u52a8\u4f5c\u7b54": "\u5f39\u9898\u81ea\u52a8\u4f5c\u7b54",
    "\u4f5c\u4e1a\u81ea\u52a8\u63d0\u4ea4": "\u81ea\u52a8\u63d0\u4ea4",
    "\u81ea\u52a8\u8fdb\u5165\u4e0b\u4e00\u8282": "\u81ea\u52a8\u5207\u6362",
    "\u81ea\u52a8\u7ffb\u5230\u4e0b\u4e00\u9898": "\u81ea\u52a8\u5207\u9898",
    "\u53ea\u7b54\u9898\u4e0d\u5237\u8bfe": "\u4ec5\u4f5c\u7b54",
    "\u8bfe\u7a0b\u4efb\u52a1": "\u4efb\u52a1",
    "\u8003\u8bd5\u6a21\u5f0f": "\u8003\u8bd5",
    "\u8fdb\u9636\u8c03\u8282": "\u5176\u4ed6"
  };''')

NEW_TABLE = (
u'''  const CONFIG_NAME_MIGRATIONS = {
    "\u89c6\u9891\u5f39\u9898\u81ea\u52a8\u4f5c\u7b54": "\u5f39\u9898\u81ea\u52a8\u4f5c\u7b54",
    "\u4f5c\u4e1a\u81ea\u52a8\u63d0\u4ea4": "\u81ea\u52a8\u63d0\u4ea4",
    "\u81ea\u52a8\u8fdb\u5165\u4e0b\u4e00\u8282": "\u81ea\u52a8\u5207\u6362",
    "\u81ea\u52a8\u7ffb\u5230\u4e0b\u4e00\u9898": "\u81ea\u52a8\u5207\u9898",
    "\u53ea\u7b54\u9898\u4e0d\u5237\u8bfe": "\u4ec5\u4f5c\u7b54",
    "\u8bfe\u7a0b\u4efb\u52a1": "\u4efb\u52a1",
    "\u8003\u8bd5\u6a21\u5f0f": "\u8003\u8bd5",
    "\u8fdb\u9636\u8c03\u8282": "\u5176\u4ed6",
    "\u7ae0\u8282\u8bbe\u7f6e": "\u4efb\u52a1",
    "\u8003\u8bd5\u8bbe\u7f6e": "\u8003\u8bd5",
    "\u5176\u4ed6\u53c2\u6570": "\u5176\u4ed6",
    "\u7ae0\u8282\u4f5c\u4e1a\u81ea\u52a8\u63d0\u4ea4": "\u81ea\u52a8\u63d0\u4ea4",
    "\u662f\u5426\u81ea\u52a8\u4e0b\u4e00\u7ae0\u8282": "\u81ea\u52a8\u5207\u6362",
    "\u53ea\u7b54\u9898\uff0c\u4e0d\u505a\u5176\u4ed6": "\u4ec5\u4f5c\u7b54",
    "\u662f\u5426\u81ea\u52a8\u5207\u6362": "\u81ea\u52a8\u5207\u9898",
    "\u5207\u6362\u3001\u7b54\u9898\u95f4\u9694\uff0c\u5355\u4f4d\u79d2": "\u64cd\u4f5c\u95f4\u9694",
    "\u6b63\u786e\u7387\u8fbe\u5230\u591a\u5c11\u81ea\u52a8\u63d0\u4ea4": "\u6b63\u786e\u7387\u9608\u503c",
    "\u7b54\u6848\u76f8\u4f3c\u5ea6\u8d85\u8fc7\u591a\u5c11\u9009\u62e9": "\u76f8\u4f3c\u5ea6\u9608\u503c",
    "\u89c6\u9891\u500d\u901f\uff081-2\uff09": "\u500d\u901f"
  };''').replace(u"\n", u"\r\n")

if src.count(OLD_TABLE) == 1:
    src = src.replace(OLD_TABLE, NEW_TABLE, 1)
    L.append(u"ok A 迁移表扩展 8 -> 19 条")
else:
    L.append(u"!! A 迁移表锚点命中 %d" % src.count(OLD_TABLE))

# ---------- B) 新增 alignConfigLabels + 调用 ----------
ANCHOR = u"  const migrateConfig = (storedConfig, defaultConfig) => {\r\n    renameConfigItemName(storedConfig);"
if src.count(ANCHOR) != 1:
    L.append(u"!! B 锚点命中 %d" % src.count(ANCHOR))
else:
    ALIGN = (
u'''  const alignConfigLabels = (node, template) => {
    if (Array.isArray(node) && Array.isArray(template)) {
      node.forEach((item, index) => {
        if (template[index] !== void 0)
          alignConfigLabels(item, template[index]);
      });
      return;
    }
    if (node && template && typeof node === "object" && typeof template === "object") {
      if (typeof template.name === "string" && typeof node.name === "string")
        node.name = template.name;
      Object.keys(template).forEach((key) => {
        if (key === "name") return;
        alignConfigLabels(node[key], template[key]);
      });
    }
  };
  const migrateConfig = (storedConfig, defaultConfig) => {
    renameConfigItemName(storedConfig);''').replace(u"\n", u"\r\n")
    src = src.replace(ANCHOR, ALIGN, 1)
    L.append(u"ok B alignConfigLabels 已插入")

CALL_ANCHOR = u"    mergedConfig.otherParams.params[0].min = defaultConfig.otherParams.params[0].min;\r\n    return mergedConfig;"
CALL_NEW = u"    mergedConfig.otherParams.params[0].min = defaultConfig.otherParams.params[0].min;\r\n    alignConfigLabels(mergedConfig, defaultConfig);\r\n    return mergedConfig;"
if src.count(CALL_ANCHOR) == 1:
    src = src.replace(CALL_ANCHOR, CALL_NEW, 1)
    L.append(u"ok B migrateConfig 内已调用 alignConfigLabels")
else:
    L.append(u"!! B 调用锚点命中 %d" % src.count(CALL_ANCHOR))

bad = [x for x in L if x.startswith("!!")]
io.open(P, "w", encoding="utf-8", newline="").write(src)
crlf = src.count(u"\r\n")
bare = src.count(u"\n") - crlf
L.append(u"chars: %d -> %d ; CRLF=%d bareLF=%d" % (orig_len, len(src), crlf, bare))
io.open(r"C:\Users\D_A\WorkBuddy\2026-10-05-13-53-42\_fix35.txt", "w", encoding="utf-8").write(u"\n".join(L))
print(u"\n".join(L))
if bad:
    print("HAS_FAIL")
