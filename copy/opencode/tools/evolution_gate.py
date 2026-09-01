# -*- coding: utf-8 -*-
# 进化门禁脚本（evolution gate）——把"必须执行的进化步骤"确定性化
# 用法：
#   python evolution_gate.py --snapshot <会话ID>   会话开始时：记录规则文件状态快照
#   python evolution_gate.py --check <会话ID>      会话结束时：检测改动→自动补流水→自动跑测试
#   python evolution_gate.py --check-5step         从 stdin 读会话消息文本，检测五步检查点标记齐全性
#   python evolution_gate.py --drain [max_n]       自愈补跑残留快照
# 设计（用户 2026-08-26 定）：机制步骤（流水落盘/测试执行/一致性校验）由本脚本 100% 确定性执行，
#   不依赖模型自觉；智能步骤（经验归纳/归属判断）仍由模型完成，脚本输出待补充清单。
# 2026-08-27 新增 --check-5step：五步检查点程序化强制（用户高优先级未完成项落地）——
#   模型执行固化的响应必须含【第一步·归纳】~【第五步·校验】五个标记，缺步由本脚本检出，
#   插件 session.idle 调用本模式并把缺步警告附加到进化检查任务文本。
import os, sys, json, re, subprocess, hashlib, datetime, tempfile

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
CFG = os.path.join(os.path.expanduser("~"), ".config", "opencode")
TOOLS = os.path.join(CFG, "tools")
TESTS = os.path.join(CFG, "tests")
LOG = os.path.join(CFG, "skills", "default", "evolution_skill", "evolution_log.txt")
SNAP_DIR = os.path.join(tempfile.gettempdir(), "opencode_gate")
WATCH_EXT = (".md", ".txt", ".py", ".js", ".jsonc")
IGNORE_DIRS = ("__pycache__", "node_modules", ".git", "archive")
STATE_FILES = ("path_map.txt", "sync_target.txt")

# 五步检查点标记（与 evolution_skill SKILL.md 五步输出格式一致；改格式需同步 SKILL.md）
FIVE_STEPS = ["第一步·归纳", "第二步·归属", "第三步·edit", "第四步·流水", "第五步·校验"]

# 固化判定四条件显式声明（2026-08-28 V2 报告采纳：把四条件从 LLM 内心判断变成必须显式输出可检测）
FOUR_COND = ["场景数", "可移植", "无重复", "边界"]

# 经验健康阈值（2026-08-28 V6 剩余问题采纳：阈值配置化，按需调整）
LOW_USE_DAYS = 60      # 使用率追踪：活跃经验最后引用超过 N 天未引用 → 低活性提示
AGED_DAYS = 180        # 条目级老化：最后验证/固化日期超过 N 天未再验证 → 老化提示
INACTIVE_DAYS = 90     # 全库活性：最近一条经验记录超过 N 天 → 框架老化提示
BARE_DECLARE_LIMIT = 3  # 四条件裸声明渐进硬告警：连续 N 次裸『是/明确』声明后升级 rc=1

WATCH_ROOTS = [os.path.join(CFG, "skills"), os.path.join(CFG, "plugins"), os.path.join(CFG, "tools"), os.path.join(CFG, "tests")]
WATCH_FILES = [os.path.join(CFG, f) for f in ("AGENTS.md", "instructions.md", "regedit.md", "docs-sync.md", "tools-manifest.md")]


def iter_watch():
    seen = set()
    for root in WATCH_ROOTS:
        for dp, dn, fn in os.walk(root):
            dn[:] = [d for d in dn if d not in IGNORE_DIRS]
            for f in fn:
                if f in STATE_FILES or f.endswith(".log") or f.endswith(".jsonl"):
                    continue
                if not f.endswith(WATCH_EXT):
                    continue
                seen.add(os.path.join(dp, f))
    for f in WATCH_FILES:
        seen.add(f)
    return sorted(seen)


