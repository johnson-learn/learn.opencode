# -*- coding: utf-8 -*-
# 给 update_skill SKILL.md 第 5 条后追加状态文件保护条目
p = r"<opencode配置目录>\skills\update_skill\SKILL.md"
with open(p, encoding="utf-8") as f:
    c = f.read()

anchor = "5. 本机状态文件："
i = c.find(anchor)
if i < 0:
    print("锚点未找到")
    raise SystemExit(1)
line_end = c.find("\n", i)
addition = "\n6. **状态文件保护（✓ 踩坑固化）**：path_map.txt 与 sync_target.txt 是本机状态文件——① 反向合入（第 0.5/4 步）复制仓库文件回本机时**必须跳过这两个文件**，否则本机真实映射会被仓库占位符版覆盖（导致 to_portable 失去映射、E: 盘真实路径泄漏进仓库、远端机器收到他机路径）；② path_convert 的 walk_convert 已内置跳过（STATE_FILES 保护）；③ 每次转换前检查 path_map.txt 完整性（值必须是真实路径，不得是 <X>=<X> 自我指涉）"
c = c[:line_end] + addition + c[line_end:]
with open(p, "w", encoding="utf-8", newline="") as f:
    f.write(c)
print("状态文件保护条目已追加")
