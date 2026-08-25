---
name: find_skill
description: 网络资源获取与 GitHub 镜像加速技能（全局 skill，仅显式触发，不靠关键词自动调用）。Use ONLY when 用户消息显式包含 "find_skill：" 或 "find_skill:"，或以 "find_skill&"、"find_skill " 与其他技能名并列后跟冒号——冒号后为用户任务。加载后执行任务：GitHub 下载失败时走镜像渠道（raw 文件/release/tarball/git clone）、pip/npm 等包管理器换国内镜像源、从技能目录网站（skillsmp.com、skills.sh、LobeHub、smithery.ai、agentskills.io）搜索与获取 skill、3GPP/ETSI/arXiv 标准文献下载、抓取服务端渲染页面内容、HF 模型镜像下载等。触发场景：github 连不上、下载失败、网络超时、找镜像、换源、获取资源、下载文件、找 skill。普通消息仅提及下载/GitHub 但无 "find_skill：" 前缀时，不调用本技能。
---

# find_skill —— 网络资源获取与镜像加速接口

## 🛠 工具依赖清单（移植到新机器时先逐项检查）

| 工具 | 用途 | 本机位置/版本 | 检查命令 | 缺失时安装 |
|---|---|---|---|---|
| curl.exe | 下载/探测（-L 重定向、-A UA 头、-m 超时、-o 输出） | Windows 自带 `<工具目录>Windows\System32\curl.exe` | `curl.exe --version` | Windows 10+ 自带 |
| node + market-cli | LobeHub 市场搜索/安装 | npx 缓存 `<用户目录>\AppData\Local\npm-cache\_npx\06aaad52133b3ed7\node_modules\@lobehub\market-cli\dist\cli.js`（含凭证 `~\.lobehub-market\credentials.json`） | `& node <cli.js> --help` | `npx -y @lobehub/market-cli register --name xxx --description xxx --source open-claw`（凭证需重新注册） |
| Python 3.12 | 下载脚本（fetch_skills.py）、MSI 校验（msilib） | `python` | `python --version` | python.org |
| tar / Expand-Archive | 解压 tarball/zip | Windows 自带 | `tar --version` | 自带 |
| 批量安装脚本 | GitHub skill 仓库批量抓取 | `<项目目录>\temp\fetch_skills.py` | `Test-Path` | 从原机复制（含 PLAN 映射表） |
| pip 清华源 | Python 包装 | `https://pypi.tuna.tsinghua.edu.cn/simple` | — | 无需装 |
| GitHub 镜像 | 直连不通时的替代渠道 | ghproxy.net（截断风险）/ gh-proxy.com（大文件首选） | `curl -sL -m 20 -o NUL -w %{http_code} https://gh-proxy.com/` | 无需装（渠道失效换下一个） |
| winget | Windows 包安装（不稳，GitHub 源常失败） | 自带 | `winget --version` | 自带 |

**移植说明**：本技能核心 = curl + 镜像渠道（无安装要求）+ market-cli（需重新注册凭证）；fetch_skills.py 脚本依赖 gh-proxy.com 可用性。

本技能是**唯一注册入口**，汇总本机实测有效的网络资源获取方法与镜像渠道（含验证状态），用于 GitHub 直连不通时的替代方案。

## 通用输出规则（全部任务遵守）

- **语言跟随提问**：用户以何种语言提问，思考、回答、输出就以何种语言（中文提问→中文回答，英文提问→英文回答）；命令、URL、代码、字段名等必要原文保持原样不翻译
- **含"输出"二字 → HTML 交付**：提问中出现"输出"二字时，最终答案必须以 HTML 文件输出（规范排版），内容详细、不限字数篇幅；HTML 保存到提问时所在工作目录并浏览器打开（用户另行指定目录时按用户指定）

## 处理流程

1. 确认目标：GitHub 文件/仓库 | Python 包 | Node 包 | 网页内容 | 技能市场 | 标准/文献 | 大模型
2. 按下表选渠道，**优先选已验证（✓）渠道**；未验证渠道失败一次即换下一个
3. 下载后校验文件完整性（大小 >10KB、magic bytes、tar -tzf 列表检查）

## 技能目录三大站（搜索/下载 skill）

| 站点 | 搜索方式 | 下载方式 | 状态 |
|---|---|---|---|
| **skillsmp.com**（200 万技能，中文界面） | `https://skillsmp.com/zh/search?q=关键词`，webfetch 直接抓（SSR 免登录） | 详情页 `/zh/creators/{owner}/{repo}/{slug}` webfetch 保存 SKILL.md；或取仓库地址走 ghproxy | ✓ 搜索+详情页均实测 |
| **skills.sh**（Vercel 目录） | API 需 Vercel OIDC（无 token 401）→ 用 sitemap 绕过：`curl sitemap.xml` → 子 sitemap 2 万 URL 本地正则过滤 | 详情页 webfetch（有 Show more 截断）；仓库 tarball 走 ghproxy | ✓ sitemap/ghproxy 实测；curl 被反爬 |
| **LobeHub**（lobehub.com 市场） | 本机 CLI 已注册凭证（见下） | `skills install <id> --dir <目录>` | ✓ 本机多次实测 |

