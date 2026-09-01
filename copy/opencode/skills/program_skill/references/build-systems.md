# program_skill 参考：构建系统进阶（Makefile/CMake 多目录、条件编译、平台判断）

> 基础模板见 `../references/compile-scripts.md`；本文件为进阶要点。

## 1. Makefile 多目录 + 自动依赖

```makefile
CC      := gcc
CFLAGS  := -std=c11 -O2 -g -Wall -Wextra -pthread
SRC_DIR := src
OBJ_DIR := build/obj
BIN     := build/app
SRCS    := $(shell find $(SRC_DIR) -name '*.c')
OBJS    := $(patsubst $(SRC_DIR)/%.c,$(OBJ_DIR)/%.o,$(SRCS))
DEPS    := $(OBJS:.o=.d)

$(BIN): $(OBJS)
	$(CC) $(CFLAGS) -o $@ $^
$(OBJ_DIR)/%.o: $(SRC_DIR)/%.c
	@mkdir -p $(dir $@)
	$(CC) $(CFLAGS) -MMD -MP -c -o $@ $<     # -MMD 自动生成头文件依赖
-include $(DEPS)                              # 头文件变更自动重编
clean:
	rm -rf build
.PHONY: all clean
```

## 2. 条件编译（宏开关）

```c
#ifdef FEATURE_X
void feature_x(void) { /* ... */ }
#endif
```
```bash
gcc -DFEATURE_X -o app src/*.c          # 开启特性
# 调试宏：
#if defined(DEBUG)
#define LOG(fmt, ...) fprintf(stderr, "[%s:%d] " fmt "\n", __FILE__, __LINE__, __VA_ARGS__)
#else
#define LOG(...) ((void)0)
#endif
```

## 3. 平台判断

```c
#ifdef _WIN32
# include <windows.h>
# define sleep_ms(x) Sleep(x)
#else
# include <time.h>
# define sleep_ms(x) (usleep((x) * 1000))
#endif
```
```cmake
if(WIN32)
  target_link_libraries(app PRIVATE ws2_32)
else()
  target_link_libraries(app PRIVATE pthread m)
endif()
```

## 4. CMake 选项与生成器表达式

```cmake
option(ENABLE_TEST "Build tests" OFF)
if(ENABLE_TEST)
  enable_testing()
  add_subdirectory(tests)
endif()
target_compile_options(app PRIVATE $<$<CONFIG:Debug>:-O0 -g> $<$<CONFIG:Release>:-O2>)
```

## 5. 交叉工具链

见 `references/embedded-build.md`（工具链文件/裸机/OpenOCD）。

## 铁律

1. -MMD 依赖文件必须（头文件改了不重编是经典坑）
2. 条件编译用显式宏开关，禁止用注释代码切换
3. 平台差异集中在一个适配头文件，禁止散落 `#ifdef` 满文件
