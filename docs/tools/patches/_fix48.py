# -*- coding: utf-8 -*-
"""
0.4.8 -> 0.4.9
好感度系统：按「累计花费」分级解锁鲸娘语录
  Lv.1 ¥0 初见(陌生的小鲸娘) / Lv.2 ¥1 搭话(点头之交) / Lv.3 ¥2 熟络(常来串门)
  Lv.4 ¥5 亲密(形影不离) / Lv.5 ¥10 相伴(鲸生有你)   —— 每级 10 条，满级 50 条
  UI 放在配置页 AI 卡片「小名」下方，带 ⓘ 说明按钮；空闲语录只从已解锁池随机取。
"""
import os
import re
import sys

P = r"C:\Users\D_A\DoubaoWork\chats\2026-10-05\new-chat-4\海底小纵队·探矿鲸娘.user.js"
OUT = r"C:\Users\D_A\WorkBuddy\2026-10-05-13-53-42\_f48out.txt"
DRY = "--dry" in sys.argv
OLD_VER = "0.4.8"
NEW_VER = "0.4.9"

log = []
def w(x):
    log.append(str(x))

raw = open(P, "rb").read().decode("utf-8")
s = raw.replace("\r\n", "\n")
orig_len = len(s)

# ── 0. 版本号替换（白名单闸门）─────────────────────────────
hits = list(re.finditer(re.escape(OLD_VER), s))
w("=== 版本号 %s 出现 %d 处 ===" % (OLD_VER, len(hits)))
bad = []
for m in hits:
    ctx = s[max(0, m.start() - 46): m.end() + 46].replace("\n", "\\n")
    ok = bool(re.search(r"(@version|HX_BUILD|v0\.|/\*|// ----|License|面板|已就位|已加载|液态玻璃|背景脉动光|可见光带|标签|hero)", ctx))
    w("  [%s] %s" % ("OK" if ok else "??", ctx))
    if not ok:
        bad.append(ctx)
if bad:
    w("!! 有非版本字面量的 %s，已中止" % OLD_VER)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    open(OUT, "w", encoding="utf-8").write("\n".join(log))
    sys.exit(1)
s = s.replace(OLD_VER, NEW_VER)

# ── 1. 空闲文案池 → 好感度分档池（含小名解析与取池逻辑）─────
OLD_POOL = (
    '  const HX_IDLE_LINES = ["{n}正在吃白饭", "{n}在等主人投喂", "{n}在啃数据海草", '
    '"{n}在数小金库", "{n}在磨鲸须", "{n}偷偷打了个哈欠", "{n}在打捞海底的算力", '
    '"{n}在擦亮小铜铃", "{n}在数今天的星星"];\n'
    '  const hxPetName = () => {\n'
    '    try {\n'
    '      const text = getStoredConfigText();\n'
    '      if (!text) return HX_DEFAULT_PET;\n'
    '      const parsed = JSON.parse(text);\n'
    '      const name = parsed && parsed.ai && parsed.ai.petName;\n'
    '      const trimmed = typeof name === "string" ? name.trim() : "";\n'
    '      return trimmed || HX_DEFAULT_PET;\n'
    '    } catch (error) { return HX_DEFAULT_PET; }\n'
    '  };\n'
    '  const hxLineText = (idx) => HX_IDLE_LINES[idx].split("{n}").join(hxPetName());\n'
    '  let hxIdleLineIdx = Math.floor(Math.random() * HX_IDLE_LINES.length);\n'
    '  let hxIdleLine = hxLineText(hxIdleLineIdx);'
)

