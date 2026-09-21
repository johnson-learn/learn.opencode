# -*- coding: utf-8 -*-
# 统一测试入口（test_runner）—— 门面 + 收口，不含测试用例。
# 设计（2026-09-16 定稿蓝图）：所有散落调用 health_check/evolution_gate/test_update_skill 的上层调用处
#   统一改调本入口；本入口按入参路由到对应子入口执行，并在前后用 tmp_registry 收口
#   （测试前 register_test_start → 调子入口 → finally cleanup_test）。
# 原则：
#   - 不含任何测试用例逻辑，用例仍归各子入口（health_check/gate/update_skill）。
#   - 子入口划分准则（新增测试就近归口）：框架机制/gate → health_check 或 gate 相关；同步机制 → update_skill；
#     进化/skill 自测 → 各 skill tests/test_skill_self.py；其余常规 → health_check 全量。
#   - 新增子入口 = 路由表加一行并在此登记（守护测试 test_test_runner 校验路由表登记子入口存在）。
import os, sys, subprocess, importlib.util

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
CFG = os.path.join(os.path.expanduser("~"), ".config", "opencode")
TOOLS = os.path.join(CFG, "tools")
TESTS = os.path.join(CFG, "tests")

PY = sys.executable

# ---- 路由表（数据化；新增子入口在此加一行，并登记到 regedit/tests-README）----
# 入参 -> (显示名, 子入口执行命令构造函数, 说明)
ROUTES = {
    "health":        ("health_check", lambda: [PY, os.path.join(TOOLS, "health_check.py"), "--run"],          "框架健康全量用例（health_check 子入口）"),
    "health-quick":  ("health_quick", lambda: [PY, os.path.join(TOOLS, "health_check.py"), "--run-quick"],    "框架健康快子集（health_check 子入口）"),
    "gate":          ("evolution_gate", lambda sid: [PY, os.path.join(TOOLS, "evolution_gate.py"), "--check", sid], "机制精准用例（evolution_gate 子入口，需 <sid>）"),
    "update":        ("update_skill", lambda: [PY, os.path.join(TESTS, "test_update_skill.py")],              "同步定向自测（update_skill 子入口）"),
}

def _load(mod_name, path):
    s = importlib.util.spec_from_file_location(mod_name, path)
    m = importlib.util.module_from_spec(s)
    s.loader.exec_module(m)
    return m

def _registry():
    return _load("tmp_registry", os.path.join(TOOLS, "tmp_registry.py"))

def register_subentry(sub_entry):
    """登记子入口 → 路由表（供守护测试校验：路由表登记的所有子入口存在）。"""
    return sub_entry in ROUTES

def list_subentries():
    """列出所有已登记子入口（守护测试用）。"""
    return sorted(ROUTES.keys())

def run(mode, sid=None, dry_run=False):
    """统一入口：按 mode 路由到子入口，前后 tmp_registry 收口。返回退出码。"""
    if mode not in ROUTES:
        sys.stderr.write("[test_runner] 未知模式: %s（可用: %s）\n" % (mode, ", ".join(sorted(ROUTES))))
        return 2
    name, cmd_fn, desc = ROUTES[mode]
    cmd = cmd_fn(sid) if sid is not None else cmd_fn()
    # 门面诊断走 stderr，保持 stdout 纯净（仅子入口输出，供 gateOut/待办透传不被门面噪音污染）
    sys.stderr.write("[test_runner] 子入口=%s | %s | %s\n" % (name, desc, " ".join(cmd)))
    if dry_run:
        sys.stderr.write("[test_runner] dry-run 不实际执行\n")
        return 0
    reg = _registry()
    reg.register_test_start(mode)
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8",
                           errors="replace", timeout=900)
        # 完整透传子入口 stdout/stderr（不得截断——gate 的待办/gateOut 依赖完整输出）
        sys.stdout.write(r.stdout if r.stdout else "")
        sys.stderr.write(r.stderr if r.stderr else "")
        sys.stdout.flush()
        return r.returncode
    finally:
        reg.cleanup_test_runner(mode)

if __name__ == "__main__":
    args = sys.argv[1:]
    if "-h" in args or "--help" in args or not args:
        print("用法: python test_runner.py <mode> [--sid <会话ID>] [--dry-run]")
        print("可用子入口: %s" % ", ".join(sorted(ROUTES)))
        print("  --health         health_check --run 全量")
        print("  --health-quick   health_check --run-quick 快子集")
        print("  --gate <sid>     evolution_gate --check <sid> 机制精准")
        print("  --update         test_update_skill 同步定向自测")
        sys.exit(0)
    mode = args[0].lstrip("-")
    sid = None
    dry = "--dry-run" in args
    if "--sid" in args:
        sid = args[args.index("--sid") + 1]
    sys.exit(run(mode, sid=sid, dry_run=dry))
