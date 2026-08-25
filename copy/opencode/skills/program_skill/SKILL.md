---
name: program_skill
description: 编程开发综合技能（全局 skill，仅显式触发，不靠关键词自动调用）。Use ONLY when 用户消息显式包含 "program_skill：" 或 "program_skill:"，或以 "program_skill&"、"program_skill " 与其他技能名并列后跟冒号——冒号后为用户任务。加载后执行任务：C/C++/Python/Shell/Java/JavaScript/TypeScript/Go/Rust 等编程语言开发、前端开发（HTML/CSS/React/Vue）、后端开发（数据库/API/框架）、构建部署、代码质量与重构、编程学习等。默认在 WSL Linux 环境（Ubuntu 22.04）编译运行。普通消息仅提及编程/代码但无 "program_skill：" 前缀时，不调用本技能。
---

# program_skill —— 编程开发综合技能

## 🛠 工具依赖清单（移植到新机器时先逐项检查）

| 工具 | 用途 | 本机位置/版本 | 检查命令 | 缺失时安装 |
|---|---|---|---|---|
| WSL2 + Ubuntu 22.04 | 默认编程环境（编译/运行/调试） | 注册名 `Ubuntu`，vhdx 在 `E:\WSL\Ubuntu2`（旧 E:\WSL\Ubuntu 为残留） | `wsl -l -v`（应显示 Ubuntu Running/Stopped, VERSION 2） | 见 `E:\software\wls\WSL安装步骤说明书.html`（MSI 247MB + rootfs 325MB 离线包） |
| Linux 工具链 | C/C++/脚本开发 | gcc/g++ 11.4、make、cmake 3.22、ninja、gdb 12.1、valgrind、strace、python3.10+pip、perl、jq、git、openssh | `wsl -d Ubuntu -e bash -c "gcc --version && g++ --version && gdb --version && python3 --version"` | `wsl -d Ubuntu -e bash -c "apt-get install -y build-essential gdb valgrind cmake ninja-build python3 python3-pip perl jq git openssh-client"`（apt 已换清华源） |
| w64devkit | Windows 原生编译备选（winpthreads） | `C:\w64devkit\w64devkit\bin\gcc.exe`（GCC 16.2.0） | `& "C:\w64devkit\w64devkit\bin\gcc.exe" --version` | gh-proxy.com 下载 `w64devkit-x64-2.9.1.7z.exe` 自解压 |
| core dump 配置 | C 崩溃调试 | `sysctl kernel.core_pattern=/root/cores/core.%e.%p` + `ulimit -c unlimited` | `wsl -d Ubuntu -e bash -c "cat /proc/sys/kernel/core_pattern"`（应非 wsl-capture-crash） | WSL 内执行配置命令（重启后需重配或写入 /etc/sysctl.d/） |
| WSL 开机自启 | 保持实例运行（防 60s idle 停止） | 计划任务 `WSL-AutoStart`（sleep 常驻） | `schtasks /query /tn "WSL-AutoStart"` | 管理员：`schtasks /create /tn "WSL-AutoStart" /tr "wsl.exe -d Ubuntu -e bash -c 'sleep 2000000000'" /sc onlogon` |
| MinGW 6.3 | ⚠ 无 pthread，禁用 | `C:\MinGW` | — | 不安装，多线程用 w64devkit/WSL |

