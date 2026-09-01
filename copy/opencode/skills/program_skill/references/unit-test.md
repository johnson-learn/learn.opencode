# program_skill 参考：C 单元测试（Unity / CTest 用例与覆盖率）

> 目标：每个新写的 C 模块配单元测试；用例实跑 + 覆盖率 gcov/lcov；测试框架详见 `modules/cpp-testing/GUIDE.md`。

## 1. 目录约定

```
project/
├── src/            # 被测源码
├── include/
├── tests/          # 测试目录（与 src 分离）
│   ├── test_foo.c
│   └── unity.c     # 框架单文件（Unity 仅 3 个文件：unity.c/unity.h/unity_internals.h）
└── Makefile
```

## 2. Unity 用例模板

```c
#include "unity.h"
#include "foo.h"

void setUp(void) {}        /* 每用例前 */
void tearDown(void) {}     /* 每用例后 */

void test_foo_add_basic(void) {
    TEST_ASSERT_EQUAL_INT(5, foo_add(2, 3));
}
void test_foo_add_overflow(void) {
    TEST_ASSERT_EQUAL_INT(INT_MAX, foo_add_sat(INT_MAX, 1));  /* 饱和加法 */
}

int main(void) {
    UNITY_BEGIN();
    RUN_TEST(test_foo_add_basic);
    RUN_TEST(test_foo_add_overflow);
    return UNITY_END();
}
```

## 3. 编译与运行（WSL）

```bash
# 编译测试（unity.c 与测试源、被测源一起编）
gcc -O0 -g -Wall -Wextra -o run_tests tests/test_foo.c tests/unity.c src/foo.c -Iinclude -Itests
./run_tests          # 输出 PASS/FAIL 与断言位置
# 覆盖率
gcc -O0 -g --coverage -o run_tests tests/test_foo.c tests/unity.c src/foo.c -Iinclude -Itests
./run_tests
gcov src/foo.c       # 生成 foo.c.gcov（行级覆盖）
```

## 4. CTest 集成（CMake 工程）

```cmake
enable_testing()
add_subdirectory(tests)          # tests/CMakeLists.txt:
#   add_executable(test_foo test_foo.c unity.c ../src/foo.c)
#   target_include_directories(test_foo PRIVATE ../include .)
#   add_test(NAME foo COMMAND test_foo)
```
运行：`ctest --output-on-failure`

## 5. 断言宏速查

| 宏 | 用途 |
|---|---|
| `TEST_ASSERT(expr)` | 真值 |
| `TEST_ASSERT_EQUAL_INT(a, b)` | 整数相等 |
| `TEST_ASSERT_EQUAL_FLOAT(a, b)` | 浮点相等 |
| `TEST_ASSERT_EQUAL_STRING(a, b)` | 字符串相等 |
| `TEST_ASSERT_NOT_NULL(p)` | 指针非空 |
| `TEST_ASSERT_NULL(p)` | 指针为空 |

## 铁律

1. 新模块必须配测试（边界条件至少 2 例：正常 + 边界/异常）
2. 用例必须先实跑通过再交付；失败输出含断言文件:行号
3. 覆盖率报告随交付附上（关键路径覆盖优先，不追求 100%）
