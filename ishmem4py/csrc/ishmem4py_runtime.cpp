/* Copyright (C) 2026 Intel Corporation
 * SPDX-License-Identifier: BSD-3-Clause
 */

#include "ishmem4py_runtime.h"

#include <ishmem.h>

extern "C" {

void ishmem4py_init(void)
{
    ishmem_init();
}

void ishmem4py_finalize(void)
{
    ishmem_finalize();
}

int ishmem4py_my_pe(void)
{
    return ishmem_my_pe();
}

int ishmem4py_n_pes(void)
{
    return ishmem_n_pes();
}

void ishmem4py_info_get_version(int *major, int *minor)
{
    ishmem_info_get_version(major, minor);
}

void ishmem4py_barrier_all(void)
{
    ishmem_barrier_all();
}

void ishmem4py_sync_all(void)
{
    ishmem_sync_all();
}

void ishmem4py_fence(void)
{
    ishmem_fence();
}

void ishmem4py_quiet(void)
{
    ishmem_quiet();
}

void *ishmem4py_malloc(size_t size)
{
    return ishmem_malloc(size);
}

void *ishmem4py_calloc(size_t count, size_t size)
{
    return ishmem_calloc(count, size);
}

void ishmem4py_free(void *ptr)
{
    ishmem_free(ptr);
}

void ishmem4py_putmem(void *dest, const void *src, size_t nbytes, int pe)
{
    ishmem_putmem(dest, src, nbytes, pe);
}

void ishmem4py_getmem(void *dest, const void *src, size_t nbytes, int pe)
{
    ishmem_getmem(dest, src, nbytes, pe);
}

uintptr_t ishmem4py_cast_ptr_to_uintptr(const void *ptr)
{
    return reinterpret_cast<uintptr_t>(ptr);
}

void *ishmem4py_cast_uintptr_to_ptr(uintptr_t value)
{
    return reinterpret_cast<void *>(value);
}

}  // extern "C"
