# -*- coding: utf-8 -*-
"""中秋打印包 PDF 生成器：3 套概念检验 30 问 + 2 张陷阱卡 + 5 张思想方法速查表。
内容直接解析自知识库 Markdown 卡片，避免转抄错误。"""
import os
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.colors import HexColor
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                TableStyle, PageBreak, KeepTogether)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

ROOT = Path(__file__).resolve().parent
KB = ROOT / "知识库" / "物理"
OUT_DIR = ROOT / "打印包"
OUT_DIR.mkdir(exist_ok=True)
OUT_PDF = OUT_DIR / "中秋打印包_物理.pdf"

# ---------- 字体 ----------
regular_font = os.environ.get("DAIMON_CJK_FONT_REGULAR")
bold_font = os.environ.get("DAIMON_CJK_FONT_BOLD")
if not regular_font or not bold_font:
    raise RuntimeError("Daimon CJK fonts unavailable")
pdfmetrics.registerFont(TTFont("DaimonCJK", regular_font))
pdfmetrics.registerFont(TTFont("DaimonCJK-Bold", bold_font))
pdfmetrics.registerFontFamily("DaimonCJK", normal="DaimonCJK",
                              bold="DaimonCJK-Bold", italic="DaimonCJK",
                              boldItalic="DaimonCJK-Bold")

# ---------- LaTeX -> Unicode ----------
GREEK = {"lambda": "λ", "theta": "θ", "Delta": "Δ", "delta": "δ",
         "varphi": "φ", "phi": "φ", "varepsilon": "ε", "epsilon": "ε",
         "pi": "π", "rho": "ρ", "mu": "μ", "alpha": "α", "beta": "β",
         "omega": "ω", "Omega": "Ω", "gamma": "γ", "sigma": "σ"}
SUB = {"0": "₀", "1": "₁", "2": "₂", "3": "₃", "4": "₄", "5": "₅",
       "6": "₆", "7": "₇", "8": "₈", "9": "₉", "a": "ₐ", "e": "ₑ",
       "i": "ᵢ", "k": "ₖ", "l": "ₗ", "m": "ₘ", "n": "ₙ", "o": "ₒ",
       "p": "ₚ", "r": "ᵣ", "s": "ₛ", "t": "ₜ", "u": "ᵤ", "v": "ᵥ",
       "x": "ₓ", "+": "₊", "-": "₋", "(": "₍", ")": "₎", "A": "ᴀ",
       "B": "ʙ"}
SUP = {"0": "⁰", "1": "¹", "2": "²", "3": "³", "4": "⁴", "5": "⁵",
       "6": "⁶", "7": "⁷", "8": "⁸", "9": "⁹", "+": "⁺", "-": "⁻",
       "n": "ⁿ", "i": "ⁱ"}
OPS = {"times": "×", "cdot": "·", "div": "÷", "pm": "±", "geq": "≥",
       "leq": "≤", "neq": "≠", "approx": "≈", "gg": "≫", "ll": "≪",
       "Rightarrow": "⇒", "rightarrow": "→", "uparrow": "↑",
       "downarrow": "↓", "infty": "∞", "propto": "∝", "prime": "′"}


def _sub(s):
    return "".join(SUB.get(c, c) for c in s)


def _sup(s):
    return "".join(SUP.get(c, c) for c in s)


def _frac_repl(m):
    a, b = m.group(1), m.group(2)
    simple = re.compile(r"^[0-9a-zA-Zα-ω]+$")
    if simple.match(a) and simple.match(b):
        return f"{a}/{b}"
    return f"({a})/({b})"


def latex2uni(s):
    s = re.sub(r"\\d?frac\{([^{}]+)\}\{([^{}]+)\}", _frac_repl, s)
    s = re.sub(r"\\frac(\d)(\d)", r"\1/\2", s)
    s = re.sub(r"\\sqrt\{([^{}]+)\}", r"√(\1)", s)
    s = s.replace("\\sqrt", "√")
    s = re.sub(r"\\overline\{([^{}]+)\}", r"\1", s)
    s = re.sub(r"\\bar\{([^{}]+)\}", r"\1", s)
    s = re.sub(r"\\(?:text|mathrm|mathbf)\{([^{}]*)\}", r"\1", s)
    for k, v in GREEK.items():
        s = s.replace("\\" + k, v)
    for k, v in OPS.items():
        s = s.replace("\\" + k, v)
    s = re.sub(r"_\{([^{}]+)\}", r"<sub>\1</sub>", s)
    s = re.sub(r"_([0-9a-zA-Z])", r"<sub>\1</sub>", s)
    s = re.sub(r"\^\{([^{}]+)\}", r"<super>\1</super>", s)
    s = re.sub(r"\^([0-9n])", r"<super>\1</super>", s)
    s = s.replace("\\,", " ").replace("\\;", " ").replace("\\ ", " ")
    s = s.replace("~", " ")
    s = s.replace("{", "").replace("}", "").replace("\\", "")
    return s


