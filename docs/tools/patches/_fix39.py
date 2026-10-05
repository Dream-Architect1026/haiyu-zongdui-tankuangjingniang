# -*- coding: utf-8 -*-
# fix39: 方案B 全量落地
#  1) 配置页顶部新增「AI」卡片（API Key + 模型），格式对齐其它卡片
#  2) 鲸娘页移除 ai-config 与 el-empty 空状态，改为单一 whale-hero：
#     空闲=同比例放大、空白区居中；作答=缩小回顶部原位 + 状态文字
#  3) 用量统计卡片固定吸底，不随内容滚动
import io, sys

P = r"C:\Users\D_A\DoubaoWork\chats\2026-10-05\new-chat-4\海底小纵队·探矿鲸娘.user.js"
CRLF = "\r\n"

with io.open(P, "r", encoding="utf-8", newline="") as f:
    t = f.read()

orig_len = len(t)
log = []


def sub_once(old, new, tag):
    global t
    old = old.replace("\n", CRLF)
    new = new.replace("\n", CRLF)
    n = t.count(old)
    assert n == 1, "[%s] 锚点命中 %d 次" % (tag, n)
    t = t.replace(old, new, 1)
    log.append("ok " + tag)


# ============ A. 配置页：补齐组件 resolve ============
sub_once(
    r'''        const _component_el_form_item = vue.resolveComponent("el-form-item");''',
    r'''        const _component_el_form_item = vue.resolveComponent("el-form-item");
        const _component_el_input = vue.resolveComponent("el-input");
        const _component_el_select = vue.resolveComponent("el-select");
        const _component_el_option = vue.resolveComponent("el-option");''',
    "A 配置页 resolve 补齐 el-input/el-select/el-option",
)

# ============ B. 配置页：顶部插入 AI 卡片 ============
sub_once(
    r'''        return vue.openBlock(), vue.createElementBlock("div", _hoisted_1$4, [
          (vue.openBlock(true), vue.createElementBlock(vue.Fragment, null, vue.renderList(_ctx.globalConfig.platformParams[_ctx.globalConfig.platformName].parts, (part) => {''',
    r'''        return vue.openBlock(), vue.createElementBlock("div", _hoisted_1$4, [
          vue.createElementVNode("div", { class: "setting-ai" }, [
            vue.createVNode(_component_el_divider, { "border-style": "dashed" }, {
              default: vue.withCtx(() => [
                vue.createElementVNode("span", { class: "setting-section-title" }, "AI")
              ]),
              _: 1
            }),
            vue.createVNode(_component_el_form_item, { class: "setting-ai-field", label: "API Key" }, {
              default: vue.withCtx(() => [
                vue.createVNode(_component_el_input, {
                  modelValue: _ctx.globalConfig.ai.deepseek.apiKey,
                  "onUpdate:modelValue": (v) => _ctx.globalConfig.ai.deepseek.apiKey = v,
                  placeholder: "DeepSeek API Key",
                  clearable: true,
                  size: "small"
                }, null, 8, ["modelValue"])
              ]),
              _: 2
            }, 1032, ["label"]),
            vue.createVNode(_component_el_form_item, { class: "setting-ai-field", label: "模型" }, {
              default: vue.withCtx(() => [
                vue.createVNode(_component_el_select, {
                  modelValue: _ctx.globalConfig.ai.deepseek.model,
                  "onUpdate:modelValue": (v) => _ctx.globalConfig.ai.deepseek.model = v,
                  size: "small"
                }, {
                  default: vue.withCtx(() => [
                    vue.createVNode(_component_el_option, { value: "deepseek-v4-pro", label: "DeepSeek V4 Pro" }),
                    vue.createVNode(_component_el_option, { value: "deepseek-flash", label: "DeepSeek Flash" })
                  ]),
                  _: 1
                }, 8, ["modelValue"])
              ]),
              _: 2
            }, 1032, ["label"])
          ]),
          (vue.openBlock(true), vue.createElementBlock(vue.Fragment, null, vue.renderList(_ctx.globalConfig.platformParams[_ctx.globalConfig.platformName].parts, (part) => {''',
    "B 配置页顶部插入 AI 卡片",
)

# ============ C. 鲸娘页：setup 头（去掉 configStore/ElInput 等，根节点改 div.whale-page） ============
sub_once(
    r'''      const configStore = useConfigStore();
      const getDisplayTitle = (question) => {''',
    r'''      const getDisplayTitle = (question) => {''',
    "C1 鲸娘页移除未用 configStore",
)

