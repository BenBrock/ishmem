/* Copyright (C) 2026 Intel Corporation
 * SPDX-License-Identifier: BSD-3-Clause
 */

#ifndef ISHMEM4PY_RUNTIME_H
#define ISHMEM4PY_RUNTIME_H

#include <stddef.h>
#include <stdint.h>

#if defined(__GNUC__)
#define ISHMEM4PY_EXPORT __attribute__((visibility("default")))
#else
#define ISHMEM4PY_EXPORT
#endif

#ifdef __cplusplus
extern "C" {
#endif

ISHMEM4PY_EXPORT void ishmem4py_init(void);
ISHMEM4PY_EXPORT void ishmem4py_finalize(void);
ISHMEM4PY_EXPORT int ishmem4py_my_pe(void);
ISHMEM4PY_EXPORT int ishmem4py_n_pes(void);
ISHMEM4PY_EXPORT void ishmem4py_info_get_version(int *major, int *minor);
ISHMEM4PY_EXPORT void ishmem4py_barrier_all(void);
ISHMEM4PY_EXPORT void ishmem4py_sync_all(void);
ISHMEM4PY_EXPORT void ishmem4py_fence(void);
ISHMEM4PY_EXPORT void ishmem4py_quiet(void);
ISHMEM4PY_EXPORT void *ishmem4py_malloc(size_t size);
ISHMEM4PY_EXPORT void *ishmem4py_calloc(size_t count, size_t size);
ISHMEM4PY_EXPORT void ishmem4py_free(void *ptr);
ISHMEM4PY_EXPORT void ishmem4py_putmem(void *dest, const void *src, size_t nbytes, int pe);
ISHMEM4PY_EXPORT void ishmem4py_getmem(void *dest, const void *src, size_t nbytes, int pe);
ISHMEM4PY_EXPORT uintptr_t ishmem4py_cast_ptr_to_uintptr(const void *ptr);
ISHMEM4PY_EXPORT void *ishmem4py_cast_uintptr_to_ptr(uintptr_t value);

#ifdef __cplusplus
}
#endif

#endif
