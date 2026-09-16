# -*- coding: utf-8 -*-
# 路径转换工具自测：to_portable/to_local 往返、STATE_FILES 保护、占位符残留检测
import os, shutil, sys, tempfile
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
TESTS_DIR = os.path.dirname(os.path.abspath(__file__))

import importlib.util
spec = importlib.util.spec_from_file_location("pc", os.path.join(TESTS_DIR, "path_convert.py"))
pc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pc)

# 动态推导本机路径（可移植：新机器自动适配）
HOME = os.environ.get("USERPROFILE", r"C:\\Users\\default").replace("/", "\\")
CFG_DIR = HOME + "\\.config\\opencode"
TMP_DIR = HOME + "\\AppData\\Local\\Temp"

pass_n, fail_n = 0, 0
def check(name, cond):
    global pass_n, fail_n
    if cond: pass_n += 1; print("  ✓ " + name)
    else: fail_n += 1; print("  ✗ " + name)

tmp = tempfile.mkdtemp(prefix="pc_test_")

# === 用例 1：真实路径 → 占位符（to_portable） ===
print("[用例1] to_portable 真实路径转占位符")
f1 = os.path.join(tmp, "a.md")
open(f1, "w", encoding="utf-8").write("路径 " + CFG_DIR + " 与 " + TMP_DIR)
pairs = pc.build_portable_map()
converted = pc.convert(open(f1, encoding="utf-8").read(), pairs)
check("配置目录转占位符", ("<" + "opencode配置目录" + ">") in converted)
check("临时目录转占位符", ("<" + "用户临时目录" + ">") in converted)
check("真实路径全部替换", HOME not in converted)

# === 用例 2：占位符 → 真实路径（to_local 往返） ===
print("[用例2] to_local 占位符转真实路径")
f2 = os.path.join(tmp, "b.md")
open(f2, "w", encoding="utf-8").write("配置 " + CFG_DIR + " 与临时 " + TMP_DIR)
local_map = pc.build_local_map()
pairs_l = [(ph, real) for ph, real in local_map.items()]
pairs_l.sort(key=lambda x: len(x[0]), reverse=True)
back = pc.convert(open(f2, encoding="utf-8").read(), pairs_l)
check("占位符转回真实路径", ("<" + "opencode配置目录" + ">") not in back and CFG_DIR in back)

# === 用例 3：往返一致性 ===
print("[用例3] 往返一致（真实→占位符→真实）")
orig = HOME + "\\AppData\\Local\\Temp\\opencode\\x.ps1"
p1 = pc.convert(orig, pairs)
p2 = pc.convert(p1, pairs_l)
check("往返后与原路径一致", p2 == orig)

# === 用例 4：STATE_FILES 保护（path_map/sync_target 不被转换） ===
print("[用例4] STATE_FILES 保护")
walk_dir = os.path.join(tmp, "walktest")
os.makedirs(walk_dir)
open(os.path.join(walk_dir, "path_map.txt"), "w", encoding="utf-8").write(r"E:\openCodeDefault=" + HOME + "\\x")
open(os.path.join(walk_dir, "sync_target.txt"), "w", encoding="utf-8").write("\\\\wsl.localhost\\x")
open(os.path.join(walk_dir, "normal.md"), "w", encoding="utf-8").write(HOME + "\\y")
pc.walk_convert(walk_dir, pairs, "test")
check("path_map.txt 未被动", (r"E:\openCodeDefault=" + HOME + "\\x") in open(os.path.join(walk_dir, "path_map.txt"), encoding="utf-8").read())
check("sync_target.txt 未被动", "\\\\wsl.localhost" in open(os.path.join(walk_dir, "sync_target.txt"), encoding="utf-8").read())
check("普通文件被转换", ("<" + "用户目录" + ">") in open(os.path.join(walk_dir, "normal.md"), encoding="utf-8").read())

# === 用例 4b：.js/.cjs/.mjs 白名单加入（2026-09-16：plugins/skill-banner.js 等需双向转换） ===
print("[用例4b] .js/.cjs/.mjs 白名单（walk_convert 双向转换）")
js_dir = os.path.join(tmp, "js_test")
os.makedirs(js_dir)
open(os.path.join(js_dir, "skill-banner.js"), "w", encoding="utf-8").write("引用 " + CFG_DIR + " 与 " + HOME + "\\x")
open(os.path.join(js_dir, "mod.cjs"), "w", encoding="utf-8").write("引用 " + CFG_DIR)
open(os.path.join(js_dir, "mod.mjs"), "w", encoding="utf-8").write("引用 " + TMP_DIR)
pc.walk_convert(js_dir, pairs, "testjs")
js_txt = open(os.path.join(js_dir, "skill-banner.js"), encoding="utf-8").read()
cjs_txt = open(os.path.join(js_dir, "mod.cjs"), encoding="utf-8").read()
mjs_txt = open(os.path.join(js_dir, "mod.mjs"), encoding="utf-8").read()
check(".js to_portable 转占位符", ("<" + "opencode配置目录" + ">") in js_txt and HOME not in js_txt)
check(".cjs to_portable 转占位符", ("<" + "opencode配置目录" + ">") in cjs_txt)
check(".mjs to_portable 转占位符", ("<" + "用户临时目录" + ">") in mjs_txt)
pairs_l_js = [(ph, real) for ph, real in pc.build_local_map().items()]
pairs_l_js.sort(key=lambda x: len(x[0]), reverse=True)
js_back = pc.convert(js_txt, pairs_l_js)
cjs_back = pc.convert(cjs_txt, pairs_l_js)
mjs_back = pc.convert(mjs_txt, pairs_l_js)
check(".js to_local 还原真实路径", ("<" + "opencode配置目录" + ">") not in js_back and CFG_DIR in js_back)
check(".cjs to_local 还原真实路径", ("<" + "opencode配置目录" + ">") not in cjs_back and CFG_DIR in cjs_back)
check(".mjs to_local 还原真实路径", ("<" + "用户临时目录" + ">") not in mjs_back and TMP_DIR in mjs_back)

