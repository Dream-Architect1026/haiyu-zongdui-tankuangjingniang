# -*- coding: utf-8 -*-
import io, shutil
P = r"C:\Users\D_A\DoubaoWork\chats\2026-10-05\new-chat-4\海底小纵队·探矿鲸娘.user.js"
shutil.copyfile(P, P + ".bak5")
src = io.open(P, encoding="utf-8").read()
out = []

before = src.count("\\\\n")   # 2 反斜杠 + n
out.append("修复前 '\\\\\\\\n'(双反斜杠+n): %d" % before)

# 只把 双反斜杠+n 收敛成 单反斜杠+n；\" 不动
src = src.replace("\\\\n", "\\n")

after = src.count("\\\\n")
out.append("修复后 '\\\\\\\\n'(双反斜杠+n): %d" % after)
out.append("修复后 '\\\\n'(单反斜杠+n): %d" % src.count("\\n") )

io.open(P, "w", encoding="utf-8", newline="").write(src)
io.open(r"C:\Users\D_A\WorkBuddy\2026-10-05-13-53-42\_fix4.txt","w",encoding="utf-8").write("\n".join(out))
print("OK")
