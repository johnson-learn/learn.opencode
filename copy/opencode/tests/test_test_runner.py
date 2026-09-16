# -*- coding: utf-8 -*-
# test_runner 统一入口守护测试：路由表登记存在 / 子入口文件存在 / dry-run 路由 / 未知模式
import os, sys, importlib.util
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

CFG = os.path.join(os.path.expanduser("~"), ".config", "opencode")
RUNNER = os.path.join(CFG, "tools", "test_runner.py")
TOOLS = os.path.join(CFG, "tools")
TESTS = os.path.join(CFG, "tests")

spec = importlib.util.spec_from_file_location("test_runner", RUNNER)
tr = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tr)

pass_n, fail_n = 0, 0
def check(name, cond):
    global pass_n, fail_n
    if cond: pass_n += 1; print("  ✓ " + name)
    else: fail_n += 1; print("  ✗ " + name)

# 1. 路由表含四个已定子入口
required = {"health", "health-quick", "gate", "update"}
present = set(tr.ROUTES.keys())
check("路由表含全部已定子入口（health/health-quick/gate/update）", required.issubset(present))

# 2. 每个子入口对应的脚本文件真实存在（路由不悬空）
check("health 子入口脚本存在", os.path.exists(os.path.join(TOOLS, "health_check.py")))
check("gate 子入口脚本存在", os.path.exists(os.path.join(TOOLS, "evolution_gate.py")))
check("update 子入口脚本存在", os.path.exists(os.path.join(TESTS, "test_update_skill.py")))

# 3. register_subentry / list_subentries 工作
check("list_subentries 列全 4 个子入口", tr.list_subentries() == sorted(required))
check("register_subentry 识别已登记子入口", tr.register_subentry("health") is True)
check("register_subentry 拒绝未登记子入口", tr.register_subentry("nope") is False)

# 4. dry-run：路由正确但不实际执行
r0 = tr.run("health", dry_run=True)
check("dry-run 模式不实际执行且返回 0", r0 == 0)

# 5. 未知模式返回 2
r_unk = tr.run("not_a_mode", dry_run=True)
check("未知模式返回 2", r_unk == 2)

print("\n结果：通过 %d 项，失败 %d 项" % (pass_n, fail_n))
sys.exit(1 if fail_n else 0)
