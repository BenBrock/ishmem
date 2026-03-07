# Copyright (C) 2026 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause

import ctypes
from dataclasses import dataclass
from typing import Optional

from ._lib import RUNTIME


class IshmemError(RuntimeError):
    pass


class IshmemStateError(IshmemError):
    pass


@dataclass(frozen=True)
class _PointerInfo:
    ptr: int
    size: int
    keepalive: object


class SymmetricMemory:
    def __init__(self, ptr: int, size: int):
        self._ptr = int(ptr)
        self._size = int(size)
        self._freed = False

    @property
    def ptr(self) -> int:
        return self._ptr

    @property
    def size(self) -> int:
        return self._size

    @property
    def freed(self) -> bool:
        return self._freed

    def _mark_freed(self) -> None:
        self._freed = True

    def read(self, size: Optional[int] = None, *, offset: int = 0, pe: Optional[int] = None) -> bytes:
        if pe is None:
            pe = my_pe()
        length = _normalize_span(self, size=size, offset=offset)
        dst = bytearray(length)
        getmem(dst, self, pe=pe, size=length, src_offset=offset)
        return bytes(dst)

    def write(self, data, *, offset: int = 0, pe: Optional[int] = None) -> int:
        if pe is None:
            pe = my_pe()
        return putmem(self, data, pe=pe, dest_offset=offset)

    def __int__(self) -> int:
        return self._ptr

    def __repr__(self) -> str:
        state = "freed" if self._freed else "active"
        return f"SymmetricMemory(ptr=0x{self._ptr:x}, size={self._size}, state={state})"


_initialized = False
_finalized = False
_live_allocations = {}


def _require_initialized() -> None:
    if not _initialized:
        raise IshmemStateError("Intel SHMEM is not initialized")


def _require_active(symm: SymmetricMemory) -> None:
    if not isinstance(symm, SymmetricMemory):
        raise TypeError("expected a SymmetricMemory instance")
    if symm.freed:
        raise IshmemStateError("symmetric allocation has already been freed")


def _normalize_span(obj, *, size: Optional[int], offset: int) -> int:
    if offset < 0:
        raise ValueError("offset must be >= 0")

    available = obj.size - offset
    if available < 0:
        raise ValueError("offset is past the end of the object")

    if size is None:
        return available
    if size < 0:
        raise ValueError("size must be >= 0")
    if size > available:
        raise ValueError("requested size extends past the end of the object")
    return size


def _ensure_contiguous_memoryview(obj, *, writable: bool):
    mv = memoryview(obj)
    if not mv.contiguous:
        raise ValueError("buffer must be contiguous")
    if writable and mv.readonly:
        raise ValueError("destination buffer must be writable")
    return mv


def _pointer_from_local_buffer(obj, *, writable: bool, offset: int = 0) -> _PointerInfo:
    if isinstance(obj, SymmetricMemory):
        _require_active(obj)
        size = _normalize_span(obj, size=None, offset=offset)
        return _PointerInfo(ptr=obj.ptr + offset, size=size, keepalive=obj)

    mv = _ensure_contiguous_memoryview(obj, writable=writable)

    if offset < 0:
        raise ValueError("offset must be >= 0")
    if offset > mv.nbytes:
        raise ValueError("offset is past the end of the buffer")

    if mv.readonly:
        if writable:
            raise ValueError("destination buffer must be writable")
        copied = (ctypes.c_char * mv.nbytes).from_buffer_copy(mv)
        return _PointerInfo(ptr=ctypes.addressof(copied) + offset, size=mv.nbytes - offset, keepalive=copied)

    raw = (ctypes.c_char * mv.nbytes).from_buffer(mv)
    return _PointerInfo(ptr=ctypes.addressof(raw) + offset, size=mv.nbytes - offset, keepalive=(mv, raw))


def _symmetric_target(obj) -> SymmetricMemory:
    _require_active(obj)
    return obj


def is_initialized() -> bool:
    return _initialized


def init() -> None:
    global _initialized
    if _initialized:
        raise IshmemStateError("Intel SHMEM is already initialized")
    if _finalized:
        raise IshmemStateError(
            "Intel SHMEM has already been finalized in this process and cannot be reinitialized"
        )
    RUNTIME.ishmem4py_init()
    _initialized = True


