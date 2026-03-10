# ishmem4py Python Package

This directory contains the installable Python package for the current `ishmem4py` MVP.

The package is intentionally thin:

- it installs the pure-Python wrapper module
- it expects the runtime shared library to already exist
- it locates that runtime through `ISHMEM4PY_RUNTIME_LIBRARY`

Typical editable install:

```bash
pip install -e /docker-mount/ishmem/ishmem4py/python
```

At runtime, set:

```bash
export ISHMEM4PY_RUNTIME_LIBRARY=/docker-mount/ishmem/build-ishmem4py-icpx-noaot/ishmem4py/python/ishmem4py/_ishmem4py_runtime.so
```
