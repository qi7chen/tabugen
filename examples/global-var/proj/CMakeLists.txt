cmake_minimum_required(VERSION 2.8)
project (CppDemo)

set(PROJECT_ROOT_DIR ${CMAKE_SOURCE_DIR})
set(UTILITY_SRC_DIR ${PROJECT_ROOT_DIR}/../../../bootstrap/cpp)

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

include_directories(${UTILITY_SRC_DIR})

set(ALL_SRC_FILES 
    main.cpp
    AutoGenConfig.h
    AutoGenConfig.cpp
    ${PROJECT_ROOT_DIR}/Utility/Conv.h
    ${PROJECT_ROOT_DIR}/Utility/Conv.cpp
    ${PROJECT_ROOT_DIR}/Utility/Logging.h
    ${PROJECT_ROOT_DIR}/Utility/Logging.cpp
    ${PROJECT_ROOT_DIR}/Utility/Portability.h
    ${PROJECT_ROOT_DIR}/Utility/Preprocessor.h
    ${PROJECT_ROOT_DIR}/Utility/Range.cpp
    ${PROJECT_ROOT_DIR}/Utility/Range.h
    ${PROJECT_ROOT_DIR}/Utility/ScopeGuard.h
    ${PROJECT_ROOT_DIR}/Utility/SparseByteSet.h
    ${PROJECT_ROOT_DIR}/Utility/Traits.h
    ${PROJECT_ROOT_DIR}/Utility/UncaughtException.h
    ${PROJECT_ROOT_DIR}/Utility/StringUtil.h
    ${PROJECT_ROOT_DIR}/Utility/StringUtil.cpp
    ${PROJECT_ROOT_DIR}/Utility/WinUtil.h
    ${PROJECT_ROOT_DIR}/Utility/WinUtil.cpp
    )

    
add_executable(${ProjectName} ${ALL_TEST_SRC_FILES})