## 其它可用站点（2026-08 验证）

| 站点 | 性质 | 用法 | 状态 |
|---|---|---|---|
| **smithery.ai** | MCP 服务器目录（16,687+），导航含 `/skills` 分类 | 网页浏览 `https://smithery.ai/skills`；CLI：`npx -y smithery`（auth/mcp add/tool call） | ✓ 页面可访问；skills 分类需登录浏览部分功能 |
| **agentskills.io** | Agent Skills 开放格式**官方规范站**（Anthropic 发起，非市场） | 规范文档 + 全站索引 `https://agentskills.io/llms.txt`；支持 skill 的客户端清单 `/clients` | ✓ 可访问；写新 skill 时查规范用 |
| **skills.directory** | 候选目录站 | — | ✗ 抓取返回空（不存在或反爬） |
| **github.com/topics/claude-skills** | GitHub topic 聚合页（官方分类入口） | GitHub 直连不通时走 kkgithub 网页镜像 | ✗ 直连不通（本机 GitHub 被墙） |

### LobeHub CLI 用法（本机凭证已注册）
```
& node "<用户目录>\AppData\Local\npm-cache\_npx\06aaad52133b3ed7\node_modules\@lobehub\market-cli\dist\cli.js" skills search --q "关键词"
（同上）skills install <identifier> --dir <目录>
（npx 方式：& "<Node目录>\npx.cmd" -y @lobehub/market-cli ...；token 失效时先 auth refresh）
```
- search/view/install 对 token 要求不同；view 报 invalid_token 时直接 install 通常可行

### skills.sh 绕过细节
- API 端点（`/api/v1/skills/*`）全部需要 Vercel OIDC token
- sitemap 链路：`sitemap.xml` → `sitemap-skills-1/2.xml`（共 2 万条 skill URL）→ 本地 `Where-Object { $_ -match "关键词" }` 过滤 ✓
- curl 直接抓页面被反爬（14 字节），必须用 webfetch
- 大仓库批量：ghproxy tarball → 递归找 SKILL.md → 装入 modules → 改名 GUIDE.md

### skillsmp.com 绕过细节
- curl 被反爬（几百字节），必须用 webfetch
- 分类入口：`/zh/categories/documents`（文档处理 9.2 万）、`/zh/occupations`（SOC 职业）
- 多详情页并行抓取时用 general 子代理批量处理（每页 SKILL.md 完整，直接落盘 GUIDE.md）

### GitHub skill 仓库批量安装脚本
- 批量脚本：`python <项目目录>\temp\fetch_skills.py [仓库名过滤]`（ghproxy 下载 tarball → 递归找 SKILL.md → 按 PLAN 映射装入目标 skill 的 modules/ → SKILL.md 改名 GUIDE.md）
- 大仓库（如 claude-office-skills 140+ 技能）装完后按白名单清理非目标模块
- 已知失败：超大仓库下载超时（pdf-converter-mineru）、超长路径（imbad0202，Windows 路径限制）、部分仓库 tarball 截断（改走 skillsmp 详情页抓取）

## 标准/文献资源站点

| 站点 | 用途 | 状态 |
|---|---|---|
| **3GPP FTP**：`https://www.3gpp.org/ftp/Specs/archive/` | 3GPP 规范 doc 格式直下（38 系列=5G NR，36 系列=4G LTE，23 系列=核心网） | ✓ NR-f40 项目验证 |
| **ETSI**：`https://www.etsi.org/deliver/etsi_ts/138300_138399/...` | 3GPP TS/TR 的 PDF 官方镜像（URL 规律：138322v190100p.pdf） | 未实测 |
| **arXiv**：`https://arxiv.org/abs/<id>` / `https://arxiv.org/pdf/<id>` | 论文摘要/PDF 直下 | 标准可用 |
| 学术 10 库（PubMed/PMC/arXiv/Crossref/Semantic Scholar/OpenAlex/CORE/Unpaywall/bioRxiv/medRxiv） | 论文检索 REST API（见 files_skill/modules 的 paper-lookup） | 免 API Key |

## GitHub 镜像渠道（直连不通时）