def conv(s):
    """markdown 片段 -> reportlab 段落文本：转义 + $..$ 公式 + **粗体** + 状态emoji"""
    parts = re.split(r"(\$[^$]+\$)", s)
    out = []
    for p in parts:
        if p.startswith("$") and p.endswith("$") and len(p) > 2:
            out.append(latex2uni(p[1:-1]))
        else:
            p = (p.replace("✅", "已掌握").replace("⚠️", "待强化")
                  .replace("⚠", "待强化").replace("❌", "未理解"))
            p = p.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            p = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", p)
            p = p.replace("**", "")  # 跨公式的粗体标记无法配对，直接去除
            p = p.replace("`", "")
            out.append(p)
    return "".join(out)


# ---------- Markdown 解析 ----------
def read_md(path):
    return path.read_text(encoding="utf-8")


def parse_numbered_lines(block):
    items = []
    for line in block.splitlines():
        m = re.match(r"^(\d+)\.\s+(.*)", line.strip())
        if m:
            items.append((int(m.group(1)), m.group(2).strip()))
    return items


def parse_md_tables(block):
    """返回 block 中所有 markdown 表格（list of list of rows）"""
    tables, cur = [], []
    for line in block.splitlines():
        ls = line.strip()
        if ls.startswith("|") and ls.endswith("|"):
            cells = [c.strip() for c in ls.strip("|").split("|")]
            if all(re.fullmatch(r":?-{2,}:?", c) for c in cells):
                continue
            cur.append(cells)
        else:
            if cur:
                tables.append(cur)
                cur = []
    if cur:
        tables.append(cur)
    return tables


def section(text, start_marker, end_markers):
    i = text.find(start_marker)
    if i < 0:
        return ""
    j = len(text)
    for m in end_markers:
        k = text.find(m, i + len(start_marker))
        if 0 <= k < j:
            j = k
    return text[i:j]


def parse_check_card(path):
    """解析概念检验 30 问卡"""
    text = read_md(path)
    part1 = section(text, "## 第一部分", ["## 第二部分"])
    part2 = section(text, "## 第二部分", ["## ✅"])
    blk_a = section(part1, "### A.", ["### B."])
    blk_b = section(part1, "### B.", ["---", "## "])
    qa = parse_numbered_lines(blk_a)
    qb = parse_numbered_lines(blk_b)
    blk_a2 = section(part2, "### A.", ["### B."])
    blk_b2 = section(part2, "### B.", ["---", "## "])
    ta = parse_md_tables(blk_a2)[0]
    tb = parse_md_tables(blk_b2)[0]
    std = section(text, "## ✅ 过关标准", ["## 错题对应", "## 备注"])
    std_items = [re.sub(r"^- \[ \]\s*", "", l.strip()) for l in std.splitlines()
                 if l.strip().startswith("- [ ]")]
    return qa, qb, ta[1:], tb[1:], std_items


def parse_trap_card(path):
    """解析陷阱卡 -> [(标题, 正文行列表)]"""
    text = read_md(path)
    core = section(text, "## 核心内容", ["## 🗣️", "## 关联卡片"])
    traps = []
    for m in re.finditer(r"### (陷阱[^\n]+)\n(.*?)(?=\n### |\n---|\Z)",
                         core, re.S):
        title = m.group(1).strip()
        body = [l.strip() for l in m.group(2).strip().splitlines()
                if l.strip()]
        traps.append((title, body))
    return traps


# ---------- 样式 ----------
INK = HexColor("#1f2430")
MUTED = HexColor("#666666")
ACCENT = HexColor("#274690")

