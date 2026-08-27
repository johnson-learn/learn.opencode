# -*- coding: utf-8 -*-
# 同步推送脚本（sync_push.py）——推送门禁脚本化：未经用户弹窗确认，脚本直接拒绝 commit/push
# 用法：python sync_push.py <确认标记文件> <git仓库目录> <commit消息文件>
#   确认标记文件由模型在用户弹窗选择"推送"后写入（含时间戳）；推送成功后自动清除标记
# 2026-08-27 修复：WSL 仓库（路径含 wsl.localhost）必须走 WSL 内 git 执行——Windows git 经 UNC 访问
#   WSL 仓库有三个坑：① SSH 无 WSL 密钥致 push 失败（Host key verification failed）② commit author 用
#   Windows git 身份与历史 WSL 提交者不一致 ③ filemode 语义差异（drvfs 权限位与 ext4 不同）
import os, sys, subprocess, json, datetime
sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def is_wsl_repo(repo):
    return "wsl.localhost" in repo.replace("\\", "/").lower()


def to_wsl_path(repo):
    # \\wsl.localhost\Ubuntu\home\... -> /home/...
    parts = repo.replace("\\", "/").strip("/").split("/")
    try:
        i = parts.index("wsl.localhost")
        return "/" + "/".join(parts[i + 2:])
    except ValueError:
        return repo


def sh_quote(s):
    return "'" + s.replace("'", "'\\''") + "'"


def run_git(args, repo):
    if is_wsl_repo(repo):
        wp = to_wsl_path(repo)
        inner = "git -C %s %s" % (sh_quote(wp), " ".join(sh_quote(a) for a in args))
        return subprocess.run(["wsl", "-d", "Ubuntu", "-e", "bash", "-c", inner],
                              capture_output=True, text=True)
    return subprocess.run(["git", "-C", repo] + args, capture_output=True, text=True)


def main():
    if len(sys.argv) < 4:
        print("用法: python sync_push.py <确认标记文件> <git仓库目录> <commit消息文件>")
        return 2
    marker, repo, msgfile = sys.argv[1], sys.argv[2], sys.argv[3]
    if not os.path.exists(marker):
        print("[sync_push] 拒绝推送：未找到用户弹窗确认标记（%s）。" % marker)
        print("[sync_push] 铁律：update_skill 第五步必须先弹窗让用户确认，确认后才能推送。")
        return 2
    try:
        data = json.load(open(marker, encoding="utf-8"))
        choice = data.get("choice", "")
        if choice != "push":
            print("[sync_push] 拒绝推送：确认标记选择为 '%s' 而非 'push'。" % choice)
            return 2
        print("[sync_push] 用户确认有效（%s 选择推送，确认时间 %s）" % (data.get("user", "user"), data.get("time", "未知")))
    except Exception as e:
        print("[sync_push] 确认标记无效：" + str(e))
        return 2
    if not os.path.exists(msgfile):
        print("[sync_push] commit 消息文件不存在：" + msgfile)
        return 2
    # 推送前可移植性残留快速检查（本机特征词）
    r = run_git(["grep", "-I", "-l", "-e", os.path.basename(os.path.expanduser("~"))], repo)
    if r.returncode == 0 and r.stdout.strip():
        hits = r.stdout.strip().splitlines()
        if any("path_map" not in h and "archive" not in h for h in hits):
            print("[sync_push] 警告：待提交内容含本机用户名特征（可能缺可移植性转换），仍继续推送前请人工复核：")
            for h in hits[:5]:
                print("  " + h)
    # WSL 分支下把消息文件路径也转成 WSL 路径（commit -F 在 WSL 内读文件）
    if is_wsl_repo(repo):
        msgfile = to_wsl_path(msgfile)
    # git add / commit / push
    steps = [
        (["add", "-A"], "add"),
        (["commit", "-q", "-F", msgfile], "commit"),
        (["push", "origin", "main"], "push"),
    ]
    for cmd, name in steps:
        r = run_git(cmd, repo)
        if r.returncode != 0 and name != "commit":
            print("[sync_push] %s 失败：%s" % (name, (r.stderr or r.stdout).strip()[-200:]))
            if name == "push":
                print("[sync_push] 本地已提交，待推送（不丢弃成果）")
                return 3
            return 1
        if name == "commit" and r.returncode != 0:
            err = (r.stderr or "").strip()
            if "nothing to commit" in err:
                print("[sync_push] 无改动可提交")
                os.remove(marker)
                return 0
            print("[sync_push] commit 失败：" + err[-200:])
            return 1
    # 清除确认标记（一次确认只允许一次推送）
    os.remove(marker)
    print("[sync_push] 推送成功，确认标记已清除（下次推送需重新弹窗确认）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
