# -*- coding: utf-8 -*-
# 框架自有文件引用审计测试：引用存在性（相对文件目录解析）/ 旧术语残留 / 双向清单一致
# 范围：框架自有文件（顶层 md、SKILL.md、references、tests/tools 文档）；排除 modules\ 第三方资源库与命令示例
import os, re, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

CFG = os.path.join(os.path.expanduser("~"), ".config", "opencode")
pass_n, fail_n = 0, 0
def check(name, cond):
    global pass_n, fail_n
    if cond: pass_n += 1; print("  ✓ " + name)
    else: fail_n += 1; print("  ✗ " + name)

def collect_framework_files():
    out = []
    for root, dirs, files in os.walk(CFG):
        dirs[:] = [d for d in dirs if d not in ("node_modules", ".git", "__pycache__", "archive", "modules", "default", "repo_face")]
        for f in files:
            if f.endswith((".md", ".txt")):
                out.append(os.path.join(root, f))
    # default 容器下 skill 的 md 也纳入（default\evolution_skill）
    default_dir = os.path.join(CFG, "skills", "default")
    for root, dirs, files in os.walk(default_dir):
        dirs[:] = [d for d in dirs if d not in ("node_modules", "__pycache__")]
        for f in files:
            if f.endswith((".md", ".txt")):
                out.append(os.path.join(root, f))
    return sorted(set(out))

def resolve_ref(fp, ref):
    # 相对引用所在文件目录解析；references/ 下跨目录引用 modules/<id>/GUIDE.md 时从 skill 根解析
    base = os.path.dirname(fp)
    if ref.startswith("modules/"):
        base = os.path.dirname(base)
    cand = os.path.normpath(os.path.join(base, ref.replace("/", "\\")))
    return cand

# 排除误报模式：命令示例/占位符/绝对路径/URL
EXCLUDE_PAT = [
    r"^http", r"\$", r"[<>{}]", r"^~", r"^[A-Za-z]:[\\/]", r"^/", r"^\.\.",
    r"\s",  # 含空格=命令示例
    r"\.json$.*\.json$",  # 无
]
def skip_ref(ref):
    for p in EXCLUDE_PAT:
        if re.search(p, ref):
            return True
    return False

files = collect_framework_files()
missing_total = []
# 特例白名单：tests 目录内文件名（SKILL.md 中裸写的 test_*.py 引用，上下文即 tests\）
tests_files = set(f for f in os.listdir(os.path.join(CFG, "tests")) if re.match(r"test_.+\.(py|js)$", f))
for fp in files:
    # 历史流水豁免：evolution_log.txt 是只增不改流水，历史旧术语为历史事实
    if fp.endswith("evolution_log.txt"):
        continue
    try:
        c = open(fp, encoding="utf-8", errors="replace").read()
    except Exception:
        continue
    for m in re.findall(r"`([^`]{2,120})`", c):
        ref = m.strip()
        if skip_ref(ref):
            continue
        if not re.search(r"\.(md|txt|py|js|json|jsonc)$", ref):
            continue
        if ref in tests_files or "skill_validate.py" in ref or "path_convert.py" in ref or "health_check.py" in ref:
            continue  # tests/tools 目录裸文件名特例
        if ref in ("README.md", "INSTALL.md", "REQUIREMENTS.md", "AGENTS.md"):
            continue  # 仓库配套文档裸文件名（仓库 copy\ 下，同步流程用语）
        if ref in ("evolution.md", "evolution_log.txt"):
            continue  # 规则文件语义引用（实际位置已在铁律固化位置行写明全路径）
        if "*" in ref:
            continue  # 通配引用（references/*.md 类）
        if "," in ref or "、" in ref:
            continue  # 多文件并列（命令示例）
        if len(ref) <= 4:
            continue  # 纯扩展名片段（正则拆分产物）
        if not os.path.exists(resolve_ref(fp, ref)):
            missing_total.append((fp.replace(CFG, ""), ref))

check("框架自有文件引用缺失为 0（实际 %d）" % len(missing_total), len(missing_total) == 0)
for fp, ref in missing_total[:10]:
    print("    缺失:", fp, "→", ref)

# 旧术语残留（历史流水豁免）
old_terms = ["evolution_history.md", "第 0.5 步", "第 0.9 步", "skills\\evolution_skill", "skills/evolution_skill",
             "用户确认（推送前强制"]
hits = []
for fp in files:
    if fp.endswith("evolution_log.txt"):
        continue
    c = open(fp, encoding="utf-8", errors="replace").read()
    for t in old_terms:
        if t in c:
            hits.append((fp.replace(CFG, ""), t))
check("旧术语残留为 0（实际 %d）" % len(hits), len(hits) == 0)
for fp, t in hits[:10]:
    print("    残留:", fp, "→", t)

# tests/README 双向一致
tr = open(os.path.join(CFG, "tests", "README.md"), encoding="utf-8", errors="replace").read()
listed = set(re.findall(r"`(test_\w+\.(?:py|js))`", tr))
actual = set(f for f in os.listdir(os.path.join(CFG, "tests")) if re.match(r"test_.+\.(py|js)$", f))
check("tests/README 双向一致（幽灵 %d / 漏登 %d）" % (len(listed - actual), len(actual - listed)),
      listed == actual)
for f in sorted(listed - actual):
    print("    幽灵:", f)
for f in sorted(actual - listed):
    print("    漏登:", f)

print("\n结果：通过 %d 项，失败 %d 项" % (pass_n, fail_n))
sys.exit(1 if fail_n else 0)