# === 用例 5：未知占位符扫描 ===
print("[用例5] 未知占位符检测（白名单机制：只报框架占位符全集内残留，文档示例尖括号词不误报）")
scan_dir = os.path.join(tmp, "scan")
os.makedirs(scan_dir)
open(os.path.join(scan_dir, "s.md"), "w", encoding="utf-8").write("残留 <项目目录> 与 <文件> 与 </html> 与 <int> 与 " + HOME)
unk = pc.scan_unknown_placeholders(scan_dir)
check("检出白名单内 <项目目录>", "<项目目录>" in unk)
check("不误报文档示例词 <文件>", "<文件>" not in unk)
check("不误报 HTML 标签 </html>", "</html>" not in unk)
check("不误报泛型 <int>", "<int>" not in unk)

# 用例 5b：工具类占位符全集检出（空值未配置的 <工具目录> 等必须报残留，防"无残留"与 setup 报警矛盾）
scan_dir2 = os.path.join(tmp, "scan2")
os.makedirs(scan_dir2)
open(os.path.join(scan_dir2, "s2.md"), "w", encoding="utf-8").write("残留 <工具目录>msys64 与 <LibreOffice目录> 与 <Node目录>")
unk2 = pc.scan_unknown_placeholders(scan_dir2)
check("检出工具类 <工具目录>（空值未配置也算残留）", "<工具目录>" in unk2)
check("检出工具类 <LibreOffice目录>", "<LibreOffice目录>" in unk2)
check("检出工具类 <Node目录>", "<Node目录>" in unk2)

# === 用例 6：占位符形式语法合法性（tests 全目录 .py 必须可 ast.parse） ===
print("[用例6] 占位符形式语法合法性（防止 \\U 转义类错误混入仓库）")
import ast
ok = True
for root, dirs, files in os.walk(TESTS_DIR):
    if ".git" in root: continue
    for f in files:
        if not f.endswith(".py"): continue
        fp = os.path.join(root, f)
        try:
            ast.parse(open(fp, encoding="utf-8").read())
        except SyntaxError as e:
            ok = False
            print("  语法错误: " + fp + " line " + str(e.lineno) + ": " + str(e.msg))
check("tests 目录全部 .py 可解析（占位符形式也必须合法）", ok)

# === 用例 7：副本与被测源一致性（防 tests/path_convert.py 漂移） ===
print("[用例7] 测试副本与被测源一致性")
src = os.path.join(HOME.replace("\\", "/").split("/")[0] + os.sep, "Users", os.path.basename(HOME.rstrip("\\")), "AppData", "Local", "Temp", "opencode", "path_convert.py")
if os.path.isfile(src):
    cpy_txt = open(os.path.join(TESTS_DIR, "path_convert.py"), encoding="utf-8").read()
    src_txt = open(src, encoding="utf-8").read()
    check("副本含 STATE_FILES", "STATE_FILES" in cpy_txt)
    check("副本含自身跳过（path_convert.py in STATE_FILES）", "path_convert.py" in cpy_txt.split("STATE_FILES =")[1].split("}")[0])
    check("副本与源 STATE_FILES 定义一致", cpy_txt.split("STATE_FILES =")[1].split("}")[0] == src_txt.split("STATE_FILES =")[1].split("}")[0])
else:
    check("源不存在（本机未部署 Temp\\opencode）→ 跳过一致性", True)

# === 用例 8：path_map 空值映射过滤（防 replace("", ph) 全局插入爆炸，2026-08-27 实测） ===
print("[用例8] 空值映射过滤（<工具目录>= 空值不产生空 key 映射）")
pmap2 = pc.build_portable_map()
check("portable map 无空 key", all(real.strip() for real, _ in pmap2))
lmap2 = pc.build_local_map()
check("local map 无空值（to_local 不误删占位符）", all(real.strip() for real in lmap2.values()))
txt8 = "- **自动类**（转换时自动推导）：" + ("<" + "用户目录" + ">") + "、" + ("<" + "opencode配置目录" + ">") + ""
conv8 = pc.convert(txt8, pmap2)
check("空值场景 convert 无全局插入（文本未爆炸膨胀）", len(conv8) <= len(txt8) * 3)
check("convert 防御：显式空 key 对直接跳过", pc.convert("hello world", [("", "<空key>")]) == "hello world")

