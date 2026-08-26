# -*- coding: utf-8 -*-
# INSTALL.md 追加语言规则验证清单
content = """

## 语言规则验证（解决"中文提问英文回答"）

install 脚本完成并重启 opencode 后，必须验证全局规则注入：

1. 检查注册：`<工具目录>\Users\\<新用户>\\.config\\opencode\\opencode.jsonc` 含 `"instructions": ["instructions.md"]`
2. 检查文件：同目录下 `instructions.md` 存在且非空
3. **完全重启 opencode**（不是新会话，是退出进程重启——instructions 只在启动时加载）
4. 新会话用中文提问验证：回答应为中文；若仍英文 → instructions 未加载：
   - 确认 opencode.jsonc 内容无误（JSON 合法、instructions 键存在）
   - 确认无项目级 opencode.json 覆盖了全局配置
   - 排查后仍无效：把 instructions 内容合并进项目 AGENTS.md 作为临时兜底
"""
with open("/home/github/learn.opencode/copy/INSTALL.md", "a", encoding="utf-8") as f:
    f.write(content)
print("INSTALL.md 已追加语言规则验证清单")
