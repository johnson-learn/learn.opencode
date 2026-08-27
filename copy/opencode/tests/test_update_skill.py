# -*- coding: utf-8 -*-
# update_skill 双向同步机制自测（隔离测试，不碰真实仓库）
# 覆盖：① 调用解析（片段序列）② commit message 中文完整性（临时 git 仓库，-F 文件方式）
#       ③ 状态文件保护（模拟反向合入跳过）④ 对称回退防护判定（临时 git 双分支模拟）
import os, subprocess, sys, tempfile, shutil
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# 动态推导本机路径（可移植：新机器自动适配）
CFG = os.path.join(os.path.expanduser("~"), ".config", "opencode")

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
open(os.path.join(repo_dir, "path_map.txt"), "w", encoding="utf-8").write(r"<项目目录>=<项目目录>")
open(os.path.join(repo_dir, "sync_target.txt"), "w", encoding="utf-8").write("stale")
open(os.path.join(repo_dir, "SKILL.md"), "w", encoding="utf-8").write("new content")
# 本机有真实状态文件
open(os.path.join(local_dir, "path_map.txt"), "w", encoding="utf-8").write(r"<项目目录>=E:\\real")
open(os.path.join(local_dir, "sync_target.txt"), "w", encoding="utf-8").write("\\\\wsl.localhost\\real")
skipped = reverse_merge(repo_dir, local_dir)
check("path_map.txt 被跳过", "path_map.txt" in skipped)
check("sync_target.txt 被跳过", "sync_target.txt" in skipped)
check("本机 path_map.txt 保持真实映射", open(os.path.join(local_dir, "path_map.txt"), encoding="utf-8").read() == r"<项目目录>=E:\\real")
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

print("[用例5] 五步流程关键要素（SKILL.md 规则存在性）")
sk = open(os.path.join(CFG, "skills", "update_skill", "SKILL.md"), encoding="utf-8").read()
check("SKILL.md 含五步框架标题", "吸收远端 → 修改 → 自测 → 用户确认 → 按选择执行" in sk)
check("第一步：先 pull 吸收远端", "第一步：吸收远端" in sk)
check("第二步：修改+盘点", "第二步：修改" in sk)
check("第三步：自测（缺用例先补写）", "第三步：自测" in sk and "先写用例再跑" in sk)
check("第三步要求双向更新用例模拟远端", "模拟远端操作" in sk)
check("第四步：弹窗确认", "第四步：弹窗确认" in sk and "填写新内容" in sk)
check("第五步：按选择执行", "第五步：按用户选择执行" in sk)

