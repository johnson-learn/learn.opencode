# files_skill 参考：图片识别（OCR）

## 图片识别（OCR）

优先级从高到低：
1. **多模态视觉直接读取**：用 read 工具直接查看图片，转录文字、表格、结构。无需任何外部依赖，最可靠。
2. **Pix2Text（p2t，本机已装，免费无限次）**：文字+公式+版面一体识别，公式直接输出 LaTeX
   ```
   & "<Python脚本目录>\p2t.exe" predict -i 图片路径 -o 输出目录 [--file-type text_formula|text|formula|page]
   ```
   - p2t 不在 PATH，必须用全路径调用；纯公式截图用 `--file-type formula`；含文字+公式的整页用 `page` 或 `text_formula`；同一张图建议跑 2 种模式交叉验证，分歧字符对照原图
   - Python 3.12 已装；模型缓存在 `<用户AppData目录>\pix2text\1.1\`、`cnocr\2.3\`、`cnstd\1.2\`（首次运行自动下载，约 1GB）
   - 小图（宽<1000px）先放大 2-3 倍再识别可显著提高准确率：`PIL.Image.resize((w*3,h*3), Image.LANCZOS)`
   - 剪贴板截图：先 `Add-Type -AssemblyName System.Windows.Forms`，再 `[System.Windows.Forms.Clipboard]::GetImage().Save($tmp,...)` 保存 PNG，再 p2t 识别
3. **Windows OCR（本机已装，零依赖，仅文字不支持公式）**：
   `powershell -NoProfile -ExecutionPolicy Bypass -File "<用户临时目录>\opencode\ocr.ps1"`（无参=读剪贴板；`-path 图片路径`=读文件）
4. **本地 OCR 工具**（若环境有）：`tesseract`（含 `chi_sim` 中文包）、`easyocr`、`paddleocr`。
5. **MarkItDown**：`modules/k-dense-ai-claude-scientific-skills-markitdown` 的图片 OCR 流程。
6. 表格类图片 → 转录为 Markdown 表格；合并单元格需人工逻辑展开。

---

# files_skill 参考：公式识别

## 公式识别

1. **图片中的公式**：多模态视觉读取 → 转录为 LaTeX（`$...$` 行内 / `$$...$$` 块级）。
2. **docx/doc 中的公式（OLE 对象，纯文本提取不出字符）**——公式核实流程（本机已跑通）：
   - 转 PDF：批量首选 **soffice.com**（快、无人值守，调用规范见「环境注意」）；单文件亦可用 Word COM `$doc.SaveAs2(pdf路径, 17)`
   - PyMuPDF 定位章节页并渲染 PNG：`import pymupdf; doc[i].get_text()` 找关键词 → `get_pixmap(dpi=300)` 保存
   - `& "<Python脚本目录>\p2t.exe" predict --file-type page/formula` 识别 → 与规范知识核对 → 标注【公式已核实】
3. **docx 中的 OMML 公式**：`pandoc -t markdown` 可自动转 LaTeX（见 `modules/anthropics-skills-docx`）。
4. **PDF 中的公式**：先 `modules/anthropics-skills-pdf` 提取文本；矢量公式可转图后用视觉识别。
5. 输出 LaTeX 时校验可编译性（括号配对、环境闭合）。

---