TIERS = [
    (1, 0, "初见", "陌生的小鲸娘", [
        "{n}正在吃白饭", "{n}在等主人投喂", "{n}在啃数据海草", "{n}在数小金库",
        "{n}在磨鲸须", "{n}偷偷打了个哈欠", "{n}在打捞海底的算力", "{n}在擦亮小铜铃",
        "{n}在数今天的星星", "{n}刚游过来，还在认路～",
    ]),
    (2, 1, "搭话", "点头之交", [
        "{n}朝主人挥了挥鳍", "{n}在主人门口转圈圈", "{n}把海草摆整齐等主人",
        "{n}记住了主人的味道", "{n}备好了一口袋小鱼干", "{n}悄悄靠近了一点点",
        "{n}从珊瑚后探头看主人", "{n}学会叫主人了", "{n}把最好的贝壳留给主人",
        "{n}今天游得比昨天近了一点",
    ]),
    (3, 2, "熟络", "常来串门", [
        "{n}主动凑过来蹭了蹭主人", "{n}想和主人一起看海", "{n}端出了珍藏的海藻茶",
        "{n}在主人脚边打了个滚", "{n}偷偷把主人写进日记", "{n}开始期待主人上线了",
        "{n}说今天也想被摸摸头", "{n}把浪花梳成了爱心", "{n}在旁边轻轻哼起鲸歌",
        "{n}已经敢抢主人的话了",
    ]),
    (4, 5, "亲密", "形影不离", [
        "{n}一刻都不想离开主人", "{n}把尾巴缠在主人手腕上", "{n}说今天也要一起加油呀",
        "{n}偷偷给主人准备了惊喜", "{n}因为主人来晚了闷闷不乐", "{n}只想被主人一个人看见",
        "{n}把整片海都搬来送给主人", "{n}说主人的名字最好听了", "{n}贴着屏幕想钻进主人怀里",
        "{n}已经算好主人何时回来了",
    ]),
    (5, 10, "相伴", "鲸生有你", [
        "{n}把心口最暖的地方留给主人", "{n}游遍整片海也只认主人", "{n}说下辈子还做主人的鲸",
        "{n}愿意为主人在沙滩上搁浅", "{n}把星星摘下来串成项链", "{n}说主人在就不怕深海",
        "{n}把主人写进了「家」里", "{n}想陪主人走完所有潮汐", "{n}说主人就是我的整片海",
        "{n}和主人，从此再不分开",
    ]),
]


def tier_obj(t):
    lv, at, name, tag, lines = t
    inner = ", ".join('"%s"' % x for x in lines)
    return '{ lv: %d, at: %d, name: "%s", tag: "%s", lines: [%s] }' % (lv, at, name, tag, inner)


TIER_JS = ",\n    ".join(tier_obj(t) for t in TIERS)

NEW_POOL = (
    '  const HX_FAV_TIERS = [\n    ' + TIER_JS + '\n  ];\n'
    '  const hxFavCost = () => {\n'
    '    try {\n'
    '      const c = Number(usageStore.cost);\n'
    '      if (isFinite(c) && c > 0) return c;\n'
    '    } catch (error) { /* 忽略 */ }\n'
    '    return 0;\n'
    '  };\n'
    '  const hxFavLevelIdx = () => {\n'
    '    const c = hxFavCost();\n'
    '    let lv = 0;\n'
    '    for (let i = 0; i < HX_FAV_TIERS.length; i += 1) {\n'
    '      if (c >= HX_FAV_TIERS[i].at) lv = i;\n'
    '    }\n'
    '    return lv;\n'
    '  };\n'
    '  const hxFavTotalLines = () => {\n'
    '    let n = 0;\n'
    '    for (let i = 0; i < HX_FAV_TIERS.length; i += 1) {\n'
    '      n += HX_FAV_TIERS[i].lines.length;\n'
    '    }\n'
    '    return n;\n'
    '  };\n'
    '  const hxUnlockedLines = () => {\n'
    '    const lv = hxFavLevelIdx();\n'
    '    const pool = [];\n'
    '    for (let i = 0; i <= lv; i += 1) {\n'
    '      const tier = HX_FAV_TIERS[i];\n'
    '      if (tier && tier.lines) pool.push.apply(pool, tier.lines);\n'
    '    }\n'
    '    return pool.length ? pool : ["{n}正在吃白饭"];\n'
    '  };\n'
    '  const hxLineCount = () => hxUnlockedLines().length;\n'
    '  const hxPetName = () => {\n'
    '    try {\n'
    '      const text = getStoredConfigText();\n'
    '      if (!text) return HX_DEFAULT_PET;\n'
    '      const parsed = JSON.parse(text);\n'
    '      const name = parsed && parsed.ai && parsed.ai.petName;\n'
    '      const trimmed = typeof name === "string" ? name.trim() : "";\n'
    '      return trimmed || HX_DEFAULT_PET;\n'
    '    } catch (error) { return HX_DEFAULT_PET; }\n'
    '  };\n'
    '  const hxLineText = (idx) => {\n'
    '    const pool = hxUnlockedLines();\n'
    '    const n = pool.length;\n'
    '    const raw = pool[((idx % n) + n) % n];\n'
    '    return String(raw).split("{n}").join(hxPetName());\n'
    '  };\n'
    '  let hxIdleLineIdx = Math.floor(Math.random() * hxLineCount());\n'
    '  let hxIdleLine = hxLineText(hxIdleLineIdx);'
)

