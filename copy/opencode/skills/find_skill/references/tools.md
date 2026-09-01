# find_skill 参考：工具依赖与站点绕过细节（按需读取）

## 🛠 工具依赖清单（移植到新机器时先逐项检查）

| 工具 | 用途 | 检查命令 | 缺失时安装 |
|---|---|---|---|
| curl.exe | 下载/探测 | `curl.exe --version` | Windows 10+ 自带 |
| node + market-cli | LobeHub 市场搜索/安装 | `& node <cli.js> --help` | `npx -y @lobehub/market-cli register --name xxx --description xxx --source open-claw`（凭证需重新注册，存 `~\.lobehub-market\credentials.json`） |
| Python 3.12 | fetch_skills.py 批量抓取、msilib 校验 | `python --version` | python.org |
| tar / Expand-Archive | 解压 | `tar --version` | 自带 |
| fetch_skills.py | GitHub skill 仓库批量抓取 | `Test-Path <opencode配置目录>\tools\fetch_skills.py` | 从原机复制（含 PLAN 映射表） |
| GitHub 镜像渠道 | 直连不通时替代 | `curl -sL -m 20 -o NUL -w %{http_code} https://gh-proxy.com/` | 无需装（渠道失效换下一个） |

**移植说明**：核心 = curl + 镜像渠道（无安装要求）+ market-cli（需重新注册凭证）。

## LobeHub CLI 用法（本机凭证已注册）

```
& node "<npx缓存>\@lobehub\market-cli\dist\cli.js" skills search --q "关键词"
（同上）skills install <identifier> --dir <目录>
（npx 方式：& "<Node目录>\npx.cmd" -y @lobehub/market-cli ...；token 失效时先 auth refresh）
```
- search/view/install 对 token 要求不同；view 报 invalid_token 时直接 install 通常可行

## skills.sh 绕过细节

- API 端点（`/api/v1/skills/*`）全部需要 Vercel OIDC token
- sitemap 链路：`sitemap.xml` → `sitemap-skills-1/2.xml`（共 2 万条 skill URL）→ 本地正则过滤 ✓
- curl 直接抓页面被反爬（14 字节），必须用 webfetch
- 大仓库批量：ghproxy tarball → 递归找 SKILL.md → 装入 modules → 改名 GUIDE.md

## skillsmp.com 绕过细节

- curl 被反爬（几百字节），必须用 webfetch
- 分类入口：`/zh/categories/documents`、`/zh/occupations`（SOC 职业）
- 多详情页并行抓取时用 general 子代理批量处理（每页 SKILL.md 完整，直接落盘 GUIDE.md）

## GitHub skill 仓库批量安装

- 批量脚本：`python <opencode配置目录>\tools\fetch_skills.py [仓库名过滤]`
- 大仓库装完后按白名单清理非目标模块
- 已知失败：超大仓库下载超时、超长路径（Windows 路径限制）、部分仓库 tarball 截断（改走 skillsmp 详情页抓取）

## 网页内容抓取细节

- SSR 页面：webfetch 直接取；JS 渲染页面：换 sitemap/JSON 接口/移动端页面
- **curl 空响应/403 时换 UA 头**（3gpp.org 等实测）：`curl.exe -A "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36" -s -L URL`
- **下载前先找"索引页"**：真实 URL 常在索引页（如 DynaReport）里；直接猜路径 403 时先抓上级目录列表提取 `href` 清单