def finalize() -> None:
    global _initialized, _finalized
    if not _initialized:
        raise IshmemStateError("Intel SHMEM is not initialized")
    if _live_allocations:
        leaked = ", ".join(f"0x{ptr:x}" for ptr in sorted(_live_allocations))
        raise IshmemStateError(
            "cannot finalize while symmetric allocations are still live; "
            f"free them first: {leaked}"
        )
    RUNTIME.ishmem4py_finalize()
    _initialized = False
    _finalized = True


def my_pe() -> int:
    _require_initialized()
    return int(RUNTIME.ishmem4py_my_pe())


def n_pes() -> int:
    _require_initialized()
    return int(RUNTIME.ishmem4py_n_pes())


def info_get_version() -> tuple[int, int]:
    major = ctypes.c_int()
    minor = ctypes.c_int()
    RUNTIME.ishmem4py_info_get_version(ctypes.byref(major), ctypes.byref(minor))
    return int(major.value), int(minor.value)


def barrier_all() -> None:
    _require_initialized()
    RUNTIME.ishmem4py_barrier_all()


def sync_all() -> None:
    _require_initialized()
    RUNTIME.ishmem4py_sync_all()


def fence() -> None:
    _require_initialized()
    RUNTIME.ishmem4py_fence()


def quiet() -> None:
    _require_initialized()
    RUNTIME.ishmem4py_quiet()


def malloc(size: int) -> SymmetricMemory:
    _require_initialized()
    if size < 0:
        raise ValueError("size must be >= 0")
    ptr = RUNTIME.ishmem4py_malloc(size)
    if size > 0 and not ptr:
        raise IshmemError(f"ishmem_malloc({size}) returned NULL")
    result = SymmetricMemory(ptr=int(ptr or 0), size=size)
    _live_allocations[result.ptr] = result
    return result


def calloc(count: int, size: int) -> SymmetricMemory:
    _require_initialized()
    if count < 0 or size < 0:
        raise ValueError("count and size must be >= 0")
    ptr = RUNTIME.ishmem4py_calloc(count, size)
    total_size = count * size
    if total_size > 0 and not ptr:
        raise IshmemError(f"ishmem_calloc({count}, {size}) returned NULL")
    result = SymmetricMemory(ptr=int(ptr or 0), size=total_size)
    _live_allocations[result.ptr] = result
    return result


def free(symm: SymmetricMemory) -> None:
    _require_initialized()
    _require_active(symm)
    RUNTIME.ishmem4py_free(ctypes.c_void_p(symm.ptr))
    _live_allocations.pop(symm.ptr, None)
    symm._mark_freed()


def putmem(
    dest: SymmetricMemory,
    src,
    *,
    pe: int,
    size: Optional[int] = None,
    dest_offset: int = 0,
    src_offset: int = 0,
) -> int:
    _require_initialized()
    dest = _symmetric_target(dest)
    src_info = _pointer_from_local_buffer(src, writable=False, offset=src_offset)
    dest_size = _normalize_span(dest, size=None, offset=dest_offset)
    nbytes = min(dest_size, src_info.size) if size is None else size

    if nbytes < 0:
        raise ValueError("size must be >= 0")
    if nbytes > dest_size:
        raise ValueError("size extends past the destination symmetric object")
    if nbytes > src_info.size:
        raise ValueError("size extends past the source buffer")

    RUNTIME.ishmem4py_putmem(
        ctypes.c_void_p(dest.ptr + dest_offset),
        ctypes.c_void_p(src_info.ptr),
        nbytes,
        pe,
    )
    return nbytes


def getmem(
    dest,
    src: SymmetricMemory,
    *,
    pe: int,
    size: Optional[int] = None,
    dest_offset: int = 0,
    src_offset: int = 0,
) -> int:
    _require_initialized()
    src = _symmetric_target(src)
    dest_info = _pointer_from_local_buffer(dest, writable=True, offset=dest_offset)
    src_size = _normalize_span(src, size=None, offset=src_offset)
    nbytes = min(dest_info.size, src_size) if size is None else size

    if nbytes < 0:
        raise ValueError("size must be >= 0")
    if nbytes > dest_info.size:
        raise ValueError("size extends past the destination buffer")
    if nbytes > src_size:
        raise ValueError("size extends past the source symmetric object")

    RUNTIME.ishmem4py_getmem(
        ctypes.c_void_p(dest_info.ptr),
        ctypes.c_void_p(src.ptr + src_offset),
        nbytes,
        pe,
    )
    return nbytes
