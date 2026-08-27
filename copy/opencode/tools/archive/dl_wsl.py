# -*- coding: utf-8 -*-
# 多镜像下载 WSL MSI 并校验完整性（msilib 可打开 = 完整）
import os, subprocess, sys

OUT = r"<用户临时目录>\wsl-installer.msi"
REPO = "microsoft/WSL"
TAG = "2.7.12"
ASSET = "wsl.2.7.12.0.x64.msi"

PROXIES = [
    ("gh-proxy.com", "https://gh-proxy.com/"),
    ("ghproxy.cc", "https://ghproxy.cc/"),
    ("ghps.cc", "https://ghps.cc/"),
    ("gh.llkk.cc", "https://gh.llkk.cc/"),
    ("ghproxy.net", "https://ghproxy.net/"),
    ("gh-proxy.net", "https://gh-proxy.net/"),
]

def verify_msi(path):
    try:
        import msilib
        db = msilib.OpenDatabase(path, msilib.MSIDBOPEN_READONLY)
        db.Close()
        return True
    except Exception as e:
        return False

for name, base in PROXIES:
    url = base + "https://github.com/{repo}/releases/download/{tag}/{asset}".format(repo=REPO, tag=TAG, asset=ASSET)
    print("[try]", name, flush=True)
    r = subprocess.run(
        ["curl.exe", "-s", "-L", "-m", "420", "--retry", "1", "-o", OUT, "-w", "%{http_code} %{size_download}", url],
        capture_output=True, text=True, timeout=600)
    print("  curl:", r.stdout.strip() or r.stderr.strip()[:100], flush=True)
    if os.path.exists(OUT) and os.path.getsize(OUT) > 200_000_000:
        print("  verifying...", flush=True)
        if verify_msi(OUT):
            print("[OK] 完整下载自", name, flush=True)
            sys.exit(0)
        else:
            print("  msilib 校验失败（损坏）", flush=True)
    else:
        print("  size too small:", os.path.getsize(OUT) if os.path.exists(OUT) else "missing", flush=True)
print("[FAIL] 所有镜像均失败", flush=True)
sys.exit(1)