def scan():
    out = {}
    for fp in iter_watch():
        if not os.path.isfile(fp):
            continue
        st = os.stat(fp)
        out[fp] = {"size": st.st_size, "mtime": st.st_mtime}
    return out


def snap_path(sid):
    return os.path.join(SNAP_DIR, "gate_" + sid.replace("/", "_").replace("\\", "_") + ".json")


def do_snapshot(sid):
    os.makedirs(SNAP_DIR, exist_ok=True)
    data = {"files": scan(), "log_size": os.path.getsize(LOG) if os.path.exists(LOG) else 0}
    with open(snap_path(sid), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)
    print("[gate] 快照完成：%d 个规则文件，log 大小 %d" % (len(data["files"]), data["log_size"]))


def classify_change(fp):
    """按 docs-sync.md 映射表分类改动文件 → 变更类型"""
    rel = fp.replace("\\", "/")
    if "/skills/" in rel and rel.endswith("SKILL.md"):
        return "skill"
    if "/tests/" in rel and (rel.endswith(".py") or rel.endswith(".js")):
        return "test"
    if "/tools/" in rel and rel.endswith(".py"):
        return "tool"
    if "/plugins/" in rel:
        return "plugin"
    base = os.path.basename(fp)
    if base in ("AGENTS.md", "instructions.md", "regedit.md", "docs-sync.md", "tools-manifest.md"):
        return "rule"
    if base == "evolution.md":
        return "rule"
    return None

# docs-sync 映射表程序化落地（单一数据源：直接解析 docs-sync.md，消除硬编码双份维护）
DOCS_SYNC_FALLBACK = {
    "skill": ["instructions.md", "regedit.md", "tests\\README.md"],
    "test": ["tests\\README.md", "regedit.md"],
    "tool": ["tools-manifest.md", "regedit.md"],
    "plugin": ["regedit.md", "tests\\README.md"],
    "rule": ["regedit.md", "instructions.md"],
}
# 变更类型 → docs-sync.md 行首关键词
TYPE_ROW_KEY = {"skill": "skill 新增", "test": "测试用例新增", "tool": "工具新增",
                "plugin": "插件变更", "rule": "流程/机制变更"}

def parse_docs_sync():
    """从 docs-sync.md 解析映射表（单一数据源）；解析失败回退硬编码表"""
    try:
        p = os.path.join(CFG, "docs-sync.md")
        c = open(p, encoding="utf-8", errors="replace").read()
        result = {}
        for row in re.findall(r"\|\s*\*\*(.*?)\*\*\s*\|\s*(.*?)\s*\|", c):
            title, files_col = row[0].strip(), row[1]
            # 提取文件名（docs-sync 文件列中文件名不带反引号，直接匹配扩展名词；
            # 2026-08-28 修复：原反引号正则提取为空导致映射全空、配套漏更检测失效；
            # 过滤条件性裸文件名 SKILL.md/AGENTS.md——"对应 SKILL.md""如需铁律"无法静态定位路径）
            fnames = [f for f in re.findall(r"([A-Za-z0-9_\\-]+\.(?:md|txt|py|js))", files_col)
                      if f not in ("SKILL.md", "AGENTS.md")]
            for key, kw in TYPE_ROW_KEY.items():
                if title.startswith(kw):
                    if fnames:
                        result[key] = [f.replace("\\", os.sep).replace("/", os.sep) for f in fnames]
        if result:
            return result
    except Exception:
        pass
    return DOCS_SYNC_FALLBACK

DOCS_SYNC_MAP = parse_docs_sync()

def check_docs_sync(changed):
    """配套漏更检测：改了 A，但 docs-sync 映射要求的 B 未同步改 → 输出警告"""
    warnings = []
    changed_set = {os.path.normpath(fp) for fp in changed}
    for fp in changed:
        ct = classify_change(fp)
        if not ct:
            continue
        for req in DOCS_SYNC_MAP.get(ct, []):
            req_path = os.path.normpath(os.path.join(CFG, req))
            if req_path not in changed_set:
                warnings.append((os.path.basename(fp), req))
    if warnings:
        print("[gate] 配套漏更检测：以下改动可能漏更配套文件（按 docs-sync.md 映射表）：")
        for src, req in warnings:
            print("  改了 %s → 应同步 %s（未检测到改动）" % (src, req))
    else:
        print("[gate] 配套漏更检测通过（docs-sync 映射要求的配套文件均已同步改动）")
    return warnings


