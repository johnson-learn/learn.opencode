---
name: files_skill
description: 综合文件识别与文档处理统一接口技能（全局 skill，仅显式触发，不靠关键词自动调用）。Use ONLY when 用户消息显式包含 "files_skill：" 或 "files_skill:"，或以 "files_skill&"、"files_skill " 与其他技能名并列后跟冒号——冒号后为用户任务。加载后执行任务：识别、读取、提取或处理任何文件资料（PDF、Word/docx、PPT/pptx、Excel/xlsx、图片、Markdown、EPUB、HWP 等），包括图片识别（OCR）、公式识别（转 LaTeX）、文字提取、流程图识别（转 Mermaid）、表格提取、文档转换、翻译、公文写作等。普通消息仅提及 PDF/Word 等关键词但无 "files_skill：" 前缀时，不调用本技能。
---

# files_skill —— 统一文件识别接口

## 🛠 工具依赖清单（移植到新机器时先逐项检查）

| 工具 | 用途 | 本机位置/版本 | 检查命令 | 缺失时安装 |
|---|---|---|---|---|
| Python 3.12 | 一切脚本基础 | `python` | `python --version` | python.org 安装（勾选 PATH） |
| Pix2Text (p2t) | 公式/版面 OCR（核心） | `C:\Users\job_p\AppData\Local\Programs\Python\Python312\Scripts\p2t.exe` | `p2t.exe predict -h` | `pip install pix2text -i 清华源`（首次跑自动下模型 ~1GB 到 %APPDATA%\pix2text 等） |
| pandoc | md⇄docx/公式转 OMML | pypandoc_binary 内嵌 | `python -c "import pypandoc; print(pypandoc.get_pandoc_path())"` | `pip install pypandoc_binary -i 清华源` |
| LibreOffice | 批量 doc/docx/pptx→PDF | `D:\Program Files\LibreOffice\LibreOfficePortable\App\libreoffice\program\soffice.com`（26.2.4 便携版） | `soffice.com --headless -env:UserInstallation=file:///C:/Temp/LO --version` | 便携版已装于 D:\Program Files\LibreOffice\LibreOfficePortable；离线包见 D:\opencode\copy\tool |
| MS Office | Word/PPT COM 生成 docx/pptx | Office 16 | `New-Object -ComObject Word.Application` | — |
| Python 文档库 | docx/pptx/xlsx/pdf 处理 | python-docx/python-pptx/openpyxl/pypdf/pdfplumber/PyMuPDF/matplotlib/PIL/chardet/pyzbar/opencv/imageio-ffmpeg | `python -c "import docx, pptx, openpyxl, pypdf, pdfplumber, pymupdf, matplotlib, PIL, chardet, pyzbar, cv2, imageio_ffmpeg"` | `pip install python-docx python-pptx openpyxl pypdf pdfplumber pymupdf matplotlib pillow chardet pyzbar opencv-python imageio-ffmpeg -i 清华源` |
| Chrome | headless 校验 HTML/JS | `C:\Program Files\Google\Chrome\Application\chrome.exe` | `Test-Path` | — |
| 本机 PS 脚本 | doc/docx 提取、OCR、页面校验 | `C:\Users\job_p\AppData\Local\Temp\opencode\*.ps1`（extract-docx/doc、ocr、check-*） | `Test-Path <脚本>` | 从原机复制整套 Temp\opencode |
| node+npx | LobeHub market-cli | npx 缓存 `06aaad52133b3ed7` 下 cli.js | `& node <cli.js> --help` | `npx -y @lobehub/market-cli`（首次拉取） |
| Mermaid CLI (mmdc) | 流程图/时序图/状态图 → SVG（示意图绘制主力） | `C:\Users\job_p\AppData\Local\Programs\nodejs\mmdc.cmd`（node v24 + 全局包） | `mmdc.cmd --version` | `npm.cmd install -g @mermaid-js/mermaid-cli`（渲染用系统 Chrome：设环境变量 `PUPPETEER_EXECUTABLE_PATH=C:\Program Files\Google\Chrome\Application\chrome.exe`；PowerShell 下须调 `mmdc.cmd` 而非 `mmdc`，因 ps1 被执行策略禁） |
| 未装（大件） | LaTeX 引擎 / tesseract / whisper | — | — | 超 200M 需用户同意 |

