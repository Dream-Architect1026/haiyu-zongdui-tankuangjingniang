# -*- coding: utf-8 -*-
"""fixprobe6：把 _mkshot.cjs（出预览图用）也同步成 el-switch。"""
import io, os

W = r"C:\Users\D_A\WorkBuddy\2026-10-05-13-53-42"
p = os.path.join(W, "_mkshot.cjs")
s = io.open(p, encoding="utf-8", newline="").read()
L = []
NL = u"\r\n" if u"\r\n" in s else u"\n"

css_anchor = u"  '.el-checkbox{display:inline-flex;align-items:center}',"
SW_CSS = (u"  '.el-switch{display:inline-flex;align-items:center;position:relative;height:16px;line-height:16px;vertical-align:middle}'," + NL +
          u"  '.el-switch__core{display:inline-flex;align-items:center;justify-content:center;position:relative;width:32px;height:16px;min-width:32px;border:1px solid #dcdfe6;border-radius:8px;background:#dcdfe6;cursor:pointer;box-sizing:border-box;transition:background-color .3s,border-color .3s}'," + NL +
          u"  '.el-switch.is-checked .el-switch__core{background:#409eff;border-color:#409eff}'," + NL +
          u"  '.el-switch__action{position:absolute;left:1px;top:1px;width:12px;height:12px;border-radius:50%;background:#fff;color:#409eff;display:flex;align-items:center;justify-content:center;font-size:9px;line-height:1;transition:left .3s}'," + NL +
          u"  '.el-switch.is-checked .el-switch__core .el-switch__action{left:calc(100% - 13px)}',")
if s.count(css_anchor) == 1:
    s = s.replace(css_anchor, css_anchor + NL + SW_CSS, 1)
    L.append(u"ok 1 el-switch 样式")
else:
    L.append(u"!! 1 命中 %d" % s.count(css_anchor))

old_row = u"""s += '<label class="el-checkbox setting-checkbox"><span class="el-checkbox__label">\u5df2\u542f\u7528</span></label>';"""
new_row = (u"s += '<div class=\"el-form-item setting-switch\"><label class=\"el-form-item__label\">\u5df2\u542f\u7528</label>'"
           u"\n      + '<div class=\"el-form-item__content\"><div class=\"el-switch el-switch--small is-checked\">'"
           u"\n      + '<span class=\"el-switch__core\"><span class=\"el-switch__action\">\u5f00</span></span>'"
           u"\n      + \"</div></div></div>\";").replace(u"\n", NL)
if s.count(old_row) == 1:
    s = s.replace(old_row, new_row, 1)
    L.append(u"ok 2 checkbox -> switch")
else:
    L.append(u"!! 2 命中 %d" % s.count(old_row))

io.open(p, "w", encoding="utf-8", newline="").write(s)
io.open(os.path.join(W, "_fixprobe6.txt"), "w", encoding="utf-8").write(u"\n".join(L))
print(u"\n".join(L))