# ── 2. 好感度 UI（配置页 AI 卡片，小名下方）────────────────
FAV_UI = '''  /* ── 好感度面板：挂在小名下面，ⓘ 可展开说明 ───────────── */
  let hxFavOpen = false;
  let hxFavTimer = null;
  const hxFavTierRows = () => HX_FAV_TIERS.map((tier) => '<li><span>Lv.' + tier.lv + ' · ¥' + tier.at + '</span><span>' + tier.name + '（' + tier.tag + '）· ' + tier.lines.length + ' 条</span></li>').join('');
  const hxFavNoteHtml = () => '<div class="fav-note">'
    + '<div>好感度跟着<b>累计花费</b>一起长——就是这台机器上为小鲸娘花掉的 token 钱，装好脚本以后一直累加，不随刷新清零。</div>'
    + '<ul class="fav-tiers">' + hxFavTierRows() + '</ul>'
    + '<div>每跨过一档多解锁 10 条语录，满级共 ' + hxFavTotalLines() + ' 条。语录只在她空闲时滚动播放；取的「小名」会自动替掉语录里的「小鲸娘」。</div>'
    + '</div>';
  const hxFavShellHtml = () => '<div class="fav-head">'
    + '<span class="fav-label">好感度</span>'
    + '<span class="fav-lv">Lv.1 · —</span>'
    + '<span class="fav-info" role="button" tabindex="0" title="好感度机制说明">i</span>'
    + '</div>'
    + '<div class="fav-bar"><i></i></div>'
    + '<div class="fav-meta"><span>—</span><span>—</span></div>'
    + hxFavNoteHtml();
  const paintFavCard = (el) => {
    if (!el) return;
    const idx = hxFavLevelIdx();
    const tier = HX_FAV_TIERS[idx] || HX_FAV_TIERS[0];
    const next = HX_FAV_TIERS[idx + 1] || null;
    const cost = hxFavCost();
    const lvEl = el.querySelector('.fav-lv');
    if (lvEl) {
      const txt = 'Lv.' + tier.lv + ' · ' + tier.name + ' · ' + tier.tag;
      if (lvEl.textContent !== txt) lvEl.textContent = txt;
    }
    const barEl = el.querySelector('.fav-bar > i');
    if (barEl) {
      const span = next ? Math.max(next.at - tier.at, 0.0001) : 1;
      const pct = next ? Math.max(0, Math.min(100, ((cost - tier.at) / span) * 100)) : 100;
      const wv = pct.toFixed(1) + '%';
      if (barEl.style.width !== wv) barEl.style.width = wv;
    }
    const metaEl = el.querySelector('.fav-meta');
    if (metaEl) {
      const left = '累计 ' + formatCost(cost) + ' · 已解锁 ' + hxLineCount() + '/' + hxFavTotalLines() + ' 条';
      const right = next ? '距 Lv.' + next.lv + ' 还差 ' + formatCost(Math.max(next.at - cost, 0)) : '已满级 · 语录全解锁';
      const html = '<span>' + left + '</span><span>' + right + '</span>';
      if (metaEl.innerHTML !== html) metaEl.innerHTML = html;
    }
  };
  const mountFavCard = () => {
    const root = hxShadow;
    if (!root) return false;
    const pet = root.querySelector('.setting-ai .setting-pet-field');
    if (!pet || !pet.parentNode) return false;
    let el = root.querySelector('.setting-ai .setting-fav-field');
    if (!el) {
      el = document.createElement('div');
      el.className = 'setting-fav-field';
      el.innerHTML = hxFavShellHtml();
      pet.parentNode.insertBefore(el, pet.nextSibling);
      const info = el.querySelector('.fav-info');
      if (info) {
        const toggle = (ev) => {
          if (ev) { ev.preventDefault(); ev.stopPropagation(); }
          hxFavOpen = !hxFavOpen;
          el.classList.toggle('is-open', hxFavOpen);
        };
        info.addEventListener('click', toggle);
        info.addEventListener('keydown', (ev) => {
          if (ev && (ev.key === 'Enter' || ev.key === ' ')) toggle(ev);
        });
      }
    }
    el.classList.toggle('is-open', hxFavOpen);
    paintFavCard(el);
    return true;
  };
  const bindFavCard = () => {
    const ensure = () => {
      try { mountFavCard(); } catch (error) { /* 忽略 */ }
    };
    ensure();
    if (hxFavTimer === null) hxFavTimer = setInterval(ensure, 1500);
  };
'''

