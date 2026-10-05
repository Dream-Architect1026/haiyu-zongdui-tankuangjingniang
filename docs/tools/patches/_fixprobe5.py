# -*- coding: utf-8 -*-
"""fixprobe5：让探针支持 el-switch（模拟 EP 的 small 开关 + inline-prompt 开/关）。"""
import io, os

W = r"C:\Users\D_A\WorkBuddy\2026-10-05-13-53-42"
p = os.path.join(W, "_mkuiprobe.cjs")
s = io.open(p, encoding="utf-8", newline="").read()
L = []
NL = u"\r\n" if u"\r\n" in s else u"\n"

# ---------- 1) EP 样式：追加 el-switch ----------
css_anchor = u"  '.el-checkbox{display:inline-flex;align-items:center}',"
SW_CSS = (u"  '.el-switch{display:inline-flex;align-items:center;position:relative;height:16px;line-height:16px;vertical-align:middle}'," + NL +
          u"  '.el-switch__core{display:inline-flex;align-items:center;justify-content:center;position:relative;width:32px;height:16px;min-width:32px;border:1px solid #dcdfe6;border-radius:8px;background:#dcdfe6;cursor:pointer;box-sizing:border-box;transition:background-color .3s,border-color .3s}'," + NL +
          u"  '.el-switch.is-checked .el-switch__core{background:#409eff;border-color:#409eff}'," + NL +
          u"  '.el-switch__action{position:absolute;left:1px;top:1px;width:12px;height:12px;border-radius:50%;background:#fff;color:#409eff;display:flex;align-items:center;justify-content:center;font-size:9px;line-height:1;transition:left .3s}'," + NL +
          u"  '.el-switch.is-checked .el-switch__core .el-switch__action{left:calc(100% - 13px)}',")
if s.count(css_anchor) == 1:
    s = s.replace(css_anchor, css_anchor + NL + SW_CSS, 1)
    L.append(u"ok 1 追加 el-switch 样式")
else:
    L.append(u"!! 1 命中 %d" % s.count(css_anchor))

# ---------- 2) settingSections：checkbox -> switch 卡片 ----------
old_row = u"""s += '<label class="el-checkbox setting-checkbox"><span class="el-checkbox__label">自动答题开关 ' + k + "</span></label>";"""
new_row = (u"s += '<div class=\"el-form-item setting-switch\"><label class=\"el-form-item__label\">\u81ea\u52a8\u7b54\u9898\u5f00\u5173 ' + k + '</label>'"
           u"\n      + '<div class=\"el-form-item__content\"><div class=\"el-switch el-switch--small' + (k % 2 ? \" is-checked\" : \"\") + '\">'"
           u"\n      + '<span class=\"el-switch__core\"><span class=\"el-switch__action\">' + (k % 2 ? \"\u5f00\" : \"\u5173\") + '</span></span>'"
           u"\n      + \"</div></div></div>\";")
new_row = new_row.replace(u"\n", NL)
if s.count(old_row) == 1:
    s = s.replace(old_row, new_row, 1)
    L.append(u"ok 2 settingSections -> switch 卡片")
else:
    L.append(u"!! 2 命中 %d" % s.count(old_row))

# ---------- 3) measure：加开关测量 ----------
m_anchor = u'out.settingSectionTitle = cs(setting.querySelector(".setting-section-title"), "color");'
MEASURE = m_anchor + NL + (u"""var sw0 = setting.querySelector(".setting-switch");
if (sw0) {
  var swLab = sw0.querySelector(".el-form-item__label");
  var swCtl = sw0.querySelector(".el-form-item__content");
  var swEl = sw0.querySelector(".el-switch");
  var swCore = sw0.querySelector(".el-switch__core");
  var swAct = sw0.querySelector(".el-switch__action");
  out.swCard = R(sw0);
  out.swLabel = R(swLab);
  out.swCtrl = R(swCtl);
  out.swEl = R(swEl);
  out.swCore = R(swCore);
  out.swAction = R(swAct);
  out.swCount = setting.querySelectorAll(".setting-switch").length;
  out.sw_labelLeftOfCtrl = R(swLab).right <= R(swCtl).left + 1;
  out.sw_ctrlPushedRight = (R(sw0).right - R(swCtl).right) <= 12;
  out.sw_coreCheckedBg = cs(swCore, "background-color");
  out.sw_actionInsideCore = R(swAct).left > R(swCore).left && R(swAct).right < R(swCore).right;
  out.sw_isSwitch = !!swEl;
  out.sw_leftoverCheckbox = setting.querySelectorAll(".el-checkbox").length;
}""").replace(u"\n", NL)
if s.count(m_anchor) == 1:
    s = s.replace(m_anchor, MEASURE, 1)
    L.append(u"ok 3 加开关测量")
else:
    L.append(u"!! 3 命中 %d" % s.count(m_anchor))

io.open(p, "w", encoding="utf-8", newline="").write(s)
io.open(os.path.join(W, "_fixprobe5.txt"), "w", encoding="utf-8").write(u"\n".join(L))
print(u"\n".join(L))
