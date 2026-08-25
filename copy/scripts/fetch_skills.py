# -*- coding: utf-8 -*-
# 批量从 GitHub（经 ghproxy 镜像）下载 skill 仓库并安装到全局 skill modules
import io, os, re, shutil, subprocess, sys, tarfile, zipfile

SKILLS_ROOT = r"C:\Users\job_p\.config\opencode\skills"
TMP = r"C:\Users\job_p\AppData\Local\Temp\opencode\skill-fetch"
os.makedirs(TMP, exist_ok=True)

# (github repo, 目标全局 skill 名, 提取过滤词列表[可为空=全量])
PLAN = [
    ("claude-office-skills/skills", "files_skill", []),
    ("jimliu/baoyu-skills", "files_skill", ["translate", "markdown", "slide", "x-"]),
    ("tanis90/pdf-converter-mineru", "files_skill", []),
    ("firecrawl/anydoc", "files_skill", []),
    ("seefreed/skills", "files_skill", ["en-to-zh"]),
    ("wshuyi/translate-pdf-skill", "files_skill", []),
    ("yrom/arxiv-paper-translator", "files_skill", []),
    ("shino369/claude-code-personal-workspace", "files_skill", ["translation"]),
    ("deusyu/translate-book", "files_skill", []),
    ("openai/skills", "files_skill", ["pdf"]),
    ("github/awesome-copilot", "files_skill", ["pdftk", "markdown-file-index"]),
    ("lllllllama/rigorpilot-skills", "find_skill", []),
    ("inference-sh/skills", "find_skill", ["web-search"]),
    ("parallel-web/parallel-agent-skills", "find_skill", []),
    ("199-biotechnologies/claude-deep-research-skill", "find_skill", []),
    ("imbad0202/academic-research-skills", "find_skill", []),
    ("firecrawl/firecrawl-workflows", "find_skill", []),
    ("lugasia/3gpp-skill", "3gpp_skill", []),
    ("kharlamenkodev/5g-nr-3gpp-skills", "3gpp_skill", ["mac"]),
    ("stanfish06/skillquarium", "3gpp_skill", ["telecommunications", "communications", "rf-microwave"]),
    ("nobodyonlyc/skills", "3gpp_skill", ["ntn"]),
    ("NousResearch/hermes-agent", "files_skill", ["ocr-and-documents", "pdf", "nano-pdf", "whisper"]),
    ("garrytan/gstack", "files_skill", ["make-pdf"]),
    ("deepseek-ai/deepseek-harness", "files_skill", ["translate"]),
]

def sh(args):
    return subprocess.run(args, capture_output=True, text=True, timeout=300)

def fetch_tarball(repo, branch="main"):
    url = f"https://ghproxy.net/https://github.com/{repo}/archive/refs/heads/{branch}.tar.gz"
    out = os.path.join(TMP, repo.replace("/", "_") + ".tar.gz")
    r = subprocess.run(["curl.exe", "-s", "-L", "-m", "180", url, "-o", out],
                       capture_output=True, text=True, timeout=300)
    if not os.path.exists(out) or os.path.getsize(out) < 5000:
        return None
    return out

def extract_and_install(repo, target, filters):
    tgz = fetch_tarball(repo)
    if not tgz:
        print(f"[FAIL download] {repo}")
        return
    extract_dir = os.path.join(TMP, "extract-" + repo.replace("/", "_"))
    shutil.rmtree(extract_dir, ignore_errors=True)
    os.makedirs(extract_dir, exist_ok=True)
    with tarfile.open(tgz, "r:gz") as t:
        t.extractall(extract_dir)
    # 找到所有 SKILL.md，父目录即 skill 模块
    skills_found = []
    for root, dirs, files in os.walk(extract_dir):
        if "SKILL.md" in files:
            skills_found.append(root)
    # 过滤
    picked = []
    for sdir in skills_found:
        name = os.path.basename(sdir).lower()
        if filters and not any(f in name for f in filters):
            continue
        picked.append(sdir)
    if not picked:
        print(f"[none] {repo}: found {len(skills_found)} skills, all filtered")
        shutil.rmtree(extract_dir, ignore_errors=True)
        return
    # 跳过 skill 文档/模板类（含 SKILL.md 但属于示例的）
    target_root = os.path.join(SKILLS_ROOT, target, "modules")
    os.makedirs(target_root, exist_ok=True)
    owner_repo = repo.replace("/", "-")
    for sdir in picked:
        mod_name = owner_repo + "-" + os.path.basename(sdir)
        dest = os.path.join(target_root, mod_name)
        if os.path.exists(dest):
            shutil.rmtree(dest, ignore_errors=True)
        shutil.copytree(sdir, dest)
        for root2, dirs2, files2 in os.walk(dest):
            for f in files2:
                if f.upper() == "SKILL.MD":
                    os.rename(os.path.join(root2, f), os.path.join(root2, "GUIDE.md"))
        print(f"[ok] {repo} -> {target}/modules/{mod_name}")
    shutil.rmtree(extract_dir, ignore_errors=True)

if __name__ == "__main__":
    only = sys.argv[1] if len(sys.argv) > 1 else None
    for repo, target, filters in PLAN:
        if only and only not in repo:
            continue
        try:
            extract_and_install(repo, target, filters)
        except Exception as e:
            print(f"[error] {repo}: {e}")
    print("=== done ===")
