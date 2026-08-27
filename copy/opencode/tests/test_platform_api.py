# 平台 API 保障测试：experimental.chat.system.transform 注入机制的可用性硬检查
# 背景（2026-08-27）：注册事件注入依赖 opencode 实验性 API（experimental.chat.system.transform），
# 该 API 是实验性接口，未来 opencode 版本可能变更/移除——本测试保证每次运行都检查该依赖是否仍成立。
# 检查方式：读取本机 opencode 二进制，确认其内部仍实现该 hook（二进制字符串证据，1.18.18 实测）。
import sys
import subprocess
from pathlib import Path
import shutil

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

pass_count = 0
fail_count = 0

def check(name, cond, extra=""):
    global pass_count, fail_count
    if cond:
        pass_count += 1
        print("  ✓ " + name + ("  " + extra if extra else ""))
    else:
        fail_count += 1
        print("  ✗ " + name + ("  " + extra if extra else ""))

def find_opencode_exe():
    # 优先级：npm 全局布局枚举 → npm root -g → PATH 中的 .exe → 解析 .cmd 包装脚本
    import os
    import re
    candidates = []
    appdata = os.environ.get("APPDATA", "")
    if appdata:
        candidates.append(str(Path(appdata) / "npm" / "node_modules" / "opencode-ai" / "bin" / "opencode.exe"))
    try:
        out = subprocess.run(["npm", "root", "-g"], capture_output=True, text=True, timeout=30)
        if out.returncode == 0 and out.stdout.strip():
            candidates.append(str(Path(out.stdout.strip()) / "opencode-ai" / "bin" / "opencode.exe"))
    except Exception:
        pass
    which = shutil.which("opencode")
    if which and which.lower().endswith(".exe"):
        candidates.append(which)
    for c in candidates:
        if Path(c).is_file():
            return c
    # 兜底：opencode.cmd 包装脚本内引用真实 exe（%~dp0 相对布局）
    cmd = shutil.which("opencode.cmd")
    if not cmd and appdata:
        cmd = str(Path(appdata) / "npm" / "opencode.cmd")
    if cmd and Path(cmd).is_file():
        try:
            txt = Path(cmd).read_text(encoding="utf-8", errors="ignore")
            m = re.search(r'"%~dp0\\([^"]+)"', txt)
            if m:
                p = (Path(cmd).parent / m.group(1).replace("/", "\\"))
                if p.is_file():
                    return str(p)
        except Exception:
            pass
    return None

HOOK = "experimental.chat.system.transform"

print("[test_platform_api] opencode 实验性 API 依赖检查")

# 1. opencode 可执行定位
exe = find_opencode_exe()
check("opencode.exe 已定位", bool(exe), exe or "未找到")
if not exe:
    print("结果：通过 %d 项，失败 %d 项" % (pass_count, fail_count))
    sys.exit(1)

# 2. 版本获取（软检查：记录版本；版本线变化时提示人工复核，不作为硬失败）
version = ""
try:
    out = subprocess.run([exe, "--version"], capture_output=True, text=True, timeout=60)
    version = out.stdout.strip()
except Exception as e:
    version = "获取失败：" + str(e)[:100]
check("opencode --version 可执行", bool(version) and "获取失败" not in version, version)
if not version.startswith("1.18"):
    print("  ⚠ 版本非 1.18 系列（当前：" + version + "），请人工复核 experimental hook 是否仍受支持")

# 3. 二进制仍实现该 hook（硬保证：版本升级/移除该 API 时此检查失败）
try:
    data = Path(exe).read_bytes()
    ascii_text = data.decode("ascii", errors="ignore")
    has_hook = HOOK in ascii_text
except Exception as e:
    has_hook = False
    print("  读取二进制失败：" + str(e)[:120])
check("二进制含 " + HOOK + "（hook 实现存在）", has_hook)

# 4. jsonc 配置文件名仍被支持（回退预案依赖：instructions 字段若重启需 opencode.jsonc）
check("二进制含 opencode.jsonc（配置文件通道存在）", "opencode.jsonc" in ascii_text if has_hook else False)

# 5. 插件注册了该 hook
config_dir = Path.home() / ".config" / "opencode"
plugin = config_dir / "plugins" / "skill-banner.js"
plugin_ok = plugin.is_file()
check("skill-banner.js 存在", plugin_ok, str(plugin))
plugin_registered = False
if plugin_ok:
    try:
        plugin_registered = HOOK in plugin.read_text(encoding="utf-8")
    except Exception:
        plugin_registered = False
check("插件注册了 " + HOOK, plugin_registered)

# 6. 4 个注入文件存在且非空
inject_files = ["instructions.md", "regedit.md", "docs-sync.md", "tools-manifest.md"]
all_files_ok = True
for f in inject_files:
    p = config_dir / f
    ok = p.is_file() and p.stat().st_size > 0
    check("注入文件存在且非空: " + f, ok, str(p))
    if not ok:
        all_files_ok = False
check("4 个注入文件全部就绪", all_files_ok)

print("结果：通过 %d 项，失败 %d 项" % (pass_count, fail_count))
sys.exit(1 if fail_count > 0 else 0)
