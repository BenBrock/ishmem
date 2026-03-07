# Copyright (C) 2026 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause

import ctypes
import os
from pathlib import Path

_RUNTIME_ENVVAR = "ISHMEM4PY_RUNTIME_LIBRARY"


def _candidate_paths():
    env_path = os.environ.get(_RUNTIME_ENVVAR)
    if env_path:
        yield Path(env_path)

    package_dir = Path(__file__).resolve().parent
    yield package_dir / "_ishmem4py_runtime.so"


def _load_runtime():
    last_error = None
    for candidate in _candidate_paths():
        if not candidate.exists():
            continue
        try:
            runtime = ctypes.CDLL(str(candidate))
        except OSError as exc:
            last_error = exc
            continue

        runtime.ishmem4py_init.argtypes = []
        runtime.ishmem4py_init.restype = None

        runtime.ishmem4py_finalize.argtypes = []
        runtime.ishmem4py_finalize.restype = None

        runtime.ishmem4py_my_pe.argtypes = []
        runtime.ishmem4py_my_pe.restype = ctypes.c_int

        runtime.ishmem4py_n_pes.argtypes = []
        runtime.ishmem4py_n_pes.restype = ctypes.c_int

        runtime.ishmem4py_info_get_version.argtypes = [
            ctypes.POINTER(ctypes.c_int),
            ctypes.POINTER(ctypes.c_int),
        ]
        runtime.ishmem4py_info_get_version.restype = None

        runtime.ishmem4py_barrier_all.argtypes = []
        runtime.ishmem4py_barrier_all.restype = None

        runtime.ishmem4py_sync_all.argtypes = []
        runtime.ishmem4py_sync_all.restype = None

        runtime.ishmem4py_fence.argtypes = []
        runtime.ishmem4py_fence.restype = None

        runtime.ishmem4py_quiet.argtypes = []
        runtime.ishmem4py_quiet.restype = None

        runtime.ishmem4py_malloc.argtypes = [ctypes.c_size_t]
        runtime.ishmem4py_malloc.restype = ctypes.c_void_p

        runtime.ishmem4py_calloc.argtypes = [ctypes.c_size_t, ctypes.c_size_t]
        runtime.ishmem4py_calloc.restype = ctypes.c_void_p

        runtime.ishmem4py_free.argtypes = [ctypes.c_void_p]
        runtime.ishmem4py_free.restype = None

        runtime.ishmem4py_putmem.argtypes = [
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.c_size_t,
            ctypes.c_int,
        ]
        runtime.ishmem4py_putmem.restype = None

        runtime.ishmem4py_getmem.argtypes = [
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.c_size_t,
            ctypes.c_int,
        ]
        runtime.ishmem4py_getmem.restype = None

        return runtime

    if last_error is not None:
        raise RuntimeError(
            "Found ishmem4py runtime library candidate but failed to load it. "
            "Ensure oneAPI runtime libraries are in LD_LIBRARY_PATH and set "
            f"{_RUNTIME_ENVVAR} if needed."
        ) from last_error

    raise RuntimeError(
        "Could not locate _ishmem4py_runtime.so. Build ishmem with "
        "-DBUILD_PYTHON_BINDINGS=ON and add the resulting build-tree python directory to "
        "PYTHONPATH, or set ISHMEM4PY_RUNTIME_LIBRARY explicitly."
    )


RUNTIME = _load_runtime()
