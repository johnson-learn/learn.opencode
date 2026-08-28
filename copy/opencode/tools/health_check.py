# -*- coding: utf-8 -*-
# 框架健康检查脚本（health_check.py）——一键输出框架健康度报告
# 检查项：①核心配置齐全 ②skill frontmatter 合法+体积门限 ③插件最近执行 ④测试全部可运行
#        ⑤门禁最近会话 idle/drain 记录 ⑥evolution_log 待处理项 ⑦平台 API 依赖保障（实验性 hook 可用性）
#        ⑧字符边界规范（框架文件 CRLF/BOM/编码一致性，铁律第 9 条防线）
#        ⑨注入量管控（四注入文件合计 ≤30KB，2026-08-28 报告评审后新增）
import os, sys, json, re, subprocess, glob, datetime
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

CFG = os.path.join(os.path.expanduser("~"), ".config", "opencode")
TESTS = os.path.join(CFG, "tests")
ok, warn, fail = [], [], []

def add_ok(t): ok.append(t)
def add_warn(t): warn.append(t)
def add_fail(t): fail.append(t)

# ① 核心配置文件齐全
core = ["AGENTS.md", "instructions.md", "regedit.md", "docs-sync.md", "tools-manifest.md", "opencode.jsonc"]
missing = [f for f in core if not os.path.exists(os.path.join(CFG, f))]
(missing and [add_fail("缺核心文件: " + f) for f in missing]) or add_ok("核心配置 %d 个文件全部存在" % len(core))

# ② 6 个 skill frontmatter 合法 + 体积门限
skills_root = os.path.join(CFG, "skills")
skill_dirs = [d for d in os.listdir(skills_root) if os.path.isdir(os.path.join(skills_root, d)) and d != "default"]
skill_dirs += [d for d in os.listdir(os.path.join(skills_root, "default")) if os.path.isdir(os.path.join(skills_root, "default", d))]
limit_kb = 15
bad_skills = []
for d in sorted(set(skill_dirs)):
    p = os.path.join(skills_root, d, "SKILL.md")
    if d == "evolution_skill":
        p = os.path.join(skills_root, "default", d, "SKILL.md")
    if not os.path.exists(p):
        bad_skills.append(d + " 缺 SKILL.md")
        continue
    c = open(p, encoding="utf-8", errors="replace").read()
    if not re.match(r"^\ufeff?---\n.*?name:.*?\n---", c, re.S):
        bad_skills.append(d + " frontmatter 异常")
    if len(c) > limit_kb * 1024:
        bad_skills.append(d + " 超 %dKB 门限(%d 字节)" % (limit_kb, len(c)))
(bad_skills and [add_fail("skill 异常: " + b) for b in bad_skills]) or add_ok("6 个 skill frontmatter 合法且体积均在门限内")

# ③ 插件最近执行（24h 内有日志）
plog = os.path.join(CFG, "plugins", "plugin-evolution.log")
if os.path.exists(plog):
    age_h = (datetime.datetime.now() - datetime.datetime.fromtimestamp(os.path.getmtime(plog))).total_seconds() / 3600
    if age_h <= 24:
        add_ok("插件最近执行正常（%.1f 小时前有日志）" % age_h)
    else:
        add_warn("插件最近 %.1f 小时无日志（可能 opencode 未重启加载新插件）" % age_h)
else:
    add_fail("插件日志不存在（skill-banner.js 未运行）")

# ④ 测试全部可运行（python 文件可 ast.parse）+ 最近全绿（可选 --run 才实跑）
py_tests = [f for f in os.listdir(TESTS) if re.match(r"test_.+\.py$", f)]
import ast as _ast
bad_py = []
for f in py_tests:
    try:
        _ast.parse(open(os.path.join(TESTS, f), encoding="utf-8").read())
    except SyntaxError as e:
        bad_py.append(f + " 语法错误 L" + str(e.lineno))
(bad_py and [add_fail("测试不可运行: " + b) for b in bad_py]) or add_ok("%d 个 Python 测试全部可解析" % len(py_tests))

# ④b 可选实跑（--run 全部 / --run-quick 快测试子集；注意：快子集不含 test_health_check 自身，防递归）
if "--run" in sys.argv or "--run-quick" in sys.argv:
    quick_only = "--run-quick" in sys.argv
    targets = ["skill_validate.py", "test_regedit.py", "test_evolution_consistency.py"] if quick_only else py_tests
    print("  [提示] 实跑模式（%s），预计耗时 %s" % (
        "快测试子集" if quick_only else "全部测试",
        "约 30~90 秒" if quick_only else "约 5~10 分钟"))
    run_fail = []
    for f in targets:
        try:
            r = subprocess.run([sys.executable, os.path.join(TESTS, f), os.path.join(CFG, "skills")] if f == "skill_validate.py" else [sys.executable, os.path.join(TESTS, f)],
                               capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=300, cwd=TESTS)
            if r.returncode != 0:
                run_fail.append(f)
        except Exception as e:
            run_fail.append(f + "(" + str(e)[:40] + ")")
    js = os.path.join(TESTS, "test_plugin.js")
    if not quick_only and os.path.exists(js):
        try:
            r = subprocess.run(["node", js], capture_output=True, text=True,
                               encoding="utf-8", errors="replace", timeout=300, cwd=TESTS)
            if r.returncode != 0:
                run_fail.append("test_plugin.js")
        except Exception as e:
            run_fail.append("test_plugin.js(" + str(e)[:40] + ")")
    label = "快测试子集（%d 个）" % len(targets) if quick_only else "全部测试（%d py + test_plugin.js）" % len(py_tests)
    (run_fail and [add_fail("实跑失败: " + f) for f in run_fail]) or add_ok("实跑%s通过" % label)

