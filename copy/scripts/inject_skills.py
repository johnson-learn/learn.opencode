# -*- coding: utf-8 -*-
# 新项目 skill 注入脚本：把全局 skill 复制为项目级 skill，并改写 description 为"默认触发"
# 用法：python inject_skills.py <目标项目目录>
import os, re, shutil, sys

GLOBAL_SKILLS = r"C:\Users\job_p\.config\opencode\skills"

def rewrite_description(text, name):
    """把'仅显式触发'的全局 description 改写为项目级默认触发"""
    # 1. 全局声明 -> 项目级声明
    text = re.sub(r"（全局 skill，仅显式触发，不靠关键词自动调用）", "（项目级 skill，默认触发）", text)
    # 2. Use ONLY when 显式限制 -> 显式+自动双通道
    text = re.sub(
        r"Use ONLY when 用户消息显式包含",
        "Use when 用户消息显式包含",
        text,
    )
    # 3. 显式语法说明保留，末尾追加默认触发说明
    tail = f"\n\n> 本项目级副本：默认触发（任务涉及本技能领域时自动调用）；显式语法 {name}：任务 仍可用。"
    if tail.strip() not in text:
        text = text + tail
    return text

def main(target):
    target_skills = os.path.join(target, ".opencode", "skills")
    os.makedirs(target_skills, exist_ok=True)
    count = 0
    for name in os.listdir(GLOBAL_SKILLS):
        src = os.path.join(GLOBAL_SKILLS, name)
        src_skill = os.path.join(src, "SKILL.md")
        if not os.path.isdir(src) or not os.path.isfile(src_skill):
            continue
        dst = os.path.join(target_skills, name)
        if os.path.exists(dst):
            shutil.rmtree(dst, ignore_errors=True)
        shutil.copytree(src, dst)
        # 改写 SKILL.md 的 description
        p = os.path.join(dst, "SKILL.md")
        with open(p, encoding="utf-8") as f:
            content = f.read()
        m = re.match(r"(---\n)([\s\S]*?)(\n---)", content)
        if m:
            fm = m.group(2)
            dm = re.search(r"(description:\s*)(.+)", fm, re.S)
            if dm:
                new_desc = rewrite_description(dm.group(2), name).replace("\n", " ")
                fm = fm[: dm.start(2)] + new_desc + fm[dm.end(2):]
                content = m.group(1) + fm + m.group(3) + content[m.end():]
        with open(p, "w", encoding="utf-8") as f:
            f.write(content)
        count += 1
        print(f"[ok] {name}")
    print(f"=== 注入完成: {count} 个 skill -> {target_skills}")

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()
    main(target)
