# -*- coding: utf-8 -*-
# 跨 skill 内容归位：
# 1) files_skill「示例图绘制（NR-f40 教学专属）」→ 3gpp_skill/references/figure-svg.md
# 2) 3gpp_skill/references/extraction-dual-track.md（通用双轨提取）→ files_skill/references/
# 3) files_skill 文字提取的 3GPP 特指措辞通用化
import os, re, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE = r"<opencode配置目录>\skills"
FILES = os.path.join(BASE, "files_skill")
G3PP = os.path.join(BASE, "3gpp_skill")

# ---- 1. 移动示例图绘制章节 ----
fp = os.path.join(FILES, "SKILL.md")
c = open(fp, encoding="utf-8").read()
m = re.search(r"(?ms)^(## 示例图绘制.*?)(?=^## |\Z)", c)
if m:
    sec = m.group(1).strip()
    open(os.path.join(G3PP, "references", "figure-svg.md"), "w", encoding="utf-8", newline="").write(
        "# 3gpp_skill 参考：示例图绘制（NR-f40 实战打磨）\n\n" + sec + "\n")
    c = c.replace(m.group(1), "")
    open(fp, "w", encoding="utf-8", newline="").write(c)
    print("[1] 示例图绘制章节已移到 3gpp_skill/references/figure-svg.md")
else:
    print("[1] 未找到示例图绘制章节")

# ---- 2. 移动双轨提取 reference ----
src = os.path.join(G3PP, "references", "extraction-dual-track.md")
dst = os.path.join(FILES, "references", "dual-track-extraction.md")
if os.path.exists(src):
    content = open(src, encoding="utf-8").read()
    content = content.replace("3gpp_skill 参考", "files_skill 参考（通用双轨提取：适用一切含 OLE 公式/图片式符号的文档，含 3GPP）")
    open(dst, "w", encoding="utf-8", newline="").write(content)
    os.remove(src)
    print("[2] 双轨提取已移到 files_skill/references/dual-track-extraction.md")
else:
    print("[2] 源文件不存在（可能已处理）")

# ---- 3. 3gpp_skill 入口引用更新 ----
gp = os.path.join(G3PP, "SKILL.md")
g = open(gp, encoding="utf-8").read()
g = g.replace("- 详见 `references/extraction-dual-track.md`", "- 双轨提取/公式核实通用流程：见 files_skill 的 `references/dual-track-extraction.md`（按需读取）")
open(gp, "w", encoding="utf-8", newline="").write(g)
print("[3] 3gpp_skill 引用已指向 files_skill")

# ---- 4. files_skill 文字提取 3GPP 措辞通用化 ----
fp2 = os.path.join(FILES, "SKILL.md")
c2 = open(fp2, encoding="utf-8").read()
c2 = c2.replace(
    "（3GPP 等文档中公式、符号、记号为图片式（OLE 对象），纯文本提取不出字符，资料读取必然不完整；双轨流程：文本提取 + soffice 转 PDF → PyMuPDF 渲染 PNG → p2t `formula/page` 模式识别，两轨合并，差异以图片识别为准（详见 3gpp_skill「文档提取双轨要求」）",
    "（一切含 OLE 公式/图片式符号的文档——3GPP 规范、学术论文、技术手册等——纯文本提取不出公式字符；双轨流程见 `references/dual-track-extraction.md`）")
open(fp2, "w", encoding="utf-8", newline="").write(c2)
print("[4] files_skill 文字提取措辞已通用化")