| 渠道 | 用法模板 | 状态 |
|---|---|---|
| **ghproxy.net**（首选） | `https://ghproxy.net/https://github.com/<owner>/<repo>/archive/refs/heads/<branch>.tar.gz` | ✓ 本机实测（tarball 2.3MB/3.6MB 成功） |
| gh-proxy.com | 同 ghproxy 格式 | △ 连通但部分路径 404；tarball 可用 |
| raw.gitmirror.com | `https://raw.gitmirror.com/<owner>/<repo>/<branch>/<path>` | ✗ 本机实测超时（len=0） |
| ghfast.top / gh.llkk.cc / mirror.ghproxy.com | 同 ghproxy 格式 | 未验证，备用 |
| kkgithub.com | GitHub 网页镜像：`https://kkgithub.com/<owner>/<repo>` | 未验证 |
| gitclone.com | git clone 镜像：`git clone https://gitclone.com/github.com/<owner>/<repo>.git` | 未验证 |

**常用资源类型**：
- 单文件（raw）：`https://ghproxy.net/https://raw.githubusercontent.com/<owner>/<repo>/<branch>/<path>`
- 整仓库：tarball/zip（如上）→ `tar -tzf` 列内容 → 只解压目标路径 `tar -xzf f.tar.gz -C 目录 "repo-main/目标子路径"`
- Release 二进制：`https://ghproxy.net/https://github.com/<owner>/<repo>/releases/download/<tag>/<file>`
- 仓库目录列表（api 在镜像上不可用，直接下 tarball 最可靠）

## 包管理器国内镜像（本机验证状态）

| 生态 | 镜像 | 用法 | 状态 |
|---|---|---|---|
| pip | 清华 TUNA | `pip install X -i https://pypi.tuna.tsinghua.edu.cn/simple` | ✓ 本机多次实测 |
| npm | npmmirror | `npm config set registry https://registry.npmmirror.com` | 标准备用 |
| conda | 清华 | `~/.condarc` channels 配 `https://mirrors.tuna.tsinghua.edu.cn/anaconda/` | 未验证 |
| LaTeX | 清华 CTAN | MiKTeX 安装器源 / TeX Live 源：`https://mirrors.tuna.tsinghua.edu.cn/CTAN/` | 未验证（本机未装 LaTeX） |
| HF 模型 | hf-mirror | `export HF_ENDPOINT=https://hf-mirror.com` | 未验证（whisper/pix2tex 模型可走此路） |
| winget | 无可靠镜像 | winget 源常指向 GitHub，失败时改用 ghproxy 直下安装包 | ✗ 本机 pandoc/tesseract 均失败 |

## 已装入 modules 的搜索/研究子技能（find_skill/modules）

| 系列 | 内容 | 依赖 |
|---|---|---|
| `lllllllama-rigorpilot-skills-*`（11 个） | paper-context-resolver 论文解析、ai-research-explore/reproduction、repo-intake、safe-debug 等 | 免费 |
| `inference-sh-skills-web-search` | 网页搜索 | 免费 |
| `parallel-web-parallel-agent-skills-*`（11 个） | parallel-deep-research、parallel-web-search、parallel-web-extract、findall 等 | 免费（需 parallel CLI 可选） |
| `firecrawl-firecrawl-workflows-*`（16 个） | firecrawl-deep-research、research-papers、knowledge-base 等 | **需 FIRECRAWL_API_KEY，先确认** |
| `199-biotechnologies-claude-deep-research-skill-*` | 深度研究工作流 | 免费 |

## 网页内容抓取

- 服务端渲染（SSR）页面：webfetch 直接取 markdown/html
- JS 渲染页面：webfetch 只能拿空壳；换 sitemap/JSON 接口/移动端页面
- 带认证的 API：先查 docs 页的认证方式；无凭证时找公开替代端点或 SSR 页面
- 大文件列表：抓 sitemap 后本地 `Where-Object { $_ -match "关键词" }` 过滤，避免逐个请求
- **curl 空响应/403 时换 UA 头**（3gpp.org 等站点实测）：`curl.exe -A "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36" -s -L URL`，或 PowerShell `Invoke-WebRequest -Headers @{"User-Agent"="..."} -UseBasicParsing`；拿到 HTML 后用 `[regex]::Matches($html,'href="([^"]+\.zip)"')` 提取下载链接清单
- **下载前先找"索引页"**：目标文件的真实 URL 常在索引页（如 DynaReport）里；直接猜路径 403 时，先抓上级目录列表/搜索引擎页提取 `href` 清单再挑版本

## 环境注意

- 中文输出优先；文件编码 UTF-8
- 临时文件放 `<用户临时目录>\opencode` 或项目 temp，用完清理
- 下载一律带 `-L`（跟随重定向）和超时 `-m`；tar 解压前先 `tar -tzf` 验证
- 与 files_skill / 3gpp_skill 联动：`find_skill&files_skill：任务` 获取资源后立即处理