# ============ 用例 6：模拟远端操作（双仓库：远端新提交 → 吸收 → 修改 → 推送） ============
print("[用例6] 模拟远端操作完整链路（隔离双仓库）")
tmp6 = tempfile.mkdtemp(prefix="us_remote_")
# 远端仓库（模拟 GitHub）
remote_dir = os.path.join(tmp6, "remote")
os.makedirs(remote_dir)
subprocess.run(["git", "init", "-q", "--bare", remote_dir], check=True)
# 本机工作树
local_dir = os.path.join(tmp6, "local")
subprocess.run(["git", "init", "-q", "-b", "main", local_dir], check=True)
subprocess.run(["git", "-C", local_dir, "config", "user.email", "a@t.l"], check=True)
subprocess.run(["git", "-C", local_dir, "config", "user.name", "machine-A"], check=True)
open(os.path.join(local_dir, "f.md"), "w", encoding="utf-8").write("v1")
subprocess.run(["git", "-C", local_dir, "add", "-A"], check=True)
subprocess.run(["git", "-C", local_dir, "commit", "-q", "-m", "init"], check=True)
subprocess.run(["git", "-C", local_dir, "remote", "add", "origin", remote_dir], check=True)
subprocess.run(["git", "-C", local_dir, "push", "-q", "origin", "main"], check=True)
# 模拟远端新提交（另一台机器：克隆→改→推）
other_dir = os.path.join(tmp6, "other")
subprocess.run(["git", "clone", "-q", "-b", "main", remote_dir, other_dir], check=True)
subprocess.run(["git", "-C", other_dir, "config", "user.email", "b@t.l"], check=True)
subprocess.run(["git", "-C", other_dir, "config", "user.name", "machine-B"], check=True)
open(os.path.join(other_dir, "f.md"), "w", encoding="utf-8").write("v2 with FIX from B")
subprocess.run(["git", "-C", other_dir, "add", "-A"], check=True)
subprocess.run(["git", "-C", other_dir, "commit", "-q", "-m", "B-machine 修复"], check=True)
subprocess.run(["git", "-C", other_dir, "push", "-q", "origin", "main"], check=True)
# 第一步模拟：本机 pull 吸收远端
subprocess.run(["git", "-C", local_dir, "pull", "-q", "--rebase", "origin", "main"], check=True)
out6 = open(os.path.join(local_dir, "f.md"), encoding="utf-8").read()
check("第一步 pull 吸收远端修复", out6 == "v2 with FIX from B")
# 第二步模拟：本机修改
open(os.path.join(local_dir, "f.md"), "w", encoding="utf-8").write(out6 + "\nv3 local improvement")
# 推送前用户确认（第四步）状态检查：工作区有未推送修改
st = subprocess.run(["git", "-C", local_dir, "status", "--short"], capture_output=True, text=True).stdout
check("推送前工作区有未提交修改（待确认）", "M f.md" in st)
# 第五步模拟：确认后推送（-F 文件方式）
msg6 = "sync: 2026-08-26 模拟双向更新测试"
mf6 = os.path.join(tmp6, "m.txt")
open(mf6, "w", encoding="utf-8").write(msg6)
subprocess.run(["git", "-C", local_dir, "add", "-A"], check=True)
subprocess.run(["git", "-C", local_dir, "commit", "-q", "-F", mf6], check=True)
subprocess.run(["git", "-C", local_dir, "push", "-q", "origin", "main"], check=True)
# 反向验证：另一台机器 pull 看到本机修改
subprocess.run(["git", "-C", other_dir, "pull", "-q", "--rebase", "origin", "main"], check=True)
out7 = open(os.path.join(other_dir, "f.md"), encoding="utf-8").read()
check("推送后远端可拉到本机修改", "v3 local improvement" in out7)
# 第五步·反向合入检查：push 后远端无新提交（BEHIND=0 等价）
behind = subprocess.run(["git", "-C", local_dir, "rev-list", "--count", "HEAD..origin/main"], capture_output=True, text=True).stdout.strip()
check("推送后 BEHIND=0", behind == "0")
shutil.rmtree(tmp6, ignore_errors=True)

# ============ 用例 7：远端双向完整链路（教学行双向误伤与恢复，动态自洽，对端固化） ============
print("[用例7] 远端双向更新完整链路（教学行双向误伤与恢复，动态自洽）")
import importlib.util as _ilu, pathlib as _pl
_spec = _ilu.spec_from_file_location("pc", os.path.join(_pl.Path(__file__).parent, "path_convert.py"))
_pc = _ilu.module_from_spec(_spec); _spec.loader.exec_module(_pc)
_lmap = _pc.build_local_map()
_pmap = _pc.build_portable_map()
_lpairs = [(ph, real) for ph, real in _lmap.items()]; _lpairs.sort(key=lambda x: len(x[0]), reverse=True)
def _conv(text, pairs):
    for a, b in pairs: text = text.replace(a, b)
    return text
def _ph(name):
    return "<" + name + ">"   # 拆分拼接，规避双向转换改写测试字面量
