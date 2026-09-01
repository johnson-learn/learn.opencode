# program_skill 参考：工具与环境全量配置（移植到新机器时先逐项检查）

## 🛠 工具依赖清单

| 工具 | 用途 | 本机位置/版本 | 检查命令 | 缺失时安装 |
|---|---|---|---|---|
| WSL2 + Ubuntu 22.04 | 默认编程环境（编译/运行/调试） | 注册名 `Ubuntu`，vhdx 在 `<WSL安装目录>\Ubuntu2`（旧 `<WSL安装目录>\Ubuntu` 为残留） | `wsl -l -v`（应显示 Ubuntu Running/Stopped, VERSION 2） | 见离线安装包目录下《WSL安装步骤说明书.html》（MSI 247MB + rootfs 325MB 离线包） |
| Linux 工具链 | C/C++/脚本开发 | gcc/g++ 11.4、make 4.3、cmake 3.22、ninja 1.10、gdb 12.1、valgrind 3.18、strace 5.16、python3.10+pip、perl 5.34、jq 1.6、git 2.34、openssh-client | `wsl -d Ubuntu -e bash -c "gcc --version && g++ --version && gdb --version && python3 --version"` | `wsl -d Ubuntu -e bash -c "apt-get install -y build-essential gdb valgrind cmake ninja-build python3 python3-pip perl jq git openssh-client"`（apt 已换清华源） |
| w64devkit | Windows 原生编译备选（winpthreads） | `C:\w64devkit\w64devkit\bin\gcc.exe`（GCC 16.2.0） | `& "C:\w64devkit\w64devkit\bin\gcc.exe" --version` | gh-proxy.com 下载 `w64devkit-x64-2.9.1.7z.exe` 自解压到盘根 |
| core dump 配置 | C 崩溃调试 | `sysctl kernel.core_pattern=<用户目录>/cores/core.%e.%p` + `ulimit -c unlimited` | `wsl -d Ubuntu -e bash -c "cat /proc/sys/kernel/core_pattern"` | WSL 内执行配置命令（重启后需重配或写入 /etc/sysctl.d/） |
| WSL 开机自启 | 保持实例运行（防 60s idle 停止） | 计划任务 `WSL-AutoStart`（sleep 常驻） | `schtasks /query /tn "WSL-AutoStart"` | 管理员：`schtasks /create /tn "WSL-AutoStart" /tr "wsl.exe -d Ubuntu -e bash -c 'sleep 2000000000'" /sc onlogon` |
| MinGW 6.3 | ⚠ 无 pthread，禁用 | `<工具目录>MinGW` | — | 不安装，多线程用 w64devkit/WSL |

**移植说明**：核心 = WSL2（离线安装包在两本说明书同目录）+ Linux 工具链（apt 一条命令重建）；w64devkit 是备选；源码目录约定 `<源码目录>\`（新机器自行创建）。

## WSL 环境全量配置（本机已验证）

- **标准调用**：`wsl -d Ubuntu -e bash -c "cd /mnt/e/<路径> && gcc -O2 -g x.c -o x && ./x"`；多线程加 `-pthread`
- **已装工具链（全量）**：
  - 编译器：gcc/g++ 11.4
  - 构建：make 4.3 / cmake 3.22 / ninja 1.10 / pkg-config / autoconf / automake / libtool
  - 调试分析：gdb 12.1 / valgrind 3.18 / strace 5.16 / htop 3.0
  - 脚本：python3 3.10 + pip + venv / perl 5.34 / jq 1.6 / bash / sed / awk
  - 开发库：libssl-dev、zlib1g-dev、libsqlite3-dev、libreadline-dev、libncurses-dev、libffi-dev、libbz2-dev、liblzma-dev、libcurl4-openssl-dev
  - 其它：git 2.34 / openssh-client / curl / wget / tree / zip / unzip
  - apt 已换清华源（`mirrors.tuna.tsinghua.edu.cn`）
- **core dump 坑**：WSL 默认 `core_pattern=|/wsl-capture-crash` 不落盘；且 /mnt 上内核写不出 core。使用前先 `ulimit -c unlimited && sysctl -w kernel.core_pattern=<用户目录>/cores/core.%e.%p && mkdir -p <用户目录>/cores`，崩溃后 `gdb ./prog <用户目录>/cores/core.*` 回溯
- **磁盘映射**：Linux→Windows 盘 `/mnt/c`、`/mnt/e`；Windows→Linux 用 `\\wsl$\Ubuntu\...`（实例 Running 时可用；映射盘符用资源管理器手动映射，net use 走不通 9P）
- **开机自启**：计划任务 `WSL-AutoStart`（登录时运行 `wsl -d Ubuntu -e bash -c "sleep 2000000000"` 保持实例，防止 60s idle 自动停止）。删除：`schtasks /delete /tn "WSL-AutoStart" /f`（管理员）
- **WSL 离线安装链路（已验证）**：gh-proxy.com 下 WSL MSI（需 msilib 校验完整性）→ 提权 msiexec → 清华镜像 wsl rootfs（列目录找真实文件名，带 `-ubuntuXX.XXlts` 后缀）→ `wsl --import`；官方 wsl --install 慢是因为发行版清单在 raw.githubusercontent.com
- **WSLg 图形**：本机不可用（向日葵 OrayIddDriver + Intel 集显 vGPU 冲突，dxg ioctl -22，RemoteApp 窗口 visible=False）；GUI 需求改用 Windows 侧编辑器

## 备选 Windows 原生编译

- **w64devkit 2.9.1**（便携 GCC 16.2.0 + winpthreads，路径 `C:\w64devkit\w64devkit\bin`，用时 `$env:PATH = "C:\w64devkit\w64devkit\bin;" + $env:PATH`；链接 winmm 需 `-lwinmm`）
- MinGW 6.3.0（<工具目录>MinGW）无 pthread 勿用
- **Linux C 验证套路**：代码加 `#ifdef _WIN32` 适配层（localtime_r→localtime_s、clock_nanosleep→Sleep(timeBeginPeriod)），w64devkit 编译通过即逻辑正确；Windows Sleep 粒度极限 ~1ms，0.5ms 级精确节拍仅 Linux 上 clock_nanosleep(TIMER_ABSTIME) 可达

## 工具安装规则与窗口管理

- 安装新工具遵循用户规则：200M 以内直接装，超过先询问；Linux 内装包走 `apt install`（非 yum，Ubuntu 是 Debian 系）
- **Windows 提权子进程窗口管理（✓ 2026-08-28 实测）**：`Start-Process powershell -Verb RunAs` 弹的提权进程，主进程非管理员时 `Stop-Process` 会静默失败 → 窗口残留。可靠停止方案 = **信号文件自毁**：子进程循环每 ~400ms 轮询 stop 信号文件（`Test-Path $stopF → exit`），主进程写信号文件即触发退出；`Stop-Process` 仅作兜底；启动参数**不加 `-NoExit`**（否则 exit 后窗口仍停留）。信号文件放 `$env:TEMP`（双方皆可写），新子进程启动前先清理残留信号