sub_once(
    r'''        const ElInput = vue.resolveComponent("el-input");
        const ElSelect = vue.resolveComponent("el-select");
        const ElOption = vue.resolveComponent("el-option");
        const ElTable = vue.resolveComponent("el-table");
        const ElTableColumn = vue.resolveComponent("el-table-column");
        const ElEmpty = vue.resolveComponent("el-empty");
        const ai = vue.unref(configStore).ai;
        return vue.openBlock(), vue.createElementBlock(vue.Fragment, null, [''',
    r'''        const ElTable = vue.resolveComponent("el-table");
        const ElTableColumn = vue.resolveComponent("el-table-column");
        return vue.openBlock(), vue.createElementBlock("div", { class: "whale-page" }, [''',
    "C2 鲸娘页根节点 Fragment -> div.whale-page",
)

# ============ D. 鲸娘页：ai-config -> whale-hero ============
sub_once(
    r'''          vue.createElementVNode("div", { class: "ai-config" }, [
            vue.createVNode(ElInput, {
              modelValue: ai.deepseek.apiKey,
              "onUpdate:modelValue": (v) => ai.deepseek.apiKey = v,
              placeholder: "DeepSeek API Key",
              clearable: true
            }, null, 8, ["modelValue"]),
            vue.createVNode(ElSelect, {
              modelValue: ai.deepseek.model,
              "onUpdate:modelValue": (v) => ai.deepseek.model = v,
              placeholder: "选择模型"
            }, {
              default: vue.withCtx(() => [
                vue.createVNode(ElOption, { value: "deepseek-v4-pro", label: "DeepSeek V4 Pro" }),
                vue.createVNode(ElOption, { value: "deepseek-flash", label: "DeepSeek Flash" })
              ]),
              _: 1
            }, 8, ["modelValue"])
          ]),''',
    r'''          vue.createElementVNode("div", {
            class: vue.normalizeClass(["whale-hero", _ctx.questionList.length ? "is-busy" : "is-idle"])
          }, [
            vue.createElementVNode("img", {
              class: "whale-hero__avatar",
              src: HX_LOGO_SRC,
              alt: "小鲸娘"
            }),
            vue.createElementVNode("div", { class: "whale-hero__bubble" }, [
              vue.createElementVNode("span", {
                class: "whale-hero__text"
              }, vue.toDisplayString(_ctx.questionList.length ? "主人别急，马上就好" : "小鲸娘正在吃白饭"), 1)
            ])
          ], 2),''',
    "D ai-config -> whale-hero（空闲/作答双态）",
)

# ============ E. 鲸娘页：删除 el-empty 空状态块 ============
sub_once(
    r'''          vue.withDirectives(vue.createElementVNode("div", null, [
            vue.createVNode(ElEmpty, { image: HX_LOGO_SRC, imageSize: 108, description: "小鲸娘正在吃白饭" })
          ], 512), [
            [vue.vShow, !_ctx.questionList.length]
          ]),
''',
    r''' ''',
    "E 移除 el-empty 空状态块",
)

