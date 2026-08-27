# -*- coding: utf-8 -*-
# 仓库门面一致性测试：门面文件与框架现状对照（检查 WSL 仓库工作树；不存在则跳过）
import os, re, sys, subprocess
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

pass_n, fail_n = 0, 0
def check(name, cond, extra=""):
    global pass_n, fail_n
    if cond: pass_n += 1; print("  ✓ " + name)
    else: fail_n += 1; print("  ✗ " + name + ("  [" + extra + "]" if extra else ""))

REPO = r"\\wsl.localhost\Ubuntu\home\github\learn.opencode"
MIRROR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "repo_face")
mode = "仓库直读"
if not os.path.exists(REPO):
    mode = "镜像回退（WSL 不可达，校验本机镜像 repo_face\\）"
    REPO = MIRROR
    print("[" + mode + "]")
else:
    print("[模式] 仓库直读（WSL 工作树）")

def rd(p):
    fp = os.path.join(REPO, p.replace("/", "\\"))
    if not os.path.exists(fp):
        return ""
    return open(fp, encoding="utf-8", errors="replace").read()

# 1. 门面文件存在
face_files = ["README.md", "COPY_README.md", "INSTALL.md", "REQUIREMENTS.md"] if mode != "仓库直读" \
    else ["README.md", "copy\\README.md", "copy\\INSTALL.md", "copy\\REQUIREMENTS.md"]
for f in face_files:
    check("门面文件存在: " + f, os.path.exists(os.path.join(REPO, f)))

def rd_face(name):
    if mode == "仓库直读":
        return rd(name)
    return rd(name)

# 2. copy/README 技能清单与框架一致
r = rd("copy\\README.md") if mode == "仓库直读" else rd("COPY_README.md")
check("copy/README 含 6 个 skill 说明", all(s in r for s in ["3gpp_skill", "files_skill", "find_skill", "program_skill", "update_skill", "evolution_skill"]))
check("copy/README 含 default 容器结构", "default" in r and "evolution_skill" in r)
check("copy/README 含进化门禁说明", "门禁" in r or "evolution_gate" in r)
check("copy/README 含无权限机器说明", "无权限机器" in r or "不需要执行 update_skill" in r)

# 3. INSTALL 关键步骤
i = rd("copy\\INSTALL.md") if mode == "仓库直读" else rd("INSTALL.md")
check("INSTALL 含部署 tests/tools/plugins", all(x in i for x in ["tests", "tools", "plugins"]))
check("INSTALL 含 WEASYPRINT 环境变量", "WEASYPRINT_DLL_DIRECTORIES" in i)
check("INSTALL 含门禁验证", "evolution_gate" in i or "plugin-evolution.log" in i)

# 4. REQUIREMENTS 权威引用 + 新工具
q = rd("copy\\REQUIREMENTS.md") if mode == "仓库直读" else rd("REQUIREMENTS.md")
check("REQUIREMENTS 指向 tools-manifest 权威", "tools-manifest.md" in q)
check("REQUIREMENTS 含 7 高价值工具关键词", all(x in q for x in ["playwright", "weasyprint", "ocrmypdf", "docxtpl"]))

# 5. 根 README 入口
root = rd("README.md") if mode == "仓库直读" else rd("ROOT_README.md")
check("根 README 含 6 个 skill 表述", "6 个 skill" in root or "6 个全局" in root)

# 6. 隐私与可移植性防线（2026-08-27 隐私事故后固化）：真实仓库直读模式检查
if mode == "仓库直读":
    # 6a. STATE_FILES 不得出现在仓库工作树（cp 时可能带入，gitignore 只挡 add 不挡工作树残留）
    state_files = [
        "copy\\opencode\\skills\\update_skill\\path_map.txt",
        "copy\\opencode\\skills\\update_skill\\sync_target.txt",
    ]
    for sf in state_files:
        check("STATE_FILES 不在工作树: " + os.path.basename(sf), not os.path.exists(os.path.join(REPO, sf)))
    # 6b. 本机隐私特征不得出现在被跟踪文件内容（工作树全量扫描；特征全部动态推导，不硬编码具体隐私词）
    import glob as _g
    banned = ["C:\\Users\\" + os.path.basename(os.path.expanduser("~"))]
    hits = []
    for ext in ("*.md", "*.py", "*.js", "*.jsonc", "*.txt", "*.ps1"):
        for fp in _g.glob(os.path.join(REPO, "copy", "**", ext), recursive=True):
            if "\\modules\\" in fp or "\\__pycache__\\" in fp or "archive" in fp:
                continue
            try:
                c = open(fp, encoding="utf-8", errors="replace").read()
            except Exception:
                continue
            for b in banned:
                if b.lower() in c.lower():
                    hits.append(fp.replace(REPO, "") + " -> " + b)
    check("被跟踪文件无本机用户名路径", len(hits) == 0, "；".join(hits[:3]) if hits else "")

    # 6c. 多份 path_convert.py 副本一致性（2026-08-27 实测：copy/scripts 旧版漂移导致 setup 用旧逻辑刷屏 900+ 误报）
    import hashlib as _hl
    pc_paths = [
        "copy\\scripts\\path_convert.py",
        "copy\\opencode\\tools\\path_convert.py",
        "copy\\opencode\\tests\\path_convert.py",
    ]
    pc_hashes = set()
    for pp in pc_paths:
        fp = os.path.join(REPO, pp)
        if os.path.exists(fp):
            pc_hashes.add(_hl.md5(open(fp, "rb").read()).hexdigest())
    check("仓库内多份 path_convert.py 内容一致", len(pc_hashes) == 1, "不一致：" + str(len(pc_hashes)) + " 个版本")

print("\n结果：通过 %d 项，失败 %d 项" % (pass_n, fail_n))
sys.exit(1 if fail_n else 0)
