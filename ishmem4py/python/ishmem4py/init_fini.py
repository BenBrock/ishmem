# Copyright (C) 2026 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause

"""Initialization, finalization, and runtime queries."""

from __future__ import annotations

import ctypes

from ._common import (
    InitStatus,
    Version,
    _check_can_finalize,
    _check_can_init,
    _get_init_status,
    _require_initialized,
    _set_finalized,
    _set_initialized,
)
from ._lib import RUNTIME
from .version import __version__

_INFO_NAME_BYTES = 256

__all__ = [
    "InitStatus",
    "Version",
    "finalize",
    "get_version",
    "info_get_name",
    "info_get_version",
    "init",
    "init_status",
    "is_initialized",
    "my_pe",
    "n_pes",
]


def init() -> None:
    """Initialize Intel SHMEM for the current process."""
    _check_can_init()
    RUNTIME.ishmem4py_init()
    _set_initialized()


def finalize() -> None:
    """Finalize Intel SHMEM for the current process."""
    _check_can_finalize()
    RUNTIME.ishmem4py_finalize()
    _set_finalized()


def init_status() -> InitStatus:
    """Return the process-local initialization state."""
    return _get_init_status()


def is_initialized() -> bool:
    """Return ``True`` if Intel SHMEM is currently initialized."""
    return init_status() == InitStatus.INITIALIZED


def my_pe() -> int:
    """Return the calling PE's global rank."""
    _require_initialized()
    return int(RUNTIME.ishmem4py_my_pe())


def n_pes() -> int:
    """Return the number of PEs in ``TEAM_WORLD``."""
    _require_initialized()
    return int(RUNTIME.ishmem4py_n_pes())


def info_get_version() -> tuple[int, int]:
    """Return the OpenSHMEM specification version reported by the runtime."""
    major = ctypes.c_int()
    minor = ctypes.c_int()
    RUNTIME.ishmem4py_info_get_version(ctypes.byref(major), ctypes.byref(minor))
    return int(major.value), int(minor.value)


def info_get_name() -> str:
    """Return the runtime vendor name."""
    name = ctypes.create_string_buffer(_INFO_NAME_BYTES)
    RUNTIME.ishmem4py_info_get_name(ctypes.cast(name, ctypes.c_void_p))
    return name.value.decode("utf-8")


def get_version() -> Version:
    """Return combined OpenSHMEM, Intel SHMEM, and ``ishmem4py`` version metadata."""
    spec_major, spec_minor = info_get_version()
    lib_major = ctypes.c_int()
    lib_minor = ctypes.c_int()
    lib_patch = ctypes.c_int()
    RUNTIME.ishmem4py_vendor_get_version(
        ctypes.byref(lib_major),
        ctypes.byref(lib_minor),
        ctypes.byref(lib_patch),
    )
    return Version(
        openshmem_spec_version=f"{spec_major}.{spec_minor}",
        ishmem4py_version=__version__,
        libishmem_version=f"{lib_major.value}.{lib_minor.value}.{lib_patch.value}",
        vendor_name=info_get_name(),
    )
