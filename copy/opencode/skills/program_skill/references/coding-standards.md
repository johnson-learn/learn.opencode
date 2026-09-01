# program_skill 参考：C 编码规范与错误处理（要点速查）

> 详细标准读 `modules/cpp-coding-standards/GUIDE.md`（取适用 C 部分）；嵌入式安全子集见 `modules/c-static-analysis/GUIDE.md`（MISRA-C 要点）。

## 1. 命名与结构

- 类型名 `snake_case_t`；函数 `snake_case`；宏/常量 `UPPER_SNAKE`；全局变量 `g_` 前缀；静态变量 `s_` 前缀
- 头文件：`#ifndef FILE_H / #define FILE_H ... #endif` 或 `#pragma once`（二选一，全项目统一）
- 每个 .c 配一个同名 .h；头文件只放声明与常量，不定义变量（inline 函数除外）

## 2. 错误处理（铁律：系统调用返回值必须检查）

```c
/* 有返回值函数：检查并传播错误码 */
int fd = open(path, O_RDONLY);
if (fd < 0) {
    fprintf(stderr, "open %s: %s\n", path, strerror(errno));
    return -1;
}

/* 内存分配：失败必须处理 */
void *p = malloc(n);
if (!p) { fprintf(stderr, "malloc failed\n"); exit(EXIT_FAILURE); }

/* 线程创建：失败必须处理 */
int rc = pthread_create(&tid, NULL, worker, arg);
if (rc != 0) { fprintf(stderr, "pthread_create: %s\n", strerror(rc)); return -1; }
```

## 3. 内存管理铁律

- 谁分配谁释放；释放后指针置 NULL（`free(p); p = NULL;`）
- 结构体配对 init/destroy：`foo_init()` 与 `foo_destroy()` 成对出现
- 数组边界：`sizeof(arr)/sizeof(arr[0])` 而非魔法数字；越界是 C 头号缺陷
- 字符串：`strncpy` 不保证 NUL 结尾——用 `snprintf` 或 `strlcpy`（自实现）；`gets` 禁用（用 `fgets`）

## 4. 多线程纪律

- 共享数据必须加锁（`pthread_mutex_t`），锁粒度最小化，持锁不做 IO
- 条件变量必须与互斥锁配对、用 while 而非 if 检查谓词
- 线程函数参数用堆分配或静态，禁止栈变量传地址

## 5. 编译器防线（交付前必过）

```bash
gcc -std=c11 -O2 -g -Wall -Wextra -Wpedantic -Wconversion -Wshadow -c src/*.c
# 零警告才算合格；-Werror 用于 CI
```

## 6. MISRA-C 要点（嵌入式子集）

- 禁止 goto（除错误出口模式）；switch 每 case 必须 break 或注释 fallthrough
- 禁用动态内存（堆）于安全关键路径；数组访问索引有界
- 显式类型转换（隐式窄化转换是缺陷源头）

## 铁律

1. 返回值必查、错误必处理，禁止静默吞错
2. 交付前 `-Wall -Wextra` 零警告
3. 内存与线程代码必须实跑（ASan/TSan/valgrind）验证
