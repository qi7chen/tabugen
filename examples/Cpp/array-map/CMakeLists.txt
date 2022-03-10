# Copyright (C) 2021-present ichenq@outlook.com. All rights reserved.
# Distributed under the terms and conditions of the Apache License.
# See accompanying files LICENSE.

include_directories(${PROJECT_ROOT_DIR})
include_directories(${PROJECT_ROOT_DIR}/array-map)

set(ALL_SRC_FILES 
    ${PROJECT_ROOT_DIR}/common/Conv.h
    ${PROJECT_ROOT_DIR}/common/Utils.h
    ${PROJECT_ROOT_DIR}/common/Utils.cpp
    ${PROJECT_ROOT_DIR}/array-map/main.cpp
    ${PROJECT_ROOT_DIR}/array-map/AutogenConfig.h
    ${PROJECT_ROOT_DIR}/array-map/AutogenConfig.cpp
    )


add_executable(Example3 ${ALL_SRC_FILES})

target_link_libraries(Example3 PRIVATE absl::any absl::base absl::bits absl::city)