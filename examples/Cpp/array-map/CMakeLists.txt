cmake_minimum_required(VERSION 3.5)
project (CppExample3)


find_package(absl CONFIG REQUIRED)

set(PROJECT_ROOT_DIR ${CMAKE_SOURCE_DIR})
set(BOOTSTRAP_SRC_DIR ${PROJECT_ROOT_DIR}/../bootstrap)


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

include_directories(${PROJECT_ROOT_DIR}/src)
include_directories(${BOOTSTRAP_SRC_DIR})

set(ALL_SRC_FILES 
    ${PROJECT_ROOT_DIR}/src/main.cpp
    ${PROJECT_ROOT_DIR}/src/AutogenConfig.h
    ${PROJECT_ROOT_DIR}/src/AutogenConfig.cpp
    ${BOOTSTRAP_SRC_DIR}/helper.h
    ${BOOTSTRAP_SRC_DIR}/helper.cpp
    )


add_executable(CppExample3 ${ALL_SRC_FILES})

target_link_libraries(CppExample3 PRIVATE absl::any absl::base absl::strings)
