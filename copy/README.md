# opencode 工作环境迁移包

> 本仓库 = 6 个全局 skill（3gpp_skill / files_skill / find_skill / program_skill / update_skill / evolution_skill）+ 全局配置 + 进化门禁 + 辅助脚本 + 一键安装脚本。
> 目标：任何一台新的 Windows 办公电脑，克隆本仓库后运行一个脚本，即可复现完整工作环境。

## 目录结构

```
copy\
├── README.md                  ← 本文件
├── INSTALL.md                 ← 新电脑安装指南（详细步骤）
├── REQUIREMENTS.md            ← 依赖清单与下载途径（官方 + 国内镜像）
├── .gitignore                 ← 排除大文件/本地数据/临时文件
├── opencode\                  ← 部署到 ~\.config\opencode\ 的全局配置
│   ├── opencode.jsonc            全局配置
│   ├── AGENTS.md                 全局铁律（8 条，每会话必达）
│   ├── instructions.md           详版协议（触发规则与进化协议）
│   ├── regedit.md                全体系注册表（组件加载方式 A~H 登记）
│   ├── docs-sync.md              配套文档同步映射表
│   ├── tools-manifest.md         工具总清单（唯一权威，分类 A~G + 待补充）
│   ├── package.json              skill-banner 插件依赖
│   ├── plugins\                 插件（会话 toast + 进化门禁触发）
│   ├── skills\                  显式触发 skill（5 个，SKILL.md + modules 子技能库）
│   │   ├── 3gpp_skill\          3GPP 移动通信标准专家
│   │   ├── files_skill\         文件识别/OCR/公式/文档处理
│   │   ├── find_skill\          网络资源获取与镜像加速
│   │   ├── program_skill\       编程开发（默认 WSL Linux）
│   │   ├── update_skill\        技能双向同步（五步：吸收远端→修改→自测→弹窗确认→推送）
│   │   └── default\evolution_skill\   进化执行器（默认触发，含进化规则 evolution.md 与流水 evolution_log.txt）
│   ├── tests\                   测试用例（10 套 229 项，随仓库同步）
│   └── tools\                   修炼工具（evolution_gate 进化门禁 / path_convert / inject_skills 等）
├── scripts\                   ← 部署到 %LOCALAPPDATA%\Temp\opencode\ 的辅助脚本
├── setup\
│   ├── setup-windows.ps1         一键安装（主脚本）
│   ├── install-wsl.ps1           WSL2 + Ubuntu 22.04
│   └── download-specs.ps1        下载 3GPP 文档
└── （git 根另有） doc\            使用说明书（WSL/编译/GitHub，静态文档）
```

## 新电脑三步上手

```powershell
# 1. 克隆仓库
git clone <你的GitHub仓库地址>
进入\copy\setup

# 2. 一键安装（按需加开关：-SkipWsl -SkipPip 等；国内网络加 -UseChinaMirror）
powershell.exe -NoProfile -ExecutionPolicy Bypass -File setup-windows.ps1 -UseChinaMirror

# 3. 重启终端，opencode 启动即带 6 个全局 skill
```

详细步骤与手动安装备查：见 `INSTALL.md`；依赖清单与下载途径：见 `REQUIREMENTS.md`。

## 同步与进化机制（双向多机）

- 本仓库支持**多机双向同步**：每台有权限的机器运行 update_skill（五步流程，推送前弹窗确认）维护框架
- 无权限机器只需 `git pull`（或重新克隆）获取更新，**不需要执行 update_skill 修改**
- 进化门禁：每次会话结束由 evolution_gate.py 自动执行固化检查（流水兜底/自动测试），不依赖人工

## 上传 GitHub 前注意

1. `data\`、`node_modules\` 等大目录已被 `.gitignore` 排除（3GPP 文档 300+ MB 不建议入 git，用 `download-specs.ps1` 新机重下或网盘拷贝）
2. 路径可移植由占位符体系保证（path_convert.py 双向转换，tools-manifest.md 为工具权威源）；新机部署后运行 `python <opencode配置目录>\tests\skill_validate.py` 与其余测试用例自检（见 tests\README.md）
3. 仓库内不含任何密钥/凭证
