# -*- coding: utf-8 -*-
"""
build_site.py — 把 Markdown 内容源构建为 GitHub Pages 静态网站（输出到 docs/）

用法：python build_site.py

内容源（修改这些文件后重新运行本脚本即可更新网站）：
  - 中秋3天辅导计划_9月25-27日.md      -> docs/plan.html
  - 家长支持/家长物理速成指南_动量篇.md -> docs/parent-guide.html
  - 知识库/**/*.md                      -> docs/kb/**/*.html（镜像目录结构）
"""
import re
import shutil
import html as html_mod
from pathlib import Path

from markdown_it import MarkdownIt

ROOT = Path(__file__).resolve().parent
DOCS = ROOT / "docs"
KB = ROOT / "知识库"

MD = MarkdownIt("gfm-like").disable("linkify")

SITE_NAME = "申悦学习 · AI 指导物理学习"

CSS = """
:root{
  --ink:#1f2430; --muted:#6b7280; --line:#e8e3d8; --paper:#fdfcf8;
  --accent:#b4540a; --accent-soft:#fdf0e2; --brand:#274690; --brand-soft:#eef2fb;
}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Hiragino Sans GB","Microsoft YaHei",sans-serif;
  color:var(--ink);background:var(--paper);line-height:1.75;font-size:16.5px}
a{color:var(--brand);text-decoration:none}
a:hover{text-decoration:underline}

.site-header{position:sticky;top:0;z-index:10;background:rgba(253,252,248,.94);backdrop-filter:blur(6px);
  border-bottom:1px solid var(--line)}
.site-header .wrap{max-width:960px;margin:0 auto;padding:.7rem 1.2rem;display:flex;align-items:center;gap:1rem;flex-wrap:wrap}
.brand{font-weight:700;color:var(--ink);white-space:nowrap}
.brand:hover{text-decoration:none}
.site-nav{margin-left:auto;display:flex;gap:.2rem;flex-wrap:wrap}
.site-nav a{padding:.35rem .8rem;border-radius:999px;color:var(--muted);font-size:.95rem}
.site-nav a:hover{background:var(--brand-soft);color:var(--brand);text-decoration:none}

main{max-width:820px;margin:0 auto;padding:2.2rem 1.4rem 4rem}
.page h1{font-size:1.9rem;line-height:1.35;margin:.2em 0 .6em}
.page h2{font-size:1.35rem;margin:1.8em 0 .5em;padding-bottom:.25em;border-bottom:2px solid var(--line)}
.page h3{font-size:1.12rem;margin:1.4em 0 .4em}
.page blockquote{margin:1em 0;padding:.6em 1em;background:var(--accent-soft);border-left:4px solid var(--accent);
  border-radius:0 8px 8px 0;color:#5b3a12}
.page code{background:#f1ede3;padding:.12em .4em;border-radius:5px;font-size:.92em;
  font-family:"Cascadia Code",Consolas,"Courier New",monospace}
.page pre{background:#23272f;color:#e8e6e3;padding:1em 1.2em;border-radius:10px;overflow:auto;line-height:1.55}
.page pre code{background:none;padding:0;color:inherit}
.page table{border-collapse:collapse;width:100%;margin:1em 0;font-size:.95rem;display:block;overflow-x:auto}
.page th,.page td{border:1px solid var(--line);padding:.45em .8em;text-align:left;vertical-align:top}
.page th{background:var(--brand-soft)}
.page hr{border:none;border-top:1px solid var(--line);margin:2.2em 0}
.page ul,.page ol{padding-left:1.4em}
.page img{max-width:100%}
.page .katex{font-size:1.05em}

.footer{border-top:1px solid var(--line);color:var(--muted);font-size:.9rem}
.footer .wrap{max-width:960px;margin:0 auto;padding:1.4rem;display:flex;flex-wrap:wrap;gap:.5rem;justify-content:space-between}

/* 首页 */
.hero{max-width:960px;margin:0 auto;padding:3.2rem 1.4rem 1rem;text-align:center}
.hero h1{font-size:2.1rem;margin:.2em 0}
.hero p.sub{color:var(--muted);font-size:1.08rem;max-width:36em;margin:.6em auto}
.chip{display:inline-block;background:var(--brand-soft);color:var(--brand);border-radius:999px;
  padding:.25em 1em;font-size:.92rem;margin:.15em}
.cards{max-width:960px;margin:0 auto;padding:1.6rem 1.4rem;display:grid;gap:1rem;
  grid-template-columns:repeat(auto-fit,minmax(240px,1fr))}
.card{display:block;background:#fff;border:1px solid var(--line);border-radius:14px;padding:1.2rem 1.3rem;
  color:var(--ink);transition:box-shadow .15s,transform .15s}
.card:hover{box-shadow:0 6px 18px rgba(31,36,48,.08);transform:translateY(-2px);text-decoration:none}
.card .icon{font-size:1.5rem}
.card h3{margin:.35em 0 .3em;font-size:1.1rem}
.card p{margin:0;color:var(--muted);font-size:.95rem;line-height:1.6}
.timeline{max-width:720px;margin:0 auto;padding:.4rem 1.4rem 2rem}
.timeline table{font-size:.95rem}
.section-title{max-width:960px;margin:0 auto;padding:2.4rem 1.4rem 0;font-size:1.25rem;font-weight:700}
.support-band{max-width:960px;margin:0 auto 2rem;padding:0 1.4rem}
.support-band .inner{background:linear-gradient(135deg,var(--brand-soft),#fff);border:1px solid var(--line);
  border-radius:14px;padding:1.2rem 1.4rem;color:var(--muted)}
.support-band strong{color:var(--ink)}

.print-btn{position:fixed;right:1.2rem;bottom:1.2rem;background:var(--accent);color:#fff;border:none;
  border-radius:999px;padding:.7em 1.4em;font-size:1rem;cursor:pointer;box-shadow:0 4px 14px rgba(180,84,10,.35)}

@media print{
  .site-header,.footer,.print-btn{display:none}
  body{background:#fff;font-size:11.5pt;line-height:1.6}
  main{max-width:none;padding:0}
  .page h1{font-size:18pt}
  .page h2{font-size:14pt;page-break-after:avoid}
  .page h3{font-size:12pt;page-break-after:avoid}
  .page table,.page pre,.page blockquote{page-break-inside:avoid}
  .page pre{white-space:pre-wrap;background:#f5f5f5;color:#000;border:1px solid #ddd}
  @page{margin:1.5cm}
}
"""

