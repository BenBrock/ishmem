# Copyright (C) 2026 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause

cmake_minimum_required(VERSION 3.17)

set(PROJECT_NAME "ishmem4py")
set(PROJECT_FULL_NAME "Intel(R) SHMEM Python bindings")

project(${PROJECT_NAME})

find_package(Python3 COMPONENTS Interpreter REQUIRED)

set(ISHMEM4PY_BUILD_ROOT "${CMAKE_CURRENT_BINARY_DIR}")
set(ISHMEM4PY_PYTHON_BUILD_ROOT "${ISHMEM4PY_BUILD_ROOT}/python")
set(ISHMEM4PY_PKG_BUILD_DIR "${ISHMEM4PY_PYTHON_BUILD_ROOT}/ishmem4py")
set(ISHMEM4PY_SOURCE_PYTHON_ROOT "${CMAKE_CURRENT_SOURCE_DIR}/python")
set(ISHMEM4PY_SOURCE_PKG_DIR "${ISHMEM4PY_SOURCE_PYTHON_ROOT}/ishmem4py")

file(COPY ${CMAKE_CURRENT_SOURCE_DIR}/test/ DESTINATION ${ISHMEM4PY_BUILD_ROOT})
file(COPY ${CMAKE_CURRENT_SOURCE_DIR}/examples/ DESTINATION ${ISHMEM4PY_BUILD_ROOT})

add_custom_target(ishmem4py-package-files
    COMMAND ${CMAKE_COMMAND} -E make_directory "${ISHMEM4PY_PYTHON_BUILD_ROOT}"
    COMMAND ${CMAKE_COMMAND} -E copy_if_different
        "${ISHMEM4PY_SOURCE_PYTHON_ROOT}/pyproject.toml"
        "${ISHMEM4PY_PYTHON_BUILD_ROOT}/pyproject.toml"
    COMMAND ${CMAKE_COMMAND} -E copy_if_different
        "${ISHMEM4PY_SOURCE_PYTHON_ROOT}/README.md"
        "${ISHMEM4PY_PYTHON_BUILD_ROOT}/README.md"
    COMMAND ${CMAKE_COMMAND} -E copy_if_different
        "${ISHMEM4PY_SOURCE_PYTHON_ROOT}/setup.py"
        "${ISHMEM4PY_PYTHON_BUILD_ROOT}/setup.py"
    COMMAND ${CMAKE_COMMAND} -E copy_directory
        "${ISHMEM4PY_SOURCE_PKG_DIR}"
        "${ISHMEM4PY_PKG_BUILD_DIR}"
    VERBATIM)

add_library(ishmem4py-runtime SHARED
    csrc/ishmem4py_runtime.cpp)

target_include_directories(ishmem4py-runtime PRIVATE
    "${SYCL_INCLUDE_SYCL_DIR}"
    "${LEVEL_ZERO_INCLUDEDIR}"
    "${ISHMEM_BUILD_ROOT}/include"
    "${PROJECT_SOURCE_DIR}/src"
    "${CMAKE_CURRENT_SOURCE_DIR}/csrc")

target_link_libraries(ishmem4py-runtime PRIVATE ishmem-static)
set_target_properties(ishmem4py-runtime PROPERTIES
    OUTPUT_NAME "_ishmem4py_runtime"
    PREFIX ""
    LIBRARY_OUTPUT_DIRECTORY "${ISHMEM4PY_PKG_BUILD_DIR}"
    RUNTIME_OUTPUT_DIRECTORY "${ISHMEM4PY_PKG_BUILD_DIR}"
    POSITION_INDEPENDENT_CODE 1)

add_custom_target(ishmem4py ALL
    DEPENDS ishmem4py-package-files ishmem4py-runtime)

message(STATUS "\n======= ishmem4py summary ========")
message(STATUS "Python interpreter:          ${Python3_EXECUTABLE}")
message(STATUS "Python package root:         ${ISHMEM4PY_PYTHON_BUILD_ROOT}")
message(STATUS "Runtime library output:      ${ISHMEM4PY_PKG_BUILD_DIR}")
message(STATUS "==================================\n")