**移植检查脚本**（一键探测）：把上表「检查命令」列逐条跑一遍，缺什么装什么；p2t 与 pandoc 是本技能的两大核心依赖，缺一不可。

本技能是**唯一注册入口**，聚合了 104 个文档处理子技能（位于 `modules/` 子目录，均为参考资源库，不独立注册）。

## 通用输出规则（全部任务遵守）

- **语言跟随提问**：用户以何种语言提问，思考、回答、输出就以何种语言（中文提问→中文回答，英文提问→英文回答）；协议原文、配置项名称、原始字段、代码、命令等必要原文保持原样不翻译
- **含"输出"二字 → HTML 交付**：提问中出现"输出"二字时，最终答案必须以 HTML 文件输出（MathJax 渲染公式、规范排版，head 模板见「公式标准显示」章节），内容详细、不限字数篇幅；HTML 保存到提问时所在工作目录并浏览器打开（用户另行指定目录时按用户指定）

## 处理流程

1. 确认目标文件类型与任务（识别/提取/转换/创建）
2. 按下表路由到对应子技能，**先阅读 `modules/<identifier>/GUIDE.md` 再按其说明执行**
3. 子技能内脚本路径均以 `modules/<identifier>/` 为基准
4. 涉及外部 API（付费服务）时，必须先征得用户同意

## 路由表（按任务）

### 图片识别 / OCR / 流程图 / 公式
| 任务 | 子技能（modules 下目录） | 说明 |
|---|---|---|
| 图片 OCR 转 Markdown（无本地 OCR 时） | `hugohe3-ppt-master-ocr_image_to_markdown` | 用多模态视觉直接转录图片中的文本/表格/结构为 Markdown |
| 批量/通用文件转 Markdown（含图片 OCR、音频转写） | `k-dense-ai-claude-scientific-skills-markitdown` | 微软 MarkItDown：PDF/DOCX/PPTX/XLSX/图片/音频/HTML/EPUB → Markdown |
| 各种文件转 Markdown（替代方案） | `steipete-agent-scripts-markdown-converter` | markitdown 同类 |
| 扫描 PDF OCR 成可搜索 PDF | `anthropics-skills-pdf` | 见其 GUIDE.md 中 OCR 章节 |
| 公式识别（图片→LaTeX） | 见下方「公式识别」章节 | 多模态视觉 + 手写/打印公式转录 |
| 流程图识别（图片→Mermaid/文本） | 见下方「流程图识别」章节 | 多模态视觉 + 结构归纳 |

### PDF
| 任务 | 子技能（modules 下目录） |
|---|---|
| PDF 全能（读/提取/合并/拆分/旋转/水印/表单/加解密/OCR） | `anthropics-skills-pdf`（首选） |
| PDF 文本提取、创建、合并 | `shareai-lab-learn-claude-code-pdf` |
| PDF 渲染视觉检查 + reportlab/pdfplumber/pypdf | `openai-skills-pdf` |
| 排版美观的 PDF 生成（报告/简历/提案）、填表单 | `minimax-ai-skills-minimax-pdf` |
| 提取文本表格、填表单、合并 | `davila7-claude-code-templates-pdf-processing`、`composiohq-awesome-claude-skills-pdf` |
| PDF 翻译成中文（保留排版） | `openclaw-skills-pdf-translate` |
| PDF 转 Markdown（含扫描件 OCR） | `duc01226-easyplatform-pdf-to-markdown` |
| PDF 转可编辑 Word | `openclaw-skills-pdf-to-docx` |

### Word / DOCX
| 任务 | 子技能（modules 下目录） |
|---|---|
| Word 全能（创建/编辑/修订/批注/目录/页码，docx-js + XML + pandoc） | `anthropics-skills-docx`（首选） |
| OpenXML SDK 三管线（新建/填写/模板格式化 + XSD 校验） | `minimax-ai-skills-minimax-docx` |
| 读取/生成 Word，跨平台 | `openclaw-skills-word-docx` |
| 中文 Word 处理（中文触发词友好） | `openclaw-skills-docx-cn` |
| python-docx 精确格式控制/批量 | `comeonoliver-skillshub-docx-format-skill` |