NAV = """<nav class="site-nav">
<a href="{base}index.html">首页</a>
<a href="{base}plan.html">3天辅导计划</a>
<a href="{base}parent-guide.html">速成指南·静电场</a>
<a href="{base}parent-guide-momentum.html">速成指南·动量</a>
<a href="{base}holiday-framework.html">长假专项框架</a>
<a href="{base}kb/index.html">知识库</a>
</nav>"""

KATEX = """
<link rel="stylesheet" href="__BASE__assets/katex/katex.min.css">
<script defer src="__BASE__assets/katex/katex.min.js"></script>
<script defer src="__BASE__assets/katex/auto-render.min.js"
  onload="renderMathInElement(document.body,{delimiters:[
    {left:'$$',right:'$$',display:true},
    {left:'$',right:'$',display:false}
  ]});"></script>
"""


def extract_title(text, fallback):
    for line in text.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return fallback


def fix_links(html):
    # 卡片间相对链接：xxx.md -> xxx.html（目录结构镜像，相对路径不变）
    return re.sub(r'(?<=href=")([^"]+?)\.md(?=")', r"\1.html", html)


def page_html(title, body_html, base, desc="", extra_after=""):
    t = html_mod.escape(title, quote=True)
    d = html_mod.escape(desc, quote=True)
    katex = KATEX.replace("__BASE__", base)
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{t} · {SITE_NAME}</title>
<meta name="description" content="{d}">
<link rel="stylesheet" href="{base}assets/style.css">
{katex}
</head>
<body>
<header class="site-header"><div class="wrap">
<a class="brand" href="{base}index.html">🌕 {SITE_NAME}</a>
{NAV.format(base=base)}
</div></header>
<main class="page">
{body_html}
</main>
{extra_after}
<footer class="footer"><div class="wrap">
<span>陪伴申悦一路到 2028 高考</span>
<span>内容维护：修改 Markdown 源文件后运行 <code>python build_site.py</code> 重新生成</span>
</div></footer>
</body>
</html>
"""


def render_md(md_path):
    text = md_path.read_text(encoding="utf-8")
    title = extract_title(text, md_path.stem)
    body = fix_links(MD.render(text))
    return title, body


def write(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def main():
    if DOCS.exists():
        shutil.rmtree(DOCS)
    (DOCS / "assets").mkdir(parents=True)
    write(DOCS / "assets" / "style.css", CSS)
    shutil.copytree(ROOT / "assets" / "katex", DOCS / "assets" / "katex")
    write(DOCS / ".nojekyll", "")

    # 打印包 PDF 同步到 docs/print/，供网站下载
    print_src = ROOT / "打印包"
    if print_src.exists():
        (DOCS / "print").mkdir(exist_ok=True)
        for pdf in print_src.glob("*.pdf"):
            shutil.copy2(pdf, DOCS / "print" / pdf.name)

    n = 0

    # 1) 根级单页
    singles = [
        (ROOT / "中秋3天辅导计划_9月25-27日.md", "plan.html", "中秋3天物理辅导计划", "中秋假期3天物理辅导：真题诊断、静电场主线突破、真题模拟与错题复盘"),
        (ROOT / "家长支持" / "家长物理速成指南_静电场篇.md", "parent-guide.html", "家长物理速成指南 · 静电场篇",
         "写给很久没碰物理的家长：山坡类比建立静电场直觉、批改四问清单与答疑"),
        (ROOT / "家长支持" / "家长物理速成指南_动量篇.md", "parent-guide-momentum.html", "家长物理速成指南 · 动量篇",
         "30分钟建立动量直觉、三道能讲给孩子听的例题、批改四问清单"),
        (ROOT / "家长支持" / "家长提问卡_费曼回话题库.md", "parent-questions.html", "家长提问卡 · 费曼回话题库",
         "家长照原话问、看关键词打钩：静电场12问+动量10问+光与振动波8问，每天睡前15分钟"),
        (ROOT / "家长支持" / "错题入库速查_考后三步.md", "mistake-intake.html", "考后错题入库速查",
         "月考后三步走：拍照→发给Kimi→查看失分分析，错题自动变卡片"),
        (ROOT / "家长支持" / "长假专项复习设计框架.md", "holiday-framework.html", "长假专项复习设计框架",
         "小长假/长假专项复习通用模板：五步法 + 3天/7天日程模板，国庆专项按此生成"),
    ]
    extra_guide = '<button class="print-btn" onclick="window.print()">🖨️ 打印速查表</button>'
    for src, out, fb_title, desc in singles:
        if not src.exists():
            print("WARN missing:", src.name)
            continue
        title, body = render_md(src)
        write(DOCS / out, page_html(title, body, "", desc,
                                    extra_after=(extra_guide if out.startswith("parent") else "")))
        n += 1

    # 2) 知识库镜像
    kb_index_html = ""
    print_card = '<button class="print-btn" onclick="window.print()">🖨️ 打印本页</button>'
    for src in sorted(KB.rglob("*.md")):
        rel = src.relative_to(KB)
        out = (DOCS / "kb" / rel).with_suffix(".html")
        title, body = render_md(src)
        # 页面位于 docs/kb/<rel>，base 需包含 kb/ 这一层：目录数 = len(rel.parts)
        base = "../" * len(rel.parts)
        html = page_html(title, body, base, f"知识库 · {title}",
                         extra_after=(print_card if "索引" not in src.name and src.name[0] != "0" else ""))
        write(out, html)
        n += 1
        if src.name == "00_知识库总索引.md":
            # docs/kb/index.html 在 kb/ 下，base 为上一级
            kb_index_html = page_html(title, body, "../", f"知识库 · {title}")

    if kb_index_html:
        write(DOCS / "kb" / "index.html", kb_index_html)
        n += 1

    # 3) 首页
    home = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{SITE_NAME}</title>
<meta name="description" content="中秋假期备战高二第一次月考，并一路陪伴到2028年高考的物理学习项目">
<link rel="stylesheet" href="assets/style.css">
</head>
<body>
<header class="site-header"><div class="wrap">
<a class="brand" href="index.html">🌕 {SITE_NAME}</a>
{NAV.format(base="")}
</div></header>

<section class="hero">
<span class="chip">📍 当前：中秋假期（9月25–27日）备战高二第一次月考</span>
<span class="chip">🆕 已按广州四校真题修订：静电场为第一主线</span>
<h1>把每一次"不懂"，<br>变成一张讲得清楚的卡片</h1>
<p class="sub">从中秋三天辅导出发，用知识库积累错题与方法，陪伴申悦到 2028 年高考。</p>
</section>

<section class="cards">
<a class="card" href="print/中秋打印包_物理.pdf" download><div class="icon">🖨️</div><h3>中秋打印包 · 点击下载</h3>
<p>A4 共 13 页四部分：概念检验 30 问 ×3（含答案）+ 易错陷阱卡 ×2 + 思想方法速查表 ×5 + 家长提问卡 30 问，打印店打开本页即可下载打印。</p></a>
<a class="card" href="plan.html"><div class="icon">📅</div><h3>中秋 3 天辅导计划（v3 定稿）</h3>
<p>9.25 真题诊断 + 静电场地基 → 9.26 静电场题型突破 + 机动板块 → 9.27 真题模拟与错题复盘，每天约 4 小时。月考范围已确认为四校真题范围。</p></a>
<a class="card" href="holiday-framework.html"><div class="icon">🏗️</div><h3>长假专项复习设计框架</h3>
<p>中秋专项是首期实例：五步法 + 3天/7天日程模板。国庆专项（10.1–10.7）将在月考分析后按此生成。</p></a>
<a class="card" href="parent-guide.html"><div class="icon">👨‍👧</div><h3>家长速成指南 · 静电场篇</h3>
<p>很久没碰物理也能陪学："山坡类比"建立静电场直觉、三道能讲给孩子听的例题、批改四问清单。</p></a>
<a class="card" href="kb/物理/素材与拓展/高二深化_物理_素材与拓展_广州四校高二上月考真题分析报告.html"><div class="icon">📊</div><h3>四校真题分析报告</h3>
<p>2025.10 华附/执信/铁一/二中月考真题逐题归纳：静电场是最大公约数，选必一因校而异。</p></a>
<a class="card" href="kb/index.html"><div class="icon">📚</div><h3>物理知识库</h3>
<p>23 张卡片：知识卡 14 + 思想方法 5 + 概念检验三件套 3 + 真题分析 1，张张可打印，碎片时间自测。</p></a>
<a class="card" href="parent-questions.html"><div class="icon">🎤</div><h3>家长提问卡 · 30 问</h3>
<p>您照原话问、看关键词打钩：每天睡前 15 分钟费曼回讲，零物理基础也能用。</p></a>
<a class="card" href="kb/复盘追踪/艾宾浩斯复习日历_中秋起.html"><div class="icon">🗓️</div><h3>艾宾浩斯复习日历</h3>
<p>按 1/2/4/7/15 天记忆曲线排好的打卡表（9.25–10.12），每天 10–20 分钟对抗遗忘。</p></a>
<a class="card" href="mistake-intake.html"><div class="icon">📥</div><h3>考后错题入库</h3>
<p>月考后三步走：拍照 → 发给 Kimi → 收失分分析，错题自动变卡片滚雪球。</p></a>
</section>

<div class="section-title">🗓️ 项目时间线</div>
<div class="timeline">
<table>
<tr><th>时间</th><th>里程碑</th></tr>
<tr><td>9.18</td><td>知识库建库；入库广州四校月考真题，修订月考范围（静电场为第一主线），卡片扩至 14 张</td></tr>
<tr><td>9.19</td><td>月考范围确认为四校真题范围，中秋计划 v3 定稿；打印包定稿；长假专项复习设计框架上线</td></tr>
<tr><td>9.25（周五）</td><td>Day 1：执信卷真题摸底 → 电场强度、电势与电势能概念地基</td></tr>
<tr><td>9.26（周六）</td><td>Day 2：静电场题型突破（电容器/偏转/综合）+ 机动板块（动量/光/振动波，说不清进度则静电场深化）</td></tr>
<tr><td>9.27（周日）</td><td>Day 3：华附卷限时模拟 → 逐题复盘 → 错题入库</td></tr>
<tr><td>9.28 当周</td><td>高二第一次月考 🎯</td></tr>
<tr><td>考后</td><td>试卷拍照入库 → AI 分析失分板块 → 更新状态表 → 每周回讲常态化</td></tr>
<tr><td>10.1–10.7</td><td>国庆长假专项：按长假专项框架设计，主线待月考分析后确定</td></tr>
</table>
</div>

<div class="support-band"><div class="inner">
<strong>给家长的话：</strong>您不需要会物理。您需要的一切都在<a href="parent-guide.html">《家长速成指南 · 静电场篇》</a>里——
直觉类比、能讲给孩子听的例题、批改四问清单。您的角色是"提问的记者"，不是"讲课的老师"；
她的角色是"讲课的小老师"。先有关系，才有成绩。
</div></div>

<footer class="footer"><div class="wrap">
<span>陪伴申悦一路到 2028 高考</span>
<span>内容维护：修改 Markdown 源文件后运行 <code>python build_site.py</code> 重新生成</span>
</div></footer>
</body>
</html>
"""
    write(DOCS / "index.html", home)
    n += 1

    print(f"OK: built {n} pages -> {DOCS}")


if __name__ == "__main__":
    main()
