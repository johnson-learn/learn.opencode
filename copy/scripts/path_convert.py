# -*- coding: utf-8 -*-
# 路径可移植转换工具：本机真实路径 <-> 占位符
# 用法:
#   python path_convert.py to_portable <目录>   目录内文件: 真实路径 -> 占位符（推送仓库前）
#   python path_convert.py to_local <目录>      目录内文件: 占位符 -> 真实路径（拉取仓库后合入本机前）
# 映射: 自动类占位符直接换算; 填写类占位符从 <用户目录>\.config\opencode\skills\update_skill\path_map.txt 读取
import os, re, sys

# 用户目录：优先 --home 参数（支持正反斜杠，统一为反斜杠用于匹配 Windows 路径），其次 USERPROFILE，最后 expanduser
def get_home():
    args = [a for a in sys.argv if a.startswith("--home=")]
    if args:
        h = args[0].split("=", 1)[1].strip('"')
        h = h.replace("/", "\\")
        if not h.endswith("\\"):
            h += "\\"
        return h
    h = os.environ.get("USERPROFILE") or os.path.expanduser("~")
    h = h.replace("/", "\\")
    if not h.endswith("\\"):
        h += "\\"
    return h

HOME = get_home()

def win_to_wsl(p):
    # Windows 路径转 WSL 挂载路径（<工具目录>xxx -> /mnt/c/xxx）
    p2 = p.replace("\\", "/")
    if len(p2) >= 2 and p2[1] == ":":
        p2 = "/mnt/" + p2[0].lower() + p2[2:]
    return p2

