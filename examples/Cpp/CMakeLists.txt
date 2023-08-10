# Copyright (C) 2021-present ichenq@outlook.com. All rights reserved.

cmake_minimum_required(VERSION 3.0)

PROJECT(TabugenCppExample)

set(CMAKE_CXX_STANDARD 11)
set(PROJECT_ROOT_DIR ${CMAKE_SOURCE_DIR})

include_directories(${PROJECT_ROOT_DIR}/src)


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

set(ALL_SRC_FILES
    ${PROJECT_ROOT_DIR}/src/Conv.h
    ${PROJECT_ROOT_DIR}/src/StringPiece.h
    ${PROJECT_ROOT_DIR}/src/StringPiece.cpp
    ${PROJECT_ROOT_DIR}/src/StringUtil.h
    ${PROJECT_ROOT_DIR}/src/StringUtil.cpp
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

add_executable(CppExample ${ALL_SRC_FILES})

