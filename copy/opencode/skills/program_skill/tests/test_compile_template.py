# -*- coding: utf-8 -*-
# program_skill L1 行为自测（2026-09-01 框架进化评审建议落地）：
# 复制 templates/c-project → 临时目录 → WSL gcc 实编译实运行（骨架真实可用验证）
import os, shutil, subprocess, sys, tempfile
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

SKILL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TPL = os.path.join(SKILL, "templates", "c-project")
pass_n, fail_n = 0, 0
def check(name, cond):
    global pass_n, fail_n
    if cond: pass_n += 1; print("  ✓ " + name)
    else: fail_n += 1; print("  ✗ " + name)

# WSL 可用性探测
r = subprocess.run(["wsl", "-d", "Ubuntu", "-e", "bash", "-c", "gcc --version | head -1"],
                   capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=60)
if r.returncode != 0:
    print("  （WSL 不可达，跳过实编译行为自测）")
    print("\n结果：通过 %d 项，失败 %d 项（跳过行为项）" % (pass_n, fail_n))
    sys.exit(0)

tmp = tempfile.mkdtemp(prefix="c_tpl_")
shutil.copytree(TPL, os.path.join(tmp, "proj"))
wsl_proj = "/tmp/c_tpl_proj_" + os.path.basename(tmp)

def wsl(cmd):
    r2 = subprocess.run(["wsl", "-d", "Ubuntu", "-e", "bash", "-c", cmd],
                        capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=300)
    return r2

# 复制进 WSL 并 make 编译
setup = ("rm -rf %s && mkdir -p %s && cp -r /mnt/c/Users/job_p/AppData/Local/Temp/%s/proj/* %s/ "
         "&& cd %s && make 2>&1 | tail -3" % (wsl_proj, wsl_proj, os.path.basename(tmp), wsl_proj, wsl_proj))
r = wsl(setup)
check("make 编译通过（gcc 零警告）", r.returncode == 0 and "error" not in r.stdout.lower() and "warning" not in r.stdout.lower())
run_out = wsl("cd %s && ./app" % wsl_proj)
check("编译产物运行输出 hello c-project", run_out.returncode == 0 and "hello c-project" in run_out.stdout)
# cmake 构建路径
cm = wsl("cd %s && rm -rf build && cmake -B build -S . > /dev/null 2>&1 && cmake --build build > /dev/null 2>&1 && ./build/app" % wsl_proj)
check("CMake 构建运行通过", cm.returncode == 0 and "hello c-project" in cm.stdout)
wsl("rm -rf %s" % wsl_proj)
shutil.rmtree(tmp, ignore_errors=True)

print("\n结果：通过 %d 项，失败 %d 项" % (pass_n, fail_n))
sys.exit(1 if fail_n else 0)
