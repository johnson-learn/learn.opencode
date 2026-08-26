# opencode 工作环境迁移包

> 本仓库 = 5 个全局 skill（3gpp_skill / files_skill / find_skill / program_skill / update_skill）+ 全局配置 + 辅助脚本 + 一键安装脚本。
> 目标：任何一台新的 Windows 办公电脑，克隆本仓库后运行一个脚本，即可复现完整工作环境。

## 目录结构

```
copy\
├── README.md                  ← 本文件
├── INSTALL.md                 ← 新电脑安装指南（详细步骤）
├── REQUIREMENTS.md            ← 依赖清单与下载途径（官方 + 国内镜像）
├── .gitignore                 ← 排除大文件/本地数据
├── opencode\                  ← 部署到 ~\.config\opencode\ 的全局配置
│   ├── opencode.jsonc            全局配置（instructions 引用）
│   ├── instructions.md           全局技能触发规则与进化协议
│   ├── evolution.md              技能进化记录
│   ├── package.json              skill-banner 插件依赖
│   ├── plugins\skill-banner.js   opencode 插件（会话创建时 toast 展示全局技能清单）
│   └── skills\                   5 个全局 skill（SKILL.md + modules 子技能库）

│   ├── tests\                      测试用例（skill 结构校验 / 插件 / 路径转换 / 双向同步，随仓库同步）
│   ├── tools\                      修炼工具（path_convert / inject_skills / fetch_skills / slim_skills 等）
│   └── tools-manifest.md           工具总清单（唯一权威，分类 A~G + 本机配置 + 待补充）
│       ├── 3gpp_skill\           3GPP 移动通信标准专家
│       ├── files_skill\          文件识别/OCR/公式/文档处理
│       ├── find_skill\           网络资源获取与镜像加速
│       ├── program_skill\        编程开发（默认 WSL Linux）
│       └── update_skill\         技能同步更新（本机进化→GitHub→其它机器移植闭环）
├── scripts\                   ← 部署到 %LOCALAPPDATA%\Temp\opencode\ 的辅助脚本
│   ├── extract-docx.ps1          提取 docx 文本
│   ├── extract-doc.ps1           提取 doc 文本
│   ├── ocr.ps1                   Windows OCR（剪贴板）
│   ├── check-headless.ps1        Chrome headless 控制台校验
│   ├── check-overlap.ps1         SVG 文字重叠检测
│   ├── check-calc.ps1            CDP 模拟点击计算器校验
│   ├── color-asn1.py             ASN.1 着色工具
│   └── inject_skills.py          新项目 skill 注入脚本
├── setup\
│   ├── setup-windows.ps1         一键安装（主脚本）
│   ├── install-wsl.ps1           WSL2 + Ubuntu 22.04
│   └── download-specs.ps1        下载 3GPP 文档库
└── data\                      ← 本地数据（不入 git）
    └── README.md                 3GPP 文档等大文件的获取说明
```

## 新电脑三步上手

```powershell
# 1. 克隆仓库
git clone <你的GitHub仓库地址> copy
cd copy/setup

# 2. 一键安装（按需加开关：-SkipWsl -SkipPip 等；国内网络加 -UseChinaMirror）
powershell.exe -NoProfile -ExecutionPolicy Bypass -File setup\setup-windows.ps1 -UseChinaMirror

# 3. 重启终端，opencode 启动即带 5 个全局 skill
```

详细步骤与手动安装备查：见 `INSTALL.md`；依赖清单与下载途径：见 `REQUIREMENTS.md`。

## 上传 GitHub 前注意

1. `data\`、`opencode\node_modules\` 等大目录已被 `.gitignore` 排除（3GPP 文档 300+ MB 不建议入 git，用 `download-specs.ps1` 新机重下或网盘拷贝）。
2. 路径可移植由占位符体系保证（path_convert.py 双向转换，tools-manifest.md 为工具权威源）；新机部署后运行 `python <opencode配置目录>\tests\skill_validate.py` 与其余测试用例自检（见 tests\README.md）。
3. 仓库内不含任何密钥/凭证（skill 规范已保证）。
