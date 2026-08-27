# -*- coding: utf-8 -*-
# SKILL.md 瘦身：把大块章节移到 references/，入口保留引用行
import os, re, sys

def slim(skill_name, move_map):
    base = os.path.join(r"<opencode配置目录>\skills", skill_name)
    p = os.path.join(base, "SKILL.md")
    with open(p, encoding="utf-8") as f:
        c = f.read()
    # frontmatter 与正文分离
    m = re.match(r"^(\ufeff?---\n.*?\n---\n)(.*)$", c, re.S)
    if not m:
        print(skill_name, ": frontmatter 解析失败")
        return
    fm, body = m.group(1), m.group(2)
    # 按 ## 切分章节
    parts = re.split(r"(?m)^(?=## )", body)
    head = ""   # 第一个 ## 之前的导言
    chapters = []
    for seg in parts:
        if seg.startswith("## "):
            chapters.append(seg)
        else:
            head = seg
    refs_dir = os.path.join(base, "references")
    os.makedirs(refs_dir, exist_ok=True)
    kept = []
    moved = []
    for ch in chapters:
        title = ch.strip().split("\n", 1)[0]
        moved_to = None
        for kw, refname in move_map.items():
            if kw in title:
                moved_to = refname
                break
        if moved_to:
            rp = os.path.join(refs_dir, moved_to)
            # 追加写入（去重：若已存在且内容相同则跳过）
            content = "# " + skill_name + " 参考：" + title.lstrip("# ").strip() + "\n\n" + ch.strip() + "\n\n---\n\n"
            if os.path.exists(rp):
                with open(rp, encoding="utf-8") as f:
                    old = f.read()
                if content.strip() in old:
                    moved.append(title)
                    continue
            with open(rp, "a", encoding="utf-8") as f:
                f.write(content)
            moved.append(title)
        else:
            kept.append(ch)
    # 入口重写：head + 保留章节 + 引用说明
    ref_lines = ""
    if moved:
        ref_lines = "\n## 详细知识（按需读取 references/，不随入口加载）\n\n"
        seen = []
        for kw, refname in move_map.items():
            if refname not in seen:
                seen.append(refname)
                ref_lines += "- 详见 `references/" + refname + "`\n"
        ref_lines += "\n"
    new_body = head.rstrip() + "\n\n" + "\n".join(ch for ch in kept if ch.strip()).rstrip() + "\n\n" + ref_lines
    with open(p, "w", encoding="utf-8", newline="") as f:
        f.write(fm + new_body.strip() + "\n")
    size = os.path.getsize(p)
    print("%s: 移出 %d 章节 -> references/, 入口现在 %d 字节" % (skill_name, len(moved), size))

slim("3gpp_skill", {
    "工具依赖清单": "tools.md",
    "3GPP 官网权威信息": "official-info.md",
    "配置链梳理输出模板": "teaching-template.md",
    "配图要求": "figure-requirements.md",
    "HTML 大文件操作安全守则": "html-check.md",
    "RAN 提案目录导航": "official-info.md",
    "文档提取双轨要求": "extraction-dual-track.md",
})

slim("files_skill", {
    "工具依赖清单": "tools.md",
    "图片识别（OCR）": "ocr-formula.md",
    "公式识别": "ocr-formula.md",
    "公式标准显示": "html-svg.md",
    "HTML/JS 交付校验": "html-svg.md",
    "流程图识别": "elements.md",
    "示例图绘制": "html-svg.md",
    "结构要素识别与输出": "elements.md",
    "图形要素处理": "elements.md",
    "音视频处理": "elements.md",
    "元数据 / 编码 / 版式检测": "elements.md",
})

slim("update_skill", {
    "工具依赖清单": "tools.md",
    "路径可移植层": "portable-paths.md",
})
