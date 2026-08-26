# -*- coding: utf-8 -*-
# update_skill commit message 规范：改 -F 文件方式（防中文摘要被 shell 丢弃）
import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
p = r"<opencode配置目录>\skills\update_skill\SKILL.md"
c = open(p, encoding="utf-8").read()

old = '2. `git commit -m "sync: YYYY-MM-DD <变更摘要>"`——摘要自动生成规则：'
new = ('2. `git commit`——必须含修改摘要，且用文件方式传递（防中文在 shell 层丢失）：'
       '`printf "sync: YYYY-MM-DD <变更摘要>" > /tmp/cmsg.txt && git commit -F /tmp/cmsg.txt`'
       '（历史教训：-m 直接带中文 message 经 PowerShell→wsl→bash 多层传递会丢失，提交只剩 "sync:"，他人无法知道改了什么）；摘要自动生成规则：')

if old in c:
    c = c.replace(old, new)
    open(p, "w", encoding="utf-8", newline="").write(c)
    print("commit message 规范已更新")
else:
    print("未匹配，当前相关行:")
    for line in c.split("\n"):
        if "git commit" in line:
            print(line[:120])
