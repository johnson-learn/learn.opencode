# program_skill 参考：嵌入式构建（CMakeLists 模板 / 工具链文件 / OpenOCD 烧录）

> 详细规则读 `modules/c-gcc-embedded-build/GUIDE.md`；本文件为本机验证过的速查。

## 1. 交叉编译工具链（arm-none-eabi）

```bash
# 安装（Ubuntu）
sudo apt install gcc-arm-none-eabi binutils-arm-none-eabi
# 检查
arm-none-eabi-gcc --version
```

## 2. CMake 工具链文件 arm-none-eabi.cmake

```cmake
set(CMAKE_SYSTEM_NAME Generic)
set(CMAKE_SYSTEM_PROCESSOR arm)
set(CMAKE_C_COMPILER arm-none-eabi-gcc)
set(CMAKE_TRY_COMPILE_TARGET_TYPE STATIC_LIBRARY)  # 避免链接测试
set(CMAKE_C_FLAGS "-mcpu=cortex-m4 -mthumb -mfloat-abi=hard -mfpu=fpv4-sp-d16 -ffunction-sections -fdata-sections" CACHE STRING "" FORCE)
set(CMAKE_EXE_LINKER_FLAGS "-T${CMAKE_SOURCE_DIR}/linker.ld -Wl,--gc-sections" CACHE STRING "" FORCE)
```

用法：`cmake -B build -DCMAKE_TOOLCHAIN_FILE=arm-none-eabi.cmake`

## 3. 嵌入式 CMakeLists 模板

```cmake
cmake_minimum_required(VERSION 3.16)
project(firmware C ASM)
set(CMAKE_C_STANDARD 11)
file(GLOB SOURCES src/*.c)
add_executable(firmware ${SOURCES})
target_include_directories(firmware PRIVATE include)
# 产物转换
add_custom_command(TARGET firmware POST_BUILD
  COMMAND arm-none-eabi-objcopy -O ihex $<TARGET_FILE:firmware> firmware.hex
  COMMAND arm-none-eabi-size $<TARGET_FILE:firmware>)
```

## 4. 裸机编译（无 CMake，直接 gcc）

```bash
arm-none-eabi-gcc -mcpu=cortex-m4 -mthumb -O2 -g -Wall -c main.c -o main.o
arm-none-eabi-gcc -T linker.ld -nostdlib -o firmware.elf main.o startup.o
arm-none-eabi-objcopy -O ihex firmware.elf firmware.hex
arm-none-eabi-size firmware.elf
```

## 5. OpenOCD 烧录

```bash
# 连接（ST-Link 示例）
openocd -f interface/stlink.cfg -f target/stm32f4x.cfg
# 烧录（另开终端）
telnet localhost 4444
> halt
> program firmware.elf verify reset
> reset run
```

## 铁律

1. 交叉编译产物必须 `size` 检查（Flash/RAM 占用）
2. 链接脚本（.ld）是裸机核心，改动必须与芯片手册对照
3. 烧录前必验 .elf 可回溯（保留调试符号版本）
