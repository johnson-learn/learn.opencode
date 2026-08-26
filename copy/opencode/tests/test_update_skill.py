# -*- coding: utf-8 -*-
# update_skill 双向同步机制自测（隔离测试，不碰真实仓库）
# 覆盖：① 调用解析（片段序列）② commit message 中文完整性（临时 git 仓库，-F 文件方式）
#       ③ 状态文件保护（模拟反向合入跳过）④ 对称回退防护判定（临时 git 双分支模拟）
import os, subprocess, sys, tempfile, shutil
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

pass_n, fail_n = 0, 0
def check(name, cond):
    global pass_n, fail_n
    if cond: pass_n += 1; print("  ✓ " + name)
    else: fail_n += 1; print("  ✗ " + name)

# ============ 用例 1：调用解析（片段序列） ============
print("[用例1] 调用解析（顺序标记序列）")
def parse_call(msg):
    """模拟 update_skill 调用解析：冒号分割，update_skill 标记=SYNC，其它=QUESTION，路径特征=DIR"""
    segs = msg.split("：")
    out = []
    for s in segs:
        s = s.strip()
        if s == "update_skill":
            out.append("SYNC")
        elif any(ch in s for ch in ("\\", "/", ":")) and s:
            out.append("DIR:" + s)
        else:
            out.append("QUESTION:" + s)
    return out

r1 = parse_call("update_skill：检查新skill")
check("update_skill：问题 → [SYNC, QUESTION]", r1 == ["SYNC", "QUESTION:检查新skill"])
r2 = parse_call("问题：update_skill")
check("问题：update_skill → [QUESTION, SYNC]", r2 == ["QUESTION:问题", "SYNC"])
r3 = parse_call("update_skill：问题：update_skill")
check("三片段交替", r3 == ["SYNC", "QUESTION:问题", "SYNC"])
r4 = parse_call("update_skill")
check("无冒号 → 仅 SYNC", r4 == ["SYNC"])
r5 = parse_call("update_skill：D:\\repo\\copy")
check("路径特征 → DIR", r5 == ["SYNC", "DIR:D:\\repo\\copy"])
r6 = parse_call("update_skill：问题：update_skill：问题2")
check("四片段依次类推", r6 == ["SYNC", "QUESTION:问题", "SYNC", "QUESTION:问题2"])

# ============ 用例 2：commit message 中文完整性（-F 文件方式） ============
print("[用例2] commit message 中文摘要完整性（文件方式，临时 git 仓库）")
tmp = tempfile.mkdtemp(prefix="us_test_")
subprocess.run(["git", "init", "-q", tmp], check=True)
subprocess.run(["git", "-C", tmp, "config", "user.email", "test@test.local"], check=True)
subprocess.run(["git", "-C", tmp, "config", "user.name", "tester"], check=True)
open(os.path.join(tmp, "f.txt"), "w", encoding="utf-8").write("x")
subprocess.run(["git", "-C", tmp, "add", "-A"], check=True)
# 模拟 update_skill 的 -F 文件方式
msg = "sync: 2026-08-26 测试中文摘要：修复对称回退防护、增加状态文件保护"
msgfile = os.path.join(tmp, "cmsg.txt")
open(msgfile, "w", encoding="utf-8").write(msg)
subprocess.run(["git", "-C", tmp, "commit", "-q", "-F", msgfile], check=True)
out = subprocess.run(["git", "-C", tmp, "log", "--format=%s", "-1"], capture_output=True, text=True, encoding="utf-8").stdout.strip()
check("commit message 中文完整无丢失", out == msg)
# 对照：-m 直接传中文（展示问题场景，不强制断言，仅记录行为）
subprocess.run(["git", "-C", tmp, "add", "-A"], check=True)
try:
    subprocess.run(["git", "-C", tmp, "commit", "-q", "-m", "直接中文消息测试"], check=True, capture_output=True)
    out2 = subprocess.run(["git", "-C", tmp, "log", "--format=%s", "-1"], capture_output=True, text=True, encoding="utf-8").stdout.strip()
    check("-m 方式本机可传中文（行为记录）", out2 == "直接中文消息测试")
except Exception as e:
    check("-m 方式失败（佐证 -F 必要性）", True)
shutil.rmtree(tmp, ignore_errors=True)

