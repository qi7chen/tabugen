# Copyright (C) 2021-present ichenq@outlook.com. All rights reserved.
# Distributed under the terms and conditions of the Apache License.
# See accompanying files LICENSE.

cmake_minimum_required(VERSION 3.5)

PROJECT(TabugenCppExample)

set(CMAKE_CXX_STANDARD 17)
set(PROJECT_ROOT_DIR ${CMAKE_SOURCE_DIR})

include_directories($ENV{VCPKG_INCLUDE_DIR})
link_directories($ENV{VCPKG_LIB_DIR})

include_directories(${PROJECT_ROOT_DIR}/src)

message("include", $ENV{VCPKG_INCLUDE_DIR})
message("lib", $ENV{VCPKG_LIB_DIR})

find_package(absl CONFIG REQUIRED)


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

set(ALL_SRC_FILES 
    ${PROJECT_ROOT_DIR}/src/common/Conv.h
    ${PROJECT_ROOT_DIR}/src/common/Utils.h
    ${PROJECT_ROOT_DIR}/src/common/Utils.cpp
    ${PROJECT_ROOT_DIR}/src/main.cpp
    ${PROJECT_ROOT_DIR}/src/BoxDefine.h
    ${PROJECT_ROOT_DIR}/src/BoxDefine.cpp
    ${PROJECT_ROOT_DIR}/src/GlobalDefine.h
    ${PROJECT_ROOT_DIR}/src/GlobalDefine.cpp
    ${PROJECT_ROOT_DIR}/src/SoldierDefine.h
    ${PROJECT_ROOT_DIR}/src/SoldierDefine.cpp
    ${PROJECT_ROOT_DIR}/src/GuideDefine.h
    ${PROJECT_ROOT_DIR}/src/GuideDefine.cpp    
    )

add_executable(Examples ${ALL_SRC_FILES})

target_link_libraries(Examples PRIVATE absl::any absl::base absl::bits absl::city)