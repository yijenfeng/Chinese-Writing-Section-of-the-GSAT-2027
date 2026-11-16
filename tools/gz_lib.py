# -*- coding: utf-8 -*-
"""國綜單元產生器的共用元件。執行方式見 tools/build_guozong.py。"""
import html
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SELF = "自編練習題：非歷屆試題，也非大考中心練習題"


def shared_css():
    """沿用國寫單元頁的樣式，確保新舊頁面外觀一致。"""
    s = open(os.path.join(ROOT, "看題判斷題型.html"), encoding="utf-8").read()
    return s[s.index("<style>") + 7 : s.index("</style>")]


EXTRA_CSS = """
  .sh-top{ display:flex; flex-wrap:wrap; gap:0.4rem 1rem; align-items:center; font-size:0.9rem; margin:0.4rem 0 0.8rem; }
  .sh-rows{ display:grid; grid-template-columns:repeat(auto-fill,minmax(250px,1fr)); gap:0.35rem 1rem; }
  .sh-row{ display:flex; align-items:center; gap:0.4rem; padding:0.25rem 0.4rem; border-radius:6px; }
  .sh-row.ok{ background:color-mix(in srgb, var(--ab) 22%, transparent); }
  .sh-row.bad{ background:var(--accent-soft); }
  .sh-no{ font-family:'JetBrains Mono',monospace; font-size:0.85rem; width:2em; text-align:right; color:var(--ink-muted); flex:none; }
  .sh-b{ width:2.1rem; height:2.1rem; border-radius:50%; border:1px solid var(--line); background:var(--surface); cursor:pointer; font-size:0.85rem; padding:0; flex:none; }
  .sh-b.on{ background:var(--accent); color:var(--accent-ink); border-color:var(--accent); }
  .sh-b:focus-visible{ outline:2px solid var(--accent); outline-offset:2px; }
  .sh-b:disabled{ cursor:default; }
  .sh-b.key{ box-shadow:0 0 0 2px var(--ab); }
  .sh-mark{ font-size:0.78rem; color:var(--ink-muted); margin-left:0.2rem; white-space:nowrap; }
  .sh-sec{ font-size:0.82rem; color:var(--ink-muted); margin:1rem 0 0.4rem; }
  .sh-w{ font-size:0.85rem; color:var(--ink-muted); }
  .sh-result{ margin-top:1.2rem; background:var(--surface); border:1px solid var(--line); border-radius:8px; padding:1rem 1.2rem; box-shadow:var(--shadow); }
  .sh-result h3{ font-size:1.1rem; margin-bottom:0.5rem; }
  .sh-result b.big{ font-family:'JetBrains Mono',monospace; font-size:1.5rem; color:var(--accent); }
  .sh-result ul{ margin:0.4rem 0 0; padding-left:1.2rem; font-size:0.93rem; }
  .btn[hidden]{ display:none; }
  .opts.long{ grid-template-columns:1fr; }
  .opts.long .opt{ flex-direction:row; align-items:baseline; gap:0.6rem; font-size:0.93rem; line-height:1.6; padding:0.5rem 0.8rem; }
  .opts.long .opt b{ flex:none; }
  .opts.long .opt span{ flex:1; }
  .opts.long .opt::after{ flex:none; margin-left:0.5rem; }
  .mopt.sel{ border-color:var(--accent); box-shadow:inset 3px 0 0 var(--accent); }
  .mopt.right.got::after{ content:"✓ 正解，你選了"; }
  .mopt.right.missed::after{ content:"✓ 正解，你沒選"; }
  .qtag.multi{ color:var(--b2-ink); background:var(--b2); }
  .qsub{ font-size:0.82rem; color:var(--ink-muted); margin:0.2rem 0 0 !important; }
  .passage{ font-family:'Noto Serif TC',serif; background:var(--surface-2); border-left:3px solid var(--line); border-radius:4px; padding:0.7rem 1rem; margin:0.4rem 0 0.8rem; line-height:1.95; font-size:0.98rem; }
  .passage p{ margin:0 0 0.6rem; } .passage p:last-child{ margin:0; }
  .passage .plabel{ font-family:'JetBrains Mono','Noto Sans TC',monospace; font-size:0.75rem; color:var(--accent); display:block; margin-bottom:0.2rem; }
  .gw-meta{ display:flex; flex-wrap:wrap; gap:0.35rem; margin:0 0 0.6rem; }
  .gw-meta span{ font-size:0.72rem; background:var(--surface-2); border:1px solid var(--line); border-radius:4px; padding:0.05rem 0.5rem; }
  .gw-meta span.hit{ background:var(--ab); color:var(--ab-ink); border-color:var(--ab); }
  dl.words{ display:grid; grid-template-columns:max-content 1fr; gap:0.25rem 0.9rem; margin:0.3rem 0 0.7rem; font-size:0.93rem; }
  dl.words dt{ font-family:'Noto Serif TC',serif; color:var(--accent); }
  dl.words dd{ margin:0; }
  @media (max-width:520px){ dl.words{ grid-template-columns:1fr; gap:0; } dl.words dd{ margin-bottom:0.4rem; } }
  .flow-line{ font-size:0.93rem; background:var(--surface-2); border-radius:6px; padding:0.5rem 0.8rem; }
  input.cell-num{ width:5.5em; background:var(--surface); border:1px solid var(--line); border-radius:6px; padding:0.3rem 0.5rem; font-size:0.9rem; }
  .zy{ font-family:'Noto Sans TC',sans-serif; color:var(--accent); white-space:nowrap; }
"""


