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
    # Windows 路径转 WSL 挂载路径（C:/xxx -> /mnt/c/xxx）
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
    m.update(load_path_map())  # 填写类（<项目目录>等）
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
    # 填写类反向
    for ph, real in pm.items():
        m.append((real, ph))
    # 排序：长路径优先
    m.sort(key=lambda x: len(x[0]), reverse=True)
    return m

def convert(text, pairs):
    for real, ph in pairs:
        text = text.replace(real, ph)
        # URL 风格（正斜杠，如 file:///C:/Users/x）也替换
        real_slash = real.replace("\\", "/")
        if real_slash != real:
            text = text.replace(real_slash, ph)
    return text

def walk_convert(root, pairs, suffix):
    count = 0
    for dirpath, dirnames, filenames in os.walk(root):
        if ".git" in dirpath.split(os.sep):
            continue
        for fn in filenames:
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
    else:
        print("用法: python path_convert.py to_portable|to_local <目录>")
