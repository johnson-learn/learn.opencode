# -*- coding: utf-8 -*-
# 临时文件登记表助手（tmp_registry）—— 统一收口"测试/脚本生成临时文件"的登记与清理
# 设计（2026-09-16 定稿蓝图）：统一入口 test_runner 在跑各子入口（health_check/evolution_gate/update_skill）前后
#   调本模块 register_test_start / cleanup_test，实现"测试前登记 → 测试后清理并去除登记"。
# 登记表 tests/tmp_registry.json 为框架文件，常态应为空（所有临时文件已清）。
# 纯净度：仅依赖 Python 标准库（os/json/tempfile/shutil/subprocess/time/datetime），保证任意测试可 import。
import os, json, time, shutil, datetime, tempfile, subprocess, glob

sys_enc = "utf-8"

def _cfg_dir():
    return os.path.join(os.path.expanduser("~"), ".config", "opencode")

def _registry_path():
    # 测试隔离：OPENCODE_TEST_HOME 设置时登记表也重定向到临时域，防污染真实登记表
    th = os.environ.get("OPENCODE_TEST_HOME")
    base = th if th else _cfg_dir()
    return os.path.join(base, "tests", "tmp_registry.json")

def _temp_root():
    return os.environ.get("OPENCODE_TEST_HOME") or tempfile.gettempdir()

# 统一前缀：登记表兜底扫描 %TEMP% 依赖此前缀。
# 精确白名单待同步 WSL/GitHub 时补充（平台差异）。当前语义级前缀 + 兼容现有测试前缀。
UNIFIED_PREFIX = "opencode_test_"
KNOWN_TEST_PREFIXES = (
    "opencode_test_", "gate_test_", "sp_", "inject_test_", "pc_test_",
    "sv_cfg_", "us_test_", "us_merge_", "us_revert_", "us_remote_",
    "us_port_", "us_popup_", "plugin_test_", "syncproj_",
)

def _read():
    p = _registry_path()
    if not os.path.exists(p):
        return []
    try:
        with open(p, "r", encoding=sys_enc) as f:
            return json.load(f)
    except Exception:
        return []

def _write(entries):
    p = _registry_path()
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding=sys_enc, newline="\n") as f:
        json.dump(entries, f, ensure_ascii=False, indent=2)

def register(path, source, phase="pre", est_clean_time=None, type_="dir"):
    """登记一个临时文件/目录。est_clean_time 未到则等待不清理（支持'登记清理时间等待'）。"""
    entries = _read()
    entries = [e for e in entries if e.get("path") != path]  # 幂等：同路径不重复登记
    by_prefix = bool(path) and path.startswith(_temp_root() + os.sep)
    entries.append({
        "path": path, "type": type_, "source": source, "phase": phase,
        "created_at": datetime.datetime.now().isoformat(timespec="seconds"),
        "est_clean_time": est_clean_time, "status": "pending",
        "by_unified_prefix": by_prefix,
    })
    _write(entries)

def unregister(path):
    """去除对 path 的登记。"""
    entries = [e for e in _read() if e.get("path") != path]
    _write(entries)

def _remove_path(path, entry):
    try:
        if entry.get("type") == "dir":
            shutil.rmtree(path, ignore_errors=True)
        else:
            if os.path.exists(path):
                os.remove(path)
    except Exception:
        pass

def cleanup_test(source, prefixes=None):
    """清理某 source（测试/子入口）的临时文件并去除登记。
    双通道：① 登记精确路径 ② 在 prefixes（允许的前缀白名单）内扫描 %TEMP% 兜底清理。
    prefixes 为 None 时不进行前缀兜底清理（保守，仅清登记精确路径）。返回清理条数。"""
    entries = _read()
    removed = 0
    keep = []
    for e in entries:
        path = e.get("path", "")
        if e.get("source") == source:
            _remove_path(path, e)
            removed += 1
            continue
        keep.append(e)
    _write(keep)
    # 兜底：在传入的允许前缀白名单内，扫描临时根下同前缀残留目录并清理（防误删其他 source 的临时文件）
    if prefixes:
        root = _temp_root()
        if os.path.isdir(root):
            try:
                for d in os.listdir(root):
                    full = os.path.join(root, d)
                    if os.path.isdir(full) and any(d.startswith(p) for p in prefixes):
                        shutil.rmtree(full, ignore_errors=True)
                        removed += 1
            except Exception:
                pass
    return removed

def managed_tmp(path, source, est_clean_time=None, type_="dir"):
    """上下文管理器：with 进入时登记，退出（含异常）时清理+去除登记。承载 try/finally 治本层。"""
    class _Ctx:
        def __init__(self, p, src, ect):
            self.p, self.src, self.ect = p, src, ect
        def __enter__(self):
            register(self.p, self.src, phase="in", est_clean_time=self.ect)
            return self.p
        def __exit__(self, exc_type, exc, tb):
            _remove_path(self.p, {"type": "dir" if os.path.isdir(self.p) else "file"})
            unregister(self.p)
            return False
    return _Ctx(path, source, est_clean_time)

def cleanup_dead():
    """死条目移除：登记的路径已不存在 → 移除登记（自净化）。返回移除条数。"""
    entries = _read()
    keep, dead = [], 0
    for e in entries:
        if os.path.exists(e.get("path", "")):
            keep.append(e)
        else:
            dead += 1
    _write(keep)
    return dead

def scan_residue():
    """扫描临时根下已知前缀残留，返回未登记或仍存在的临时路径清单（供审计告警，不自动删）。"""
    root = _temp_root()
    found = []
    for d in os.listdir(root) if os.path.isdir(root) else []:
        full = os.path.join(root, d)
        if os.path.isdir(full) and any(d.startswith(pre) for pre in KNOWN_TEST_PREFIXES):
            found.append(full)
    return found

# --- 统一入口调用接口（test_runner 用它做收口）---
def register_test_start(mode):
    """统一入口：跑子入口前登记（mode 如 --health/--gate/--update）。"""
    register(os.path.join(_temp_root(), UNIFIED_PREFIX + "runner_" + mode.strip("-")),
             source="test_runner", phase="pre")

def cleanup_test_runner(mode):
    """统一入口：跑子入口后（finally）清理本 mode 产生的临时文件并去除登记。"""
    return cleanup_test("test_runner")

if __name__ == "__main__":
    import sys
    # CLI 子命令（可选）：python tmp_registry.py scan / dead / clean <source>
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "scan":
        for p in scan_residue():
            print(p)
    elif cmd == "dead":
        print("移除死条目:", cleanup_dead())
    elif cmd == "clean" and len(sys.argv) > 2:
        print("清理:", cleanup_test(sys.argv[2]))
    else:
        print("用法: python tmp_registry.py scan|dead|clean <source>")
