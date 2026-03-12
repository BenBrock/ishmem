# ishmem4py Python Package

`ishmem4py` supports two install modes.

## Standard Install

Build `ishmem` with `-DBUILD_PYTHON_BINDINGS=ON`, then install from the build tree:

```bash
pip install /path/to/ishmem-build/ishmem4py/python
```

That package directory includes `_ishmem4py_runtime.so`, so `ISHMEM4PY_RUNTIME_LIBRARY` is not
needed.

## Editable / Dev Install

For active development:

```bash
pip install -e /path/to/ishmem-src/ishmem4py/python
```

Point the editable package at the CMake-built runtime:

```bash
export ISHMEM4PY_RUNTIME_LIBRARY=/path/to/ishmem-build/ishmem4py/python/ishmem4py/_ishmem4py_runtime.so
```

## Runtime Environment

The package still depends on the surrounding Intel SHMEM runtime setup:

```bash
source /opt/intel/oneapi/setvars.sh
unset ISHMEM_DIR
export ISHMEM_RUNTIME=OPENSHMEM
export LD_LIBRARY_PATH=/path/to/openshmem/lib:$LD_LIBRARY_PATH
```

For source-tree testing:

```bash
export PYTHONPATH=/path/to/ishmem-src/ishmem4py/python:/path/to/ishmem-src/ishmem4py/test
```

## Notes

- `import ishmem4py` and `import ishmem4py.core` both expose the full public API.
- The runtime library is loaded lazily, so importing the package for documentation or static
  inspection does not require a live Intel SHMEM runtime.
- The exported API is limited to functionality that has been validated in the current
  OpenSHMEM-backed test environment.