def classify_new(fp):
    """新增文件分类（A+C 方案 2026-08-28：适配决策的前置分类）"""
    rel = fp.replace("\\", "/")
    if "/skills/" in rel and rel.endswith("SKILL.md"):
        return "新 skill 入口（需登记 regedit 技能层 + instructions 清单 + 触发方式判定）"
    if "/skills/" in rel and rel.endswith((".md", ".py", ".ps1", ".txt")):
        return "skill 附属文件（references/脚本：判定是否路由表引用 + 入口按需读取）"
    if "/tests/" in rel:
        return "测试文件（需登记 tests\\README + regedit 测试层 + 挂入门禁自动测试链）"
    if "/tools/" in rel and rel.endswith((".py", ".ps1")):
        return "工具/脚本（需登记 tools-manifest + regedit 工具层）"
    if "/plugins/" in rel:
        return "插件文件（需登记 regedit 插件层 + test_plugin 用例）"
    base = os.path.basename(fp)
    if base.endswith(".md") or base.endswith(".jsonc"):
        return "规则/配置文档（判定 E 类注入还是 F 类按需 + 30KB 注入量管控）"
    return "其它新增（判定一次性任务产物则建议存档 tools\\archive 或忽略）"


def experience_health():
    """经验健康引擎（方案丁 2026-08-28 一体化；V4 方案甲' 2026-08-28 升级为条目结构化扫描）
    数据源 = evolution_log.txt。新条目（含"状态："字段的结构化格式）按字段精确扫描；
    旧自由文本条目用启发式兜底（不误报）。扫描项：
    ①待二次验证条目全量清单（结构化+启发式，top5+总数）②deprecated 记录清单与规则文件标记校验
    ③条目级老化（最后验证/固化日期 >180 天）+ 全库级活性信号"""
    if not os.path.exists(LOG):
        return
    text = open(LOG, encoding="utf-8", errors="replace").read()
    lines = text.splitlines()
    out = []
    # 解析结构化条目（新格式：以 [日期] 标题 开头，后续行含"状态："字段）
    entries = []
    cur = None
    for ln in lines:
        m = re.match(r"\[(\d{4}-\d{2}-\d{2})\]\s*(.*)", ln.strip())
        if m:
            if cur:
                entries.append(cur)
            cur = {"date": m.group(1), "title": m.group(2)[:110], "status": "active",
                   "scenes": "", "verified": "", "keywords": "", "raw": ln.strip()[:200]}
        elif cur is not None:
            if ln.startswith("- 状态："):
                cur["status"] = ln[len("- 状态："):].strip()
            elif ln.startswith("- 场景数："):
                cur["scenes"] = ln[len("- 场景数："):].strip()
            elif ln.startswith("- 最后验证："):
                cur["verified"] = ln[len("- 最后验证："):].strip()
            elif ln.startswith("- 核心关键词："):
                cur["keywords"] = ln[len("- 核心关键词："):].strip()
            elif ln.startswith("- 归属："):
                cur["owner"] = ln[len("- 归属："):].strip()
            cur["raw"] += " | " + ln.strip()[:120]
    if cur:
        entries.append(cur)
    # ① 待二次验证清单（结构化优先，启发式兜底）
    pending = [e for e in entries if e["status"] == "待二次验证"]
    if not pending:
        pending = [{"title": l.strip()[11:][:100], "raw": l.strip()[:150]}
                   for l in lines if "待二次验证" in l and "二次验证通过" not in l and l.strip().startswith("[20")]
    if pending:
        out.append("[经验健康] 待二次验证条目 %d 条（请在相关任务中主动套用验证并追加结果）：" % len(pending))
        for e in pending[-5:]:
            out.append("    · %s" % (e["title"] if isinstance(e, dict) and "title" in e else e))
        if len(pending) > 5:
            out.append("    （另有 %d 条更早的待验证条目，见 evolution_log）" % (len(pending) - 5))
    # ② deprecated 记录清单 + 规则文件标记校验
    dep_entries = [e for e in entries if e["status"] == "deprecated"]
    dep_heuristic = [l.strip()[:150] for l in lines if ("deprecat" in l.lower()) and l.strip().startswith("[20")]
    if dep_entries or dep_heuristic:
        rule_files = []
        for root in WATCH_ROOTS:
            for dp, dn, fn in os.walk(root):
                dn[:] = [d for d in dn if d not in IGNORE_DIRS]
                for f in fn:
                    if f.endswith(".md"):
                        rule_files.append(os.path.join(dp, f))
        marks = 0
        for rf in rule_files:
            try:
                marks += open(rf, encoding="utf-8", errors="replace").read().count("[DEPRECATED]")
            except Exception:
                pass
        if marks == 0:
            out.append("[经验健康] 有 %d 条 deprecation 记录但规则文件无 [DEPRECATED] 显式标记（状态只写流水不可见——请在对应规则条目加前缀标记）；最近弃用记录：%s"
                       % (len(dep_entries) + len(dep_heuristic), (dep_entries[-1]["title"] if dep_entries else dep_heuristic[-1])[:80]))
        else:
            out.append("[经验健康] deprecation 记录 %d 条，规则文件 [DEPRECATED] 标记 %d 处；最近弃用：%s（若该条未在规则文件显式标记请补）"
                       % (len(dep_entries) + len(dep_heuristic), marks, (dep_entries[-1]["title"] if dep_entries else dep_heuristic[-1])[:80]))
    # ②b deprecated 条目定位（V5 方案甲'：结构化条目的核心关键词是否出现在规则文件的 [DEPRECATED] 段落）
    if dep_entries:
        for e in dep_entries:
            kws = [k.strip() for k in (e.get("keywords") or "").replace("、", ",").split(",") if k.strip()]
            if not kws:
                continue
            found = False
            for rf in rule_files:
                try:
                    c = open(rf, encoding="utf-8", errors="replace").read()
                    for para in c.split("\n\n"):
                        if ("[DEPRECATED]" in para or "~~" in para) and any(k in para for k in kws):
                            found = True
                            break
                    if found:
                        break
                except Exception:
                    pass
            if not found:
                out.append("[经验健康] deprecated 定位：『%s』已弃用但其核心关键词未出现在任何规则文件的 [DEPRECATED] 标记段落（请在对应规则条目补显式标记）" % e["title"][:70])
    # ③ 条目级老化（结构化条目：最后验证或固化日期 >180 天）
    today = datetime.date.today()
    aged = []
    for e in entries:
        dstr = e["verified"][:10] if e["verified"] and e["verified"][:10][:4].isdigit() else e["date"]
        try:
            d = datetime.date(*map(int, dstr.split("-")))
            if (today - d).days > AGED_DAYS and e["status"] == "active":
                aged.append((e["date"], e["title"][:80]))
        except Exception:
            pass
    if aged:
        out.append("[经验健康] 条目级老化：%d 条活跃经验超过 180 天未再验证（外部环境可能已变化，建议抽查重验）：" % len(aged))
        for d, t in aged[-5:]:
            out.append("    · [%s] %s" % (d, t))
    # ③b 低活性扫描（V5 方案甲'：插件写 evolution_trace.jsonl 的最后引用日期 → >60 天未引用提示下沉）
    trace_file = os.path.join(CFG, "skills", "default", "evolution_skill", "evolution_trace.jsonl")
    if os.path.exists(trace_file):
        last_use = {}
        try:
            for ln in open(trace_file, encoding="utf-8", errors="replace"):
                try:
                    j = json.loads(ln)
                    if "entry" in j and "t" in j:
                        last_use[j["entry"]] = j["t"][:10]
                except Exception:
                    pass
        except Exception:
            pass
        low = []
        for e in entries:
            if e["status"] != "active" or not e.get("keywords"):
                continue
            lu = last_use.get(e["title"])
            dstr = (lu or e["verified"][:10]) if (lu or e["verified"][:10][:4].isdigit()) else e["date"]
            try:
                d = datetime.date(*map(int, dstr.split("-")))
                if (today - d).days > LOW_USE_DAYS:
                    low.append((e["date"], e["title"][:80]))
            except Exception:
                pass
        if low:
            out.append("[经验健康] 低活性：%d 条活跃经验超过 60 天未被引用（使用率追踪为程序化信号，建议下沉 references/ 或标注 deprecated）：" % len(low))
            for d, t in low[-5:]:
                out.append("    · [%s] %s" % (d, t))
    # ④ 归属分组统计（2026-09-01 框架进化评审建议：分域健康监控前提——流水条目带"归属：xxx_skill"字段）
    owners = {}
    for e in entries:
        ow = (e.get("owner") or "").strip()
        if not ow:
            continue
        owners.setdefault(ow, {"n": 0, "last": ""})
        owners[ow]["n"] += 1
        if e.get("date", "") > owners[ow]["last"]:
            owners[ow]["last"] = e.get("date", "")
    if owners:
        parts = []
        for k in sorted(owners):
            parts.append("%s %d 条(最近 %s)" % (k, owners[k]["n"], owners[k]["last"]))
        out.append("[经验健康] 按归属分组（结构化 active 条目）：" + "、".join(parts))
    else:
        out.append("[经验健康] 归属分组：流水条目尚无『归属：xxx_skill』字段（进化第四步结构化格式请补归属字段，分域健康监控依赖此字段）")
    # 全库级活性信号
    last_date = None
    for ln in reversed(lines):
        m = re.match(r"\[(\d{4}-\d{2}-\d{2})\]", ln.strip())
        if m:
            try:
                last_date = datetime.date(*map(int, m.group(1).split("-")))
            except Exception:
                pass
            break
    if last_date and (today - last_date).days > INACTIVE_DAYS:
        out.append("[经验健康] 老化提示：最近一条经验记录于 %s（%d 天前）——框架超过 90 天未产生新经验，建议抽查重验" % (last_date.isoformat(), (today - last_date).days))
    for o in out:
        print(o)


