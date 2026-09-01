---
name: files_skill
description: 综合文件识别与文档处理统一接口技能（全局 skill，仅显式触发，不靠关键词自动调用）。Use ONLY when 用户消息显式包含 "files_skill：" 或 "files_skill:"，或以 "files_skill&"、"files_skill " 与其他技能名并列后跟冒号——冒号后为用户任务。加载后执行任务：识别、读取、提取或处理任何文件资料（PDF、Word/docx、PPT/pptx、Excel/xlsx、图片、Markdown、EPUB、HWP 等），包括图片识别（OCR）、公式识别（转 LaTeX）、文字提取、流程图识别（转 Mermaid）、表格提取、文档转换、翻译、公文写作等。普通消息仅提及 PDF/Word 等关键词但无 "files_skill：" 前缀时，不调用本技能。
collaborates_with:
  - 3gpp_skill
  - find_skill
  - program_skill
---
# files_skill —— 统一文件识别接口

## 典型触发场景

- "files_skill：把这份扫描 PDF 转成可搜索 PDF"
- "files_skill：识别图片中的公式并转 LaTeX"
- "files_skill：提取这个 docx 的文本和图片式公式"
- "把这个 PDF 翻译成中文并保留排版（隐式匹配可推荐本技能）"
- "files_skill：批量把 doc/docx 转成 PDF"

## 不处理的边界

- 不处理 3GPP 标准内容的语义分析（推荐 3gpp_skill）
- 不写业务代码（推荐 program_skill）
- 付费 API 子技能（Nutrient/LandingAI/translate-image 等）须先经用户确认


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

> **python-pptx 表格 + LibreOffice 渲染双坑（本机实测 2026-08-31）**：
> ① a:tbl 中**无任何文本的空 cell** 会导致 LibreOffice 渲染时其所在行被折叠、整行内容丢失——空 cell 必须写入空格占位文本；② a:tcPr 的 `rowSpan`+`vMerge` 垂直合并结构 LibreOffice 渲染错误（vMerge 之后的行被丢弃）——表格垂直合并改用「组首行写文字 + 其余行空格占位 + 连续同色填充」伪合并。生成后渲染校验：LibreOffice 转 PDF + PyMuPDF `get_text()` 比对关键字符串存在性（注意 PDF 提取会在中西文/数字间插空格，匹配需容错）；当前模型不支持看图时此法为 PPT 排版校验主通道。

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



## 文字提取

- **docx/doc 批量文本提取（本机脚本，实战验证可用）**：
  - docx：`powershell -NoProfile -ExecutionPolicy Bypass -File "<用户临时目录>\opencode\extract-docx.ps1"`
  - doc（老格式，先 soffice.com 批量转 docx：`--convert-to docx --outdir 目录 *.doc`，再提取）：`powershell -NoProfile -ExecutionPolicy Bypass -File "<用户临时目录>\opencode\extract-doc.ps1"`
  - **⚠ 铁律：提取文本必须同步用图片识别工具（p2t）核实**——3GPP 等文档中公式、符号、记号为图片式（OLE 对象），纯文本提取不出字符，资料读取必然不完整；双轨流程：文本提取 + soffice 转 PDF → PyMuPDF 渲染 PNG → p2t `formula/page` 模式识别，两轨合并，差异以图片识别为准（详见 3gpp_skill「文档提取双轨要求」）
- 原生文本 PDF/docx/pptx/xlsx → 首选对应 Anthropics 官方技能（`modules/anthropics-skills-pdf` / `-docx` / `-pptx`）。
- 扫描件 → 走 OCR 章节流程。
- 统一兜底：MarkItDown 转 Markdown 后读取。



## 环境注意

- 本机为 Windows + PowerShell，无全局 node/npm 命令时用 `& "<Node目录>\npx.cmd"`。
- 中文输出优先；文件编码保持 UTF-8。
- **已装环境**：
  - Python 3.12（pip，默认源连不上时用清华镜像 `-i https://pypi.tuna.tsinghua.edu.cn/simple`）
  - Pix2Text 1.1.6（p2t，全路径调用见「图片识别」章节）
  - pandoc（pypandoc_binary，`python -c "import pypandoc; pypandoc.convert_file(...)"` 调用；md→docx 时公式自动转 OMML）
  - python-docx 1.2.0 / python-pptx 1.0.2 / openpyxl 3.1.5 / matplotlib / pypdf 6.16.1 / pdfplumber 0.11.10 / PyMuPDF
  - chardet 7.6.0（编码检测）/ pyzbar 0.1.9（条码二维码解码）
  - opencv-python（视频抽帧）/ imageio-ffmpeg 0.6.0（`imageio_ffmpeg.get_ffmpeg_exe()` 取 ffmpeg 路径，视频抽帧/音频转换用）
  - jupyter（IPython + ipykernel，.ipynb 可本机运行）
  - Chrome（headless 校验用）：`<Chrome目录>\chrome.exe`
  - Office 16（Word/PPT COM 转 PDF、生成 docx/pptx 用）
  - LibreOffice 26.2.5（批量无头转换，soffice 调用规范见下）
  - 未装（需询问用户后再装）：LaTeX 引擎（MiKTeX/TeX Live，>1GB）、whisper 语音转写（含模型 >500MB）、tesseract（备选 OCR，p2t 已覆盖）
- **LibreOffice soffice 调用规范（本机已验证）**：
  - 必须用 `soffice.com`（非 .exe，命令行输出正常）且带独立 profile 防首次初始化卡死：
    ```
    & "<LibreOffice目录>\program\soffice.com" --headless "-env:UserInstallation=file:///<用户临时目录>/LO-profile" --convert-to pdf --outdir 输出目录 源文件
    ```
  - 批量：`--convert-to pdf --outdir 目录 *.docx`（支持 doc/docx/pptx/xlsx→pdf；过滤器可用 `writer_pdf_Export`、`impress_pdf_Export` 等）
  - stderr 的 "Could not find platform independent libraries" 为无害噪音，看输出目录是否生成文件即可
- 多模态视觉读取（read 工具看图）依赖当前模型能力：不支持图片的模型直接跳到 p2t/Windows OCR 流程。
- 需安装新工具时，先告知用户再安装。
- 任何需要 API Key / 付费服务的子技能（Nutrient、LandingAI），使用前必须征得用户确认。



## 详细知识（按需读取 references/，不随入口加载）

- 详见 `references/tools.md`
- 详见 `references/ocr-formula.md`
- 详见 `references/html-svg.md`
- 详见 `references/elements.md`
