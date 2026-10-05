import io
p = r"C:\Users\D_A\DoubaoWork\chats\2026-10-05\new-chat-4\海底小纵队·探矿鲸娘.user.js"
src = io.open(p, encoding="utf-8").read()

subs = [
 # 副标题
 ("选择云端 DeepSeek 或本地 AI，配置后即可自动答题。",
  "选择云端 DeepSeek，填入 API Key 后即可自动答题。"),
 # 卡片 01
 ("在「答题」页面顶部选择：<strong>云端 DeepSeek</strong>（效果稳定，需 API Key）或<strong>本地 AI</strong>（免费、保护隐私，需运行 Ollama 等 OpenAI 兼容服务）。",
  "在「答题」页面顶部选择<strong>云端 DeepSeek</strong>，效果稳定，只需一个 API Key。"),
 # 卡片 02
 ("前往 platform.deepseek.com 注册并创建 sk- 开头的 API Key，填入后选择模型（Flash 速度快、V4 Pro 推理强），刷新页面即可自动答题。",
  "前往 platform.deepseek.com 注册并创建 sk- 开头的 API Key，填入后选择模型（<strong>V4 Pro 推理最强，推荐</strong>；Flash 速度快），刷新页面即可自动答题。"),
 # 卡片 03 -> 换成实用技巧
 ("本地：启动 Ollama",
  "提高准确率"),
 ("推荐使用 LM Studio：启动后开启本地服务器（默认 http://localhost:1234/v1）并加载模型（如 qwen3.5-9b），地址与模型名填入后刷新即可；Ollama（http://localhost:11434/v1）同理。",
  "遇到不确定的题目，建议切到 <strong>V4 Pro</strong>；连续多题失败时先手动做一题，脚本会参考历史答案。题目若含图片或公式，尽量保持选项文字完整，有助于判定。"),
]
n = 0
for a, b in subs:
    if a in src:
        src = src.replace(a, b, 1); n += 1
    else:
        io.open(r"C:\Users\D_A\WorkBuddy\2026-10-05-13-53-42\_miss.txt","a",encoding="utf-8").write("MISS: " + a[:40] + "\n")
io.open(p, "w", encoding="utf-8", newline="").write(src)
print("replaced", n, "of", len(subs))
