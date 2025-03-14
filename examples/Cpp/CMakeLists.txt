# learn you some cmake
# https://modern-cmake-cn.github.io/Modern-CMake-zh_CN/README_GitBook.html

cmake_minimum_required(VERSION 3.15)

project(TabugenCpp LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 11)

set(Boost_USE_STATIC_LIBS ON)  # only find static libs
set(Boost_USE_DEBUG_LIBS OFF)  # ignore debug libs and
set(Boost_USE_RELEASE_LIBS ON)  # only find release libs
set(Boost_USE_MULTITHREADED ON)
set(Boost_USE_STATIC_RUNTIME ON)  # link Boost Static libraries

find_package(Boost REQUIRED COMPONENTS algorithm lexical_cast)
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

set(SRC_DIR ${CMAKE_SOURCE_DIR}/src)

set(ALL_SRC_FILES
    ${SRC_DIR}/Config.h
    ${SRC_DIR}/Config.cpp
    ${SRC_DIR}/Conv.h
    ${SRC_DIR}/rapidcsv.h
    ${SRC_DIR}/main.cpp
    )


include_directories(${SRC_DIR})

add_executable(TabugenCpp ${ALL_SRC_FILES})

target_link_libraries(TabugenCpp PRIVATE Boost::lexical_cast Boost::algorithm)
