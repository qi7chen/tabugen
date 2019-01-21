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
    ${UTILITY_SRC_DIR}/Utility/Conv.h
    ${UTILITY_SRC_DIR}/Utility/Conv.cpp
    ${UTILITY_SRC_DIR}/Utility/Logging.h
    ${UTILITY_SRC_DIR}/Utility/Logging.cpp
    ${UTILITY_SRC_DIR}/Utility/Portability.h
    ${UTILITY_SRC_DIR}/Utility/Preprocessor.h
    ${UTILITY_SRC_DIR}/Utility/Range.cpp
    ${UTILITY_SRC_DIR}/Utility/Range.h
    ${UTILITY_SRC_DIR}/Utility/ScopeGuard.h
    ${UTILITY_SRC_DIR}/Utility/SparseByteSet.h
    ${UTILITY_SRC_DIR}/Utility/Traits.h
    ${UTILITY_SRC_DIR}/Utility/UncaughtException.h
    ${UTILITY_SRC_DIR}/Utility/StringUtil.h
    ${UTILITY_SRC_DIR}/Utility/StringUtil.cpp
    ${UTILITY_SRC_DIR}/Utility/WinUtil.h
    ${UTILITY_SRC_DIR}/Utility/WinUtil.cpp
    )

    
add_executable(CppDemo ${ALL_SRC_FILES})