S = {
    "title": ParagraphStyle("t", fontName="DaimonCJK-Bold", fontSize=24,
                            leading=32, textColor=INK, alignment=1),
    "subtitle": ParagraphStyle("st", fontName="DaimonCJK", fontSize=13,
                               leading=20, textColor=MUTED, alignment=1),
    "h1": ParagraphStyle("h1", fontName="DaimonCJK-Bold", fontSize=16,
                         leading=22, textColor=ACCENT, spaceBefore=6,
                         spaceAfter=8),
    "h2": ParagraphStyle("h2", fontName="DaimonCJK-Bold", fontSize=12.5,
                         leading=17, textColor=INK, spaceBefore=10,
                         spaceAfter=5),
    "body": ParagraphStyle("b", fontName="DaimonCJK", fontSize=10.5,
                           leading=16, textColor=INK),
    "q": ParagraphStyle("q", fontName="DaimonCJK", fontSize=10.5,
                        leading=16.5, textColor=INK, spaceBefore=1.5,
                        spaceAfter=1.5),
    "small": ParagraphStyle("s", fontName="DaimonCJK", fontSize=9,
                            leading=13.5, textColor=MUTED),
    "cell": ParagraphStyle("c", fontName="DaimonCJK", fontSize=9.5,
                           leading=13.5, textColor=INK),
    "cellb": ParagraphStyle("cb", fontName="DaimonCJK-Bold", fontSize=9.5,
                            leading=13.5, textColor=INK),
    "note": ParagraphStyle("n", fontName="DaimonCJK", fontSize=10,
                           leading=15, textColor=HexColor("#5b3a12"),
                           backColor=HexColor("#fdf0e2"), borderPadding=6,
                           spaceBefore=6, spaceAfter=6),
}


def P(text, style="body"):
    return Paragraph(conv(text), S[style])


def three_line_table(rows, widths, header=True):
    data = []
    for i, row in enumerate(rows):
        st = "cellb" if (header and i == 0) else "cell"
        data.append([Paragraph(conv(str(c)), S[st]) for c in row])
    t = Table(data, colWidths=widths, repeatRows=1 if header else 0)
    style = [
        ("LINEABOVE", (0, 0), (-1, 0), 1.2, INK),
        ("LINEBELOW", (0, -1), (-1, -1), 1.2, INK),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]
    if header:
        style.append(("LINEBELOW", (0, 0), (-1, 0), 0.6, INK))
    t.setStyle(TableStyle(style))
    return t


def blank_line(width_chars=28):
    return "＿" * 12


# ---------- 页眉页脚 ----------
def later_pages(canvas, doc):
    canvas.saveState()
    w, h = A4
    canvas.setFont("DaimonCJK", 8.5)
    canvas.setFillColor(MUTED)
    canvas.drawString(2.2 * cm, h - 1.3 * cm, "中秋打印包 · 物理（概念检验 + 陷阱清单 + 思想方法速查 + 家长提问卡）")
    canvas.drawRightString(w - 2.2 * cm, h - 1.3 * cm, "申悦学习 2026.9")
    canvas.setStrokeColor(HexColor("#dddddd"))
    canvas.line(2.2 * cm, h - 1.5 * cm, w - 2.2 * cm, h - 1.5 * cm)
    canvas.drawCentredString(w / 2, 1.1 * cm, f"第 {doc.page} 页")
    canvas.restoreState()


def first_page(canvas, doc):
    canvas.saveState()
    w, h = A4
    canvas.setFont("DaimonCJK", 8.5)
    canvas.setFillColor(MUTED)
    canvas.drawCentredString(w / 2, 1.1 * cm, f"第 {doc.page} 页")
    canvas.restoreState()


# ---------- 内容组装 ----------
story = []

# 封面
story.append(Spacer(1, 3.2 * cm))
story.append(Paragraph("中秋打印包 · 物理", S["title"]))
story.append(Spacer(1, 0.4 * cm))
story.append(Paragraph("概念检验三件套 + 陷阱清单 + 思想方法速查 + 家长提问卡", S["subtitle"]))
story.append(Paragraph("中秋假期 2026.9.25–9.27 · 备战高二第一次月考", S["subtitle"]))
story.append(Spacer(1, 1.2 * cm))
cover_items = [
    "第一部分　概念检验三件套：静电场 30 问 / 动量 30 问 / 光与振动波 30 问",
    "第二部分　陷阱清单：静电场 10 条 / 动量 8 条（考前 10 分钟只看这个）",
    "第三部分　思想方法速查五表：守恒 / 图像 / 类比 / 临界字典 / 定义式与仪式",
    "第四部分　家长提问卡 30 问：照原话问、看关键词打钩（每天睡前 15 分钟）",
]
for it in cover_items:
    story.append(Paragraph(conv(it), ParagraphStyle(
        "ci", parent=S["body"], fontSize=11.5, leading=20, alignment=1)))
