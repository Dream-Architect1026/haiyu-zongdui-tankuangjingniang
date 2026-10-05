# -*- coding: utf-8 -*-
"""fix35b：扩展迁移表（覆盖 17:52 之前的老世代名字）。

fix35 的 A 步失败原因：OLD_TABLE 用了 \n，而文件是 CRLF → 命中 0。
本次改为「块定位」：找到 CONFIG_NAME_MIGRATIONS = { 到最近的 }; 整块替换，
完全不依赖换行符。

老世代名字（来自 20.m 备份实测）：
  分组 章节设置 / 考试设置 / 其他参数
  项   章节作业自动提交 / 是否自动下一章节 / 只答题，不做其他 / 视频倍速（1-2）
       是否自动切换 / 切换、答题间隔，单位秒 / 正确率达到多少自动提交 / 答案相似度超过多少选择
"""
import io, os

P = r"C:\Users\D_A\DoubaoWork\chats\2026-10-05\new-chat-4\海底小纵队·探矿鲸娘.user.js"
L = []

src = io.open(P, encoding="utf-8", newline="").read()
orig_len = len(src)

START = u"  const CONFIG_NAME_MIGRATIONS = {"
END = u"};"

i = src.find(START)
if i < 0:
    L.append(u"!! 未找到 CONFIG_NAME_MIGRATIONS")
else:
    j = src.find(END, i)
    if j < 0:
        L.append(u"!! 未找到结束 };")
    else:
        j += len(END)
        old_block = src[i:j]
        L.append(u"旧块长度 %d 字符" % len(old_block))

        NEW = u"""  const CONFIG_NAME_MIGRATIONS = {
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
  };"""
        NEW = NEW.replace(u"\n", u"\r\n")
        src = src[:i] + NEW + src[j:]
        L.append(u"新块长度 %d 字符（19 条映射）" % len(NEW))

bad = [x for x in L if x.startswith("!!")]
io.open(P, "w", encoding="utf-8", newline="").write(src)
crlf = src.count(u"\r\n"); bare = src.count(u"\n") - crlf
L.append(u"chars: %d -> %d ; CRLF=%d bareLF=%d" % (orig_len, len(src), crlf, bare))
io.open(r"C:\Users\D_A\WorkBuddy\2026-10-05-13-53-42\_fix35b.txt", "w", encoding="utf-8").write(u"\n".join(L))
print(u"\n".join(L))
if bad:
    print("HAS_FAIL")