# ============ 用例 3：状态文件保护（模拟反向合入跳过） ============
print("[用例3] 反向合入状态文件保护（模拟）")
def reverse_merge(src_dir, dst_dir):
    """模拟反向合入：复制仓库文件回本机，跳过状态文件"""
    skipped = []
    for f in os.listdir(src_dir):
        if f in ("path_map.txt", "sync_target.txt"):
            skipped.append(f)
            continue
        shutil.copy2(os.path.join(src_dir, f), os.path.join(dst_dir, f))
    return skipped

tmp2 = tempfile.mkdtemp(prefix="us_merge_")
repo_dir = os.path.join(tmp2, "repo"); os.makedirs(repo_dir)
local_dir = os.path.join(tmp2, "local"); os.makedirs(local_dir)
# 仓库有占位符版状态文件（会污染本机的情况）
open(os.path.join(repo_dir, "path_map.txt"), "w", encoding="utf-8").write("<项目目录>=<项目目录>")
open(os.path.join(repo_dir, "sync_target.txt"), "w", encoding="utf-8").write("stale")
open(os.path.join(repo_dir, "SKILL.md"), "w", encoding="utf-8").write("new content")
# 本机有真实状态文件
open(os.path.join(local_dir, "path_map.txt"), "w", encoding="utf-8").write("<项目目录>=E:\\real")
open(os.path.join(local_dir, "sync_target.txt"), "w", encoding="utf-8").write("\\\\wsl.localhost\\real")
skipped = reverse_merge(repo_dir, local_dir)
check("path_map.txt 被跳过", "path_map.txt" in skipped)
check("sync_target.txt 被跳过", "sync_target.txt" in skipped)
check("本机 path_map.txt 保持真实映射", open(os.path.join(local_dir, "path_map.txt"), encoding="utf-8").read() == "<项目目录>=E:\\real")
check("SKILL.md 正常合入", open(os.path.join(local_dir, "SKILL.md"), encoding="utf-8").read() == "new content")
shutil.rmtree(tmp2, ignore_errors=True)

# ============ 用例 4：对称回退防护判定（临时 git 双分支模拟） ============
print("[用例4] 对称回退防护判定（git log 最后修改者）")
tmp3 = tempfile.mkdtemp(prefix="us_revert_")
subprocess.run(["git", "init", "-q", tmp3], check=True)
subprocess.run(["git", "-C", tmp3, "config", "user.email", "a@t.l"], check=True)
subprocess.run(["git", "-C", tmp3, "config", "user.name", "A"], check=True)
open(os.path.join(tmp3, "p.py"), "w", encoding="utf-8").write("v1")
subprocess.run(["git", "-C", tmp3, "add", "-A"], check=True)
subprocess.run(["git", "-C", tmp3, "commit", "-q", "-m", "init"], check=True)
# 模拟远端机器（B）提交修复
subprocess.run(["git", "-C", tmp3, "config", "user.name", "B-machine"], check=True)
open(os.path.join(tmp3, "p.py"), "w", encoding="utf-8").write("v2 with FIX")
subprocess.run(["git", "-C", tmp3, "add", "-A"], check=True)
subprocess.run(["git", "-C", tmp3, "commit", "-q", "-m", "B-machine 修复"], check=True)
# 判定：本机源文件是 v1（落后），仓库 HEAD 是 B-machine 的 v2
def judge_revert(local_content, repo_file):
    """模拟 0.5 步判定：仓库最后修改者非本机且内容不一致 → 本机落后，先吸收"""
    last_author = subprocess.run(["git", "-C", tmp3, "log", "-1", "--format=%an", "--", "p.py"], capture_output=True, text=True).stdout.strip()
    repo_content = open(repo_file, encoding="utf-8").read()
    if last_author != "A" and local_content != repo_content:
        return "本机落后：先吸收仓库版本再同步（对称回退防护生效）"
    return "本机领先或一致：正常正向同步"
verdict = judge_revert("v1", os.path.join(tmp3, "p.py"))
check("检测到本机落后（对称回退防护判定正确）", verdict.startswith("本机落后"))
verdict2 = judge_revert("v2 with FIX", os.path.join(tmp3, "p.py"))
check("本机与仓库一致时正常同步", verdict2 == "本机领先或一致：正常正向同步")
shutil.rmtree(tmp3, ignore_errors=True)

print("\n结果：通过 %d 项，失败 %d 项" % (pass_n, fail_n))
sys.exit(1 if fail_n else 0)