### PPTX / 演示文稿
| 任务 | 子技能（modules 下目录） |
|---|---|
| PPT 全能（创建/解析/编辑/合并拆分/模板/备注/批注） | `anthropics-skills-pptx`（首选） |
| 从零生成（封面/TOC/章节/总结页）、编辑、提取 | `minimax-ai-skills-pptx-generator` |
| 创建/编辑幻灯片、布局、备注 | `davila7-claude-code-templates-pptx` |
| 从大纲/数据生成 PPT，模板/图表/AI 图 | `openclaw-skills-pptx-creator` |

### Excel / 电子表格
| 任务 | 子技能（modules 下目录） |
|---|---|
| 分析、透视表、图表 | `davila7-claude-code-templates-excel-analysis` |
| 读写编辑 .xlsx、格式化、导出 CSV/JSON/MD | `openclaw-skills-excel` |
| 中文 Excel 处理（公式、图表） | `openclaw-skills-xlsx-cn` |
| xlwings 操控实时 Excel | `openclaw-skills-excel-automation` |

### Markdown 转换
| 任务 | 子技能（modules 下目录） |
|---|---|
| Markdown → Word/PPT/PDF（Pandoc） | `openclaw-skills-md-to-office` |
| Obsidian 格式 Markdown | `kepano-obsidian-skills-obsidian-markdown` |
| Markdown → HTML（GFM/CommonMark） | `github-awesome-copilot-markdown-to-html` |

### 翻译
| 任务 | 子技能（modules 下目录） | 说明 |
|---|---|---|
| 通用专业翻译（英⇄中、多语言互译、本地化，模型原生能力，免费无 API） | `foreveryh-claude-skills-tutorial-translator`（首选） | 保留技术术语、代码块、Markdown 格式、语气 |
| 英译中专用 | `seefreed-skills-en-to-zh-translator` | skills.sh 来源，直接对口英→中 |
| 中文翻译工作流（宝玉出品） | `jimliu-baoyu-skills-baoyu-translate` | 中文社区技能 |
| 翻译专家方法论 | `shino369-claude-code-personal-workspace-translation-expertise` | 术语表/风格一致性 |
| 整书翻译 | `deusyu-translate-book-translate-book-main` | 章节化长文本翻译 |
| PDF 翻译成中文（保留排版，weasyprint CJK） | `openclaw-skills-pdf-translate` | 逐节翻译生成 Markdown + PDF |
| PDF 翻译（提取→翻译→Markdown） | `forceinjection-ai-fundermentals-pdf-translator` | 通用目标语言 |
| PDF 翻译（wshuyi 版） | `wshuyi-translate-pdf-skill-translate-pdf` | 备选方案 |
| arXiv 论文翻译（含 PDF 转 PNG 预处理） | `yrom-arxiv-paper-translator-arxiv-paper-translator`、`yrom-arxiv-paper-translator-convert-pdf-to-png` | 学术论文场景 |
| 图片翻译（OCR 提取+翻译+去字，需 `TRANSLATEIMAGE_API_KEY` 付费 API，先确认） | `openclaw-skills-translate-image` | translateimage.io，漫画/截图场景 |

