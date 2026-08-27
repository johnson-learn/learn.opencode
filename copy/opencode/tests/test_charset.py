# -*- coding: utf-8 -*-
# 字符边界规范防线测试（test_charset.py）——框架文件 CRLF/BOM/编码一致性扫描
# 背景（2026-08-27 用户定）：Windows PowerShell(GBK) ↔ Python/Node/WSL(UTF-8) 跨界易发生
#   编码/换行转换事故（LF→CRLF 破坏插件 frontmatter 解析、GBK 中文乱码等）。
#   本测试程序化扫描框架关键文件，保证 UTF-8 无 BOM + LF 行尾，health_check 必跑。
import os, sys, glob

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
CFG = os.path.join(os.path.expanduser("~"), ".config", "opencode")
pass_n, fail_n = 0, 0

def check(name, cond, extra=""):
    global pass_n, fail_n
    if cond:
        pass_n += 1
        print("  ✓ " + name)
    else:
        fail_n += 1
        print("  ✗ " + name + ("  [" + extra + "]" if extra else ""))

# 扫描范围：规则文件 + 插件 + 工具 + 测试 + 各 skill 的 SKILL.md 与 references（排除第三方 modules）
targets = []
for f in ("AGENTS.md", "instructions.md", "regedit.md", "docs-sync.md", "tools-manifest.md", "opencode.jsonc"):
    targets.append(os.path.join(CFG, f))
targets += glob.glob(os.path.join(CFG, "plugins", "*.js"))
targets += glob.glob(os.path.join(CFG, "tools", "*.py"))
targets += glob.glob(os.path.join(CFG, "tests", "*.py")) + glob.glob(os.path.join(CFG, "tests", "*.js"))
for sd in glob.glob(os.path.join(CFG, "skills", "*", "SKILL.md")) + glob.glob(os.path.join(CFG, "skills", "default", "*", "SKILL.md")):
    targets.append(sd)
targets += glob.glob(os.path.join(CFG, "skills", "**", "references", "*.md"), recursive=True)
targets += [os.path.join(CFG, "skills", "default", "evolution_skill", "evolution.md")]

targets = [t for t in targets if os.path.isfile(t)]

crlf_hits = []
bom_hits = []
undecodable = []
for fp in targets:
    try:
        raw = open(fp, "rb").read()
    except Exception:
        continue
    if raw.startswith(b"\xef\xbb\xbf"):
        bom_hits.append(fp)
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        undecodable.append(fp)
        continue
    if "\r\n" in text:
        crlf_hits.append(fp)

rel = lambda p: p.replace(CFG, r"<opencode配置目录>")
check("框架文件扫描 %d 个" % len(targets), len(targets) > 0, str(len(targets)))
check("无 CRLF 文件（LF 行尾统一）", len(crlf_hits) == 0, "、".join(rel(f) for f in crlf_hits[:5]))
check("无 BOM 文件（UTF-8 无 BOM）", len(bom_hits) == 0, "、".join(rel(f) for f in bom_hits[:5]))
check("全部可 UTF-8 解码", len(undecodable) == 0, "、".join(rel(f) for f in undecodable[:5]))

# 防护规则存在性：AGENTS.md 铁律第 9 条已固化
agents = open(os.path.join(CFG, "AGENTS.md"), encoding="utf-8", errors="replace").read()
check("AGENTS.md 含铁律第 9 条字符边界规范", "字符边界规范" in agents and "9." in agents)
check("铁律含文件化传递约定", "文件化" in agents)
check("铁律含写文件规范（encoding/newline）", "newline" in agents)

print("结果：通过 %d 项，失败 %d 项" % (pass_n, fail_n))
sys.exit(1 if fail_n else 0)
