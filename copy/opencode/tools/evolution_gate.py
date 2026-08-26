# -*- coding: utf-8 -*-
# 进化门禁脚本（evolution gate）——把"必须执行的进化步骤"确定性化
# 用法：
#   python evolution_gate.py --snapshot <会话ID>   会话开始时：记录规则文件状态快照
#   python evolution_gate.py --check <会话ID>      会话结束时：检测改动→自动补流水→自动跑测试
# 设计（用户 2026-08-26 定）：机制步骤（流水落盘/测试执行/一致性校验）由本脚本 100% 确定性执行，
#   不依赖模型自觉；智能步骤（经验归纳/归属判断）仍由模型完成，脚本输出待补充清单。
import os, sys, json, subprocess, hashlib, datetime, tempfile

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
CFG = os.path.join(os.path.expanduser("~"), ".config", "opencode")
TOOLS = os.path.join(CFG, "tools")
TESTS = os.path.join(CFG, "tests")
LOG = os.path.join(CFG, "skills", "default", "evolution_skill", "evolution_log.txt")
SNAP_DIR = os.path.join(tempfile.gettempdir(), "opencode_gate")
WATCH_EXT = (".md", ".txt", ".py", ".js", ".jsonc")
IGNORE_DIRS = ("__pycache__", "node_modules", ".git", "archive")
STATE_FILES = ("path_map.txt", "sync_target.txt")

WATCH_ROOTS = [os.path.join(CFG, "skills"), os.path.join(CFG, "plugins"), os.path.join(CFG, "tools")]
WATCH_FILES = [os.path.join(CFG, f) for f in ("AGENTS.md", "instructions.md", "regedit.md", "tools-manifest.md")]


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
    if not changed:
        print("[gate] 无规则文件改动，门禁通过（无需固化）")
        os.remove(sp)
        return 0
    print("[gate] 检测到 %d 个规则文件改动：" % len(changed))
    for fp in changed:
        print("  -", fp.replace(CFG, "<opencode配置目录>"))
    # 1. 流水自动追加（若本会话模型未正常追加记录）
    log_size_now = os.path.getsize(LOG) if os.path.exists(LOG) else 0
    appended = False
    if log_size_now == snap["log_size"]:
        entry = ("[%s] 会话自动门禁（%s） → 机制步骤已由 evolution_gate 脚本确定性执行：本会话改动 %d 个规则文件（清单见下）；"
                 "智能归纳待模型补充\n" % (datetime.date.today().isoformat(), sid, len(changed)))
        entry += "".join("- " + fp.replace(CFG, "<opencode配置目录>") + "\n" for fp in changed)
        with open(LOG, "a", encoding="utf-8") as f:
            f.write(entry + "\n")
        appended = True
        print("[gate] 流水骨架已自动追加（模型未记录时兜底）")
    else:
        print("[gate] 流水已有本会话记录（模型已正常追加），不重复")
    # 2. 按改动类型自动跑对应测试
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
    if any(fp.endswith("regedit.md") for fp in changed):
        run_test("test_regedit", [py, os.path.join(TESTS, "test_regedit.py")])
    if any("plugins" in fp for fp in changed):
        run_test("test_plugin", ["node", os.path.join(TESTS, "test_plugin.js")])
    run_test("test_evolution_consistency", [py, os.path.join(TESTS, "test_evolution_consistency.py")])
    print("[gate] 自动测试结果：")
    for name, (rc, tail) in results.items():
        print("  %s: rc=%s | %s" % (name, rc, tail))
    # 3. 待模型补充清单
    print("[gate] 待模型补充（智能部分）：五步流程第 1-3 步（归纳经验/归属判定/edit 固化到可执行载体）")
    print("[gate] 机器完成：流水兜底追加=%s、对应测试已自动执行" % ("是" if appended else "否(模型已记录)"))
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


if __name__ == "__main__":
    if len(sys.argv) >= 3 and sys.argv[1] == "--snapshot":
        sys.exit(do_snapshot(sys.argv[2]))
    if len(sys.argv) >= 3 and sys.argv[1] == "--check":
        sys.exit(do_check(sys.argv[2]))
    if len(sys.argv) >= 2 and sys.argv[1] == "--drain":
        mn = int(sys.argv[2]) if len(sys.argv) >= 3 else 3
        sys.exit(do_drain(mn))
    print(__doc__)
    sys.exit(1)
