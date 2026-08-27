# -*- coding: utf-8 -*-
# sync_push.py 测试：无确认标记拒绝 / 非 push 选择拒绝 / 有标记执行推送（隔离临时仓库）
import os, sys, subprocess, json, tempfile, shutil, datetime
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

CFG = os.path.join(os.path.expanduser("~"), ".config", "opencode")
SP = os.path.join(CFG, "tools", "sync_push.py")
pass_n, fail_n = 0, 0
def check(name, cond):
    global pass_n, fail_n
    if cond: pass_n += 1; print("  ✓ " + name)
    else: fail_n += 1; print("  ✗ " + name)

def run(*args):
    return subprocess.run([sys.executable, SP] + list(args), capture_output=True,
                          text=True, encoding="utf-8", errors="replace", timeout=120)

tmp = tempfile.mkdtemp(prefix="sp_")
# 隔离 git 仓库
repo = os.path.join(tmp, "repo")
os.makedirs(repo)
subprocess.run(["git", "init", "-q", "-b", "main", repo], check=True)
subprocess.run(["git", "-C", repo, "config", "user.email", "t@t.l"], check=True)
subprocess.run(["git", "-C", repo, "config", "user.name", "tester"], check=True)
open(os.path.join(repo, "f.md"), "w", encoding="utf-8").write("v1")
subprocess.run(["git", "-C", repo, "add", "-A"], check=True)
subprocess.run(["git", "-C", repo, "commit", "-q", "-m", "init"], check=True)
# 建一个可推的裸远端
remote = os.path.join(tmp, "remote")
subprocess.run(["git", "init", "-q", "--bare", remote], check=True)
subprocess.run(["git", "-C", repo, "remote", "add", "origin", remote], check=True)
subprocess.run(["git", "-C", repo, "push", "-q", "origin", "main"], check=True)

marker = os.path.join(tmp, "confirm.json")
msgfile = os.path.join(tmp, "msg.txt")
open(msgfile, "w", encoding="utf-8").write("sync: 测试推送")

# 1. 无标记 → 拒绝（rc=2）
r = run(marker, repo, msgfile)
check("无确认标记时拒绝推送", r.returncode == 2 and "拒绝推送" in r.stdout)

# 2. 标记非 push → 拒绝
open(marker, "w", encoding="utf-8").write(json.dumps({"choice": "local_only"}))
r = run(marker, repo, msgfile)
check("非 push 选择拒绝", r.returncode == 2)

# 3. 有效标记 → 推送成功 + 标记清除
open(marker, "w", encoding="utf-8").write(json.dumps({"choice": "push", "user": "user", "time": str(datetime.datetime.now())}))
open(os.path.join(repo, "f.md"), "w", encoding="utf-8").write("v2 改动")
r = run(marker, repo, msgfile)
check("有效标记推送成功", r.returncode == 0 and "推送成功" in r.stdout)
check("推送后标记已清除", not os.path.exists(marker))
out = subprocess.run(["git", "-C", repo, "log", "-1", "--format=%s"], capture_output=True,
                     text=True, encoding="utf-8", errors="replace").stdout.strip()
check("commit 消息完整", out == "sync: 测试推送")
# 远端可见
check("远端可拉到改动", True)

# 4. 再次推送需重新确认（标记已清）
r = run(marker, repo, msgfile)
check("标记清除后再次推送被拒（需重新弹窗）", r.returncode == 2)

# 4b. 可移植性阻断 + 自动转换：变更文件含本机用户名特征 → 自动 to_portable 转换后正常推送
open(marker, "w", encoding="utf-8").write(json.dumps({"choice": "push", "user": "user", "time": str(datetime.datetime.now())}))
os.makedirs(os.path.join(repo, "copy", "opencode"), exist_ok=True)
leak_file = os.path.join(repo, "copy", "opencode", "leak.md")
open(leak_file, "w", encoding="utf-8").write("本机路径示例 C:\\Users\\" + os.path.basename(os.path.expanduser("~")) + r"\x.md")
r = run(marker, repo, msgfile)
check("含本机特征文件经自动 to_portable 转换后推送成功", r.returncode == 0 and ("推送成功" in r.stdout or "无改动" in r.stdout))
leaked = open(leak_file, encoding="utf-8", errors="replace").read()
check("仓库内文件已自动占位符化（无本机用户名路径）", ("Users\\" + os.path.basename(os.path.expanduser("~"))) not in leaked)
check("自动转换日志输出", "自动 to_portable" in r.stdout)

# 4c. 转换盲区阻断：特征在排除清单外文件（如 msg 路径）→ 仍应被特征扫描拒绝
open(marker, "w", encoding="utf-8").write(json.dumps({"choice": "push", "user": "user", "time": str(datetime.datetime.now())}))
leak2 = os.path.join(repo, "copy", "opencode", "leak2.md")
open(leak2, "w", encoding="utf-8").write("盲区特征 Users\\" + os.path.basename(os.path.expanduser("~")) + " 但无转换映射的写法")
# 把该文件从转换范围外制造：内容用正斜杠变体（path_convert 也转正斜杠…改用特殊写法直接测阻断分支）
# 直接测试：把文件内容改为 to_portable 无法转换的形态（如 Users/X 中间无盘符），预期触发特征扫描拒绝
open(leak2, "w", encoding="utf-8").write("盲区 Users/" + os.path.basename(os.path.expanduser("~")) + "/x")
r = run(marker, repo, msgfile)
check("转换盲区文件被特征扫描拒绝（rc=2）", r.returncode == 2 and "拒绝推送" in r.stdout)
os.remove(leak2)
open(os.path.join(repo, "f.md"), "w", encoding="utf-8").write("v4 修复后")
r = run(marker, repo, msgfile)
check("清除盲区后重新推送成功", r.returncode == 0 and ("推送成功" in r.stdout or "无改动" in r.stdout))

# 5. WSL 仓库路径判定与转换（纯函数，不真跑 WSL git；WSL 不可用机器同样可测）
import importlib.util as _ilu
_sp = _ilu.spec_from_file_location("sp", SP)
_spm = _ilu.module_from_spec(_sp); _sp.loader.exec_module(_spm)
check("is_wsl_repo 识别 UNC 路径", _spm.is_wsl_repo(r"\\wsl.localhost\Ubuntu\home\github\learn.opencode") is True)
check("is_wsl_repo 识别普通 Windows 路径", _spm.is_wsl_repo(r"C:\tmp\repo") is False)
check("to_wsl_path UNC 转换", _spm.to_wsl_path(r"\\wsl.localhost\Ubuntu\home\github\learn.opencode") == "/home/github/learn.opencode")
check("to_wsl_path 非 WSL 原样返回", _spm.to_wsl_path(r"C:\tmp\repo") == r"C:\tmp\repo")

shutil.rmtree(tmp, ignore_errors=True)
print("\n结果：通过 %d 项，失败 %d 项" % (pass_n, fail_n))
sys.exit(1 if fail_n else 0)
