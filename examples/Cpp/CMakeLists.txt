# learn you some cmake
# https://modern-cmake-cn.github.io/Modern-CMake-zh_CN/README_GitBook.html

cmake_minimum_required(VERSION 3.8)

project(TabugenCpp LANGUAGES CXX)

set(PROJECT_ROOT_DIR ${CMAKE_SOURCE_DIR})

set(Boost_USE_STATIC_LIBS ON)  # only find static libs
set(Boost_USE_DEBUG_LIBS OFF)  # ignore debug libs and
set(Boost_USE_RELEASE_LIBS ON)  # only find release libs
set(Boost_USE_MULTITHREADED ON)
set(Boost_USE_STATIC_RUNTIME ON)  # link Boost Static libraries

find_package(Boost REQUIRED)
if (Boost_FOUND)
    message(STATUS "include Boost dir ${Boost_INCLUDE_DIRS}")
    include_directories(${Boost_INCLUDE_DIRS})
    link_directories(${Boost_LIBRARY_DIRS})
else()
    message(WARNING "Boost not found")
endif()

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

set(ALL_LIB_FILES
    ${PROJECT_ROOT_DIR}/src/BoxDefine.h
    ${PROJECT_ROOT_DIR}/src/BoxDefine.cpp
    ${PROJECT_ROOT_DIR}/src/GlobalDefine.h
    ${PROJECT_ROOT_DIR}/src/GlobalDefine.cpp
    ${PROJECT_ROOT_DIR}/src/SoldierDefine.h
    ${PROJECT_ROOT_DIR}/src/SoldierDefine.cpp
    ${PROJECT_ROOT_DIR}/src/GuideDefine.h
    ${PROJECT_ROOT_DIR}/src/GuideDefine.cpp
    )

add_library(conflib STATIC ${ALL_LIB_FILES})
target_include_directories(conflib PUBLIC ${PROJECT_ROOT_DIR}/src)
target_compile_features(conflib PUBLIC cxx_std_11)

add_executable(tabugencpp ${PROJECT_ROOT_DIR}/src/main.cpp)
target_link_libraries(tabugencpp PRIVATE conflib)

