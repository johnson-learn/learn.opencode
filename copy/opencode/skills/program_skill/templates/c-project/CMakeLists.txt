cmake_minimum_required(VERSION 3.16)
project(app C)

set(CMAKE_C_STANDARD 11)
if(NOT CMAKE_BUILD_TYPE)
  set(CMAKE_BUILD_TYPE Debug)
endif()
set(CMAKE_C_FLAGS "-O2 -g -Wall -Wextra")

find_package(Threads REQUIRED)

file(GLOB SOURCES src/*.c)
add_executable(app ${SOURCES})
target_include_directories(app PRIVATE include)
target_link_libraries(app PRIVATE Threads::Threads m)
