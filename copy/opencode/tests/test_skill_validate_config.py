# -*- coding: utf-8 -*-
# skill_validate 配置机制测试：门限修改/忽略选择/持久化生效（隔离临时目录）
import os, sys, shutil, tempfile, subprocess, json
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
SV = os.path.join(TESTS_DIR, "skill_validate.py")
pass_n, fail_n = 0, 0
def check(name, cond):
    global pass_n, fail_n
    if cond: pass_n += 1; print("  ✓ " + name)
    else: fail_n += 1; print("  ✗ " + name)

# 隔离：备份真实配置
REAL_CFG = os.path.join(TESTS_DIR, "skill_validate_config.json")
bak = None
if os.path.exists(REAL_CFG):
    bak = open(REAL_CFG, encoding="utf-8").read()

tmp = tempfile.mkdtemp(prefix="sv_cfg_")
try:
    # 造两个 skill：big（10KB）、small（1KB）
    big_dir = os.path.join(tmp, "big_skill"); os.makedirs(big_dir)
    small_dir = os.path.join(tmp, "small_skill"); os.makedirs(small_dir)
    big_fm = "---\nname: big_skill\ndescription: test big skill\n---\n" + "# " + "x" * 10240
    small_fm = "---\nname: small_skill\ndescription: test small skill\n---\n# small"
    open(os.path.join(big_dir, "SKILL.md"), "w", encoding="utf-8").write(big_fm)
    open(os.path.join(small_dir, "SKILL.md"), "w", encoding="utf-8").write(small_fm)

    def run(*args):
        return subprocess.run([sys.executable, SV] + list(args), capture_output=True, text=True, encoding="utf-8", errors="replace")

    # 1. 默认阈值 8KB → big 超限待决
    r = run(tmp)
    check("默认阈值下 big 超限进入待决", "待决" in r.stdout and "big_skill" in r.stdout)
    check("small 不超限", "small_skill" not in r.stdout.replace("校验结果", ""))

    # 2. --ignore big_skill → 静默通过
    r = run("--ignore", "big_skill", tmp)
    check("忽略后无待决无警告", "待决 0 个" in r.stdout and "警告 0 个" in r.stdout)

    # 3. 持久化生效：重跑（不传 ignore）仍通过
    r = run(tmp)
    check("忽略选择持久化（重跑仍生效）", "待决 0 个" in r.stdout)

    # 4. --set-limit 12 → 取消忽略后也不超限
    r = run("--set-limit", "12", tmp)
    check("门限值修改为 12KB", "12KB" in r.stdout or "门限值已设为 12KB" in r.stdout)

    # 5. ignore_all → 全部静默
    r = run("--ignore-all", tmp)
    check("ignore-all 生效", "待决 0 个" in r.stdout)

    # 6. --show-config
    r = run("--show-config")
    check("show-config 可读配置", "size_limit_kb" in r.stdout)

finally:
    # 恢复真实配置
    if bak is not None:
        open(REAL_CFG, "w", encoding="utf-8").write(bak)
    elif os.path.exists(REAL_CFG):
        os.remove(REAL_CFG)
    shutil.rmtree(tmp, ignore_errors=True)

print("\n结果：通过 %d 项，失败 %d 项" % (pass_n, fail_n))
sys.exit(1 if fail_n else 0)
