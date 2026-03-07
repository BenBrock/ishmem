# ishmem4py

`ishmem4py` is a new Python binding layer for Intel SHMEM being developed in-tree in the
`ishmem` repository. The immediate target is a CPU-initiated MVP that can initialize Intel
SHMEM, allocate symmetric memory, and perform basic `put` and `get` operations from Python.

## Why A New Shim Layer

Intel SHMEM's installed interface is not a drop-in target for a pure-Python FFI layer:

- the public header is C++, not C
- the installed library is a static archive (`libishmem.a`)
- exported symbols are C++ mangled

For `ishmem4py`, the binding strategy is therefore:

1. add a very small C ABI runtime shim linked against Intel SHMEM
2. load that shim from Python
3. keep the Python layer thin and name APIs after Intel SHMEM/OpenSHMEM where possible

This keeps the MVP simple and makes future growth predictable.

## MVP Scope

The first deliverable is intentionally narrow:

- library setup and teardown
  - `init`
  - `finalize`
  - `my_pe`
  - `n_pes`
  - `barrier_all`
  - `quiet`
- symmetric memory management
  - `malloc`
  - `calloc`
  - `free`
- CPU-initiated RMA
  - `putmem`
  - `getmem`
- Python memory object support sufficient to:
  - allocate symmetric memory from Python
  - keep symmetric allocations as explicit handles
  - stage local data in and out from Python buffers
  - run multi-PE ring-style smoke tests

Out of scope for the initial MVP:

- device-initiated communication
- SYCL queue or work-group extensions
- full typed API coverage (`ishmem_int_put`, `ishmem_float_get`, and similar)
- team management beyond world-team queries
- atomics, signaling, reductions, collectives, or wait/test routines

## Memory Model For The MVP

The MVP treats symmetric allocations as opaque Python objects, not as directly dereferenceable
Python buffers.

That choice matches Intel SHMEM's default memory model more closely:

- the symmetric heap may reside in device memory
- host loads and stores are not generally valid on symmetric heap pointers
- host `putmem` and `getmem` are the portable way to move data between Python-visible memory
  and symmetric objects

In practice, the MVP uses normal Python buffer-protocol objects (`bytes`, `bytearray`,
`memoryview`, and similar) as the local source or destination for host-initiated RMA calls.

`ISHMEM_ENABLE_ACCESSIBLE_HOST_HEAP=1` remains useful as an optional mode for debugging or
future richer views, but it is not required by the first implementation.

## Planned Layout

The implementation is expected to live under `ishmem/ishmem4py/` with roughly this structure:

```text
ishmem4py/
  CMakeLists.txt
  README.md
  csrc/
    ishmem4py_runtime.cpp
    ishmem4py_runtime.h
  python/
    ishmem4py/
      __init__.py
      _lib.py
      core.py
  test/
    smoke_test.py
    ring_test.py
  examples/
    init_fini.py
    ring_put_get.py
```

## API Shape

The Python API will stay close to Intel SHMEM/OpenSHMEM naming at the low level.

Expected MVP entry points:

```python
import ishmem4py as ishmem

ishmem.init()
pe = ishmem.my_pe()
npes = ishmem.n_pes()

buf = ishmem.malloc(1024)
zeros = ishmem.calloc(256, 4)

ishmem.putmem(remote_buf, local_buf, pe=1)
ishmem.getmem(local_buf, remote_buf, pe=1)

ishmem.barrier_all()
ishmem.quiet()
ishmem.free(buf)
ishmem.finalize()
```

The Python `SymmetricMemory` object exposes the symmetric address and allocation size, along with
convenience `read()` and `write()` helpers implemented in terms of same-PE `getmem` and `putmem`.

## Build Integration Plan

The preferred integration is an optional top-level CMake target, for example:

```text
-DBUILD_PYTHON_BINDINGS=ON
```

Expected responsibilities:

- build the C ABI runtime shim with `icpx`
- link it against the existing Intel SHMEM library objects or installed library
- place the resulting shared library beside the Python package
- keep the rest of the core Intel SHMEM build unchanged when Python bindings are disabled

## Current Build And Test Flow

The current branch has been validated with an in-tree build and source-tree Python package.

Build:

```bash
source /opt/intel/oneapi/setvars.sh

cmake -S /docker-mount/ishmem \
  -B /docker-mount/ishmem/build-ishmem4py-icpx-noaot \
  -DCMAKE_C_COMPILER=icx \
  -DCMAKE_CXX_COMPILER=icpx \
  -DENABLE_OPENSHMEM=ON \
  -DSHMEM_DIR=/home/xiii/pkg/SOS-2026-03-06 \
  -DBUILD_PYTHON_BINDINGS=ON \
  -DBUILD_UNIT_TESTS=OFF \
  -DBUILD_PERF_TESTS=OFF \
  -DBUILD_EXAMPLES=OFF \
  -DBUILD_APPS=OFF \
  -DENABLE_AOT_COMPILATION=OFF

cmake --build /docker-mount/ishmem/build-ishmem4py-icpx-noaot --target ishmem4py -j4
```

Run environment:

```bash
unset ISHMEM_DIR
export LD_LIBRARY_PATH=/home/xiii/pkg/SOS-2026-03-06/lib:$LD_LIBRARY_PATH
export PYTHONPATH=/docker-mount/ishmem/ishmem4py/python
export ISHMEM4PY_RUNTIME_LIBRARY=/docker-mount/ishmem/build-ishmem4py-icpx-noaot/ishmem4py/python/ishmem4py/_ishmem4py_runtime.so
export ISHMEM_RUNTIME=OPENSHMEM
```

Smoke test:

```bash
mpiexec -n 1 /docker-mount/ishmem/scripts/ishmrun \
  python3 /docker-mount/ishmem/ishmem4py/test/smoke_test.py
```

Two-PE ring test:

```bash
mpiexec -n 2 /docker-mount/ishmem/scripts/ishmrun \
  python3 /docker-mount/ishmem/ishmem4py/test/ring_test.py
```

Important notes:

- Running without `ishmrun` is not reliable on multi-device nodes because Intel SHMEM needs the
  normal PE-to-device mapping.
- The current Intel SHMEM lifecycle should be treated as one-shot per process: initialize once,
  finalize once, and do not attempt to reinitialize after finalization.

## Test Plan

The MVP needs both local smoke coverage and multi-PE verification:

- single-PE smoke test
  - init/finalize
  - malloc/calloc/free
  - basic local typed view checks
- two-PE RMA test
  - each PE allocates symmetric source and destination buffers
  - PE `i` writes a known pattern
  - `putmem` and `getmem` exchange data around a ring
  - barriers validate global completion and correctness

Tests should be runnable through the same launcher expectations as the rest of `ishmem`.

## Known Risks / Open Questions

- Actual runtime verification depends on available Intel GPU + Intel SHMEM backend environment.
- The installed Intel SHMEM package is static-only, so distribution/packaging needs extra care.
- Full typed API coverage will likely benefit from code generation once the MVP lands.

## Short-Term Deliverables

Within the current time box, the target is:

1. land the build scaffolding and written plan
2. implement the runtime shim for the MVP API set
3. add the thin Python package
4. add at least one example and basic tests
5. verify as much as the current environment permits and document any gaps
