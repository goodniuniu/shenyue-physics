import sys
sys.stdout.reconfigure(encoding='utf-8')
import pdfplumber
p = r"知识库/物理/电学学习资料(教师版).pdf"
with pdfplumber.open(p) as pdf:
    print("pages:", len(pdf.pages))
    texts = []
    for i, page in enumerate(pdf.pages):
        t = page.extract_text() or ""
        texts.append(f"--- page {i+1} ---\n" + t)
out = "知识库/物理/素材与拓展/真题试卷/提取文本/电学学习资料(教师版).txt"
with open(out, "w", encoding="utf-8") as f:
    f.write("\n".join(texts))
print("chars:", sum(len(t) for t in texts))
