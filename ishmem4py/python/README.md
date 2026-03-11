# ishmem4py Python Package

This directory supports two install modes.

## Standard install

Build `ishmem` with `-DBUILD_PYTHON_BINDINGS=ON`, then install the package from the build tree:

```bash
pip install /path/to/ishmem-build/ishmem4py/python
```

That build-tree package includes `_ishmem4py_runtime.so`, so `ishmem4py` can load its own runtime
without `ISHMEM4PY_RUNTIME_LIBRARY`.

## Editable / dev install

Install the source tree in editable mode when you are actively changing the Python code:

```bash
pip install -e /path/to/ishmem-src/ishmem4py/python
```

For editable installs, point the package at the runtime produced by your CMake build:

```bash
export ISHMEM4PY_RUNTIME_LIBRARY=/path/to/ishmem-build/ishmem4py/python/ishmem4py/_ishmem4py_runtime.so
```

In both modes, external runtime dependencies such as oneAPI, PTI, and the OpenSHMEM backend still
need to be visible through your normal environment setup.
