# files_skill 参考：🛠 工具依赖清单（移植到新机器时先逐项检查）

## 🛠 工具依赖清单（移植到新机器时先逐项检查）

| 工具 | 用途 | 本机位置/版本 | 检查命令 | 缺失时安装 |
|---|---|---|---|---|
| Python 3.12 | 一切脚本基础 | `python` | `python --version` | python.org 安装（勾选 PATH） |
| Pix2Text (p2t) | 公式/版面 OCR（核心） | `<Python脚本目录>\p2t.exe` | `p2t.exe predict -h` | `pip install pix2text -i 清华源`（首次跑自动下模型 ~1GB 到 %APPDATA%\pix2text 等） |
| pandoc | md⇄docx/公式转 OMML | pypandoc_binary 内嵌 | `python -c "import pypandoc; print(pypandoc.get_pandoc_path())"` | `pip install pypandoc_binary -i 清华源` |
| LibreOffice | 批量 doc/docx/pptx→PDF | `<LibreOffice目录>\program\soffice.com`（26.2.5） | `soffice.com --headless -env:UserInstallation=file:///<工具目录>Temp/LO --version` | winget `TheDocumentFoundation.LibreOffice`（离线包放 <离线安装包目录> 同法） |
| MS Office | Word/PPT COM 生成 docx/pptx | Office 16 | `New-Object -ComObject Word.Application` | — |
| Python 文档库 | docx/pptx/xlsx/pdf 处理 | python-docx/python-pptx/openpyxl/pypdf/pdfplumber/PyMuPDF/matplotlib/PIL/chardet/pyzbar/opencv/imageio-ffmpeg | `python -c "import docx, pptx, openpyxl, pypdf, pdfplumber, pymupdf, matplotlib, PIL, chardet, pyzbar, cv2, imageio_ffmpeg"` | `pip install python-docx python-pptx openpyxl pypdf pdfplumber pymupdf matplotlib pillow chardet pyzbar opencv-python imageio-ffmpeg -i 清华源` |
| Chrome | headless 校验 HTML/JS | `<Chrome目录>\chrome.exe` | `Test-Path` | — |
| 本机 PS 脚本 | doc/docx 提取、OCR、页面校验 | `<用户临时目录>\opencode\*.ps1`（extract-docx/doc、ocr、check-*） | `Test-Path <脚本>` | 从原机复制整套 Temp\opencode |
| node+npx | LobeHub market-cli | npx 缓存 `06aaad52133b3ed7` 下 cli.js | `& node <cli.js> --help` | `npx -y @lobehub/market-cli`（首次拉取） |
| Mermaid CLI (mmdc) | 流程图/时序图/状态图 → SVG（示意图绘制主力） | `<用户AppData目录>\npm\mmdc.cmd`（node v24 + 全局包） | `mmdc.cmd --version` | `npm.cmd install -g @mermaid-js/mermaid-cli`（渲染用系统 Chrome：设环境变量 `PUPPETEER_EXECUTABLE_PATH=<Chrome目录>\chrome.exe`；PowerShell 下须调 `mmdc.cmd` 而非 `mmdc`，因 ps1 被执行策略禁） |
| 未装（大件） | LaTeX 引擎 / tesseract / whisper | — | — | 超 200M 需用户同意 |

**移植检查脚本**（一键探测）：把上表「检查命令」列逐条跑一遍，缺什么装什么；p2t 与 pandoc 是本技能的两大核心依赖，缺一不可。

本技能是**唯一注册入口**，聚合了 104 个文档处理子技能（位于 `modules/` 子目录，均为参考资源库，不独立注册）。

---