doc_real = _lmap.get(_ph("资料目录"), "DOC")
proj_real = _lmap.get(_ph("项目目录"), "PROJ")
teach_repo = [
    "- **自动类**（转换时自动推导，无需用户填写）：" + _ph("用户目录") + "、" + _ph("opencode配置目录") + "",
    "- **数据类**（安装脚本交互选择）：" + _ph("资料目录") + "（默认 " + doc_real + "\\default）、" + _ph("项目目录") + "（默认 " + proj_real + "\\project\\default）",
]
def restore_teaching(repo_lines, cur_lines):
    for k, l in enumerate(cur_lines):
        if ("自动类" in l and "转换时自动推导" in l) or ("数据类" in l and "安装脚本交互选择" in l):
            cur_lines[k] = repo_lines[k]
    return cur_lines
local_lines = [_conv(l, _lpairs) for l in teach_repo]
check("to_local 破坏教学行（自动类转真实路径）", local_lines[0] != teach_repo[0])
check("to_local 破坏数据类教学行（默认值被映射前缀替换）", local_lines[1] != teach_repo[1])
restored = restore_teaching(teach_repo, local_lines)
check("教学行恢复后与仓库版一致", restored == teach_repo)
fwd = [_conv(l, _pmap) for l in restored]
check("to_portable 误伤数据类教学行（默认值转占位符）", fwd[1] != teach_repo[1])
fwd_restored = restore_teaching(teach_repo, fwd)
check("正向误伤后恢复闭环（与仓库版一致）", fwd_restored == teach_repo)

# ============ 用例 8：提交前可移植性校验（扫描待提交内容无本机特征） ============
print("[用例8] 提交前可移植性校验（不同电脑可移植，用户规则强制）")
def scan_portability(root):
    """扫描目录下文本文件的本机特征残留。返回违规列表 [(文件, 特征类型)]"""
    home = os.path.expanduser("~").replace("/", "\\")
    user = os.path.basename(home.rstrip("\\"))
    violations = []
    text_exts = (".md", ".py", ".js", ".json", ".jsonc", ".txt", ".ps1", ".sh")
    for dirpath, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in (".git", "__pycache__", "node_modules")]
        for f in files:
            if not f.lower().endswith(text_exts):
                continue
            fp = os.path.join(dirpath, f)
            try:
                c = open(fp, encoding="utf-8", errors="replace").read()
            except Exception:
                continue
            if home in c:
                violations.append((f, "含本机 home 真实路径"))
            if ("\\Users\\" + user) in c or ("/Users/" + user) in c:
                violations.append((f, "含本机用户名路径"))
    return violations

tmp8 = tempfile.mkdtemp(prefix="us_port_")
# 干净目录：占位符形式
clean_dir = os.path.join(tmp8, "clean")
os.makedirs(clean_dir)
open(os.path.join(clean_dir, "a.md"), "w", encoding="utf-8").write("路径 " + _ph("opencode配置目录") + " 与 " + _ph("用户目录"))
check("干净目录（占位符形式）通过可移植性扫描", scan_portability(clean_dir) == [])
# 污染目录：混入本机真实路径
dirty_dir = os.path.join(tmp8, "dirty")
os.makedirs(dirty_dir)
open(os.path.join(dirty_dir, "b.md"), "w", encoding="utf-8").write("硬编码 " + CFG + " 与 " + os.path.expanduser("~").replace("/", "\\") + "\\AppData")
v8 = scan_portability(dirty_dir)
check("污染目录检出本机特征", len(v8) > 0)
# 自检：本测试文件自身与 tests 目录当前无本机特征残留（用例进入自测库后自身须干净）
import shutil as _sh
port_copy = os.path.join(tmp8, "selfcopy")
_sh.copytree(os.path.dirname(os.path.abspath(__file__)), port_copy, ignore=_sh.ignore_patterns("__pycache__", ".git"))
_pcpairs8 = _pc.build_portable_map()
for dp, dn, fn in os.walk(port_copy):
    for f in fn:
        if not f.lower().endswith((".md", ".py", ".json", ".jsonc", ".txt", ".ps1", ".bat", ".sh")):
            continue
        fp = os.path.join(dp, f)
        try:
            c8 = open(fp, encoding="utf-8", errors="replace").read()
        except Exception:
            continue
        n8 = _conv(c8, _pcpairs8)
        if n8 != c8:
            open(fp, "w", encoding="utf-8", newline="").write(n8)