# ============ F. CSS 追加 ============
CSS = r'''    + "\n.main-page .whale-page{flex:1 1 auto;min-height:0;display:flex;flex-direction:column;gap:8px;padding:2px 1px 0 1px;box-sizing:border-box;max-width:100%}"
    + "\n.main-page .whale-page>.question_table{flex:1 1 auto;min-height:0;overflow-y:auto;overflow-x:hidden}"
    + "\n.main-page .whale-page>.usage-bar{margin-top:0!important}"
    + "\n.main-page .whale-hero{flex:0 0 auto;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:10px;box-sizing:border-box;max-width:100%}"
    + "\n.main-page .whale-hero__avatar{display:block;width:44px;height:44px;object-fit:contain;border-radius:18px;background:radial-gradient(circle at 50% 40%,rgba(56,226,255,.16),rgba(6,14,30,.30));border:1px solid rgba(56,226,255,.24);box-shadow:0 4px 14px rgba(2,8,24,.30);transition:width .34s cubic-bezier(.34,1.24,.64,1),height .34s cubic-bezier(.34,1.24,.64,1),border-radius .34s ease}"
    + "\n.main-page .whale-hero__bubble{display:inline-flex;align-items:center;gap:6px;padding:2px 11px;border:1px solid var(--hx-line);border-radius:20px;background:var(--hx-glass);box-shadow:0 4px 14px rgba(2,8,24,.22);max-width:100%;box-sizing:border-box}"
    + "\n.main-page .whale-hero__text{font-size:12px;line-height:1.6;color:var(--hx-ink-dim);text-align:center;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;transition:font-size .34s ease}"
    + "\n.main-page .whale-hero.is-idle{flex:1 1 auto;min-height:0;gap:16px;padding:4px 0 18px}"
    + "\n.main-page .whale-hero.is-idle .whale-hero__avatar{width:156px;height:156px;border-radius:22px}"
    + "\n.main-page .whale-hero.is-idle .whale-hero__bubble{padding:5px 16px}"
    + "\n.main-page .whale-hero.is-idle .whale-hero__text{font-size:14px;color:var(--hx-ink)}"
    + "\n.main-page .whale-hero.is-busy{flex-direction:row;gap:9px;padding:2px 2px 0}"
    + "\n.main-page .whale-hero.is-busy .whale-hero__avatar{animation:hxWhaleBreath 2.4s ease-in-out infinite}"
    + "\n.main-page .whale-hero.is-busy .whale-hero__bubble{border-color:rgba(56,226,255,.26);background:rgba(56,226,255,.07)}"
    + "\n.main-page .whale-hero.is-busy .whale-hero__text{color:var(--hx-cyan)}"
    + "\n.main-page .whale-hero.is-busy .whale-hero__text:after{content:'';display:inline-block;width:1.1em;text-align:left;animation:hxWhaleDots 1.6s steps(1,end) infinite}"
    + "\n@keyframes hxWhaleBreath{0%,100%{transform:scale(1);box-shadow:0 4px 14px rgba(2,8,24,.30)}50%{transform:scale(1.07);box-shadow:0 4px 18px rgba(56,226,255,.34)}}"
    + "\n@keyframes hxWhaleDots{0%{content:''}25%{content:'.'}50%{content:'..'}75%{content:'...'}}"
    + "\n@media (prefers-reduced-motion:reduce){.main-page .whale-hero.is-busy .whale-hero__avatar,.main-page .whale-hero.is-busy .whale-hero__text:after{animation:none}}"
    + "\n.main-page .setting .el-form-item.setting-ai-field{display:flex!important;align-items:center;gap:8px}"
    + "\n.main-page .setting .el-form-item.setting-ai-field>.el-form-item__label{flex:0 0 54px;justify-content:flex-start!important;font-size:12px;color:var(--hx-ink-dim)!important}"
    + "\n.main-page .setting .el-form-item.setting-ai-field>.el-form-item__content{flex:1 1 auto;min-width:0;margin-left:0!important;display:flex}"
    + "\n.main-page .setting .el-form-item.setting-ai-field .el-input,.main-page .setting .el-form-item.setting-ai-field .el-select{width:100%!important}"
    + "\n.main-page .setting>div.setting-ai{border-color:rgba(56,226,255,.24)}"
'''

sub_once(
    r'''    + "\n.main-page .setting .el-input-number{width:112px!important}"''',
    r'''    + "\n.main-page .setting .el-input-number{width:112px!important}"
''' + CSS.rstrip("\r\n"),
    "F CSS 追加（鲸娘双态 + AI 卡片）",
)

# ============ 复核 ============
chk = [
    ('div.setting-ai', t.count('{ class: "setting-ai" }')),
    ('whale-page', t.count('class: "whale-page"')),
    ('whale-hero', t.count('"whale-hero"')),
    ('ElEmpty 调用', t.count('vue.createVNode(ElEmpty')),
    ('ai-config VNode', t.count('vue.createElementVNode("div", { class: "ai-config" }')),
    ('resolve el-input', t.count('resolveComponent("el-input")')),
    ('正文字符串 主人别急', t.count("主人别急，马上就好")),
    ('正文字符串 吃白饭', t.count("小鲸娘正在吃白饭")),
]
for k, v in chk:
    log.append("chk %s = %d" % (k, v))
assert chk[0][1] == 1, "setting-ai 卡片未生成"
assert chk[1][1] == 1, "whale-page 根节点未生成"
assert chk[3][1] == 0, "ElEmpty 调用仍有残留"
assert chk[4][1] == 0, "ai-config VNode 仍有残留"
assert chk[5][1] >= 1, "el-input resolve 全丢了"
assert chk[6][1] == 1, "作答态文案缺失"
assert chk[7][1] >= 1, "空闲态文案缺失"

crlf = t.count("\r\n")
bare = t.count("\n") - crlf
log.append("chars: %d -> %d ; CRLF=%d bareLF=%d" % (orig_len, len(t), crlf, bare))
assert bare == 0, "出现裸 LF"

with io.open(P, "w", encoding="utf-8", newline="") as f:
    f.write(t)

sys.stdout.write("\n".join(log) + "\n")
