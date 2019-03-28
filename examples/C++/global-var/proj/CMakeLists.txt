cmake_minimum_required(VERSION 2.8)
project (CppDemo)

set(PROJECT_ROOT_DIR ${CMAKE_SOURCE_DIR})

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

include_directories(${PROJECT_ROOT_DIR})

set(ALL_SRC_FILES 
    main.cpp
    AutoGenConfig.h
    AutoGenConfig.cpp
    Utility/Conv.h
    Utility/Conv.cpp
    Utility/Logging.h
    Utility/Logging.cpp
    Utility/Portability.h
    Utility/Preprocessor.h
    Utility/Range.cpp
    Utility/Range.h
    Utility/ScopeGuard.h
    Utility/SparseByteSet.h
    Utility/Traits.h
    Utility/UncaughtException.h
    Utility/StringUtil.h
    Utility/StringUtil.cpp
    Utility/WinUtil.h
    Utility/WinUtil.cpp
    )

    
add_executable(CppDemo ${ALL_SRC_FILES})