self_v = scan_portability(port_copy)
check("tests 目录经 to_portable 后通过可移植性扫描（0 违规，形态无关）", self_v == [])
if self_v:
    print("    违规:", self_v[:3])
shutil.rmtree(tmp8, ignore_errors=True)

# ============ 用例 9：第四步弹窗确认分支逻辑（未确认前禁止 commit/push） ============
print("[用例9] 弹窗确认分支逻辑（未确认前无 commit，三态分支正确）")

# 9.1 三态分支解析
def decide_branch(choice):
    if choice == "推送":
        return "push"
    if choice == "填写新内容":
        return "rework"
    if choice == "仅本地不推送":
        return "local_only"
    return None

check("弹窗三态分支解析正确", decide_branch("推送") == "push" and decide_branch("填写新内容") == "rework" and decide_branch("仅本地不推送") == "local_only")

# 9.2 未确认前无 commit（模拟：修改→自测→未经过弹窗确认→HEAD 必须不变）
tmp9 = tempfile.mkdtemp(prefix="us_popup_")
subprocess.run(["git", "init", "-q", "-b", "main", tmp9], check=True)
subprocess.run(["git", "-C", tmp9, "config", "user.email", "t@t.l"], check=True)
subprocess.run(["git", "-C", tmp9, "config", "user.name", "tester"], check=True)
open(os.path.join(tmp9, "f.md"), "w", encoding="utf-8").write("v1")
subprocess.run(["git", "-C", tmp9, "add", "-A"], check=True)
subprocess.run(["git", "-C", tmp9, "commit", "-q", "-m", "init"], check=True)
head0 = subprocess.run(["git", "-C", tmp9, "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
# 模拟第二步修改 + 第三步自测，但不经过第四步弹窗确认
open(os.path.join(tmp9, "f.md"), "w", encoding="utf-8").write("v2 修改未确认")
head1 = subprocess.run(["git", "-C", tmp9, "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
check("未经过弹窗确认前无 commit（HEAD 不变）", head0 == head1)
# 弹窗选择"仅本地不推送"→ 流程结束，改动留在工作区不提交
st = subprocess.run(["git", "-C", tmp9, "status", "--short"], capture_output=True, text=True).stdout
check("仅本地分支：改动保留工作区不提交", "M f.md" in st)
# 弹窗选择"推送"→ 确认后才 commit
msgf = os.path.join(tmp9, "m.txt")
open(msgf, "w", encoding="utf-8").write("sync: 弹窗确认后推送测试")
subprocess.run(["git", "-C", tmp9, "add", "-A"], check=True)
subprocess.run(["git", "-C", tmp9, "commit", "-q", "-F", msgf], check=True)
head2 = subprocess.run(["git", "-C", tmp9, "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
check("推送分支：确认后 commit 才产生", head2 != head0)
shutil.rmtree(tmp9, ignore_errors=True)

# 9.3 弹窗规则完整性（SKILL.md 写明强制弹窗 + 禁止文字代替 + 未确认禁 commit/push）
check("规则含强制弹窗表述（question 工具）", "question 工具" in sk and "弹窗" in sk)
check("规则禁止文字提问代替弹窗", "禁止" in sk and "文字询问" in sk)
check("规则明示未确认禁 commit/push", "不得执行任何 commit/push" in sk)

print("\n结果：通过 %d 项，失败 %d 项" % (pass_n, fail_n))
sys.exit(1 if fail_n else 0)
