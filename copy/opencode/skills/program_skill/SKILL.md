---
name: program_skill
description: C 编程与编译专家技能（全局 skill，仅显式触发，不靠关键词自动调用）。Use ONLY when 用户消息显式包含 "program_skill：" 或 "program_skill:"，或以 "program_skill&"、"program_skill " 与其他技能名并列后跟冒号——冒号后为用户任务。加载后执行任务：C 语言开发（嵌入式/系统级/网络通信/协议栈）、C 编译脚本生成（Batch/PS/Bash 动态编译）、构建工具链（GCC/CMake/Make/arm-none-eabi）、静态分析与内存安全、调试（gdb/valgrind/core dump）与性能优化、C 单元测试；C++/Shell/Python 仅作为 C 构建与验证的辅助。默认在 WSL Linux 环境（Ubuntu 22.04）编译运行，备选 w64devkit Windows 原生编译。普通消息仅提及编程/C 代码但无 "program_skill：" 前缀时，不调用本技能。
collaborates_with:
  - files_skill
  - find_skill
---

# program_skill —— C 编程与编译

## 典型触发场景

- "program_skill：写一个 C 程序（多线程+链表+消息队列）并编译运行"
- "program_skill：这个段错误怎么排查（gdb/valgrind/core dump）"
- "program_skill：生成 C 编译脚本（多文件自动依赖）"
- "program_skill：CMake 工程搭建与交叉编译（arm-none-eabi）"
- "program_skill：给这段 C 代码写单元测试（Unity/CTest + 覆盖率）"

## 不处理的边界

- 不做文档/PDF/图片处理（推荐 files_skill）
- 不做 3GPP 协议分析（推荐 3gpp_skill）
- 不做 Go/Rust/Java/前端/后端业务开发（本技能聚焦 C；需要时另建独立 skill）
- 默认 WSL Linux 环境编译运行；Windows 原生需求须用户明确（备选 w64devkit）

## 🛠 工具依赖清单（摘要，详版见 references/tools.md）

| 工具 | 用途 | 检查命令 |
|---|---|---|
| WSL2 + Ubuntu 22.04 | 默认编译/运行/调试环境 | `wsl -l -v` |
| Linux 工具链 | gcc 11.4/cmake 3.22/gdb 12.1/valgrind/strace | `wsl -d Ubuntu -e bash -c "gcc --version && gdb --version"` |
| w64devkit | Windows 原生 GCC 备选（winpthreads） | `& "C:\w64devkit\w64devkit\bin\gcc.exe" --version` |

