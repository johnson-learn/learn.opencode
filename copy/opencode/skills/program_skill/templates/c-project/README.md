# C 工程骨架（program_skill templates/c-project）

标准 C11 工程骨架：新项目复制本目录后按需改名。

## 结构

```
c-project/
├── src/main.c           # 入口（可增删 .c，构建自动扫描）
├── include/             # 头文件（按需创建）
├── Makefile             # 增量构建：make / make clean
├── CMakeLists.txt       # CMake 构建：cmake -B build && cmake --build build
└── .gitignore
```

## 构建（WSL 默认环境）

```bash
cd /mnt/e/opencode_code/<项目> && make && ./app
# 或 cmake：
cmake -B build && cmake --build build && ./build/app
```

## 约定

- 新 .c 放 src/ 即自动纳入构建（Makefile/CMake 均扫描 src/*.c）
- 多线程加 -pthread（已内置）
- 编译零警告交付：-Wall -Wextra 全开
