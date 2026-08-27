# files_skill 参考：流程图识别

## 流程图识别

1. 多模态视觉读取流程图图片 → 归纳节点、连线、判断分支。
2. 输出 **Mermaid** 语法（`flowchart TD` / `graph LR`）以便后续渲染或复用。
3. 若流程图出现在 PDF/docx 中，先提取对应页/图片，再做视觉识别。
4. 复杂交叉连线建议标注说明，不要强行压平。

---

# files_skill 参考：结构要素识别与输出

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

---

# files_skill 参考：图形要素处理

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

---

# files_skill 参考：音视频处理

## 音视频处理

- 音频：`modules/k-dense-ai-claude-scientific-skills-markitdown`（语音转写）；whisper 未装（>500MB，需询问用户）
- 视频抽帧：已装 opencv + imageio-ffmpeg，`cv2.VideoCapture(path)` 逐帧读；ffmpeg 路径 `imageio_ffmpeg.get_ffmpeg_exe()`；抽帧后按图片流程识别

---

# files_skill 参考：元数据 / 编码 / 版式检测

## 元数据 / 编码 / 版式检测

- 元数据：PDF 用 pypdf `reader.metadata`；docx 用 python-docx `core_properties`（作者/日期/版本）
- 编码检测：chardet 已装，`chardet.detect(raw_bytes)`；快速路径先 UTF-8 解码失败后试 GBK
- 版式检测：PyMuPDF `page.rect` / `page.rotation` 判断页面尺寸与横竖版（A4=595×842pt，Letter=612×792pt）
- 竖排/RTL 文字：p2t 竖排支持有限，中文竖排标注【竖排文本】；阿拉伯文/希伯来文 RTL 参考 `modules/openclaw-skills-pdf-translate`

---

