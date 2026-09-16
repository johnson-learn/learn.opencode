# -*- coding: utf-8 -*-
# tmp_registry 守护测试：登记/去登记/清理/死条目移除/上下文管理器/前缀扫描
import os, sys, json, tempfile, importlib.util, shutil
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

TEST_TMP = tempfile.mkdtemp(prefix="opencode_test_reg_")
os.environ["OPENCODE_TEST_HOME"] = TEST_TMP  # 隔离到临时目录，防污染真实登记表
# TEST_TMP 作为隔离根存在，tmp_registry 的 _temp_root() 与登记表 base 都指向它

CFG = os.path.join(os.path.expanduser("~"), ".config", "opencode")
REG = os.path.join(CFG, "tools", "tmp_registry.py")
spec = importlib.util.spec_from_file_location("tmp_registry", REG)
r = importlib.util.module_from_spec(spec)
spec.loader.exec_module(r)

pass_n, fail_n = 0, 0
def check(name, cond):
    global pass_n, fail_n
    if cond: pass_n += 1; print("  ✓ " + name)
    else: fail_n += 1; print("  ✗ " + name)

# 登记表路径（隔离到 TEST_TMP）
regfile = r._registry_path()

# 1. register / unregister
r.register("/tmp/zzz_noexist_dir", source="t1", phase="pre")
entries = r._read()
check("register 后登记表含一条", len(entries) == 1 and entries[0]["source"] == "t1")
check("登记幂等（同路径不重复）", (r.register("/tmp/zzz_noexist_dir", source="t1"), len(r._read()))[1] == 1)
r.unregister("/tmp/zzz_noexist_dir")
check("unregister 后登记表清空", len(r._read()) == 0)

# 2. cleanup_dead 死条目移除
r.register(os.path.join(TEST_TMP, "real_dir_abc"), source="t2")
os.makedirs(os.path.join(TEST_TMP, "real_dir_abc"), exist_ok=True)
r.register(os.path.join(TEST_TMP, "ghost_dir_xyz"), source="t3")  # 幽灵（路径不存在）
os.makedirs(os.path.join(TEST_TMP, "ghost_dir_xyz"), exist_ok=True)  # 先建再删，制造死条目
shutil.rmtree(os.path.join(TEST_TMP, "ghost_dir_xyz"), ignore_errors=True)
dead = r.cleanup_dead()
check("cleanup_dead 移除幽灵死条目", dead == 1)
check("真实存在的登记保留", len(r._read()) == 1)

# 3. managed_tmp 上下文管理器（try/finally 治本）
with r.managed_tmp(os.path.join(TEST_TMP, "ctx_dir"), source="t4") as p:
    os.makedirs(p, exist_ok=True)
    check("with 内已登记", any(e.get("source") == "t4" and e.get("path") == os.path.join(TEST_TMP, "ctx_dir") for e in r._read()))
check("with 退出后路径已清理", not os.path.exists(os.path.join(TEST_TMP, "ctx_dir")))
check("with 退出后登记已去除", all(e.get("path") != os.path.join(TEST_TMP, "ctx_dir") for e in r._read()))

# 4. cleanup_test 按 source 清理
r.register(os.path.join(TEST_TMP, "srcA_dir"), source="testA")
os.makedirs(os.path.join(TEST_TMP, "srcA_dir"), exist_ok=True)
n = r.cleanup_test("testA")
check("cleanup_test 清理并去登记", n == 1 and not os.path.exists(os.path.join(TEST_TMP, "srcA_dir")))

# 5. scan_residue 前缀扫描
os.makedirs(os.path.join(TEST_TMP, "gate_test_scanme"), exist_ok=True)
os.makedirs(os.path.join(TEST_TMP, "opencode_test_scanto"), exist_ok=True)
res = r.scan_residue()
check("scan_residue 扫到已知前缀残留", any("gate_test_scanme" in p for p in res) and any("opencode_test_scanto" in p for p in res))

# 5b. 防误删精确化：_is_framework_tmp_dir 的防误删双判据（前缀 + 最小后缀）
# 拒绝过短/极简目录名（防短前缀撞非框架目录），拒绝裸前缀目录
_ok_len1 = r._is_framework_tmp_dir("gate_test_abcd1234")
_ok_len2 = r._is_framework_tmp_dir("sp_abcd1234")
_check_no1 = r._is_framework_tmp_dir("sp_a")          # 前缀后仅 1 字符，不足 MIN_SUFFIX=3
_check_no2 = r._is_framework_tmp_dir("us_ab")         # 前缀后仅 2 字符
_check_no3 = r._is_framework_tmp_dir("gate_test_")    # 裸前缀目录（无后缀）
_check_no4 = r._is_framework_tmp_dir("microsoft_cache")  # 非框架前缀
check("防误删：有效后缀目录被识别为框架临时目录", _ok_len1 and _ok_len2)
check("防误删：短前缀（后缀<MIN_SUFFIX）不被误判", (not _check_no1) and (not _check_no2) and (not _check_no3))
check("防误删：非框架前缀目录不被误判", not _check_no4)

# 6. 登记表文件存在且为列表结构
check("登记表文件存在且初态为列表", os.path.exists(regfile) and isinstance(r._read(), list))

# 清理隔离目录
shutil.rmtree(TEST_TMP, ignore_errors=True)

print("\n结果：通过 %d 项，失败 %d 项" % (pass_n, fail_n))
sys.exit(1 if fail_n else 0)