story.append(Spacer(1, 1.0 * cm))
story.append(Paragraph(conv("用法：检验卷先做题后对答案（答案区在每套后半部分），错题回知识库对应卡片补课；"
                            "陷阱清单与速查五表贴在书桌前，碎片时间扫一眼。"), S["note"]))
story.append(PageBreak())

# 第一部分：概念检验三件套
CHECK_CARDS = [
    ("第一套　静电场基本概念过关 30 问",
     KB / "概念检验" / "高二深化_物理_概念检验_静电场基本概念过关30问.md"),
    ("第二套　动量基本概念过关 30 问",
     KB / "概念检验" / "高二深化_物理_概念检验_动量基本概念过关30问.md"),
    ("第三套　光与振动波基本概念过关 30 问",
     KB / "概念检验" / "高二深化_物理_概念检验_光与振动波基本概念过关30问.md"),
]

story.append(Paragraph("第一部分　概念检验三件套", S["h1"]))
story.append(P("每套 30 题（判断 20 + 填空 10），建议用时 20 分钟。判断题在题后（　）内打 √ 或 ×；"
               "填空题把关键词写在横线上。全部做完再翻后面的答案区。过关标准：判断错 ≤ 2、填空对 ≥ 8。"))
story.append(Spacer(1, 8))

for ci, (name, path) in enumerate(CHECK_CARDS):
    qa, qb, ta, tb, std = parse_check_card(path)
    story.append(Paragraph(name, S["h1"]))
    story.append(Paragraph("A. 判断题（每题一句话，√ 或 ×）", S["h2"]))
    for n, q in qa:
        story.append(Paragraph(conv(f"{n}. {q}（　）"), S["q"]))
    story.append(Spacer(1, 6))
    story.append(Paragraph("B. 填空题（写关键词 / 公式）", S["h2"]))
    for n, q in qb:
        q2 = q.replace("______", "＿" * 10)
        story.append(Paragraph(conv(f"{n}. {q2}"), S["q"]))
    story.append(Spacer(1, 8))
    story.append(Paragraph("答案与一句话解析（做完再看）", S["h2"]))
    story.append(three_line_table([["题", "答案", "一句话解析"]] + ta,
                                  [1.2 * cm, 1.6 * cm, 13.4 * cm]))
    story.append(Spacer(1, 6))
    story.append(three_line_table([["题", "答案"]] + tb, [1.2 * cm, 15.0 * cm]))
    story.append(Spacer(1, 6))
    story.append(Paragraph("过关标准", S["h2"]))
    for it in std:
        story.append(Paragraph(conv("□ " + it), S["q"]))
    if ci < len(CHECK_CARDS) - 1:
        story.append(PageBreak())

story.append(PageBreak())

# 第二部分：陷阱清单
story.append(Paragraph("第二部分　陷阱清单（考前 10 分钟只看这个）", S["h1"]))
TRAP_CARDS = [
    ("静电场常见陷阱 10 条",
     KB / "易错警示与辨析" / "高二深化_物理_易错警示与辨析_静电场常见陷阱.md"),
    ("动量常见陷阱 8 条",
     KB / "易错警示与辨析" / "高二深化_物理_易错警示与辨析_动量常见陷阱.md"),
]
for name, path in TRAP_CARDS:
    story.append(Paragraph(name, S["h2"]))
    for title, body in parse_trap_card(path):
        block = [Paragraph("<b>" + conv(title) + "</b>", S["q"])]
        for line in body:
            line = line.lstrip("- ").strip()
            if line:
                block.append(Paragraph(conv("　" + line),
                                       ParagraphStyle("tr", parent=S["q"],
                                                      fontSize=10, leading=15)))
        story.append(KeepTogether(block))
    story.append(Spacer(1, 10))

story.append(PageBreak())

# 第三部分：思想方法速查五表
story.append(Paragraph("第三部分　思想方法速查五表", S["h1"]))

def grab_table(path, header_keyword):
    for t in parse_md_tables(read_md(path)):
        if any(header_keyword in c for c in t[0]):
            return t
    return None