def load_path_map():
    m = {}
    # path_map 位置：HOME（Windows）下的 .config\opencode\...；WSL 内转 /mnt/c
    win_p = HOME + ".config\\opencode\\skills\\update_skill\\path_map.txt"
    candidates = [win_p, win_to_wsl(win_p)]
    for p in candidates:
        if os.path.isfile(p):
            with open(p, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#") or "=" not in line:
                        continue
                    k, v = line.split("=", 1)
                    m[k.strip()] = v.strip()
            break
    return m

# 占位符 -> 本机真实路径（to_local 用）；自动类用 HOME 推导（Windows 反斜杠格式）
def build_local_map():
    h = HOME
    m = {
        "<用户目录>": h.rstrip("\\"),
        "<opencode配置目录>": h + ".config\\opencode",
        "<opencode数据目录>": h + ".local\\share\\opencode",
        "<用户临时目录>": h + "AppData\\Local\\Temp",
        "<用户AppData目录>": h + "AppData\\Roaming",
        "<用户桌面目录>": h + "Desktop",
        "<WSL用户映射>": "/mnt/c/Users/" + os.path.basename(h.rstrip("\\")),
        "<Python脚本目录>": h + "AppData\\Roaming\\Python\\Python312\\Scripts",
    }
    # 填写类（<项目目录>等）；过滤空值映射（如 <工具目录>= 未填写），防止 to_local 误删占位符
    m.update({ph: real for ph, real in load_path_map().items() if ph.strip() and real.strip()})
    return m

# 本机真实路径 -> 占位符（to_portable 用）；必须含所有本机已知路径
def build_portable_map():
    pm = load_path_map()
    h = HOME  # 反斜杠结尾的 Windows 用户目录
    m = [
        (h + ".config\\opencode", "<opencode配置目录>"),
        (h + ".local\\share\\opencode", "<opencode数据目录>"),
        (h + "AppData\\Local\\Temp", "<用户临时目录>"),
        (h + "AppData\\Roaming", "<用户AppData目录>"),
        (h + "Desktop", "<用户桌面目录>"),
        ("/mnt/c/Users/" + os.path.basename(h.rstrip("\\")), "<WSL用户映射>"),
        (h + "AppData\\Roaming\\Python\\Python312\\Scripts", "<Python脚本目录>"),
        (h.rstrip("\\"), "<用户目录>"),
    ]
    # 填写类反向；过滤空值映射（path_map 中 <工具目录>= 等未填写项），
    # 否则生成 ("", ph) 会让 convert 的 replace("", ph) 在文本中每字符间插入占位符（2026-08-27 实测爆炸）
    for ph, real in pm.items():
        if ph.strip() and real.strip():
            m.append((real, ph))
    # 排序：长路径优先
    m.sort(key=lambda x: len(x[0]), reverse=True)
    return m

def convert(text, pairs):
    for real, ph in pairs:
        # 防御：空 key 映射（path_map 空值填写）直接跳过，防 replace("", ph) 全局插入
        if not real or not ph:
            continue
        text = text.replace(real, ph)
        # URL 风格（正斜杠，如 file:///<工具目录>Users/x）也替换
        real_slash = real.replace("\\", "/")
        if real_slash != real:
            text = text.replace(real_slash, ph)
    return text

# 状态文件保护：这些本机特定文件不参与任何转换（防止 path_map 自我指涉；path_convert.py 自身含占位符键，转换会自毁）
STATE_FILES = {"path_map.txt", "sync_target.txt", "path_convert.py"}

def walk_convert(root, pairs, suffix):
    count = 0
    for dirpath, dirnames, filenames in os.walk(root):
        rel = os.path.relpath(dirpath, root)
        parts = rel.split(os.sep)
        if ".git" in parts:
            continue
        # 测试与历史脚本目录不参与路径转换：测试文件用动态路径推导 + 模拟路径字符串字面量，
        # 转换会污染测试数据（2026-08-27 实测：r"C:\tmp\repo" 被误转 <工具目录>tmp\repo）
        if "tests" in parts or "archive" in parts:
            continue
        for fn in filenames:
            if fn.lower() in STATE_FILES:
                continue
            if not fn.lower().endswith((".md", ".jsonc", ".json", ".txt", ".ps1", ".py", ".bat", ".sh")):
                continue
            p = os.path.join(dirpath, fn)
            try:
                with open(p, encoding="utf-8") as f:
                    content = f.read()
            except (UnicodeDecodeError, OSError):
                continue
            new = convert(content, pairs)
            if new != content:
                with open(p, "w", encoding="utf-8", newline="") as f:
                    f.write(new)
                count += 1
                print("[ok] " + os.path.relpath(p, root))
    print("=== %s 完成: %d 个文件转换" % (suffix, count))

# 框架填写类占位符全集（与 setup-windows.ps1 第 7 节 $leftover 检测口径一致：5 数据类 + 5 工具类；
# 新增填写类需两处同步）。注意：全集含工具类——path_map 中工具类空值（如 <工具目录>= 未探测到）时，
# 对应占位符未转换属"未配置残留"，必须检出提示用户补 path_map，不得因空值过滤而漏报（2026-08-27 实测矛盾告警教训）
FILL_KEYS = {"<资料目录>", "<3GPP文档库目录>", "<项目目录>", "<源码目录>", "<离线安装包目录>",
             "<工具目录>", "<WSL安装目录>", "<LibreOffice目录>", "<Chrome目录>", "<Node目录>"}

def scan_unknown_placeholders(root):
    """扫描目录中残留的框架占位符——只报告白名单全集（自动类 + 填写类 FILL_KEYS）内的残留。
    文档示例尖括号词（<文件>、<目录>、HTML/XML 标签、C++ 泛型 <int>、正则模式等）一律不报
    （2026-08-27 实测：宽正则 r"<[^<>\\s]{2,40}>" 产生 900+ 行误报）。"""
    known = set(build_local_map().keys()) | FILL_KEYS
    unknown = set()
    pat = re.compile(r"<[^<>\s]{2,40}>")
    for dirpath, dirnames, filenames in os.walk(root):
        rel = os.path.relpath(dirpath, root)
        parts = rel.split(os.sep)
        if ".git" in parts:
            continue
        if "tests" in parts or "archive" in parts:
            continue
        for fn in filenames:
            if fn.lower() in STATE_FILES:
                continue
            if not fn.lower().endswith((".md", ".jsonc", ".json", ".txt", ".ps1", ".py", ".bat", ".sh")):
                continue
            p = os.path.join(dirpath, fn)
            try:
                with open(p, encoding="utf-8") as f:
                    c = f.read()
            except (UnicodeDecodeError, OSError):
                continue
            for m in pat.finditer(c):
                t = m.group(0)
                if t in known:
                    unknown.add(t)
    return unknown

if __name__ == "__main__":
    argv = [a for a in sys.argv[1:] if not a.startswith("--home=")]
    mode = argv[0] if argv else ""
    root = argv[1] if len(argv) > 1 else "."
    if mode == "to_portable":
        walk_convert(root, build_portable_map(), "to_portable")
    elif mode == "to_local":
        pairs = [(ph, real) for ph, real in build_local_map().items()]
        pairs.sort(key=lambda x: len(x[0]), reverse=True)
        walk_convert(root, pairs, "to_local")
        unk = scan_unknown_placeholders(root)
        if unk:
            print("=== 警告：残留未转换占位符（请补充 path_map.txt 后重跑 to_local）===")
            for u in sorted(unk):
                print("  " + u)
        else:
            print("=== 占位符全部转换完成，无残留 ===")
    else:
        print("用法: python path_convert.py to_portable|to_local <目录> [--home=用户目录]")
