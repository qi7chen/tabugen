# Copyright (C) 2021-present ichenq@outlook.com. All rights reserved.
# Distributed under the terms and conditions of the Apache License.
# See accompanying files LICENSE.

cmake_minimum_required(VERSION 3.5)

PROJECT(TabugenCppExample)

set(CMAKE_CXX_STANDARD 11)
set(PROJECT_ROOT_DIR ${CMAKE_SOURCE_DIR})

include_directories($ENV{VCPKG_INCLUDE_DIR})
link_directories($ENV{VCPKG_LIB_DIR})

message("include", $ENV{VCPKG_INCLUDE_DIR})
message("lib", $ENV{VCPKG_LIB_DIR})


if(MSVC)
  add_definitions (-wd4146 -wd4800)
endif()

if (WIN32)
  add_definitions(
    -D_WIN32_WINNT=0x0601 
    -DWIN32_LEAN_AND_MEAN 
    -D _CRT_SECURE_NO_WARNINGS
    -D_SCL_SECURE_NO_WARNINGS 
    -DNOMINMAX
    )
endif()

find_package(absl CONFIG REQUIRED)


add_subdirectory(basic)
add_subdirectory(array-map)
add_subdirectory(global-var)
add_subdirectory(inner-class)