# ⑤ 门禁最近会话 idle/drain 记录（快照目录 + 插件日志）
snap_dir = os.path.join(os.environ.get("TEMP", os.path.expanduser("~\\AppData\\Local\\Temp")), "opencode_gate")
resid = glob.glob(os.path.join(snap_dir, "gate_*.json"))
if resid:
    add_warn("门禁残留 %d 个快照未消费（下次 session.created 的 --drain 会补跑）" % len(resid))
else:
    add_ok("门禁无残留快照（idle 正常或 drain 已补跑）")
if os.path.exists(plog):
    tail = open(plog, encoding="utf-8", errors="replace").read()[-4000:]
    idle_n = tail.count("session.idle 触发")
    drain_n = tail.count("--drain") + tail.count("drain")
    add_ok("门禁最近日志：idle 触发 %d 次、drain 相关 %d 次" % (idle_n, drain_n))

# ⑥ evolution_log 待处理项（近 10 条中含"待模型补充"骨架条目数）
elog = os.path.join(CFG, "skills", "default", "evolution_skill", "evolution_log.txt")
if os.path.exists(elog):
    c = open(elog, encoding="utf-8", errors="replace").read()
    pending = c.count("智能归纳待模型补充")
    if pending > 0:
        add_warn("evolution_log 有 %d 条门禁骨架待模型补充智能归纳" % pending)
    else:
        add_ok("evolution_log 无待处理骨架条目")

# ⑦ 平台 API 依赖保障（实验性 hook 可用性；opencode 升级移除 API 时此处失败告警）
api_test = os.path.join(TESTS, "test_platform_api.py")
try:
    r = subprocess.run([sys.executable, api_test], capture_output=True, text=True,
                       encoding="utf-8", errors="replace", timeout=180, cwd=TESTS)
    if r.returncode == 0:
        add_ok("平台 API 保障通过（experimental.chat.system.transform 可用）")
    else:
        tail = (r.stdout + r.stderr)[-200:].replace("\n", " ")
        add_fail("平台 API 保障失败（实验性 hook 可能已被移除或二进制变动）：" + tail)
except Exception as e:
    add_fail("平台 API 保障无法执行：" + str(e)[:80])

# ⑧ 字符边界规范（铁律第 9 条防线：框架文件 CRLF/BOM/编码一致性）
charset_test = os.path.join(TESTS, "test_charset.py")
try:
    r = subprocess.run([sys.executable, charset_test], capture_output=True, text=True,
                       encoding="utf-8", errors="replace", timeout=180, cwd=TESTS)
    if r.returncode == 0:
        add_ok("字符边界规范通过（框架文件 UTF-8 无 BOM + LF 统一）")
    else:
        tail = (r.stdout + r.stderr)[-200:].replace("\n", " ")
        add_fail("字符边界扫描失败（存在 CRLF/BOM/编码异常文件，需立即归一修复）：" + tail)
except Exception as e:
    add_fail("字符边界扫描无法执行：" + str(e)[:80])

# ⑨ 注入量管控（四注入文件合计 ≤30KB，超限告警触发精简；2026-08-28 报告评审后新增）
INJECT_FILES = ["instructions.md", "regedit.md", "tools-manifest.md", "docs-sync.md"]
INJECT_LIMIT_KB = 30
total_bytes = 0
missing_inj = []
for f in INJECT_FILES:
    p = os.path.join(CFG, f)
    if os.path.exists(p):
        total_bytes += os.path.getsize(p)
    else:
        missing_inj.append(f)
if missing_inj:
    add_warn("注入文件缺失：%s" % "、".join(missing_inj))
total_kb = total_bytes / 1024.0
if total_kb > INJECT_LIMIT_KB:
    add_warn("注入总量 %.1fKB 超过 %dKB 上限（触发精简：优先压缩示例段落/重复摘要，大表保留速览头行）" % (total_kb, INJECT_LIMIT_KB))
else:
    add_ok("注入总量 %.1fKB 在上限 %dKB 内（instructions/regedit/tools-manifest/docs-sync）" % (total_kb, INJECT_LIMIT_KB))

print("【框架健康度报告】 %s" % datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
print("-" * 60)
for t in ok:
    print("  [OK]   " + t)
for t in warn:
    print("  [警告] " + t)
for t in fail:
    print("  [失败] " + t)
print("-" * 60)
print("结论：OK %d 项 / 警告 %d 项 / 失败 %d 项" % (len(ok), len(warn), len(fail)))
sys.exit(1 if fail else 0)