def do_check(sid):
    sp = snap_path(sid)
    if not os.path.exists(sp):
        print("[gate] 无快照（会话开始未执行 --snapshot），跳过")
        return 0
    with open(sp, encoding="utf-8") as f:
        snap = json.load(f)
    changed = []
    cur = scan()
    for fp, st in snap["files"].items():
        if fp not in cur or cur[fp] != st:
            changed.append(fp)
    # A+C 方案（2026-08-28）：新增/删除文件检测——旧逻辑只对比快照内文件，新增文件不进门禁；
    # 现在显式检出，供进化检查任务做"适配决策"（四问分析 + 弹窗用户决定）
    new_files = sorted(fp for fp in cur if fp not in snap["files"])
    deleted = sorted(fp for fp in snap["files"] if fp not in cur)
    if not changed and not new_files and not deleted:
        print("[gate] 无规则文件改动，门禁通过（无需固化）")
        os.remove(sp)
        return 0
    print("[gate] 检测到 %d 个规则文件改动：" % len(changed))
    for fp in changed:
        print("  -", fp.replace(CFG, r"<opencode配置目录>"))
    if new_files:
        print("[gate] 【新增文件】%d 个（待适配决策：按四问分析→弹窗用户决定 适配/忽略/存档；纳入验收=test_regedit+skill_validate+test_instructions 全绿）：" % len(new_files))
        for fp in new_files:
            print("  [+%s] %s" % (classify_new(fp).split("（")[0], fp.replace(CFG, r"<opencode配置目录>")))
        for fp in new_files:
            print("    → %s" % classify_new(fp))
    if deleted:
        print("[gate] 【删除文件】%d 个（若为框架组件需在 regedit 撤销登记并跑 test_regedit）：" % len(deleted))
        for fp in deleted:
            print("  [-]", fp.replace(CFG, r"<opencode配置目录>"))
    if not changed:
        # 仅新增/删除（本会话无既有文件改动）：不跑流水兜底与测试，直接清理快照
        print("[gate] 无既有规则文件改动，仅新增/删除检测（适配决策由进化检查任务执行）")
        os.remove(sp)
        return 0
    # 0. 配套漏更检测（docs-sync 映射表反向校验）
    docs_sync_warnings = check_docs_sync(changed)
    # 1. 流水自动追加（若本会话模型未正常追加记录）
    log_size_now = os.path.getsize(LOG) if os.path.exists(LOG) else 0
    appended = False
    if log_size_now == snap["log_size"]:
        entry = ("[%s] 会话自动门禁（%s） → 机制步骤已由 evolution_gate 脚本确定性执行：本会话改动 %d 个规则文件（清单见下）；"
                 "智能归纳待模型补充\n" % (datetime.date.today().isoformat(), sid, len(changed)))
        entry += "".join("- " + fp.replace(CFG, r"<opencode配置目录>") + "\n" for fp in changed)
        with open(LOG, "a", encoding="utf-8") as f:
            f.write(entry + "\n")
        appended = True
        print("[gate] 流水骨架已自动追加（模型未记录时兜底）")
    else:
        print("[gate] 流水已有本会话记录（模型已正常追加），不重复")
    # 2. 按改动类型自动跑对应测试（docs-sync.md 映射表程序化落地：一致性测试全跑，防配套漏更）
    results = {}
    def run_test(name, cmd, cwd=TESTS):
        try:
            r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8",
                               errors="replace", timeout=180, cwd=cwd)
            results[name] = (r.returncode, r.stdout.strip().splitlines()[-1] if r.stdout.strip() else "")
        except Exception as e:
            results[name] = (-1, str(e)[:100])
    py = sys.executable
    if any("skills" in fp for fp in changed):
        run_test("skill_validate", [py, os.path.join(TESTS, "skill_validate.py"), os.path.join(CFG, "skills")])
    # L1 领域自测精准触发（2026-09-01 框架进化评审：改哪个 skill 跑哪个 skill 的 tests/test_skill_self.py）
    skill_hits = set()
    for fp in list(changed) + list(new_files):
        m = re.match(r"skills[/\\](?:default[/\\])?([A-Za-z0-9_]+)", fp.replace(CFG, "").lstrip("\\/"))
        if m:
            skill_hits.add(m.group(1))
    for sk in sorted(skill_hits):
        base = os.path.join(CFG, "skills", "default", sk) if sk == "evolution_skill" else os.path.join(CFG, "skills", sk)
        t = os.path.join(base, "tests", "test_skill_self.py")
        if os.path.isfile(t):
            run_test("L1:" + sk, [py, t])
        if sk == "program_skill":
            t2 = os.path.join(base, "tests", "test_compile_template.py")
            if os.path.isfile(t2):
                run_test("L1:program_compile", [py, t2])
    if any(fp.endswith("regedit.md") for fp in changed):
        run_test("test_regedit", [py, os.path.join(TESTS, "test_regedit.py")])
    if any("plugins" in fp for fp in changed):
        run_test("test_plugin", ["node", os.path.join(TESTS, "test_plugin.js")])
    run_test("test_evolution_consistency", [py, os.path.join(TESTS, "test_evolution_consistency.py")])
    # docs-sync 映射表相关一致性：任何改动都跑（登记/清单/总表配套同步的机器校验）
    run_test("test_instructions", [py, os.path.join(TESTS, "test_instructions.py")])
    run_test("test_regedit", [py, os.path.join(TESTS, "test_regedit.py")])
    run_test("test_tools_manifest", [py, os.path.join(TESTS, "test_tools_manifest.py")])
    print("[gate] 自动测试结果：")
    for name, (rc, tail) in results.items():
        print("  %s: rc=%s | %s" % (name, rc, tail))
    # 3. 待模型补充清单
    print("[gate] 待模型补充（智能部分）：五步流程第 1-3 步（归纳经验/归属判定/edit 固化到可执行载体）")
    print("[gate] 机器完成：流水兜底追加=%s、对应测试已自动执行" % ("是" if appended else "否(模型已记录)"))
    # 4. 二次验证状态计数（2026-08-28 V2 报告采纳：程序化统计"待二次验证"未闭环条目，主动提示）
    if os.path.exists(LOG):
        _lc = open(LOG, encoding="utf-8", errors="replace").read()
        _p = _lc.count("待二次验证")
        _v = _lc.count("二次验证通过")
        if _p > _v:
            print("[gate] 二次验证未闭环：待二次验证 %d 条 / 已验证通过 %d 条——请在相关任务中主动套用验证并追加结果" % (_p, _v))
    # 5. 经验健康引擎（方案丁 2026-08-28：待验证清单/deprecated 标记校验/老化扫描一体化）
    experience_health()
    os.remove(sp)
    return 0


