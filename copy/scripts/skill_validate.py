# -*- coding: utf-8 -*-
# skill 自检脚本：校验全局 skill 的 frontmatter 合法性与路由引用完整性
# 用法: python skill_validate.py [skills目录]
# 配置管理（用户选择，持久化于 skill_validate_config.json，后续一致性生效）:
#   python skill_validate.py --show-config
#   python skill_validate.py --set-limit <KB数> [skills目录]     修改门限值
#   python skill_validate.py --ignore <skill名> [skills目录]     忽略指定 skill 超限
#   python skill_validate.py --ignore-all [skills目录]           忽略全部超限
import os, re, sys, json
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

CONFIG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "skill_validate_config.json")
DEFAULT_LIMIT_KB = 8

def load_config():
    try:
        with open(CONFIG, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"size_limit_kb": DEFAULT_LIMIT_KB, "ignored_skills": [], "ignore_all": False}

def save_config(cfg):
    with open(CONFIG, "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)

def validate(root, cfg=None):
    cfg = cfg or load_config()
    errors, warnings, pending = [], [], []
    limit_kb = int(cfg.get("size_limit_kb", DEFAULT_LIMIT_KB))
    limit_bytes = limit_kb * 1024
    if not os.path.isdir(root):
        print("目录不存在:", root)
        return 1
    # default 是"默认触发"分类容器：校验其子目录内的 skill，而非 default 本身
    skill_entries = []
    for name in sorted(os.listdir(root)):
        d = os.path.join(root, name)
        if not os.path.isdir(d):
            continue
        if name == "default":
            for sub in sorted(os.listdir(d)):
                if os.path.isdir(os.path.join(d, sub)):
                    skill_entries.append((sub, os.path.join(d, sub)))
            continue
        skill_entries.append((name, d))
    for name, skill_dir in skill_entries:
        p = os.path.join(skill_dir, "SKILL.md")
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
        for ref in set(re.findall(r"`modules/([^`/]+)`", c)):
            if not os.path.isdir(os.path.join(skill_dir, "modules", ref)):
                errors.append("%s: 路由表引用缺失 modules/%s" % (name, ref))
        if len(c) > limit_bytes:
            if cfg.get("ignore_all") or name in cfg.get("ignored_skills", []):
                continue
            warnings.append("%s: SKILL.md %d 字节（阈值 %dKB，大块内容移 references/）" % (name, len(c), limit_kb))
            pending.append(name)
    print("=== 校验结果 ===")
    for e in errors:
        print("[错误]", e)
    for w in warnings:
        print("[警告]", w)
    if pending:
        print("=== 超限待决清单（请选择处理方式，选择后持久化生效）===")
        print("选择1 修改门限值: python skill_validate.py --set-limit <新KB数> <skills目录>")
        print("选择2 忽略指定:   python skill_validate.py --ignore <skill名> <skills目录>（可逐个）")
        print("选择3 忽略全部:   python skill_validate.py --ignore-all <skills目录>")
        print("待决:", ", ".join(pending))
    if not errors and not warnings and not pending:
        print("全部通过")
    print("错误 %d 个，警告 %d 个，待决 %d 个" % (len(errors), len(warnings), len(pending)))
    return 1 if errors else 0

def main():
    args = sys.argv[1:]
    root_default = os.path.join(os.path.expanduser("~"), ".config", "opencode", "skills")
    root = root_default
    # 提取子命令
    action = None
    value = None
    rest = []
    i = 0
    while i < len(args):
        a = args[i]
        if a in ("--set-limit", "--ignore") and i + 1 < len(args):
            action, value = a, args[i + 1]
            i += 2
        elif a == "--ignore-all":
            action = a
            i += 1
        elif a == "--show-config":
            action = a
            i += 1
        else:
            rest.append(a)
            i += 1
    if rest:
        root = rest[0]
    cfg = load_config()
    if action == "--show-config":
        print("当前配置:", json.dumps(cfg, ensure_ascii=False, indent=2))
        print("配置文件:", CONFIG)
        return 0
    if action == "--set-limit":
        try:
            cfg["size_limit_kb"] = int(value)
        except ValueError:
            print("门限值必须为整数 KB:", value)
            return 1
        save_config(cfg)
        print("门限值已设为 %dKB（持久化）" % cfg["size_limit_kb"])
    elif action == "--ignore":
        if value not in cfg["ignored_skills"]:
            cfg["ignored_skills"].append(value)
            save_config(cfg)
        print("已忽略超限:", value, "（持久化）")
    elif action == "--ignore-all":
        cfg["ignore_all"] = True
        save_config(cfg)
        print("已忽略全部超限（持久化）")
    return validate(root, cfg)

if __name__ == "__main__":
    sys.exit(main())
