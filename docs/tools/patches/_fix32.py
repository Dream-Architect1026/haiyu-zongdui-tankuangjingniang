# -*- coding: utf-8 -*-
"""fix32：配置页布尔项 el-checkbox -> el-switch（标签在左、开关在右）。

改动：
 1) 注册 el-switch 组件
 2) platformParams 的 boolean 分支：el-checkbox(label) -> el-form-item(label, class=setting-switch) 内嵌 el-switch
 3) otherParams 的 boolean 分支：同上
 4) 追加 .setting-switch 布局 CSS（space-between 让开关贴右）+ 深色主题开关配色
"""
import io, os

P = r"C:\Users\D_A\DoubaoWork\chats\2026-10-05\new-chat-4\海底小纵队·探矿鲸娘.user.js"
L = []

src = io.open(P, encoding="utf-8", newline="").read()
orig_len = len(src)

# ---------- 1) 注册组件 ----------
old_reg = u'        const _component_el_checkbox = vue.resolveComponent("el-checkbox");'
new_reg = old_reg + u'\r\n        const _component_el_switch = vue.resolveComponent("el-switch");'
if src.count(old_reg) == 1:
    src = src.replace(old_reg, new_reg, 1)
    L.append(u"ok 1 注册 el-switch")
else:
    L.append(u"!! 1 命中 %d" % src.count(old_reg))

# ---------- 2) platformParams boolean 分支 ----------
a1 = u'param.type === "boolean" ? (vue.openBlock(), vue.createBlock(_component_el_checkbox, {'
e1 = u'"onUpdate:modelValue", "label"]))'
i1 = src.find(a1)
if i1 < 0:
    L.append(u"!! 2 未找到 platformParams boolean 分支")
else:
    j1 = src.find(e1, i1)
    if j1 < 0:
        L.append(u"!! 2 未找到 platformParams 结束锚点")
    else:
        j1 += len(e1)
        NEW1 = (u'param.type === "boolean" ? (vue.openBlock(), vue.createBlock(_component_el_form_item, {\r\n'
                u'                    key: 0,\r\n'
                u'                    class: "setting-switch",\r\n'
                u'                    label: param.name\r\n'
                u'                  }, {\r\n'
                u'                    default: vue.withCtx(() => [\r\n'
                u'                      vue.createVNode(_component_el_switch, {\r\n'
                u'                        modelValue: param.value,\r\n'
                u'                        "onUpdate:modelValue": ($event) => param.value = $event,\r\n'
                u'                        "inline-prompt": true,\r\n'
                u'                        "active-text": "\u5f00",\r\n'
                u'                        "inactive-text": "\u5173",\r\n'
                u'                        size: "small"\r\n'
                u'                      }, null, 8, ["modelValue", "onUpdate:modelValue"])\r\n'
                u'                    ]),\r\n'
                u'                    _: 2\r\n'
                u'                  }, 1032, ["label"]))')
        src = src[:i1] + NEW1 + src[j1:]
        L.append(u"ok 2 platformParams boolean -> switch")

# ---------- 3) otherParams boolean 分支 ----------
a2 = u'item.type === "boolean" ? (vue.openBlock(), vue.createBlock(_component_el_checkbox, {'
e2 = u'"onUpdate:modelValue"]))'
i2 = src.find(a2)
if i2 < 0:
    L.append(u"!! 3 未找到 otherParams boolean 分支")
else:
    j2 = src.find(e2, i2)
    if j2 < 0:
        L.append(u"!! 3 未找到 otherParams 结束锚点")
    else:
        j2 += len(e2)
        NEW2 = (u'item.type === "boolean" ? (vue.openBlock(), vue.createBlock(_component_el_form_item, {\r\n'
                u'                  key: 0,\r\n'
                u'                  class: "setting-switch",\r\n'
                u'                  label: item.name\r\n'
                u'                }, {\r\n'
                u'                  default: vue.withCtx(() => [\r\n'
                u'                    vue.createVNode(_component_el_switch, {\r\n'
                u'                      modelValue: item.value,\r\n'
                u'                      "onUpdate:modelValue": ($event) => item.value = $event,\r\n'
                u'                      "inline-prompt": true,\r\n'
                u'                      "active-text": "\u5f00",\r\n'
                u'                      "inactive-text": "\u5173",\r\n'
                u'                      size: "small"\r\n'
                u'                    }, null, 8, ["modelValue", "onUpdate:modelValue"])\r\n'
                u'                  ]),\r\n'
                u'                  _: 2\r\n'
                u'                }, 1032, ["label"]))')
        src = src[:i2] + NEW2 + src[j2:]
        L.append(u"ok 3 otherParams boolean -> switch")

# ---------- 4) CSS ----------
css_anchor = u'.main-page .setting .el-checkbox__label{font-size:12px;color:var(--hx-ink)!important}"'
if src.count(css_anchor) != 1:
    L.append(u"!! 4 CSS 锚点命中 %d" % src.count(css_anchor))
else:
    CSS = [
        u'.main-page .setting .el-form-item.setting-switch{display:flex!important;align-items:center;justify-content:space-between;gap:8px;height:28px;margin:0!important;padding:0 9px;border:1px solid var(--hx-line);border-radius:9px;background:rgba(6,14,30,.42);transition:border-color .2s,background .2s}',
        u'.main-page .setting .el-form-item.setting-switch:hover{border-color:rgba(56,226,255,.42);background:rgba(56,226,255,.08)}',
        u'.main-page .setting .el-form-item.setting-switch>.el-form-item__label{flex:1 1 auto;min-width:0;margin:0!important;padding:0!important;font-size:12px;line-height:1.3;color:var(--hx-ink)!important;text-align:left;justify-content:flex-start}',
        u'.main-page .setting .el-form-item.setting-switch>.el-form-item__content{flex:0 0 auto;margin-left:auto!important;display:flex;justify-content:flex-end;align-items:center;min-width:0;line-height:1}',
        u'.main-page .setting .el-form-item.setting-switch .el-form-item__error{display:none}',
        u'.main-page .setting .el-switch{--el-switch-on-color:var(--hx-cyan,#38e2ff);--el-switch-off-color:rgba(255,255,255,.12)}',
        u'.main-page .setting .el-switch .el-switch__core{border-color:rgba(120,190,255,.30)}',
        u'.main-page .setting .el-switch.is-checked .el-switch__core{border-color:transparent}',
        u'.main-page .setting .el-switch.is-checked .el-switch__core .el-switch__action{color:var(--hx-cyan,#38e2ff)}',
    ]
    add = u"".join(u'\r\n    + "\\n' + c + u'"' for c in CSS)
    src = src.replace(css_anchor, css_anchor + add, 1)
    L.append(u"ok 4 CSS 追加 %d 条" % len(CSS))

bad = [x for x in L if x.startswith("!!")]
io.open(P, "w", encoding="utf-8", newline="").write(src)
crlf = src.count(u"\r\n")
bare = src.count(u"\n") - crlf
L.append(u"chars: %d -> %d ; CRLF=%d bareLF=%d" % (orig_len, len(src), crlf, bare))
io.open(r"C:\Users\D_A\WorkBuddy\2026-10-05-13-53-42\_fix32.txt", "w", encoding="utf-8").write(u"\n".join(L))
print(u"\n".join(L))
if bad:
    print("HAS_FAIL")