def do_drain(max_n=3):
    """自愈机制：扫描 SNAP_DIR 中残留快照（上次会话 idle 未触发 --check 的遗留），逐个补跑门禁。
    解决"门禁依赖插件正确调用 session.idle"的单点故障——即使 idle 断了，下次会话开始时自动补执行。
    max_n：最多补跑快照数（防残留过多时长时间阻塞，超出部分仅审计记录）"""
    if not os.path.isdir(SNAP_DIR):
        print("[gate] 无快照目录，无残留快照")
        return 0
    snaps = sorted(f for f in os.listdir(SNAP_DIR) if f.startswith("gate_") and f.endswith(".json"))
    if not snaps:
        print("[gate] 无残留快照（上次会话门禁正常执行）")
        return 0
    skipped = snaps[max_n:]
    snaps = snaps[:max_n]
    if skipped:
        audit = os.path.join(SNAP_DIR, "gate_audit.log")
        with open(audit, "a", encoding="utf-8") as f:
            f.write("[%s] drain 跳过 %d 个超限残留快照（max_n=%d）: %s\n"
                    % (datetime.datetime.now().isoformat(), len(skipped), max_n, ", ".join(skipped)))
        print("[gate] 超限跳过 %d 个残留快照（仅审计，见 gate_audit.log）" % len(skipped))
    print("[gate] 检测到 %d 个残留快照（上次会话门禁未执行），自动补跑：" % len(snaps))
    for f in snaps:
        sid = f[len("gate_"):-len(".json")]
        print("[gate] 补跑会话 %s" % sid)
        do_check(sid)
    return 0


