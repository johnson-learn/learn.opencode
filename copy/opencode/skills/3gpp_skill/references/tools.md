# 3gpp_skill 参考：🛠 工具依赖清单（移植到新机器时先逐项检查）

## 🛠 工具依赖清单（移植到新机器时先逐项检查）

| 工具 | 用途 | 本机位置/版本 | 检查命令 | 缺失时安装 |
|---|---|---|---|---|
| Pix2Text (p2t) | 公式/符号图片识别（双轨提取必备） | `<Python脚本目录>\p2t.exe` | `p2t.exe predict -h` | `pip install pix2text -i 清华源` |
| LibreOffice soffice | 文档批量转 PDF（公式核实链路） | `<LibreOffice目录>\program\soffice.com` | 见 files_skill 检查命令 | winget LibreOffice |
| Python + PyMuPDF | 页面渲染 PNG、文本搜索 | `python` + `pymupdf` | `python -c "import pymupdf, docx"` | `pip install pymupdf python-docx -i 清华源` |
| matplotlib | 结构图/走势图 SVG 生成（配图主力之一） | `python -c "import matplotlib"`（3.11+） | 同上 | `pip install matplotlib -i 清华源` |
| Mermaid CLI (mmdc) | 流程图/时序图/状态图 → SVG（配图主力之一） | `<用户AppData目录>\npm\mmdc.cmd`（node v24 + 全局包） | `mmdc.cmd --version` | `npm.cmd install -g @mermaid-js/mermaid-cli`；渲染设 `$env:PUPPETEER_EXECUTABLE_PATH` 指向系统 Chrome；PowerShell 下用 `mmdc.cmd` 非 `mmdc`（ps1 被执行策略禁） |
| PS 提取脚本 | doc/docx 文本提取 | `<用户临时目录>\opencode\extract-docx.ps1` / `extract-doc.ps1` | `Test-Path <脚本>` | 从原机复制 Temp\opencode |
| 网络抓取 | FTP 目录/下载（需 UA 头） | PowerShell `Invoke-WebRequest` / `curl.exe -A` | `curl.exe --version` | Windows 自带 |
| 本机文档库 | 本地规范（仅用户明确要求时用） | `<3GPP文档库目录>\` | `Test-Path` | 从 3GPP FTP 重新下载（流程见官网权威信息章节） |
| 本机 6G 文档 | TR 22.870/38.914 存档 | `<项目目录>\temp\6G\` | `Test-Path` | 按「FTP 访问技巧」重下 |

**移植说明**：本技能核心链路 = 文本提取 + p2t 图片识别 + soffice 转 PDF + PyMuPDF 渲染，四件套缺一不可；网络抓取与本地文档库为可选项（缺时全部走官网实时获取）。

本技能是**唯一注册入口**，聚合了 13 个 3GPP/通信子技能（位于 `modules/`，资源库不独立注册），并内嵌 NR-f40 项目验证过的工作铁律。

---

