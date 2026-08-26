# -*- coding: utf-8 -*-
# tools-manifest 完整性测试：表结构一致 / 分类计数吻合 / 待补充无重复 / B 类包可导入
import os, re, sys, importlib.util
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

MANIFEST = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools-manifest.md")
pass_n, fail_n = 0, 0
def check(name, cond):
    global pass_n, fail_n
    if cond: pass_n += 1; print("  ✓ " + name)
    else: fail_n += 1; print("  ✗ " + name)

c = open(MANIFEST, encoding="utf-8").read()

# 1. 结构：七个分类章节齐全（A~G）+ 本机配置 + 待补充
for sec in ["## A. 基础环境", "## B. Python 环境与核心包", "## C. 文档处理工具",
            "## D. OCR 与公式识别", "## E. 网络与同步", "## F. 编程环境",
            "## G. 校验与辅助", "## 本机配置", "## 待补充"]:
    check("章节存在: " + sec, sec in c)

# 2. 分类速览计数 vs 各分类表实际行数
cats = {}
for m in re.finditer(r"\|\s*([A-G])\.\s*[^|]+\|\s*(\d+)\s*\|", c):
    cats[m.group(1)] = int(m.group(2))
def count_rows(sec_name, next_sec):
    i = c.find(sec_name)
    j = c.find(next_sec, i + 1)
    seg = c[i:j] if j > 0 else c[i:]
    return len([l for l in seg.splitlines() if re.match(r"^\|\s*\S", l)
                and "---" not in l and "检查命令" not in l and not l.startswith("| 类别")])
next_map = {"A": "## B.", "B": "## C.", "C": "## D.", "D": "## E.", "E": "## F.", "F": "## G.", "G": "## 本机配置"}
sec_map = {"A": "## A. 基础环境", "B": "## B. Python 环境与核心包", "C": "## C. 文档处理工具",
           "D": "## D. OCR 与公式识别", "E": "## E. 网络与同步", "F": "## F. 编程环境", "G": "## G. 校验与辅助"}
for cat in "ABCDEFG":
    actual = count_rows(sec_map[cat], next_map[cat])
    check("分类 %s 计数吻合（速览 %d = 实际 %d）" % (cat, cats.get(cat, 0), actual), cats.get(cat) == actual)

# 3. 待补充清单项不重复出现在已装分类
pend = c[c.find("## 待补充"):]
for item in ["FFmpeg", "yt-dlp", "ImageMagick"]:
    body = c[:c.find("## 待补充")]
    check("待补充 %s 未混入已装分类" % item, item not in body)

# 4. B 类 Python 包可导入实测（别名映射）
alias = {"pix2text": "pix2text", "pypandoc_binary": "pypandoc", "python-docx": "docx",
         "python-pptx": "pptx", "openpyxl": "openpyxl", "xlrd": "xlrd", "pypdf": "pypdf",
         "pdfplumber": "pdfplumber", "pymupdf": "pymupdf", "matplotlib": "matplotlib",
         "pillow": "PIL", "chardet": "chardet", "pyzbar": "pyzbar",
         "opencv-python": "cv2", "imageio-ffmpeg": "imageio_ffmpeg", "playwright": "playwright",
         "weasyprint": "weasyprint", "docxtpl": "docxtpl", "jinja2": "jinja2",
         "python-magic-bin": "magic", "ocrmypdf": "ocrmypdf"}
importable = 0
for pkg, mod in alias.items():
    if importlib.util.find_spec(mod) is not None:
        importable += 1
check("B 类关键包可导入（%d/%d）" % (importable, len(alias)), importable >= len(alias) - 1)

# 5. 每行表结构：4 列（工具|用途|安装命令|检查命令）；本机配置表（3 列）不参与
body_secs = c[:c.find("## 本机配置")]
bad_rows = []
for l in body_secs.splitlines():
    if l.startswith("|") and "---" not in l and "检查命令" not in l and "说明" not in l \
       and not re.match(r"^\|\s*[A-G]\.\s", l) \
       and not l.startswith("| 类别") and not l.startswith("| 注册项"):
        if l.count("|") < 5:
            bad_rows.append(l[:50])
check("表格行均为 4 列", len(bad_rows) == 0)
if bad_rows: print("    坏行:", bad_rows[:3])

print("\n结果：通过 %d 项，失败 %d 项" % (pass_n, fail_n))
sys.exit(1 if fail_n else 0)