### 综合 / 特殊场景
| 任务 | 子技能（modules 下目录） |
|---|---|
| **claude-office-skills 系列（43 个，GitHub 办公技能大合集）**：batch-convert、batch-processor、doc-parser、doc-pipeline、docx-manipulation、excel-automation、file-organizer、md-to-office、office-mcp、office-to-md、pdf-compress/converter/extraction/form-filler/merge-split/ocr/to-docx/watermark、pptx-manipulation、smart-ocr、table-extractor、xlsx-manipulation、chart-designer、diagram-creator、layout-analyzer、template-engine、transcription-automation、html-slides、ai-slides、report-generator 等 | `claude-office-skills-skills-<名称>` |
| **baoyu 中文系列（6 个）**：translate、format-markdown、markdown-to-html、url-to-markdown、slide-deck、danger-x-to-markdown | `jimliu-baoyu-skills-baoyu-*` |
| Word/Excel/PPT 一体化 MCP 服务 | `openclaw-skills-office-mcp` |
| docx/pdf/pptx/xlsx 四格式统一处理 | `travisjneuman-.claude-document-skills` |
| 文档处理/转换/OCR/提取/签署/填表（Nutrient DWS API，需 API Key，先确认） | `affaan-m-everything-claude-code-nutrient-document-processing` |
| 办公全流程 + LibreOffice | `sickn33-antigravity-awesome-skills-office-productivity` |
| 韩文 HWP/HWPX 文档 | `seocholaw-hwpx-legal-skill` |
| 智能文档解析（结构化提取、发票/表单、批量分类，LandingAI，需 API Key，先确认） | `andrewyng-context-hub-document-extraction` |
| 中文公文写作（决议/通知/报告等规范格式 + Word 导出） | `zhaohui-yang-official-document-drafting` |
| 文档协作写作（结构化流程：上下文转移→迭代润色→读者验证，Anthropic 官方） | `anthropics-skills-doc-coauthoring` |
| 读 arXiv 论文（按 URL 解析结构、公式、方法） | `karpathy-nanochat-read-arxiv-paper` |
| 学术论文检索（PubMed/PMC/arXiv/Crossref/Semantic Scholar 等 10 库 REST API） | `k-dense-ai-scientific-agent-skills-paper-lookup` |
| 任意文档转 Markdown（firecrawl anydoc） | `firecrawl-anydoc-convert-documents-to-markdown` |
| Markdown → 出版级 PDF（gstack） | `garrytan-gstack-make-pdf` |
| DeepSeek 官方双语文档翻译工作流（简报→逐段翻译→整篇翻译→配对校验） | `deepseek-ai-deepseek-harness-dsh-translate-docs` |
| PDF/扫描件文本提取（pymupdf、marker-pdf） | `nousresearch-hermes-agent-ocr-and-documents` |
| OpenAI 官方 PDF 处理 | `openai-skills-pdf` |
| PDFtk 服务器 | `github-awesome-copilot-pdftk-server` |
| Markdown 文件索引维护 | `github-awesome-copilot-update-markdown-file-index` |

## 图片识别（OCR）

