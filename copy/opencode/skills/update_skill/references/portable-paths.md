# update_skill 参考：路径可移植层（双向同步必须执行的转换）

## 路径可移植层（双向同步必须执行的转换）

> 仓库（GitHub）里的文件必须保持**占位符形式**（可移植）；本机源文件保持**真实路径**（本机使用）。双向同步时自动转换，禁止把本机真实路径推上 GitHub。

### 占位符体系
- **自动类**（转换时自动推导，无需用户填写）：`<用户目录>`、`<opencode配置目录>`、`<opencode数据目录>`、`<用户临时目录>`、`<用户AppData目录>`、`<用户桌面目录>`、`<WSL用户映射>`、`<Python脚本目录>`
- **工具类**（安装脚本自动探测本机实际安装目录并写入 path_map.txt，无需用户填写）：`<LibreOffice目录>`（找 soffice.com）、`<Chrome目录>`（找 chrome.exe）、`<Node目录>`（PATH 中 node 位置）、`<工具目录>`（找 w64devkit\bin\gcc.exe）、`<WSL安装目录>`（注册表 Lxss BasePath）
- **数据类**（安装脚本交互选择：直接回车=默认目录，输入路径=用户定制；存于 path_map.txt）：`<资料目录>`（默认 `D:\opencode\doc\default`）、`<3GPP文档库目录>`（默认 `D:\opencode\doc\3gpp`）、`<项目目录>`（默认 `D:\opencode\project\default`）、`<源码目录>`（默认 `D:\opencode\code\default`）、`<离线安装包目录>`（默认 `D:\opencode\tool\default`）

### 转换流程（集成进同步三环节）
1. **本机 → 仓库**：合入前先对仓库文件跑 `python3 <仓库>/copy/scripts/path_convert.py to_portable --home="<本机用户目录正斜杠>" <仓库>/copy/opencode`（及 scripts 目录）——把本机合入内容中的真实路径转为占位符
2. **仓库 → 本机**（反向合入，第 0.5 步与第 4 步均适用）：把仓库文件复制回本机后，对本机文件跑 `python3 <仓库>/copy/scripts/path_convert.py to_local --home="<本机用户目录正斜杠>" <本机opencode配置目录>`（及 Temp\opencode）——把占位符转回本机真实路径
3. **远端路径技巧的防御（关键）**：远端文件全部是占位符形式，反向合入到本机时**必须经 to_local 转换**，否则本机 skill 出现占位符导致工具路径失效；to_local 结束自动输出"残留未转换占位符"清单——**出现未知占位符（远端新定义的填写类）时，提示用户补充本机 path_map.txt 后重跑 to_local，不得带着占位符继续使用**
4. 转换前后各跑一次 `grep -rl "<本机用户名>" <目录>`（正向）与占位符残留扫描（反向）残留检查，为 0 才可提交/合入
5. 本机状态文件：`<opencode配置目录>\skills\update_skill\path_map.txt`（填写类占位符→本机真实路径映射，**不进仓库**，同步排除）；远端新增占位符时同步更新该文件
6. **状态文件保护（✓ 踩坑固化）**：path_map.txt 与 sync_target.txt 是本机状态文件——① 反向合入（第 0.5/4 步）复制仓库文件回本机时**必须跳过这两个文件**，否则本机真实映射会被仓库占位符版覆盖（导致 to_portable 失去映射、E: 盘真实路径泄漏进仓库、远端机器收到他机路径）；② path_convert 的 walk_convert 已内置跳过（STATE_FILES 保护，含 path_convert.py 自身，防 to_local 自毁——其源码含占位符键）；③ 每次转换前检查 path_map.txt 完整性（值必须是真实路径，不得是 `<X>=<X>` 自我指涉）；④ 同理会话内先跑 to_local 再核对 path_map.txt 键是否原样，**勿删该跳过逻辑**；⑤ **正向同步 cp（本机→仓库）同样必须显式跳过这两个文件**——`cp -r skills/*` 会把他机真实映射带进仓库工作树（虽被 .gitignore 挡住提交，但污染工作树、可能被其它机器反向合入时误复制）
7. **教学列表保护（✓ 本机实测踩坑）**：本技能「占位符体系」章节中列举占位符名的三行（自动类/工具类/数据类枚举）会被 to_local 转换为本机真实路径，使教学文档失真——反向合入后**按仓库版本恢复这三行**（占位符名必须保持原样，不能变成本机路径）；**to_portable 同样会误伤**：教学行默认值（如 `D:\opencode\doc\default`）若与某机 path_map 值前缀相同，会被转成自指涉（`<资料目录>\default`）——正向提交前必须 git diff 检查教学行，被误伤即恢复仓库版

---

