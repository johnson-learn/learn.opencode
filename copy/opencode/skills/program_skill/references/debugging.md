# program_skill 参考：C 调试指南（gdb / valgrind / core dump 排查路径）

## 1. 段错误排查标准路径

```bash
# ① 编译带调试信息 + 地址消毒（首选一步到位）
gcc -g -O0 -fsanitize=address -o prog prog.c
./prog                                    # ASan 直接报泄漏/越界位置

# ② 无 ASan 时：core dump 回溯
ulimit -c unlimited
sysctl -w kernel.core_pattern=<用户目录>/cores/core.%e.%p
mkdir -p <用户目录>/cores
./prog                                    # 崩溃生成 core 文件
gdb ./prog <用户目录>/cores/core.*
(gdb) bt full                             # 回溯完整调用栈与局部变量

# ③ 交互式 gdb 定位
gdb ./prog
(gdb) run
(gdb) bt
(gdb) frame 3
(gdb) print variable
(gdb) info locals
```

## 2. core dump 配置坑（WSL 实测）

- WSL 默认 `core_pattern=|/wsl-capture-crash`：core 被系统进程吃掉、不落盘
- **/mnt 上内核写不出 core**（9P 文件系统限制）：core_pattern 必须指向 Linux 内路径（如 `/cores`）或用 Windows 绝对路径（`<工具目录>Users\...` 形式经 WSL 互操作可以写入）；写入 Windows 盘时 gdb 加载用 `gdb ./prog <Windows路径>`（drvfs 直接可读）
- 重启后配置丢失：写入 `/etc/sysctl.d/99-core.conf` 持久化：`echo 'kernel.core_pattern=C:\Users\<用户名>\cores\core.%e.%p' | sudo tee /etc/sysctl.d/99-core.conf && sudo sysctl -p /etc/sysctl.d/99-core.conf`
- 检查：`cat /proc/sys/kernel/core_pattern`（非 wsl-capture-crash 即生效）

## 3. 内存泄漏定位（valgrind）

```bash
valgrind --leak-check=full --show-leak-kinds=all ./prog
# 输出解读：definitely lost=真泄漏必须修；indirectly lost=结构体级泄漏；
#           possibly lost=可能有；still reachable=退出时未释放（通常可接受）
valgrind --tool=helgrind ./prog    # 数据竞争检测（多线程）
```

## 4. 竞态与性能

```bash
gcc -g -O1 -fsanitize=thread -o prog prog.c && ./prog   # TSan 数据竞争
perf stat ./prog                                        # 性能统计（CPU/分支/缓存）
strace -c ./prog                                        # 系统调用耗时分布
```

## 5. 死锁/挂起排查

```bash
# 挂起时另开终端 attach：
gdb -p <PID>
(gdb) thread apply all bt          # 所有线程栈——锁在哪一目了然
```

## 铁律

1. 先 ASan 后 gdb：ASan 一步定位越界/泄漏；只有 ASan 不可用才走 core+bt
2. 所有线程栈 `thread apply all bt` 是死锁排查第一步
3. valgrind 的 definitely lost 必须清零才算内存安全交付