**移植说明**：核心 = WSL2 + Linux 工具链（apt 一条命令重建）；w64devkit 备选；源码目录约定 `<源码目录>\`（新机器自行创建，详见 references/tools.md）。

## 通用输出规则

- **语言跟随提问**：用户以何种语言提问，思考、回答、输出就以何种语言；代码、命令、报错信息、字段名等必要原文保持原样不翻译
- **含"输出"二字 → HTML 交付**：最终答案以 HTML 文件输出（代码高亮、规范排版），内容详细不限篇幅；保存到提问时所在工作目录并浏览器打开

## 处理流程

1. 确认任务类型：写码 / 编译脚本 / 构建系统 / 静态分析 / 调试 / 测试 / 性能
2. 按路由表先读 `modules/<目录>/GUIDE.md` 再按其说明执行
3. **编程任务默认 WSL Linux 环境**：编译运行一律 `wsl -d Ubuntu -e bash -c "..."`，源码固定放 `<源码目录>\`（Linux 内 `/mnt/e/opencode_code/`）；多线程加 `-pthread`
4. 未命中任何子技能时，按通用 C 实践直接作答；项目骨架复制 `templates/c-project/`
5. 需要联网获取依赖/镜像/资料联动 find_skill；文档处理联动 files_skill

## 路由表（按任务，4 族）

### ① C 核心族（首选）
| 任务 | 子技能（modules 下目录） | 说明 |
|---|---|---|
| C 编译脚本生成（多文件自动依赖） | `c-compile-script-generator` | ★最高频：Batch/PS/Bash 动态编译脚本 |
| GCC 嵌入式工程构建 | `c-gcc-embedded-build` | CMake + arm-none-eabi，扫描/编译/ELF 分析 |
| 静态分析 | `c-static-analysis` | cppcheck/clang-tidy/GCC analyzer/MISRA-C |
| 嵌入式 C 开发 | `c-embedded-systems` | STM32/ESP32/FreeRTOS/裸机/实时 |
| 内存安全 | `c-memory-safety-patterns` | 所有权/资源管理/防泄漏模式 |

### ② C++ 扩展族（仅取对 C 有用部分）
| 任务 | 子技能 | 说明 |
|---|---|---|
| 编译链接标志 | `cpp-compiler-flags` | -O/-march/LTO/PGO，C 同样适用 |
| 编码标准 | `cpp-coding-standards` | 取适用 C 的部分 |
| 测试框架 | `cpp-testing` | GoogleTest/CTest/覆盖率/sanitizers，C 单测同样适用 |

### ③ Shell 服务族（为 C 构建流程服务）
| 任务 | 子技能 | 说明 |
|---|---|---|
| Linux 构建脚本 | `shell-linux-shell-scripting` | 环境搭建/自动化 |
| Bash 终端 | `shell-bash-linux` | 编译命令组合/管道/错误处理 |
| 防御性脚本 | `shell-bash-defensive-patterns` | 编译脚本健壮性/CI |

### ④ 通用工程族（C 项目工程化）
| 任务 | 子技能 | 说明 |
|---|---|---|
| 多线程架构 | `general-threading-architecture` | 核心隔离/SPSC/低延迟 |
| AI 结对编程 | `general-pair-programming` | TDD/代码审查/安全扫描 |

## 核心铁律（逐条可检验）

1. **C 代码必须实编译实运行验证**：写出的 C 代码必须在 WSL 里 `gcc -Wall -Wextra` 无警告编译并实际跑通，禁止只给代码不验证
2. **内存与线程安全优先**：涉及指针/动态内存/多线程时，主动加边界检查与防泄漏措施；多线程必须 `-pthread`
3. **编译脚本幂等可重入**：生成的编译脚本必须支持重复执行、自动依赖扫描、失败非零退出
4. **环境双轨**：Linux 代码加 `#ifdef _WIN32` 适配层，w64devkit 编译通过即逻辑正确（0.5ms 级精确节拍仅 Linux 可达）
5. **错误处理显式**：系统调用/库函数返回值必须检查，禁止忽略错误码

## 环境注意（摘要，详版见 references/tools.md）

- 默认 WSL2 + Ubuntu 22.04.5；标准调用 `wsl -d Ubuntu -e bash -c "cd /mnt/e/<路径> && gcc -O2 -g x.c -o x && ./x"`
- core dump 需先配置（/mnt 写不出 core 的坑）：`ulimit -c unlimited && sysctl -w kernel.core_pattern=...`，详见 references/debugging.md
- 备选 w64devkit 2.9.1（Windows 原生 GCC 16.2 + winpthreads）；MinGW 6.3 无 pthread 勿用
- 安装新工具：200M 以内直接装，超过先询问；Linux 内 `apt install`

## 详细知识索引（按需读取，不随入口注入）

- 详见 `references/tools.md`（WSL/w64devkit/工具链全量配置与移植）
- 详见 `references/compile-scripts.md`（动态编译脚本模板库）
- 详见 `references/debugging.md`（gdb/valgrind/core dump 排查）
- 详见 `references/coding-standards.md`（C 编码规范与错误处理）
- 详见 `references/unit-test.md`（Unity/CTest 用例与覆盖率）
- 详见 `references/embedded-build.md`（交叉编译/工具链文件/OpenOCD）
- 详见 `references/deploy-remote.md`（ssh/rsync 远程编译运行与日志回传）
- 详见 `references/build-systems.md`（Makefile 多目录/条件编译/平台判断）
- 工程骨架：`templates/c-project/`（新项目直接复制）

## 本 skill 经验索引（分域健康监控台账）

> 本 skill 相关经验在 `<opencode配置目录>\skills\default\evolution_skill\evolution_log.txt` 中带「归属：program_skill」字段的条目；active 条目摘要：编译脚本三版套路（Bash/Batch/PS）、WSL 环境全量配置、core dump 落盘坑、w64devkit 双轨验证、Windows 提权子进程窗口管理。低活性/待验证条目由经验健康引擎（gate --check）按归属分组提示。
