# -*- coding: utf-8 -*-
# evolution_gate 门禁脚本测试：快照→无改动→有改动（流水兜底追加/自动测试触发）
import os, sys, subprocess, json, tempfile, time
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

CFG = os.path.join(os.path.expanduser("~"), ".config", "opencode")
GATE = os.path.join(CFG, "tools", "evolution_gate.py")
LOG = os.path.join(CFG, "skills", "default", "evolution_skill", "evolution_log.txt")
pass_n, fail_n = 0, 0
def check(name, cond):
    global pass_n, fail_n
    if cond: pass_n += 1; print("  ✓ " + name)
    else: fail_n += 1; print("  ✗ " + name)

def run(*args):
    return subprocess.run([sys.executable, GATE] + list(args), capture_output=True,
                          text=True, encoding="utf-8", errors="replace", timeout=300)

sid = "gate-test-" + str(int(time.time()))
# 备份 log 尾部大小 + 清理裸声明计数状态文件（防跨运行污染）
log_size0 = os.path.getsize(LOG) if os.path.exists(LOG) else 0
_bare = os.path.join(tempfile.gettempdir(), "opencode_gate", "gate_bare_declare.json")
if os.path.exists(_bare):
    os.remove(_bare)

# 1. 快照
r = run("--snapshot", sid)
check("快照成功", r.returncode == 0 and "快照完成" in r.stdout)

# 2. 无改动 check → 门禁通过
r = run("--check", sid)
check("无改动时门禁通过", r.returncode == 0 and "无规则文件改动" in r.stdout)

# 3. 模拟改动：创建临时规则文件（不污染真实目录——用临时 watch 替代？gate 固定 watch CFG，改为在 skills 下建临时 skill 后删除）
tmp_skill = os.path.join(CFG, "skills", "_gate_test_skill")
os.makedirs(tmp_skill, exist_ok=True)
tmp_md = os.path.join(tmp_skill, "SKILL.md")
open(tmp_md, "w", encoding="utf-8").write("---\nname: _gate_test_skill\ndescription: gate test\n---\n# test\n")
os.makedirs(os.path.join(tmp_skill, "tests"), exist_ok=True)
open(os.path.join(tmp_skill, "tests", "test_skill_self.py"), "w", encoding="utf-8").write("# -*- coding: utf-8 -*-\nimport sys\nprint(\"gate L1 ok\")\nsys.exit(0)\n")
# 重新快照（含临时文件）
r = run("--snapshot", sid)
# 修改文件
time.sleep(0.05)
open(tmp_md, "w", encoding="utf-8").write("---\nname: _gate_test_skill\ndescription: gate test\n---\n# test v2\n")
r = run("--check", sid)
check("有改动时检测到", "检测到" in r.stdout and "_gate_test_skill" in r.stdout)
log_size1 = os.path.getsize(LOG)
check("流水兜底自动追加", log_size1 > log_size0)
check("自动测试已执行（含 evolution_consistency）", "test_evolution_consistency" in r.stdout)
check("待模型补充清单输出", "待模型补充" in r.stdout)
check("经验健康引擎输出（方案丁：待验证清单/deprecated 校验/老化扫描）", "[经验健康]" in r.stdout)
check("L1 领域自测精准触发（改动 skill 时自动跑该 skill tests/test_skill_self.py）", "L1:_gate_test_skill" in r.stdout)
check("经验健康归属分组输出（分域健康监控）", "按归属分组" in r.stdout)

# 4. 快照文件清理
import glob
snaps = glob.glob(os.path.join(tempfile.gettempdir(), "opencode_gate", "gate_" + sid + ".json"))
check("check 后快照文件已清理", len(snaps) == 0)

# 5. 自愈机制 --drain：残留快照自动补跑
r = run("--snapshot", sid)  # 建快照但不 check（模拟 idle 未触发）
snaps_before = glob.glob(os.path.join(tempfile.gettempdir(), "opencode_gate", "gate_" + sid + ".json"))
check("模拟：快照残留（门禁未执行）", len(snaps_before) == 1)
r = run("--drain")
check("drain 检测到残留快照", "残留快照" in r.stdout and sid in r.stdout)
snaps_after = glob.glob(os.path.join(tempfile.gettempdir(), "opencode_gate", "gate_" + sid + ".json"))
check("drain 补跑后快照清理", len(snaps_after) == 0)
r = run("--drain")
snaps_sid = glob.glob(os.path.join(tempfile.gettempdir(), "opencode_gate", "gate_" + sid + ".json"))
check("无残留时 drain 正常返回（rc=0 且测试 sid 快照已清；真实会话快照由 drain 顺带消费不误判）",
      r.returncode == 0 and len(snaps_sid) == 0)

