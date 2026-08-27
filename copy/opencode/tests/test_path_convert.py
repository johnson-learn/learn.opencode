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

shutil.rmtree(tmp, ignore_errors=True)
print("\n结果：通过 %d 项，失败 %d 项" % (pass_n, fail_n))
sys.exit(1 if fail_n else 0)
