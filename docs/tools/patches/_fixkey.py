# -*- coding: utf-8 -*-
"""把 DONATE_KEY 从易错的 \\xNN 字符串字面量改为 base64 存储，杜绝 charCodeAt 转义歧义。"""
import base64, re, io

P = r"C:\Users\D_A\DoubaoWork\chats\2026-10-05\new-chat-4\海底小纵队·探矿鲸娘.user.js"
BAK = r"C:\Users\D_A\DoubaoWork\chats\2026-10-05\new-chat-4\海底小纵队·探矿鲸娘.user.js.bak"

with io.open(P, encoding="utf-8") as f:
    src = f.read()
with io.open(BAK, encoding="utf-8") as f:
    bak = f.read()

raw = base64.b64decode(re.search(r'data:image/jpeg;base64,([A-Za-z0-9+/=]+)', bak).group(1))
SALT = b"HXWHALE-DONATE-V1"
KEY = bytes([0x5A, 0x3C, 0x91, 0xE7, 0x2B, 0xD4, 0x68, 0xAF])

payload = raw + SALT
enc = bytes(payload[i] ^ KEY[i % len(KEY)] for i in range(len(payload)))
enc_b64 = base64.b64encode(enc).decode()
key_b64 = base64.b64encode(KEY).decode()

digest = 7
for i, b in enumerate(raw):
    digest = ((digest * 33 + b) & 0xFFFFFFFF) + (i % 7)
    digest &= 0xFFFFFFFF
sign = format(digest, "x")
print("raw:", len(raw), "key_b64:", key_b64, "sig:", sign)

import textwrap
chunks = textwrap.wrap(enc_b64, 96)
new_b64_block = "const DONATE_B64 = [\n    " + ",\n    ".join('"%s"' % c for c in chunks) + "\n  ];"

# 替换 KEY 定义
src = re.sub(r'const DONATE_KEY = "[^"]*";',
             'const DONATE_KEY = "%s";' % key_b64, src, count=1)
# 替换 SIG
src = re.sub(r'const DONATE_SIG = "[0-9a-f]*";',
             'const DONATE_SIG = "%s";' % sign, src, count=1)
# 替换 B64 块
src = re.sub(r'const DONATE_B64 = \[[\s\S]*?\];', new_b64_block, src, count=1)
# 替换密钥解析：base64 -> bytes
src = src.replace(
    'const key = DONATE_KEY.split("").map((ch) => ch.charCodeAt(0));',
    'const key = Uint8Array.from(atob(DONATE_KEY), (ch) => ch.charCodeAt(0));'
)
with io.open(P, "w", encoding="utf-8", newline="") as f:
    f.write(src)
print("patched: KEY -> base64, SIG ->", sign)