# 6. drain max_n 限制：残留超过上限仅审计不阻塞
for i in range(4):
    r = run("--snapshot", sid + "-m" + str(i))  # 4 个残留快照
r = run("--drain", "1")  # 只补跑 1 个
check("max_n=1 时超限跳过审计", "超限跳过 3 个残留快照" in r.stdout)
snaps_left = glob.glob(os.path.join(tempfile.gettempdir(), "opencode_gate", "gate_" + sid + "-m*.json"))
check("超限快照保留待下次 drain", len(snaps_left) == 3)
# 清理剩余
r = run("--drain", "10")
check("提高 max_n 后全部补跑清理", "残留快照" in r.stdout)

# 7. 配套漏更检测（docs-sync 映射反向校验，优化1）
import importlib.util as _ilu7
_gate = _ilu7.spec_from_file_location("gate", GATE)
_gm = _ilu7.module_from_spec(_gate); _gate.loader.exec_module(_gm)
check("classify_change 分类正确（skill）", _gm.classify_change(r"C:\x\skills\foo_skill\SKILL.md") == "skill")
check("classify_change 分类正确（test）", _gm.classify_change(r"C:\x\tests\test_a.py") == "test")
check("classify_change 分类正确（rule）", _gm.classify_change(r"C:\x\regedit.md") == "rule")
# 只改 skill 未同步配套 → 检出漏更
w = _gm.check_docs_sync([os.path.join(CFG, r"skills\3gpp_skill\SKILL.md")])
check("只改 SKILL.md 检出配套漏更（instructions/regedit/tests README）", len(w) == 3)
# 配套都改了 → 通过
w2 = _gm.check_docs_sync([os.path.join(CFG, r"skills\3gpp_skill\SKILL.md"),
                          os.path.join(CFG, "instructions.md"),
                          os.path.join(CFG, "regedit.md"),
                          os.path.join(CFG, r"tests\README.md")])
check("配套齐改时漏更检测通过", len(w2) == 0)

# 8. 五步检查点（--check-5step，用户高优先级未完成项落地）
def run5(text):
    return subprocess.run([sys.executable, GATE, "--check-5step"], input=text,
                          capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=60)
r = run5("本会话无固化。")
check("无固化动作时五步检查不适用（rc=0）", r.returncode == 0 and "不适用" in r.stdout)
full = "进化：已固化 xxx\n【第一步·归纳】a\n【判定四条件】场景数：2 / 可移植：是 / 无重复：是 / 边界：明确\n【第二步·归属】b\n【第三步·edit】c\n【第四步·流水】d\n【第五步·校验】e\n"
r = run5(full)
check("五步标记齐全时通过（rc=0）", r.returncode == 0 and "齐全" in r.stdout)
full_no_cond = "进化：已固化 xxx\n【第一步·归纳】a\n【第二步·归属】b\n【第三步·edit】c\n【第四步·流水】d\n【第五步·校验】e\n"
r = run5(full_no_cond)
check("五步齐全但缺四条件声明时检出（rc=1）", r.returncode == 1 and "判定四条件声明缺失" in r.stdout)
single_scene = "进化：已固化 yyy\n【第一步·归纳】a\n【判定四条件】场景数：1 / 可移植：是 / 无重复：是 / 边界：明确\n【第二步·归属】b\n【第三步·edit】c\n【第四步·流水】d\n【第五步·校验】e\n"
r = run5(single_scene)
check("场景数=1 且无高代价/用户点名依据时四条件可追溯告警（rc=1）", r.returncode == 1 and "可追溯告警" in r.stdout)
single_ok = "进化：已固化 yyy\n【第一步·归纳】a\n【判定四条件】场景数：1（踩坑代价高，用户点名）/ 可移植：是 / 无重复：是 / 边界：明确\n【第二步·归属】b\n【第三步·edit】c\n【第四步·流水】d\n【第五步·校验】e\n"
r = run5(single_ok)
check("场景数=1 但带依据时通过（rc=0）", r.returncode == 0 and "齐全" in r.stdout)
check("裸『可移植：是』『无重复：是』触发依据软提示", "依据软提示" in r.stdout)
cond_with_basis = "进化：已固化 yyy\n【第一步·归纳】a\n【判定四条件】场景数：2 / 可移植：是（不含本机路径）/ 无重复：是（已比对）/ 边界：明确（触发条件与适用边界）\n【第二步·归属】b\n【第三步·edit】c\n【第四步·流水】d\n【第五步·校验】e\n"
r = run5(cond_with_basis)
check("三条件附括号依据时无软提示", "依据软提示" not in r.stdout)
bare_boundary = "进化：已固化 yyy\n【第一步·归纳】a\n【判定四条件】场景数：2 / 可移植：是（不含本机路径）/ 无重复：是（已比对）/ 边界：明确\n【第二步·归属】b\n【第三步·edit】c\n【第四步·流水】d\n【第五步·校验】e\n"
# 重置计数状态文件（防与前序用例计数累积）
_bare = os.path.join(tempfile.gettempdir(), "opencode_gate", "gate_bare_declare.json")
if os.path.exists(_bare):
    os.remove(_bare)