# ── 3. 新增 CSS（最后一个 push，一定赢）────────────────────
CSS_RULES = [
    "/* ==== v0.4.9 : 好感度面板（累计花费分级解锁语录）==== */",
    ".main-page .setting-fav-field{margin:2px 0 8px;padding:8px 10px 9px;border:1px solid rgba(140,200,255,.20);border-radius:12px;background:linear-gradient(160deg,rgba(56,226,255,.09),rgba(155,107,255,.07));backdrop-filter:blur(11px) saturate(140%);-webkit-backdrop-filter:blur(11px) saturate(140%);transition:border-color .28s ease,box-shadow .28s ease}",
    ".main-page .setting-fav-field:hover{border-color:rgba(120,225,255,.42);box-shadow:0 6px 18px rgba(6,20,44,.30)}",
    ".main-page .fav-head{display:flex;align-items:center;gap:6px;line-height:16px}",
    ".main-page .fav-label{flex:0 0 auto;font-size:11px;font-weight:600;color:var(--hx-ink);letter-spacing:.4px}",
    ".main-page .fav-lv{flex:0 1 auto;min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;font-size:10.5px;padding:1px 7px;border-radius:20px;border:1px solid rgba(120,225,255,.38);color:#8ce8ff;background:rgba(56,226,255,.10)}",
    ".main-page .fav-info{margin-left:auto;flex:0 0 auto;width:15px;height:15px;padding:0;line-height:13px;text-align:center;font-size:10px;font-style:italic;font-weight:700;font-family:Georgia,serif;color:#9fd8ff;border:1px solid rgba(140,200,255,.45);border-radius:50%;background:rgba(255,255,255,.06);cursor:pointer;-webkit-user-select:none;user-select:none;transition:color .24s ease,border-color .24s ease,box-shadow .24s ease}",
    ".main-page .fav-info:hover{color:#fff;border-color:#8ce8ff;box-shadow:0 0 9px rgba(56,226,255,.55)}",
    ".main-page .fav-bar{margin:7px 0 5px;height:5px;border-radius:20px;background:rgba(255,255,255,.09);overflow:hidden}",
    ".main-page .fav-bar>i{display:block;height:100%;width:0;border-radius:20px;background:linear-gradient(90deg,#38e2ff,#9b6bff);box-shadow:0 0 8px rgba(56,226,255,.55);transition:width .5s cubic-bezier(.22,1,.36,1)}",
    ".main-page .fav-meta{display:flex;align-items:center;justify-content:space-between;gap:8px;font-size:10px;line-height:14px;color:var(--hx-ink-dim);font-variant-numeric:tabular-nums}",
    ".main-page .fav-meta>span{overflow:hidden;text-overflow:ellipsis;white-space:nowrap}",
    ".main-page .fav-note{display:none;margin-top:8px;padding-top:7px;border-top:1px dashed rgba(140,200,255,.22);font-size:10.2px;line-height:16px;color:var(--hx-ink-dim)}",
    ".main-page .setting-fav-field.is-open .fav-note{display:block;animation:favNoteIn .3s ease both}",
    ".main-page .fav-note b{color:#8ce8ff;font-weight:600}",
    ".main-page .fav-note .fav-tiers{margin:5px 0 0;padding:0;list-style:none}",
    ".main-page .fav-note .fav-tiers li{display:flex;gap:6px;line-height:15px}",
    ".main-page .fav-note .fav-tiers li>span:first-child{flex:0 0 62px;color:#9fd8ff}",
    "@keyframes favNoteIn{from{opacity:0}to{opacity:1}}",
    "@media (prefers-reduced-motion: reduce){.main-page .fav-bar>i,.main-page .setting-fav-field{transition:none!important}.main-page .setting-fav-field.is-open .fav-note{animation:none!important}}",
]

_css_lines = []
for i, rule in enumerate(CSS_RULES):
    prefix = '    "' if i == 0 else '    + "'
    _css_lines.append(prefix + '\\n' + rule + '"\n')
CSS_JS = (
    "\n  // ---- v0.4.9 ----\n"
    "  LAYOUT_CSS_PARTS.push(\n"
    + "".join(_css_lines)
    + "  );\n"
)

# ── 4. 探针 / 诊断 ─────────────────────────────────────────
PROBE = (
    "      w.__HX_FAV__ = () => {\n"
    "        const i = hxFavLevelIdx();\n"
    "        const t = HX_FAV_TIERS[i] || HX_FAV_TIERS[0];\n"
    "        const nx = HX_FAV_TIERS[i + 1] || null;\n"
    "        return { cost: hxFavCost(), level: t.lv, name: t.name, tag: t.tag, unlocked: hxLineCount(), total: hxFavTotalLines(), nextAt: nx ? nx.at : null, note: hxFavOpen, mounted: !!(hxShadow && hxShadow.querySelector('.setting-fav-field')) };\n"
    "      };\n"
)

