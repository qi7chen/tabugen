# learn you some cmake
# https://modern-cmake-cn.github.io/Modern-CMake-zh_CN/README_GitBook.html

cmake_minimum_required(VERSION 3.15)

project(TabugenCpp LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
#set(CMAKE_TOOLCHAIN_FILE, $ENV{VCPKG_ROOT}/scripts/buildsystems/vcpkg.cmake)

find_package(fmt CONFIG REQUIRED)
find_package(absl CONFIG REQUIRED)


if(MSVC)
  add_definitions (-wd4146 -wd4800)
endif()

if (WIN32)
  add_definitions(
    -D_WIN32_WINNT=0x0601
    -DWIN32_LEAN_AND_MEAN
    -D_CRT_SECURE_NO_WARNINGS
    -D_SCL_SECURE_NO_WARNINGS
    -DNOMINMAX
    )
endif()

set(SRC_DIR ${CMAKE_SOURCE_DIR}/src)

set(ALL_SRC_FILES
    ${SRC_DIR}/Config.h
    ${SRC_DIR}/Config.cpp
    ${SRC_DIR}/main.cpp
    )


include_directories(${SRC_DIR})

add_executable(TabugenCpp ${ALL_SRC_FILES})

target_link_libraries(TabugenCpp PRIVATE fmt::fmt absl::base absl::strings)