def esc(s):
    return html.escape(s, quote=True)


def step(tag, body):
    return '<div class="step"><span class="step-tag">%s</span>%s</div>\n' % (tag, body)


def table(heads, rows, kfirst=True):
    h = "".join("<th>%s</th>" % x for x in heads)
    out = []
    for r in rows:
        cells = []
        for i, c in enumerate(r):
            cells.append('<td class="k">%s</td>' % c if (i == 0 and kfirst) else "<td>%s</td>" % c)
        out.append("<tr>%s</tr>" % "".join(cells))
    return '<div class="table-wrap"><table><thead><tr>%s</tr></thead><tbody>%s</tbody></table></div>' % (h, "".join(out))


def section(sid, kicker, title, body):
    return (
        '  <section class="part prose" id="%s">\n    <div class="part-kicker"><b>%s</b></div>\n    <h2>%s</h2>\n%s\n  </section>\n'
        % (sid, kicker, title, body)
    )


def words(pairs):
    return '<dl class="words">%s</dl>' % "".join("<dt>%s</dt><dd>%s</dd>" % p for p in pairs)


def src_tag(ref=None):
    t = SELF + ("（考點參考 %s）" % ref if ref else "")
    return '<span class="srctag selfmade">%s</span>' % t


class Counter:
    def __init__(self):
        self.n = 0
        self.mc = 0
        self.w = 0

    def next(self):
        self.n += 1
        return self.n


def _opts(opts, multi):
    cls = "opt mopt" if multi else "opt"
    return "".join(
        '<button type="button" class="%s" data-opt="%s" aria-pressed="false"><b>%s</b><span>%s</span></button>' % (cls, L, L, o)
        for L, o in zip("ABCDE", opts)
    )


def mc(c, q, opts, ans, expl, ref=None, pre=""):
    """單選題。ans 為 A–E 其中之一。"""
    assert ans in "ABCDE"[: len(opts)], (q, ans)
    c.mc += 1
    return (
        '      <div class="qcard quiz" data-answer="%s">\n'
        '        <div class="qhead"><span class="qnum">%d</span><span class="qtag">單選</span>%s</div>\n'
        "        %s<p>%s</p>\n"
        '        <div class="opts long" role="group" aria-label="選項">%s</div>\n'
        '        <div class="quiz-fb" hidden><p class="verdict"></p><p>%s</p><button type="button" class="btn ghost small quiz-reset">重新作答</button></div>\n'
        "      </div>\n"
    ) % (ans, c.next(), src_tag(ref), pre, q, _opts(opts, False), expl)