# === 用例 9：安装约定位置转换（2026-09-17 修订：改为转无盘符占用符，符合仓库无盘符双向可移植铁律） ===
print("[用例9] 安装约定位置 to_portable 转无盘符占位符（仓库无盘符铁律）")
_pf9 = os.environ.get("ProgramFiles", r"C:\Program Files")
_pf86_9 = os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)")
_sr9 = os.environ.get("SystemRoot", r"C:\Windows")
_sd9 = os.environ.get("SystemDrive", "C:")
_gt9 = (r"装 " + _pf9 + r"\Git 与 " + _pf86_9 + r"\X 与 " + _sr9 + r"\sys 与 " + _sd9 + r"\Temp\LO "
        r"与 C:\msys64\ucrt64\bin 与 C:\w64devkit\bin 与 C:\Users\<用户名>\.config 与 " + _sd9 + r"/Temp/LO2 与 " + HOME + r"\real 与 " + CFG_DIR)
conv9 = pc.convert(_gt9, pairs)
check("ProgramFiles 转 <程序文件目录>", ("<程序文件目录>\\Git" in conv9) and (r"C:\Program Files\Git" not in conv9) and (r"C:\PROGRAM FILES\Git" not in conv9))
check("ProgramFiles(x86) 转 <程序文件目录(x86)>", ("<程序文件目录(x86)>\\X" in conv9) and (_pf86_9 + r"\X" not in conv9))
check("SystemRoot 转 <系统目录>", ("<系统目录>\\sys" in conv9) and (_sr9 + r"\sys" not in conv9))
check("C:\\msys64 转 <msys64目录>", ("<msys64目录>\\ucrt64\\bin" in conv9) and ("C:\\msys64" not in conv9))
check("C:\\w64devkit 转 <w64devkit目录>", ("<w64devkit目录>\\bin" in conv9) and ("C:\\w64devkit" not in conv9))
check("C:\\Users\\<用户名> 转 <用户目录>", ("<用户目录>\\.config" in conv9) and ("C:\\Users\\<用户名>" not in conv9))
check("Temp 正斜杠转 <系统临时目录>", ("<系统临时目录>/LO2" in conv9) and (_sd9 + ":/Temp/LO2" not in conv9))
check("本机真实用户目录仍正常转占位符(<用户目录>)", HOME not in conv9 and ("<" + "用户目录" + ">") in conv9)
check("配置目录仍正常转占位符", CFG_DIR not in conv9 and ("<" + "opencode配置目录" + ">") in conv9)
# 约定占位符 to_local 可还原真实路径（双向可移植）
pairs_l9 = [(ph, r) for ph, r in pc.build_local_map().items()]
pairs_l9.sort(key=lambda x: len(x[0]), reverse=True)
_pf9 = os.environ.get("ProgramFiles", r"C:\Program Files")
_sr9 = os.environ.get("SystemRoot", r"C:\Windows")
_sd9 = os.environ.get("SystemDrive", "C:")
back9 = pc.convert("<程序文件目录>\\Git 与 <系统目录>\\sys 与 <msys64目录>\\ucrt64\\bin 与 <系统临时目录>\\LO", pairs_l9)
check("约定占位符 to_local 还原真实路径（双向可移植）",
      _pf9 + r"\Git" in back9 and _sr9 + r"\sys" in back9 and r"C:\msys64\ucrt64\bin" in back9 and _sd9 + r"\Temp\LO" in back9)

# 用例 9b：guard 只作用于盘符根映射——约定位置下的长映射（如 <LibreOffice目录>）仍正常转换
pairs_custom = [("C:\\Program Files\\LibreOffice", "<LibreOffice目录>"), ("C:\\", "<工具目录>")]
txt9b = r"装 C:\Program Files\LibreOffice\program\soffice.com 与 C:\Program Files\Other\x 与 C:\msys64\y 与 C:\Users\<用户名>\z"
conv9b = pc.convert(txt9b, pairs_custom)
check("guard 下长映射正常转换（<LibreOffice目录> 生效）", "<LibreOffice目录>\\program\\soffice.com" in conv9b)
check("guard 前缀保留字面（C:\\Program Files\\Other 不被根映射吞）", r"C:\Program Files\Other\x" in conv9b)
check("guard 前缀保留字面（C:\\msys64 不被根映射吞）", r"C:\msys64\y" in conv9b)
check("C:\\Users\\<用户名> 字面保留", r"C:\Users\<用户名>\z" in conv9b)

shutil.rmtree(tmp, ignore_errors=True)
print("\n结果：通过 %d 项，失败 %d 项" % (pass_n, fail_n))
sys.exit(1 if fail_n else 0)
