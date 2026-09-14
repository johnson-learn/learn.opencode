# -*- coding: utf-8 -*-
# task_tracking_skill L1 领域自测（2026-09-14 新建）：入口规范 / 模块引用无悬空 / references 无悬空 / 技能特定断言
import os, re, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

SKILL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
pass_n, fail_n = 0, 0
def check(name, cond):
    global pass_n, fail_n
    if cond: pass_n += 1; print("  ✓ " + name)
    else: fail_n += 1; print("  ✗ " + name)

SKILL_MD = os.path.join(SKILL, "SKILL.md")
c = open(SKILL_MD, encoding="utf-8", errors="replace").read()

# 1. 入口规范
m = re.search(r"^---\n(.*?)\n---", c, re.S)
check("frontmatter 存在", bool(m))
fm = m.group(1) if m else ""
check("name 为 task_tracking_skill", re.search(r"^name:\s*task_tracking_skill\s*$", fm, re.M) is not None)
dm = re.search(r"^description:\s*(.*)$", fm, re.M)
check("description 为默认触发型（任务窗执行器）", dm and "默认触发" in dm.group(1) and "任务窗" in dm.group(1) and "todowrite" in dm.group(1))
check("description ≤1024 字符", dm and len(dm.group(1)) <= 1024)

# 2. 模块引用无悬空（本 skill 非聚合型，应无 modules）
mod_dir = os.path.join(SKILL, "modules")
mods = set(os.listdir(mod_dir)) if os.path.isdir(mod_dir) else set()
check("无 modules（非聚合型）", len(mods) == 0)

# 3. references 无悬空
ref_dir = os.path.join(SKILL, "references")
ref_files = set(re.findall(r"`references/([\w\-]+\.md)`", c))
have = set(os.listdir(ref_dir)) if os.path.isdir(ref_dir) else set()
missing = sorted(f for f in ref_files if f not in have)
check("references 索引无悬空（缺失: %s）" % ",".join(missing) if missing else "references 索引无悬空（引用 %d 个）" % len(ref_files), len(missing) == 0)

# 4. 技能特定断言：任务窗强制流程要素（对应 AGENTS 铁律第 8 条动作化）
check("含第0步：收到新要求第一步即建/更新任务窗", "第0步" in c or "收到新要求/新消息，第一步" in c)
check("含核心要求：实时更新（每完成一个任务即更新该条目状态直至全清）", ("实时更新" in c) and ("每完成一个任务" in c) and ("全部条目 completed" in c or "全部 completed" in c))
check("含每步完成立即标记", "立即标记" in c and "禁止最后批量补标记" in c)
check("含用户更新要求同步主+子智能体任务窗", "用户更新要求" in c and "子智能体" in c)
check("含任务量大用子智能体分担并行且纳入任务窗", "子智能体" in c and "分担并行" in c)
check("含先建窗再动工/禁止先做后补窗", "先建/更新窗再动工" in c or "先做后补窗" in c)
check("引用 AGENTS 铁律第 8 条", "铁律第 8 条" in c or "铁律第8条" in c)
check("引用 instructions 第 6 条长任务执行节奏", "第 6 条" in c or "长任务执行节奏" in c)
check("含工具依赖清单章节", "工具依赖清单" in c)
check("含本 skill 经验索引", "经验索引" in c)
check("templates 任务窗模板存在", os.path.isdir(os.path.join(SKILL, "templates")) and os.path.isfile(os.path.join(SKILL, "templates", "todo-template.md")))

print("\n结果：通过 %d 项，失败 %d 项" % (pass_n, fail_n))
sys.exit(1 if fail_n else 0)