def ms(c, q, opts, ans, expl, ref=None, pre=""):
    """多選題。ans 為正確選項字母組成的字串，例如 'ACE'。"""
    assert ans and all(a in "ABCDE"[: len(opts)] for a in ans) and ans == "".join(sorted(ans)), (q, ans)
    c.mc += 1
    return (
        '      <div class="qcard mquiz" data-answer="%s">\n'
        '        <div class="qhead"><span class="qnum">%d</span><span class="qtag multi">多選</span>%s</div>\n'
        "        %s<p>%s</p>\n"
        '        <p class="qsub">可以選一個以上。選好後按「對答案」，會依學測多選題的計分方式算分。</p>\n'
        '        <div class="opts long" role="group" aria-label="選項">%s</div>\n'
        '        <div class="toolbar"><button type="button" class="btn small mq-check">對答案</button></div>\n'
        '        <div class="quiz-fb" hidden><p class="verdict"></p><p>%s</p><button type="button" class="btn ghost small quiz-reset">重新作答</button></div>\n'
        "      </div>\n"
    ) % (ans, c.next(), src_tag(ref), pre, q, _opts(opts, True), expl)


def written(c, q, ref_html, ref=None, pre="", label="我的答案", ph="先寫下自己的答案，再打開參考答案。內容會自動儲存在這台裝置。", rows=3, tag="手寫"):
    """手寫題：作答欄會自動儲存，參考答案可展開。"""
    c.w += 1
    wid = "q%d" % c.w
    return (
        '      <div class="qcard">\n'
        '        <div class="qhead"><span class="qnum">%d</span><span class="qtag alt">%s</span>%s</div>\n'
        "        %s<p>%s</p>\n"
        '        <div class="save-wrap"><label class="field-label" for="%s">%s<span class="saved">已儲存</span></label>'
        '<textarea id="%s" data-save="%s" rows="%d" placeholder="%s"></textarea></div>\n'
        '        <details class="refans"><summary>參考答案</summary><div class="ans">'
        '<p class="ref-note">本站自編參考答案，非大考中心公布的答案，只示範一種寫法。</p>%s</div></details>\n'
        "      </div>\n"
    ) % (c.next(), tag, src_tag(ref), pre, q, wid, label, wid, wid, rows, esc(ph), ref_html)


def passage(*paras, label=None):
    lab = '<span class="plabel">%s</span>' % label if label else ""
    return '<div class="passage">%s%s</div>' % (lab, "".join("<p>%s</p>" % p for p in paras))


def practice(title, lede, cards, sid="practice", score=True):
    sc = '<span class="quiz-score" id="quiz-score"></span>' if score else ""
    return (
        '  <section class="practice prose" id="%s">\n    <h2>%s</h2>\n    <p class="lede-line">%s%s</p>\n    <div class="qlist">\n%s    </div>\n  </section>\n'
        % (sid, title, lede, sc, cards)
    )


def page(slug, num, part, title, sub, lede, toc, body, closing, sources):
    toc_html = "".join('<li><a href="#%s"><b>%d</b>%s</a></li>' % (i, n, t) for n, (i, t) in enumerate(toc, 1))
    src = "".join("<li>%s</li>" % s for s in sources)
    out = """<!DOCTYPE html>
<html lang="zh-Hant">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>%(title)s｜筱葳學測國文</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Serif+TC:wght@500;600;700&family=Noto+Sans+TC:wght@400;500;700&family=JetBrains+Mono:wght@400;500;700&display=swap">
<style>%(css)s</style>
<style>%(extra)s</style>
</head>
<body data-page="%(slug)s">
<nav class="site-nav"><a href="index.html">← 回到國文學習地圖</a></nav>
<div class="page">
  <header class="hero">
    <span class="eyebrow">%(part)s・%(num)d</span>
    <h1>%(title)s</h1>
    <p class="sub">%(sub)s</p>
    <div class="hero-rule"></div>
  </header>
  <section class="lede prose">
    %(lede)s
    <ul class="toc">%(toc)s</ul>
  </section>
%(body)s
  <section class="closing prose"><div class="card"><h2>下一步</h2>%(closing)s</div></section>
  <section class="prose"><h2 style="font-size:1.1rem;margin-bottom:0.5rem;">資料來源</h2><ul class="sources">%(src)s</ul></section>
  <footer><span>筱葳學測國文</span><span>國文學習地圖・國綜</span></footer>
</div>
<script src="app.js" defer></script>
</body>
</html>
""" % dict(title=title, css=shared_css(), extra=EXTRA_CSS, slug=slug, part=part, num=num, sub=sub, lede=lede, toc=toc_html, body=body, closing=closing, src=src)
    assert not re.search(r"<(script)[^>]*>(?!</script>)", out.replace('<script src="app.js" defer></script>', ""))
    open(os.path.join(ROOT, slug + ".html"), "w", encoding="utf-8").write(out)
    return out
