# -*- coding: utf-8 -*-
# evolution 一致性测试：evolution.md 近 N 条记录声明的机制/环节/流程 必须落在对应规则文件（防"规则当记录"遗漏）
import os, re, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

CFG = os.path.join(os.path.expanduser("~"), ".config", "opencode")
pass_n, fail_n = 0, 0
def check(name, cond):
    global pass_n, fail_n
    if cond: pass_n += 1; print("  ✓ " + name)
    else: fail_n += 1; print("  ✗ " + name)

evo = open(os.path.join(CFG, "skills", "default", "evolution_skill", "evolution.md"), encoding="utf-8").read()
hist = open(os.path.join(CFG, "skills", "default", "evolution_skill", "evolution_log.txt"), encoding="utf-8").read()
agents = open(os.path.join(CFG, "AGENTS.md"), encoding="utf-8").read()
reg = open(os.path.join(CFG, "regedit.md"), encoding="utf-8").read()
evo_skill = open(os.path.join(CFG, "skills", "default", "evolution_skill", "SKILL.md"), encoding="utf-8").read()
us_skill = open(os.path.join(CFG, "skills", "update_skill", "SKILL.md"), encoding="utf-8").read()

# 1. 归属二分铁律已写入 AGENTS.md 与 evolution_skill
check("AGENTS.md 含归属二分铁律", "归属二分铁律" in agents and "只写 evolution_log.txt = 归属失败" in agents)
check("evolution_skill 含归属二分判定", "归属二分判定" in evo_skill and "归属失败" in evo_skill)
check("AGENTS.md 含流程类变更须同步 SKILL.md+regedit", "流程类变更必须同步 SKILL.md 与 regedit.md" in agents)

# 2. evolution_log.txt 近 5 条记录（追加式=最新在尾部，排除门禁机器骨架条目）声明的「术语」在对应规则文件出现
entries = [e for e in re.findall(r"\[2026-08-26\][^\[]+", hist) if "会话自动门禁" not in e]
recent = entries[-5:]
rule_files = agents + reg + evo_skill + us_skill + evo
# 声明模式：「术语」/『术语』 视为机制/环节声明（近 5 条记录内）
declared = set()
for e in recent:
    for m in re.findall(r"[「『]([^」』]{2,30})[」』]", e):
        declared.add(m)
check("近 5 条记录含可核查的机制声明（%d 项）" % len(declared), len(declared) > 0)
missing = [d for d in declared if d not in rule_files]
check("声明全部落入规则文件（缺失 %d 项）" % len(missing), len(missing) == 0)
if missing:
    print("    缺失:", missing[:5])

# 3. 具体抽查：对端修改评审环节 必须已在 update_skill SKILL.md
check("「对端修改评审」环节已固化入 update_skill SKILL.md", "对端修改评审" in us_skill)
check("回退注释三要素格式已固化", "提交 commit" in us_skill and "时间" in us_skill and "回退原因" in us_skill)
check("可移植性校验环节已固化入 SKILL.md", "可移植性校验" in us_skill)
check("五步框架已固化入 SKILL.md", "第一步：吸收远端" in us_skill and "第四步：弹窗确认" in us_skill)

# 4. evolution.md 规则文件定位抽查（用户 2026-08-26 新定义）
check("evolution.md 为规则文件（非流水）", "进化规则" in evo and "规则文件" in evo)
check("evolution_log.txt 存在且只增不改声明", "只增不改" in hist)
check("evolution.md 更新须弹窗确认", "弹窗让用户确认" in evo or "弹窗" in evo and "确认" in evo)
check("evolution.md 更新须核对历史", "evolution_log.txt" in evo)
check("evolution_skill 含历史流水追加铁律", "evolution_log.txt" in evo_skill and "只增不改" in evo_skill)
check("evolution_skill 含规则更新弹窗确认流程", "弹窗让用户确认" in evo_skill)

print("\n结果：通过 %d 项，失败 %d 项" % (pass_n, fail_n))
sys.exit(1 if fail_n else 0)