def do_check_5step():
    """五步检查点检测：stdin 读会话消息文本，检测固化响应是否含五步标记。
    返回 0=齐全/不适用，1=缺步（插件把缺步警告附加到进化检查任务）。
    stdin 字节流按 utf-8 解码（与插件 execSync input / python subprocess encoding=utf-8 配对）。"""
    text = sys.stdin.buffer.read().decode("utf-8", errors="replace")
    has_cure = ("已固化" in text) and ("无固化项" not in text)
    if not has_cure:
        print("[gate] 本会话无固化动作（无『已固化』声明），五步检查点不适用")
        return 0
    missing = [s for s in FIVE_STEPS if ("【" + s + "】") not in text]
    cond_missing = [k for k in FOUR_COND if ("判定四条件" not in text) or (k + "：" not in text and k + ":" not in text)]
    # 可追溯性检测（2026-08-28 V3 报告采纳）：场景数=1 时必须给出"踩坑代价高/用户点名"依据
    trace_warn = ""
    if ("判定四条件" in text) and ("场景数：1" in text or "场景数:1" in text) and ("踩坑代价高" not in text and "用户点名" not in text):
        trace_warn = "[gate] 四条件可追溯告警：场景数=1 但未标注『踩坑代价高/用户点名』依据——按判定四条件规则，单场景固化必须有高代价或用户点名理由，请补充依据或降级为流水事实类"
    if not missing and not cond_missing and not trace_warn:
        # 三条件依据软提示（齐全通过时也检查——2026-08-28 V4 方案甲'：防裸『可移植：是』『无重复：是』声明；
        # V5 方案甲' 扩展：『边界：明确』无依据同样软提示——4/4 条件内容检测齐；
        # V6 剩余问题采纳：连续 BARE_DECLARE_LIMIT 次裸声明 → 渐进升级硬告警 rc=1）
        soft = []
        for kw in ("可移植", "无重复", "边界"):
            m = re.search(kw + r"：(是|明确)", text)
            if m:
                tail = text[m.end():m.end() + 25]
                if "（" not in tail and "(" not in tail:
                    soft.append(kw)
        if soft:
            bare_file = os.path.join(SNAP_DIR, "gate_bare_declare.json")
            today_s = datetime.date.today().isoformat()
            count = 1
            try:
                if os.path.exists(bare_file):
                    d = json.load(open(bare_file, encoding="utf-8"))
                    if d.get("date") == today_s:
                        count = d.get("count", 0) + 1
            except Exception:
                pass
            try:
                os.makedirs(SNAP_DIR, exist_ok=True)
                json.dump({"date": today_s, "count": count}, open(bare_file, "w", encoding="utf-8"))
            except Exception:
                pass
            if count >= BARE_DECLARE_LIMIT:
                try:
                    json.dump({"date": today_s, "count": 0}, open(bare_file, "w", encoding="utf-8"))
                except Exception:
                    pass
                print("[gate] 四条件硬告警：连续 %d 次裸声明『%s』（软提示已升级为硬告警 rc=1，计数已清零）——请为每个『是/明确』条件附括号依据（可移植：是（不含本机路径）/ 无重复：是（已比对 XX）/ 边界：明确（触发条件与适用边界））" % (count, "、".join(soft)))
                return 1
            print("[gate] 四条件依据软提示（第 %d/%d 次）：%s 声明为『是/明确』但未附括号依据；连续 %d 次将升级硬告警" % (count, BARE_DECLARE_LIMIT, "、".join(soft), BARE_DECLARE_LIMIT))
        print("[gate] 五步检查点齐全（第一步·归纳~第五步·校验标记全部出现）且判定四条件已显式声明")
        return 0
    if missing:
        print("[gate] 五步检查点缺失：%s" % "、".join(missing))
    if cond_missing:
        print("[gate] 判定四条件声明缺失：%s（固化响应第一步必须显式输出【判定四条件】场景数：X / 可移植：是 / 无重复：是 / 边界：明确——四条件是把判定从 LLM 内心判断变为可检测输出的程序化要求）" % "、".join(cond_missing))
    if trace_warn:
        print(trace_warn)
    print("[gate] 五步检查点强制要求：执行固化必须按五步流程逐步输出【第一步·归纳】~【第五步·校验】"
          "结构化中间结果（格式见 evolution_skill SKILL.md），缺失步骤请在补做任务中补齐并重新声明")
    return 1


if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] == "--check-5step":
        sys.exit(do_check_5step())
    if len(sys.argv) >= 3 and sys.argv[1] == "--snapshot":
        sys.exit(do_snapshot(sys.argv[2]))
    if len(sys.argv) >= 3 and sys.argv[1] == "--check":
        sys.exit(do_check(sys.argv[2]))
    if len(sys.argv) >= 2 and sys.argv[1] == "--drain":
        mn = int(sys.argv[2]) if len(sys.argv) >= 3 else 3
        sys.exit(do_drain(mn))
    print(__doc__)
    sys.exit(1)
