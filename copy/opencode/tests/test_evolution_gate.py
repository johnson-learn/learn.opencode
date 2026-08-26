# -*- coding: utf-8 -*-
# evolution_gate 门禁脚本测试：快照→无改动→有改动（流水兜底追加/自动测试触发）
import os, sys, subprocess, json, tempfile, time
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

CFG = os.path.join(os.path.expanduser("~"), ".config", "opencode")
GATE = os.path.join(CFG, "tools", "evolution_gate.py")
LOG = os.path.join(CFG, "skills", "default", "evolution_skill", "evolution_log.txt")
pass_n, fail_n = 0, 0
def check(name, cond):
    global pass_n, fail_n
    if cond: pass_n += 1; print("  ✓ " + name)
    else: fail_n += 1; print("  ✗ " + name)

def run(*args):
    return subprocess.run([sys.executable, GATE] + list(args), capture_output=True,
                          text=True, encoding="utf-8", errors="replace", timeout=300)

sid = "gate-test-" + str(int(time.time()))
# 备份 log 尾部大小
log_size0 = os.path.getsize(LOG) if os.path.exists(LOG) else 0

# 1. 快照
r = run("--snapshot", sid)
check("快照成功", r.returncode == 0 and "快照完成" in r.stdout)

# 2. 无改动 check → 门禁通过
r = run("--check", sid)
check("无改动时门禁通过", r.returncode == 0 and "无规则文件改动" in r.stdout)

# 3. 模拟改动：创建临时规则文件（不污染真实目录——用临时 watch 替代？gate 固定 watch CFG，改为在 skills 下建临时 skill 后删除）
tmp_skill = os.path.join(CFG, "skills", "_gate_test_skill")
os.makedirs(tmp_skill, exist_ok=True)
tmp_md = os.path.join(tmp_skill, "SKILL.md")
open(tmp_md, "w", encoding="utf-8").write("---\nname: _gate_test_skill\ndescription: gate test\n---\n# test\n")
# 重新快照（含临时文件）
r = run("--snapshot", sid)
# 修改文件
time.sleep(0.05)
open(tmp_md, "w", encoding="utf-8").write("---\nname: _gate_test_skill\ndescription: gate test\n---\n# test v2\n")
r = run("--check", sid)
check("有改动时检测到", "检测到" in r.stdout and "_gate_test_skill" in r.stdout)
log_size1 = os.path.getsize(LOG)
check("流水兜底自动追加", log_size1 > log_size0)
check("自动测试已执行（含 evolution_consistency）", "test_evolution_consistency" in r.stdout)
check("待模型补充清单输出", "待模型补充" in r.stdout)

# 4. 快照文件清理
import glob
snaps = glob.glob(os.path.join(tempfile.gettempdir(), "opencode_gate", "gate_" + sid + ".json"))
check("check 后快照文件已清理", len(snaps) == 0)

# 清理临时 skill + 从 log 移除测试追加？（log 只增不改——测试追加的骨架留在 log 是污染，但"只增不改"禁删。处理：测试使用独立 log？gate 的 LOG 固定。为不污染，测试后把刚追加的骨架条目标记为测试条目？不能删。折中：保留（它记录了 gate 机制验证事实，无害））
import shutil
shutil.rmtree(tmp_skill, ignore_errors=True)
print("  （注：gate 测试在 evolution_log.txt 追加的骨架条目保留——只增不改铁律）")

print("\n结果：通过 %d 项，失败 %d 项" % (pass_n, fail_n))
sys.exit(1 if fail_n else 0)