METHOD = KB / "典型题型与方法"

# 表1 守恒
t = grab_table(METHOD / "高二深化_物理_典型题型与方法_思想方法_守恒思想.md", "守恒条件")
story.append(Paragraph("表 1　三大守恒对照（守恒三问：守哪笔账？条件够吗？谁偷走了？）", S["h2"]))
story.append(three_line_table(t, [2.2 * cm, 3.4 * cm, 2.0 * cm, 3.6 * cm, 4.8 * cm]))
story.append(Spacer(1, 8))

# 表2 图像
t = grab_table(METHOD / "高二深化_物理_典型题型与方法_思想方法_图像通用手册.md", "斜率")
story.append(Paragraph("表 2　图像通用手册（先看轴，再斜率，面积想累积；轴下为负）", S["h2"]))
story.append(three_line_table(t, [2.0 * cm, 2.6 * cm, 3.2 * cm, 3.2 * cm, 5.0 * cm]))
story.append(Spacer(1, 8))

# 表3 类比
t = grab_table(METHOD / "高二深化_物理_典型题型与方法_思想方法_类比迁移.md", "静电场")
story.append(Paragraph("表 3　类比迁移：重力场 ↔ 静电场（直觉带路，公式收账）", S["h2"]))
story.append(three_line_table(t, [4.4 * cm, 4.8 * cm, 6.8 * cm]))
story.append(Spacer(1, 8))

# 表4 临界字典
t = grab_table(METHOD / "高二深化_物理_典型题型与方法_思想方法_恰好临界条件字典.md", "立即翻译成")
story.append(Paragraph("表 4　「恰好」临界条件字典（见到恰好先停笔，临界方程送上门）", S["h2"]))
story.append(three_line_table(t, [5.4 * cm, 7.2 * cm, 3.4 * cm]))
story.append(Spacer(1, 8))

# 表5 定义式 vs 决定式
t = grab_table(METHOD / "高二深化_物理_典型题型与方法_思想方法_方向与符号的第一仪式.md", "定义式")
story.append(Paragraph("表 5　定义式 vs 决定式（见到「成正比」先问：这是定义式还是决定式）", S["h2"]))
story.append(three_line_table(t, [2.4 * cm, 6.0 * cm, 7.6 * cm]))
story.append(Spacer(1, 8))
story.append(Paragraph(conv("两个动笔仪式：矢量题先念「正方向是……」，静电场题先念「符号带全……」。"
                            "三个先约定：正方向、零势点、参考系——先声明，后一致。"), S["note"]))

story.append(PageBreak())

# 第四部分：家长提问卡（费曼回话题库）
story.append(Paragraph("第四部分　家长提问卡（费曼回话题库 30 问）", S["h1"]))
story.append(P("家长照「您这样问」原话提问，孩子口头回答；对照「过关信号」里的关键词，意思对就打 √，"
               "磕绊标 ⚠️、答不上标 ❌。答不上就去最后一列指路的卡片复习。每天睡前 5 题，错了别纠正，"
               "说「再讲讲」就好。"))
story.append(Spacer(1, 8))

QUESTIONS_MD = ROOT / "家长支持" / "家长提问卡_费曼回话题库.md"
Q_SECTIONS = ["静电场（12 问）", "动量（10 问）", "光与振动波（8 问）"]
q_tables = parse_md_tables(read_md(QUESTIONS_MD))[:3]
for si, (sec_name, qt) in enumerate(zip(Q_SECTIONS, q_tables)):
    story.append(Paragraph(sec_name, S["h2"]))
    # 表头：# / 您这样问 / 过关信号 / 不会就去看
    story.append(three_line_table(
        [["#", "您这样问", "过关信号（听到这些意思就 √）", "不会就去看"]] + qt[1:],
        [0.9 * cm, 5.6 * cm, 6.3 * cm, 3.4 * cm]))
    story.append(Spacer(1, 10))

# ---------- 构建 ----------
doc = SimpleDocTemplate(str(OUT_PDF), pagesize=A4,
                        topMargin=2.0 * cm, bottomMargin=1.8 * cm,
                        leftMargin=2.2 * cm, rightMargin=2.2 * cm,
                        title="中秋打印包 · 物理", author="申悦学习")
doc.build(story, onFirstPage=first_page, onLaterPages=later_pages)
print("OK:", OUT_PDF)
