# -*- coding: utf-8 -*-
# files_skill 残留 3GPP 特指措辞通用化
import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE = r"<opencode配置目录>\skills\files_skill"

# 1. dual-track-extraction.md 通用化
p1 = BASE + r"\references\dual-track-extraction.md"
c = open(p1, encoding="utf-8").read()
c = c.replace(
    "# files_skill 参考：通用双轨提取：适用一切含 OLE 公式/图片式符号的文档（3GPP）",
    "# files_skill 参考：文档提取双轨要求（文字 + 图片识别，必须同步执行）")
c = c.replace(
    "**3GPP 文档中公式、符号、记号大量为图片式（OLE 对象/截图）**",
    "**一切含 OLE 公式/图片式符号的文档（3GPP 规范、学术论文、技术手册等）中，公式、符号、记号大量为图片式（OLE 对象/截图）**")
open(p1, "w", encoding="utf-8", newline="").write(c)
print("[1] dual-track-extraction.md 已通用化")

# 2. SKILL.md 来源标注通用化
p2 = BASE + r"\SKILL.md"
c = open(p2, encoding="utf-8").read()
c = c.replace("本机脚本，NR-f40 验证可用", "本机脚本，实战验证可用")
open(p2, "w", encoding="utf-8", newline="").write(c)
print("[2] SKILL.md 来源标注已通用化")

# 3. html-svg.md 校验脚本通用化
p3 = BASE + r"\references\html-svg.md"
c = open(p3, encoding="utf-8").read()
c = c.replace("`check-cdp.ps1` / `check-cdp2.ps1` / `check-pdcch.ps1`（CDP 模拟点击并核对数值）",
              "`check-cdp.ps1` / `check-cdp2.ps1`（CDP 模拟点击并核对数值；各教学专题的 check-* 脚本同理）")
open(p3, "w", encoding="utf-8", newline="").write(c)
print("[3] html-svg.md 已通用化")