**移植说明**：核心 = WSL2（离线安装包在 E:\software\wls，含两本说明书）+ Linux 工具链（apt 一条命令重建）；w64devkit 是备选；源码目录约定 `E:\opencode_code\`（新机器自行创建）。

本技能是**唯一注册入口**，按语言/功能分类聚合编程子技能（位于 `modules/`，资源库不独立注册）。

## 分类体系（modules 目录前缀）

| 前缀 | 类别 |
|---|---|
| `c-*` | C 语言 |
| `cpp-*` | C++ |
| `py-*` | Python |
| `shell-*` | Shell/脚本 |
| `js-*` | JavaScript/TypeScript |
| `frontend-*` | 前端框架（React/Vue/CSS） |
| `backend-*` | 后端（数据库/API/服务） |
| `lang-*` | 其它语言（Go/Rust/Java/...） |
| `general-*` | 通用工程（质量/重构/调试/构建） |

## 通用输出规则（全部任务遵守）

- **语言跟随提问**：用户以何种语言提问，思考、回答、输出就以何种语言（中文提问→中文回答，英文提问→英文回答）；代码、命令、报错信息、字段名等必要原文保持原样不翻译
- **含"输出"二字 → HTML 交付**：提问中出现"输出"二字时，最终答案必须以 HTML 文件输出（代码高亮、规范排版），内容详细、不限字数篇幅；HTML 保存到提问时所在工作目录并浏览器打开（用户另行指定目录时按用户指定）

## 处理流程

1. 确认任务语言/类别 → 路由到对应前缀的子技能，**先读 `modules/<目录>/GUIDE.md` 再按其说明执行**
2. **编程任务默认使用 WSL Linux 环境**（用户已确认）：编译、运行、调试一律走 `wsl -d Ubuntu -e bash -c "..."`，**源码固定放 `E:\opencode_code\`**（Windows 盘，Linux 内经 `/mnt/e/opencode_code/` 访问）
3. 未命中任何子技能时，按通用编程实践直接作答
4. 需要联网获取依赖/镜像/资料时联动 find_skill；需要文档处理时联动 files_skill

## 路由表（按语言/功能）

| 类别 | 子技能（modules 下目录） | 说明 |
|---|---|---|
| C 语言 | `c-gcc-embedded-build` | GCC 嵌入式工程构建（CMake + arm-none-eabi-gcc，扫描/编译/重建/ELF 大小分析） |
| C 语言 | `c-compile-script-generator` | C 编译脚本生成器（Batch/PowerShell/Bash 的 GCC 动态编译脚本） |
| C 语言 | `c-static-analysis` | 嵌入式 C/C++ 静态分析（cppcheck/clang-tidy/GCC analyzer/MISRA-C） |
| C 语言 | `c-embedded-systems` | 嵌入式 C（STM32/ESP32/FreeRTOS/裸机/功耗优化/实时系统） |
| C 语言 | `c-memory-safety-patterns` | 内存安全（RAII/所有权/智能指针/资源管理，C/C++/Rust 通用） |
| C++ | `cpp-compiler-flags` | C++ 编译/链接标志（GCC/Clang/MSVC/MinGW/IntelLLVM，-O/-march/LTO/PGO） |
| C++ | `cpp-coding-standards` | C++ Core Guidelines 编码标准（现代/安全/惯用） |
| C++ | `cpp-testing` | C++ 测试（GoogleTest/CTest、覆盖率、sanitizers） |
| Shell | `shell-linux-shell-scripting` | Linux 生产脚本（系统管理/监控/备份/用户管理模板） |
| Shell | `shell-bash-linux` | Bash/Linux 终端模式（关键命令/管道/错误处理） |
| Shell | `shell-bash-defensive-patterns` | 防御性 Bash（生产级脚本/CI/CD/容错） |
| 其它语言 | `lang-go-concurrency` | Go 并发（goroutine/channel/sync/context） |
| 通用工程 | `general-threading-architecture` | 系统级线程架构（拓扑感知线程固定/核心隔离/SPSC/低延迟） |
| 通用工程 | `general-pair-programming` | AI 结对编程（驱动/导航模式、TDD、代码审查、安全扫描） |
| Python | `py-*` | 待安装 |
| JavaScript/TS | `js-*` | 待安装 |
| 前端 | `frontend-*` | 待安装 |
| 后端 | `backend-*` | 待安装 |

## 环境注意

- **编程默认环境：WSL Linux（用户已确认）**。本机 WSL2 + Ubuntu 22.04.5 LTS @ E:\WSL\Ubuntu（实际 vhdx 在 E:\WSL\Ubuntu2 的注册实例）
  - 已装工具链（全量）：
    - 编译器：gcc/g++ 11.4
    - 构建：make 4.3 / cmake 3.22 / ninja 1.10 / pkg-config / autoconf / automake / libtool
    - 调试分析：gdb 12.1 / valgrind 3.18 / strace 5.16 / htop 3.0
    - 脚本：python3 3.10 + pip + venv / perl 5.34 / jq 1.6 / bash / sed / awk
    - 开发库：libssl-dev、zlib1g-dev、libsqlite3-dev、libreadline-dev、libncurses-dev、libffi-dev、libbz2-dev、liblzma-dev、libcurl4-openssl-dev
    - 其它：git 2.34 / openssh-client / curl / wget / tree / zip / unzip
    - apt 已换清华源（`mirrors.tuna.tsinghua.edu.cn`）
  - 标准调用：`wsl -d Ubuntu -e bash -c "cd /mnt/e/<路径> && gcc -O2 -g x.c -o x && ./x"`；多线程加 `-pthread`
  - **core dump**：WSL 默认 `core_pattern=|/wsl-capture-crash` 不落盘；且 /mnt 上内核写不出 core。使用前先 `ulimit -c unlimited && sysctl -w kernel.core_pattern=/root/cores/core.%e.%p && mkdir -p /root/cores`，崩溃后 `gdb ./prog /root/cores/core.*` 回溯
  - **磁盘映射**：Linux→Windows 盘 `/mnt/c`、`/mnt/e`；Windows→Linux 用 `\\wsl$\Ubuntu\...`（实例 Running 时可用；映射盘符用资源管理器手动映射，net use 走不通 9P）
  - **开机自启**：计划任务 `WSL-AutoStart`（登录时运行 `wsl -d Ubuntu -e bash -c "sleep 2000000000"` 保持实例，防止 60s idle 自动停止）。删除：`schtasks /delete /tn "WSL-AutoStart" /f`（管理员）
  - WSL 离线安装链路（已验证）：gh-proxy.com 下 WSL MSI（需 msilib 校验完整性）→ 提权 msiexec → 清华镜像 wsl rootfs（列目录找真实文件名，带 `-ubuntuXX.XXlts` 后缀）→ `wsl --import`；官方 wsl --install 慢是因为发行版清单在 raw.githubusercontent.com
  - WSLg 图形：本机不可用（向日葵 OrayIddDriver + Intel 集显 vGPU 冲突，dxg ioctl -22，RemoteApp 窗口 visible=False）；GUI 需求改用 Windows 侧编辑器
- 备选 Windows 原生编译：**w64devkit 2.9.1**（便携 GCC 16.2.0 + winpthreads，路径 `C:\w64devkit\w64devkit\bin`，用时 `$env:PATH = "C:\w64devkit\w64devkit\bin;" + $env:PATH`；链接 winmm 需 `-lwinmm`）；MinGW 6.3.0（C:\MinGW）无 pthread 勿用
- Linux C 验证套路：代码加 `#ifdef _WIN32` 适配层（localtime_r→localtime_s、clock_nanosleep→Sleep(timeBeginPeriod)），w64devkit 编译通过即逻辑正确；Windows Sleep 粒度极限 ~1ms，0.5ms 级精确节拍仅 Linux 上 clock_nanosleep(TIMER_ABSTIME) 可达
- 中文输出优先；文件编码 UTF-8
- 安装新工具遵循用户规则：200M 以内直接装，超过先询问；Linux 内装包走 `apt install`（非 yum，Ubuntu 是 Debian 系）