优先级从高到低：
1. **多模态视觉直接读取**：用 read 工具直接查看图片，转录文字、表格、结构。无需任何外部依赖，最可靠。
2. **Pix2Text（p2t，本机已装，免费无限次）**：文字+公式+版面一体识别，公式直接输出 LaTeX
   ```
   & "C:\Users\job_p\AppData\Local\Programs\Python\Python312\Scripts\p2t.exe" predict -i 图片路径 -o 输出目录 [--file-type text_formula|text|formula|page]
   ```
   - p2t 不在 PATH，必须用全路径调用；纯公式截图用 `--file-type formula`；含文字+公式的整页用 `page` 或 `text_formula`；同一张图建议跑 2 种模式交叉验证，分歧字符对照原图
   - Python 3.12 已装；模型缓存在 `C:\Users\job_p\AppData\Roaming\pix2text\1.1\`、`cnocr\2.3\`、`cnstd\1.2\`（首次运行自动下载，约 1GB）
   - 小图（宽<1000px）先放大 2-3 倍再识别可显著提高准确率：`PIL.Image.resize((w*3,h*3), Image.LANCZOS)`
   - 剪贴板截图：先 `Add-Type -AssemblyName System.Windows.Forms`，再 `[System.Windows.Forms.Clipboard]::GetImage().Save($tmp,...)` 保存 PNG，再 p2t 识别
3. **Windows OCR（本机已装，零依赖，仅文字不支持公式）**：
   `powershell -NoProfile -ExecutionPolicy Bypass -File "C:\Users\job_p\AppData\Local\Temp\opencode\ocr.ps1"`（无参=读剪贴板；`-path 图片路径`=读文件）
4. **本地 OCR 工具**（若环境有）：`tesseract`（含 `chi_sim` 中文包）、`easyocr`、`paddleocr`。
5. **MarkItDown**：`modules/k-dense-ai-claude-scientific-skills-markitdown` 的图片 OCR 流程。
6. 表格类图片 → 转录为 Markdown 表格；合并单元格需人工逻辑展开。

## 公式识别

1. **图片中的公式**：多模态视觉读取 → 转录为 LaTeX（`$...$` 行内 / `$$...$$` 块级）。
2. **docx/doc 中的公式（OLE 对象，纯文本提取不出字符）**——公式核实流程（本机已跑通）：
   - 转 PDF：批量首选 **soffice.com**（快、无人值守，调用规范见「环境注意」）；单文件亦可用 Word COM `$doc.SaveAs2(pdf路径, 17)`
   - PyMuPDF 定位章节页并渲染 PNG：`import pymupdf; doc[i].get_text()` 找关键词 → `get_pixmap(dpi=300)` 保存
   - `& "C:\Users\job_p\AppData\Local\Programs\Python\Python312\Scripts\p2t.exe" predict --file-type page/formula` 识别 → 与规范知识核对 → 标注【公式已核实】
3. **docx 中的 OMML 公式**：`pandoc -t markdown` 可自动转 LaTeX（见 `modules/anthropics-skills-docx`）。
4. **PDF 中的公式**：先 `modules/anthropics-skills-pdf` 提取文本；矢量公式可转图后用视觉识别。
5. 输出 LaTeX 时校验可编译性（括号配对、环境闭合）。

## 公式标准显示（HTML 输出规范）

- **所有输出公式必须标准排版（MathJax/LaTeX），包括协议原文引用中的公式**；禁止 ⌈⌉、⌊⌋、N_RB^、log2( 等纯文本伪公式
- **多讲次 HTML 讲义必须"主线串联"**（用户实测反馈"没逻辑、没串起来"的教训）：① 主线 = 功能的生命周期问题链（为什么需要→用什么测→怎么配→报什么→怎么算→怎么交付→时限→回顾），每讲只回答一个问题；② 每讲开头"设问（承接第 X 讲）"、结尾"小结（把球交给下一讲）"显式桥接（.bridge 样式块）；③ 末讲做"全程回顾（每步标注对应讲次）"+ 主线收口一句话；④ 拆多文件时导航页给学习地图（讲次递进关系）+ 每文件顶部导航条；⑤ 旧文件/机械拼接文件改造：补"主线三件套"（文首导览块 + 每讲承接块 + 收口块），桥接块定位用每讲第二个 h2（唯一）向前找最近 `<h2>`，禁用重复标题做锚点
- **每个知识点"先详细解析、最后才提炼"**（用户两次点名"过于简单"）：原文引用 → 逐句翻译 → 逐项/逐符号解析 → 公式 → 数值例题 → 注意点 → 末尾才给提炼总结；提炼表放章节最后；禁止一句话提炼带过
- **主线必须落实到"基站-UE 如何使用"**：每专题第 1 讲给"四问定位"（含义/作用/目的/应用场景）；机制讲次后加"双视角落地讲次"——双端流程对照表（基站 N 步↔UE N 步）、参数双端使用总表（配置方→给谁 | 基站如何使用 | UE 如何使用）、基站内部决策（规范外原理，标注【解读/推导】）、核心网 QoS 输入
- **ASN.1 配置链着色必查**：扫描全部 `<pre>` 块，含 `::=`/`SEQUENCE {` 却无 `class="rv"` 即为遗漏（历史文件曾整专题 10 块无着色）；规则化着色时多词类型（BIT STRING/OCTET STRING）放类型交替前面防拆分，着色后复查 `BIT</span> STRING` 类残留
- **专题收尾自查**：维护"讲次↔规范章节贡献矩阵"逐条核对各规范覆盖（防整块遗漏）；任务标记完成前确认实质内容落地（禁止"机制相同"带过）；<b>正文禁止"与 XX 同构/完全相同"式带过</b>——相似专题必须原样展开重列公式表格；<b>配图数量不限越多越好</b>（公式分解图/对比图/走势图均可）；残留扫描排除 `<script>` 段与 `<svg>` 段（JS 的 Math.log2 与图内 Unicode 数学符号是合法写法）
- HTML head 模板：
  ```html
  <script>window.MathJax = { tex: { inlineMath: [['$','$'],['\\(','\\)']], displayMath: [['$$','$$']] } };</script>
  <script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-chtml.js"></script>
  ```
- **SVG 图内公式/变量**：用 `<tspan baseline-shift="sub|super">` 原生上下标（如 `N<tspan baseline-shift="sub">BWP,i</tspan><tspan baseline-shift="super">start,μ</tspan>`）；**禁用 foreignObject 嵌 MathJax**（渲染错位）
- SVG 标注布局：错行 + 虚线引线指向；任何文字/图标不得重叠（指向虚线除外）
- JS 动态输出的公式：输出 `\(...\)` 后用 `try{MathJax.typesetPromise([元素]);}catch(e){}` 重新排版

## HTML/JS 交付校验（本机脚本，交付前必跑）

- 全部页面 JS 检查：`powershell -NoProfile -ExecutionPolicy Bypass -File "C:\Users\job_p\AppData\Local\Temp\opencode\check-bwp.ps1"`（Chrome headless 抓 console 错误）
- 计算器点击验证：`check-cdp.ps1` / `check-cdp2.ps1` / `check-pdcch.ps1`（CDP 模拟点击并核对数值）
- SVG 重叠检测：`check-overlap.ps1`（getBBox 两两检测）
- Chrome 路径：`C:\Program Files\Google\Chrome\Application\chrome.exe`
- 计算器 JS 规范：函数名避开保留字；不用 ES6（for...of 等）；id 引用一律 document.getElementById

## 流程图识别

1. 多模态视觉读取流程图图片 → 归纳节点、连线、判断分支。
2. 输出 **Mermaid** 语法（`flowchart TD` / `graph LR`）以便后续渲染或复用。
3. 若流程图出现在 PDF/docx 中，先提取对应页/图片，再做视觉识别。
4. 复杂交叉连线建议标注说明，不要强行压平。

## 示意图绘制（文本/数据 → SVG，NR-f40 实战打磨）

**判据**：涉及空间关系 / 时序关系 / 块结构 / 流程跳转 / 处理链五类关键关系时，仅文字不够，必须配图。**禁止手写 SVG 坐标**（易错位、布局差）——按图类选工具自动生成：

| 图类 | 工具 | 生成方式 | 典型用例 |
|---|---|---|---|
| 流程图（决策/双路径/多分支） | **Mermaid flowchart**（首选） | 写 `.mmd` → `mmdc.cmd -i x.mmd -o x.svg -b white` 渲染 | 按需 SI 双路径、端到端流程、状态机 |
| 信令/时序图 | **Mermaid sequenceDiagram**（首选） | 同上 | RACH 流程、SI 请求/响应、寻呼时序 |
| 状态图/类图/甘特 | Mermaid stateDiagram / classDiagram / gantt | 同上 | RRC 状态机、修改周期甘特排布 |
| 结构/网格/频谱块图 | **matplotlib**（首选） | `pcolormesh` 网格着色 + `scatter` 打点 + `annotate` 引线 → `savefig(x.svg)`；中文字体 `plt.rcParams['font.sans-serif']=['Microsoft YaHei']` | SSB 时频块图、资源网格、Point A 频域关系 |
| 走势图/曲线/波形 | **matplotlib** | `plot`/`barh`/`axvspan`/`fill_between` | 波束扫描时间轴、门限曲线、时序排布 |
| 精细标注空间图 | matplotlib `annotate`（xytext 错行）优先；手写 SVG 仅兜底 | — | 带多引线标注的示意图 |

**工作流**：① Mermaid：写 `.mmd` 源码 → 设 `$env:PUPPETEER_EXECUTABLE_PATH`（指向系统 Chrome）→ `& "C:\Users\job_p\AppData\Local\Programs\nodejs\mmdc.cmd" -i in.mmd -o out.svg -b white`（注意用 mmdc.cmd 而非 mmdc，ps1 被执行策略禁）；② matplotlib：脚本 `savefig(out.svg, format='svg')`；③ 两种产出 SVG 后嵌入 HTML 的 `<figure>`，与手写 SVG 同跑重叠检测兜底；④ 图内变量用 Mermaid/matplotlib 原生上下标（matplotlib 用 LaTeX mathtext 如 `$k_{SSB}$`；Mermaid 支持 HTML 实体 `<sub>`）。

**质量要点**：文字/图标不重叠（重叠检测归零）；超宽文字缩小字号适配而非硬挤；图内与图注统一用正式符号（正文 MathJax `\(...\)`、图内 mathtext/HTML 下标）；禁止自造比喻词汇。

## 结构要素识别与输出

- **目录/大纲/标题层级**：
  - docx：python-docx 遍历段落样式（Heading 1-9）或 `pypandoc.convert_file(docx, 'markdown')` 后取 `#` 层级；生成 TOC 用 pandoc `--toc`
  - PDF：PyMuPDF `doc.get_toc()` 直接拿书签目录；无书签则 p2t `--file-type page` 逐页识别标题行
  - 输出：层级列表（缩进/Markdown 标题）+ HTML 导航页
- **图题/表题/编号体系**：正则提取 `图\s*\d+[-\d]*`、`Table\s*\d+(\.\d+)*`、`式\s*\(\d+-\d+\)`，与图/表位置关联；输出时保持原编号并做交叉引用
- **页眉页脚/页码**：docx 用 python-docx `section.header/footer`；PDF 用 pdfplumber 按页边距区域提取；生成 docx 页码用域代码 `PAGE`/`NUMPAGES`
- **批注/修订痕迹**：`modules/anthropics-skills-docx`（tracked changes `<w:ins>/<w:del>`、comments 六文件体系）；PDF 批注用 pypdf `page.annotations`
- **书签/超链接/交叉引用**：docx 用 python-docx hyperlink + pandoc；PDF 链接用 pypdf `/Annots`；输出 HTML 时锚点 `id` + `<a href="#...">`
- **参考文献**：识别 `[1]`、`[XX]` 标注并解析条目；输出按 GB/T 7714 / IEEE / APA 格式模板生成

## 图形要素处理

- **数据图表（柱/折/饼/散点）**：
  - 识别：视觉估计坐标轴范围与数据点近似值（标注"近似重绘"），或从 Excel/CSV 拿原始数据
  - 重绘：matplotlib 输出矢量 SVG/PDF（中文字体 `plt.rcParams['font.sans-serif']=['Microsoft YaHei']`）
- **Mermaid 扩展图类**：思维导图 `mindmap`、时序图 `sequenceDiagram`、甘特图 `gantt`、状态图 `stateDiagram`——纯文本生成，可嵌入 Markdown/HTML 渲染
- **矩阵/阵列**：p2t `--file-type formula` 输出 `\begin{matrix}`/`\begin{array}` 转标准 LaTeX
- **化学式/结构式**：依赖多模态视觉模型；当前模型不支持时标注【待识别】并保存原图
- **条码/二维码**：pyzbar 已装，直接 `pyzbar.decode(PIL.Image)` 解码（QR 码、EAN-13 等一维码均支持）
- **签章/手写体**：依赖多模态视觉；OCR 工具均不可靠，标注【需人工核对】
- **SVG 示意图生成规范**：见「公式标准显示」章节（tspan 上下标、错行标注、重叠检测）

## 音视频处理

- 音频：`modules/k-dense-ai-claude-scientific-skills-markitdown`（语音转写）；whisper 未装（>500MB，需询问用户）
- 视频抽帧：已装 opencv + imageio-ffmpeg，`cv2.VideoCapture(path)` 逐帧读；ffmpeg 路径 `imageio_ffmpeg.get_ffmpeg_exe()`；抽帧后按图片流程识别

## 元数据 / 编码 / 版式检测

- 元数据：PDF 用 pypdf `reader.metadata`；docx 用 python-docx `core_properties`（作者/日期/版本）
- 编码检测：chardet 已装，`chardet.detect(raw_bytes)`；快速路径先 UTF-8 解码失败后试 GBK
- 版式检测：PyMuPDF `page.rect` / `page.rotation` 判断页面尺寸与横竖版（A4=595×842pt，Letter=612×792pt）
- 竖排/RTL 文字：p2t 竖排支持有限，中文竖排标注【竖排文本】；阿拉伯文/希伯来文 RTL 参考 `modules/openclaw-skills-pdf-translate`

## 文字提取

- **docx/doc 批量文本提取（本机脚本，NR-f40 验证可用）**：
  - docx：`powershell -NoProfile -ExecutionPolicy Bypass -File "C:\Users\job_p\AppData\Local\Temp\opencode\extract-docx.ps1"`
  - doc（老格式，先 soffice.com 批量转 docx：`--convert-to docx --outdir 目录 *.doc`，再提取）：`powershell -NoProfile -ExecutionPolicy Bypass -File "C:\Users\job_p\AppData\Local\Temp\opencode\extract-doc.ps1"`
  - **⚠ 铁律：提取文本必须同步用图片识别工具（p2t）核实**——3GPP 等文档中公式、符号、记号为图片式（OLE 对象），纯文本提取不出字符，资料读取必然不完整；双轨流程：文本提取 + soffice 转 PDF → PyMuPDF 渲染 PNG → p2t `formula/page` 模式识别，两轨合并，差异以图片识别为准（详见 3gpp_skill「文档提取双轨要求」）
- 原生文本 PDF/docx/pptx/xlsx → 首选对应 Anthropics 官方技能（`modules/anthropics-skills-pdf` / `-docx` / `-pptx`）。
- 扫描件 → 走 OCR 章节流程。
- 统一兜底：MarkItDown 转 Markdown 后读取。

## 环境注意

- 本机为 Windows + PowerShell，无全局 node/npm 命令时用 `& "C:\Program Files\nodejs\npx.cmd"`。
- 中文输出优先；文件编码保持 UTF-8。
- **已装环境**：
  - Python 3.12（pip，默认源连不上时用清华镜像 `-i https://pypi.tuna.tsinghua.edu.cn/simple`）
  - Pix2Text 1.1.6（p2t，全路径调用见「图片识别」章节）
  - pandoc（pypandoc_binary，`python -c "import pypandoc; pypandoc.convert_file(...)"` 调用；md→docx 时公式自动转 OMML）
  - python-docx 1.2.0 / python-pptx 1.0.2 / openpyxl 3.1.5 / matplotlib / pypdf 6.16.1 / pdfplumber 0.11.10 / PyMuPDF
  - chardet 7.6.0（编码检测）/ pyzbar 0.1.9（条码二维码解码）
  - opencv-python（视频抽帧）/ imageio-ffmpeg 0.6.0（`imageio_ffmpeg.get_ffmpeg_exe()` 取 ffmpeg 路径，视频抽帧/音频转换用）
  - jupyter（IPython + ipykernel，.ipynb 可本机运行）
  - Chrome（headless 校验用）：`C:\Program Files\Google\Chrome\Application\chrome.exe`
  - Office 16（Word/PPT COM 转 PDF、生成 docx/pptx 用）
  - LibreOffice 26.2.4 便携版（批量无头转换，soffice 调用规范见下）
  - 未装（需询问用户后再装）：LaTeX 引擎（MiKTeX/TeX Live，>1GB）、whisper 语音转写（含模型 >500MB）、tesseract（备选 OCR，p2t 已覆盖）
- **LibreOffice soffice 调用规范（本机已验证）**：
  - 必须用 `soffice.com`（非 .exe，命令行输出正常）且带独立 profile 防首次初始化卡死：
    ```
    & "D:\Program Files\LibreOffice\LibreOfficePortable\App\libreoffice\program\soffice.com" --headless "-env:UserInstallation=file:///C:/Users/job_p/AppData/Local/Temp/LO-profile" --convert-to pdf --outdir 输出目录 源文件
    ```
  - 批量：`--convert-to pdf --outdir 目录 *.docx`（支持 doc/docx/pptx/xlsx→pdf；过滤器可用 `writer_pdf_Export`、`impress_pdf_Export` 等）
  - stderr 的 "Could not find platform independent libraries" 为无害噪音，看输出目录是否生成文件即可
- 多模态视觉读取（read 工具看图）依赖当前模型能力：不支持图片的模型直接跳到 p2t/Windows OCR 流程。
- 需安装新工具时，先告知用户再安装。
- 任何需要 API Key / 付费服务的子技能（Nutrient、LandingAI），使用前必须征得用户确认。
