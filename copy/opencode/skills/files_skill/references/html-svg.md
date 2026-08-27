# files_skill 参考：公式标准显示（HTML 输出规范）

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

---

# files_skill 参考：HTML/JS 交付校验（本机脚本，交付前必跑）

## HTML/JS 交付校验（本机脚本，交付前必跑）

- 全部页面 JS 检查：`powershell -NoProfile -ExecutionPolicy Bypass -File "<用户临时目录>\opencode\check-bwp.ps1"`（Chrome headless 抓 console 错误）
- 计算器点击验证：`check-cdp.ps1` / `check-cdp2.ps1`（CDP 模拟点击并核对数值；各教学专题的 check-* 脚本同理）
- SVG 重叠检测：`check-overlap.ps1`（getBBox 两两检测）
- Chrome 路径：`<Chrome目录>\chrome.exe`
- 计算器 JS 规范：函数名避开保留字；不用 ES6（for...of 等）；id 引用一律 document.getElementById

---