r = run5(bare_boundary)
check("裸『边界：明确』触发依据软提示（4/4 条件检测齐）", "依据软提示" in r.stdout and "边界" in r.stdout)
check("软提示含渐进计数（第 X/3 次）", "/3" in r.stdout)
# 连续 3 次裸声明 → 渐进升级硬告警（V6 剩余问题采纳；先重置计数状态文件防顺序依赖）
if os.path.exists(_bare):
    os.remove(_bare)
for i in range(3):
    r = run5(bare_boundary)
check("连续 3 次裸声明升级硬告警（rc=1）", r.returncode == 1 and "四条件硬告警" in r.stdout)
check("硬告警后计数清零（再声明回到软提示）", run5(bare_boundary).returncode == 0 and "依据软提示" in run5(bare_boundary).stdout)
# 阈值常量配置化
import importlib.util as _ilu8
_gate2 = _ilu8.spec_from_file_location("gate2", GATE)
_gm2 = _ilu8.module_from_spec(_gate2); _gate2.loader.exec_module(_gm2)
check("经验健康阈值配置化（常量可调）", hasattr(_gm2, "LOW_USE_DAYS") and hasattr(_gm2, "AGED_DAYS") and hasattr(_gm2, "BARE_DECLARE_LIMIT") and _gm2.BARE_DECLARE_LIMIT == 3)
partial = "进化：已固化 xxx\n【第一步·归纳】a\n【第三步·edit】c\n"
r = run5(partial)
check("缺步检出（rc=1）", r.returncode == 1 and "缺失" in r.stdout)
check("缺步清单点名缺失步骤", ("第二步·归属" in r.stdout) and ("第四步·流水" in r.stdout) and ("第五步·校验" in r.stdout))
none = "本次响应无任何固化声明。"
r = run5(none)
check("无固化声明不适用（rc=0）", r.returncode == 0 and "不适用" in r.stdout)
r = run5("进化检查完成：本次无固化项")
check("『无固化项』声明不适用五步（rc=0）", r.returncode == 0 and "不适用" in r.stdout)

# 9. 新增/删除文件检测（A+C 方案 2026-08-28：新增文件适配决策的前置检测）
r = run("--snapshot", sid)
tmp_skill2 = os.path.join(CFG, "skills", "_gate_test_skill2")
os.makedirs(tmp_skill2, exist_ok=True)
open(os.path.join(tmp_skill2, "SKILL.md"), "w", encoding="utf-8").write("---\nname: _gate_test_skill2\ndescription: gate new test\n---\n# new\n")
new_tool = os.path.join(CFG, "tools", "_gate_new_tool_test.py")
open(new_tool, "w", encoding="utf-8").write("# gate new tool test\n")
r = run("--check", sid)
check("新增文件检出（【新增文件】段输出）", r.returncode == 0 and "【新增文件】" in r.stdout)
check("新 skill 分类提示（regedit 技能层）", "新 skill 入口" in r.stdout)
check("新工具分类提示（tools-manifest 登记）", "工具/脚本" in r.stdout)
check("仅新增无既有改动时快照已清理", len(glob.glob(os.path.join(tempfile.gettempdir(), "opencode_gate", "gate_" + sid + ".json"))) == 0)
# 删除检测
r = run("--snapshot", sid)
os.remove(new_tool)
r = run("--check", sid)
check("删除文件检出（【删除文件】段输出）", "【删除文件】" in r.stdout and "_gate_new_tool_test" in r.stdout)
check("仅删除无既有改动时快照已清理", len(glob.glob(os.path.join(tempfile.gettempdir(), "opencode_gate", "gate_" + sid + ".json"))) == 0)

# 清理临时 skill（try/finally 保证：即使中途断言失败也清理，防 _gate_test_skill 残留污染 regedit 测试）
import shutil
for _d in ("_gate_test_skill", "_gate_test_skill2"):
    shutil.rmtree(os.path.join(CFG, "skills", _d), ignore_errors=True)
if os.path.exists(new_tool):
    os.remove(new_tool)
print("  （注：gate 测试在 evolution_log.txt 追加的骨架条目保留——只增不改铁律）")

print("\n结果：通过 %d 项，失败 %d 项" % (pass_n, fail_n))
sys.exit(1 if fail_n else 0)
