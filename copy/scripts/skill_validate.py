# -*- coding: utf-8 -*-
# skill 自检脚本：校验全局 skill 的 frontmatter 合法性与路由引用完整性
# 用法: python skill_validate.py [skills目录]
import os, re, sys

def validate(root):
    errors, warnings = [], []
    if not os.path.isdir(root):
        print("目录不存在:", root)
        return 1
    for name in sorted(os.listdir(root)):
        skill_dir = os.path.join(root, name)
        p = os.path.join(skill_dir, "SKILL.md")
        if not os.path.isdir(skill_dir):
            continue
        if not os.path.isfile(p):
            errors.append("%s: 缺 SKILL.md" % name)
            continue
        with open(p, encoding="utf-8") as f:
            c = f.read()
        m = re.match(r"^\ufeff?---\n(.*?)\n---", c, re.S)
        if not m:
            errors.append("%s: frontmatter 缺失或格式错误" % name)
            continue
        fm = m.group(1)
        nm = re.search(r"name:\s*(\S+)", fm)
        if not nm:
            errors.append("%s: frontmatter 缺 name" % name)
        elif nm.group(1) != name:
            errors.append("%s: name(%s) 与目录名(%s) 不一致" % (name, nm.group(1), name))
        dm = re.search(r"description:\s*(.+)", fm, re.S)
        if not dm:
            errors.append("%s: frontmatter 缺 description" % name)
        elif len(dm.group(1).strip()) > 1024:
            errors.append("%s: description 超 1024 字符(%d)" % (name, len(dm.group(1))))
        # 路由表引用检查：modules/<xxx> 路径存在性
        for ref in set(re.findall(r"`modules/([^`/]+)`", c)):
            if not os.path.isdir(os.path.join(skill_dir, "modules", ref)):
                errors.append("%s: 路由表引用缺失 modules/%s" % (name, ref))
        # 入口规模警告（>8KB 提示瘦身）
        if len(c) > 8192:
            warnings.append("%s: SKILL.md %d 字节（建议 ≤8KB，大块内容移 references/）" % (name, len(c)))
    print("=== 校验结果 ===")
    for e in errors:
        print("[错误]", e)
    for w in warnings:
        print("[警告]", w)
    if not errors and not warnings:
        print("全部通过")
    print("错误 %d 个，警告 %d 个" % (len(errors), len(warnings)))
    return 1 if errors else 0

if __name__ == "__main__":
    root = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.expanduser("~"), ".config", "opencode", "skills")
    sys.exit(validate(root))
