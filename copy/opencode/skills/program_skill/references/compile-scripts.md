# program_skill 参考：C 编译脚本模板库（动态编译脚本套路）

> 核心套路：扫描源文件 → 自动依赖 → 编译 → 链接 → 运行。三版（Bash/Batch/PowerShell）按环境选用；全部幂等可重入、失败非零退出。
> 更精细的生成规则优先读 `modules/c-compile-script-generator/GUIDE.md`。

## 1. 单文件编译（Bash，WSL 内）

```bash
#!/bin/bash
# 用法: ./build.sh <源文件.c> [额外gcc参数]
set -e
src="${1:?用法: ./build.sh <源文件.c>}"
out="${src%.c}"
gcc -O2 -g -Wall -Wextra -o "$out" "$src" ${@:2}
./"$out"
```

## 2. 多文件自动依赖（Bash，目录内全部 .c）

```bash
#!/bin/bash
# 用法: ./build.sh [输出名，默认 main]
set -e
OUT="${1:-main}"
SRCS=$(find . -maxdepth 1 -name '*.c' | sort)
CFLAGS="${CFLAGS:--O2 -g -Wall -Wextra -pthread}"
gcc $CFLAGS -o "$OUT" $SRCS
./"$OUT"
```

## 3. 静态库 / 动态库

```bash
# 静态库 libfoo.a
gcc -c -fPIC foo.c bar.c
ar rcs libfoo.a foo.o bar.o
# 动态库 libfoo.so（链接到使用程序: gcc main.c -L. -lfoo -Wl,-rpath,.）
gcc -shared -fPIC -o libfoo.so foo.c bar.c
```

## 4. 交叉编译（arm-none-eabi，嵌入式）

```bash
#!/bin/bash
# 裸机交叉编译：无系统库，需链接脚本
set -e
TARGET=arm-none-eabi-
$TARGET'gcc' -mcpu=cortex-m4 -mthumb -O2 -g -Wall -c main.c -o main.o
$TARGET'gcc' -T linker.ld -nostdlib -o firmware.elf main.o
$TARGET'objcopy' -O ihex firmware.elf firmware.hex
$TARGET'size' firmware.elf
```

## 5. CMakeLists 模板（多目录工程）

```cmake
cmake_minimum_required(VERSION 3.16)
project(app C)

set(CMAKE_C_STANDARD 11)
set(CMAKE_C_FLAGS "-O2 -g -Wall -Wextra")
find_package(Threads REQUIRED)

file(GLOB_RECURSE SOURCES src/*.c)
add_executable(app ${SOURCES})
target_include_directories(app PRIVATE include)
target_link_libraries(app PRIVATE Threads::Threads m)
```

## 6. PowerShell 动态编译（Windows 侧调 w64devkit 或 wsl）

```powershell
# 用法: .\build.ps1 [输出名]
param([string]$Out = "main")
$ErrorActionPreference = "Stop"
$gcc = "C:\w64devkit\w64devkit\bin\gcc.exe"
$srcs = Get-ChildItem -Filter *.c | ForEach-Object { $_.Name }
& $gcc -O2 -g -Wall -Wextra -pthread -o $Out $srcs
if ($LASTEXITCODE -ne 0) { throw "编译失败" }
& ".\$Out.exe"
```

## 7. Makefile 模板（增量编译）

```makefile
CC      := gcc
CFLAGS  := -O2 -g -Wall -Wextra -pthread
SRCS    := $(wildcard src/*.c)
OBJS    := $(SRCS:.c=.o)
TARGET  := app

all: $(TARGET)
$(TARGET): $(OBJS)
	$(CC) $(CFLAGS) -o $@ $^
%.o: %.c
	$(CC) $(CFLAGS) -c -o $@ $<
clean:
	rm -f $(OBJS) $(TARGET)
.PHONY: all clean
```

## 铁律

1. 编译必须 `-Wall -Wextra` 且零警告交付；警告即缺陷
2. 脚本失败必须非零退出（`set -e` / `throw` / Make 错误即停）
3. 动态扫描源文件，新增 .c 无需改脚本
4. 多线程一律 `-pthread`（Windows w64devkit 为 winpthreads，同样支持）