DIAG = (
    "          petName: hxPetName(),\n"
    "          fav: { cost: hxFavCost(), level: hxFavLevelIdx() + 1, unlocked: hxLineCount(), total: hxFavTotalLines(), mounted: !!(hxShadow && hxShadow.querySelector('.setting-fav-field')) },\n"
)

# ── 应用 ───────────────────────────────────────────────────
patches = [
    ("空闲池→好感度池", OLD_POOL, NEW_POOL, 1),
    ("roll 上限", "    if (HX_IDLE_LINES.length > 1) {", "    if (hxLineCount() > 1) {", 1),
    ("roll 取随机", "        next = Math.floor(Math.random() * HX_IDLE_LINES.length);",
     "        next = Math.floor(Math.random() * hxLineCount());", 1),
    ("好感度 UI 块", "  const CAN_USE_ADOPTED_SHEETS = (() => {",
     FAV_UI + "\n  const CAN_USE_ADOPTED_SHEETS = (() => {", 1),
    ("绑定调用", "      try { bindTabRouter(); } catch (error2) { /* 忽略 */ }\n",
     "      try { bindTabRouter(); } catch (error2) { /* 忽略 */ }\n"
     "      try { bindFavCard(); } catch (error2) { /* 忽略 */ }\n", 1),
    ("探针 __HX_FAV__", "applied: hxDefaultTabApplied });\n",
     "applied: hxDefaultTabApplied });\n" + PROBE, 1),
    ("DIAG fav", "          petName: hxPetName(),\n", DIAG, 1),
    ("新 CSS 块", 'const layoutCss = LAYOUT_CSS_PARTS.join("");',
     CSS_JS + '\nconst layoutCss = LAYOUT_CSS_PARTS.join("");', 1),
]

w("")
w("=== 补丁预检（共 %d 项）===" % len(patches))
fails = []
for name, old, new, exp in patches:
    cnt = s.count(old)
    flag = "OK" if cnt == exp else "NG"
    w("  [%s] %-18s 期望=%d 实际=%d" % (flag, name, exp, cnt))
    if cnt != exp:
        fails.append("%s: 期望 %d 实际 %d" % (name, exp, cnt))
        w("       << %s" % old[:110].replace("\n", "\\n"))

# 目标侧不应存在的旧标识符
w("")
w("=== 负向自检 ===")
w("  HX_IDLE_LINES 现存 = %d（应被全部替换）" % s.count("HX_IDLE_LINES"))
w("  setting-pet-field 现存 = %d（小名锚点）" % s.count("setting-pet-field"))
w("  HX_FAV_TIERS 现存 = %d" % s.count("HX_FAV_TIERS"))
if s.count("setting-pet-field") < 2:
    fails.append("setting-pet-field 锚点不足（小名输入未就位）")

if fails:
    w("")
    w("!! 预检失败，未写入任何改动：")
    for f in fails:
        w("   - " + f)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    open(OUT, "w", encoding="utf-8").write("\n".join(log))
    sys.exit(1)

w("")
w("全部匹配，开始写入…")
for name, old, new, exp in patches:
    s = s.replace(old, new)

# ── 写入后自检 ─────────────────────────────────────────────
left = s.count("HX_IDLE_LINES")
w("")
w("=== 写入后自检 ===")
w("  HX_IDLE_LINES 残留 = %d" % left)
w("  hxLineCount 出现 = %d" % s.count("hxLineCount"))
w("  HX_FAV_TIERS 出现 = %d" % s.count("HX_FAV_TIERS"))
w("  {n} 占位 = %d" % s.count("{n}"))
if left != 0:
    w("!! 残留旧标识符，判定失败")
    open(OUT, "w", encoding="utf-8").write("\n".join(log))
    sys.exit(1)

out_bytes = s.replace("\n", "\r\n").encode("utf-8")
crlf = s.count("\n")
w("")
w("orig_chars=%d  new_chars=%d" % (orig_len, len(s)))
w("bytes=%d  crlf=%d  bare_lf=0" % (len(out_bytes), crlf))

if DRY:
    w("")
    w("DRY RUN —— 未写入文件")
else:
    open(P, "wb").write(out_bytes)
    w("")
    w("已写入：%s" % P)

os.makedirs(os.path.dirname(OUT), exist_ok=True)
open(OUT, "w", encoding="utf-8").write("\n".join(log))
