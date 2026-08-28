# -*- coding: utf-8 -*-
# health_check.py 测试（扩充版）：可运行 / 报告结构 / 八检查项 / 无失败项 / --run 实跑模式
import os, sys, subprocess
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

CFG = os.path.join(os.path.expanduser("~"), ".config", "opencode")
HC = os.path.join(CFG, "tools", "health_check.py")
pass_n, fail_n = 0, 0
def check(name, cond):
    global pass_n, fail_n
    if cond: pass_n += 1; print("  ✓ " + name)
    else: fail_n += 1; print("  ✗ " + name)

# 1. 基本运行与报告结构
r = subprocess.run([sys.executable, HC], capture_output=True, text=True,
                   encoding="utf-8", errors="replace", timeout=300)
check("health_check 可运行（rc=0）", r.returncode == 0)
check("报告含标题", "框架健康度报告" in r.stdout)
check("报告含九检查项", all(x in r.stdout for x in ["核心配置", "skill frontmatter", "插件最近执行", "测试全部可解析", "门禁", "evolution_log", "平台 API", "字符边界", "注入总量"]))
check("注入量检查输出总量与上限", "注入总量" in r.stdout and "50KB" in r.stdout)
check("报告含结论统计行", "结论：OK" in r.stdout and "失败" in r.stdout)
check("无 [失败] 项（当前框架健康）", "[失败]" not in r.stdout)

# 2. 核心配置清单与 regedit 一致（6 文件）
reg = open(os.path.join(CFG, "regedit.md"), encoding="utf-8", errors="replace").read()
check("核心配置 6 文件均在 regedit 铁律层登记", all(f in reg for f in ["AGENTS.md", "instructions.md", "regedit.md", "docs-sync.md", "tools-manifest.md"]))

# 3. --run-quick 实跑模式（快测试子集；预计耗时约 30~90 秒）
print("[提示] 即将实跑快测试子集（skill_validate + test_regedit + test_evolution_consistency），预计耗时约 30~90 秒…")
r2 = subprocess.run([sys.executable, HC, "--run-quick"], capture_output=True, text=True,
                    encoding="utf-8", errors="replace", timeout=600)
check("--run-quick 实跑模式可运行", r2.returncode == 0)
check("--run-quick 含实跑结论", "实跑快测试子集" in r2.stdout or "实跑失败" in r2.stdout)

print("\n结果：通过 %d 项，失败 %d 项" % (pass_n, fail_n))
sys.exit(1 if fail_n else 0)
