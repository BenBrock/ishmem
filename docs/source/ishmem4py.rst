.. _ishmem4py:

--------------------
ishmem4py Bindings
--------------------

``ishmem4py`` is the in-tree Python interface for Intel(R) SHMEM.
It targets the same host-side workflow that the C and C++ Intel SHMEM APIs already support,
while adopting a small, Python-oriented surface inspired by ``nvshmem4py`` where the models
overlap.

The current binding is intentionally synchronous and host-driven.
It does not yet expose Intel SHMEM queue-based extensions or device-initiated Python APIs.

.. currentmodule:: ishmem4py

Import styles:

.. code-block:: python

   import ishmem4py as ishmem
   # or
   import ishmem4py.core as ishmem

API Reference
^^^^^^^^^^^^^

Initialization and Queries
""""""""""""""""""""""""""

.. autosummary::

   init
   finalize
   init_status
   is_initialized
   my_pe
   n_pes
   info_get_version
   info_get_name
   get_version
   Version

Memory Management
"""""""""""""""""

.. autosummary::

   malloc
   calloc
   buffer
   free
   ptr
   ishmem_ptr
   SymmetricMemory
   MemoryPointer

Remote Memory Access
""""""""""""""""""""

.. autosummary::

   put
   get
   putmem
   getmem
   fence
   quiet

Collectives
"""""""""""

.. autosummary::

   barrier_all
   sync_all
   barrier
   sync
   broadcast
   collect
   fcollect
   alltoall
   reduce
   reducescatter

Teams
"""""

.. autosummary::

   TEAM_WORLD
   TEAM_SHARED
   TEAM_INVALID
   Team
   team_my_pe
   team_n_pes
   team_translate_pe
   team_sync

Basic Example
^^^^^^^^^^^^^

.. literalinclude:: ../../ishmem4py/examples/init_fini.py
   :language: python

RMA Example
^^^^^^^^^^^

.. literalinclude:: ../../ishmem4py/examples/ring_put_get.py
   :language: python

Memory Model
^^^^^^^^^^^^

``ishmem4py`` keeps symmetric allocations as explicit Python objects instead of exposing the
symmetric heap as a general Python buffer.
That is deliberate:

- Intel SHMEM symmetric memory may not be directly host-accessible in every runtime mode.
- Explicit ``put`` and ``get`` calls are the portable host-side mechanism.
- Python can still use ordinary local buffers such as ``bytes``, ``bytearray``, and
  ``memoryview`` as the source or destination for host-initiated RMA.

Example:

.. code-block:: python

   ishmem.init()
   try:
       buf = ishmem.malloc(16)
       buf.write(b"abcd")

       host = bytearray(16)
       ishmem.get(host, buf, pe=ishmem.my_pe())
   finally:
       ishmem.free(buf)
       ishmem.finalize()

Collectives and Teams
^^^^^^^^^^^^^^^^^^^^^

World-team collectives are available directly from Python:

.. code-block:: python

   reduce_src = ishmem.malloc(4)
   reduce_dst = ishmem.calloc(1, 4)

   reduce_src.write((ishmem.my_pe() + 1).to_bytes(4, "little", signed=True))
   ishmem.reduce("sum", reduce_dst, reduce_src, dtype="int32")

``reducescatter`` is also available for API compatibility with ``nvshmem4py``.
Intel SHMEM does not currently expose a host-side primitive for it, so ``ishmem4py`` implements
that operation as a small software fallback on top of ``reduce``.

The binding also exposes team objects and team query or synchronization routines.
Those APIs follow Intel SHMEM handles rather than CUDA-object wrappers.

Building and Installing
^^^^^^^^^^^^^^^^^^^^^^^

Build Intel SHMEM with Python bindings enabled:

.. code-block:: bash

   cmake -S /path/to/ishmem -B /path/to/build -DBUILD_PYTHON_BINDINGS=ON ...
   cmake --build /path/to/build --target ishmem4py -j4

Install from the build tree:

.. code-block:: bash

   pip install /path/to/build/ishmem4py/python

For editable development, install the source tree and point it at the built runtime:

.. code-block:: bash

   pip install -e /path/to/ishmem/ishmem4py/python
   export ISHMEM4PY_RUNTIME_LIBRARY=/path/to/build/ishmem4py/python/ishmem4py/_ishmem4py_runtime.so

Testing
^^^^^^^

Typical source-tree test environment:

.. code-block:: bash

   unset ISHMEM_DIR
   export PYTHONPATH=/path/to/ishmem/ishmem4py/python:/path/to/ishmem/ishmem4py/test
   export ISHMEM4PY_RUNTIME_LIBRARY=/path/to/build/ishmem4py/python/ishmem4py/_ishmem4py_runtime.so
   export LD_LIBRARY_PATH=/path/to/openshmem/lib:$LD_LIBRARY_PATH
   export ISHMEM_RUNTIME=OPENSHMEM

Examples:

.. code-block:: bash

   mpiexec -n 1 ishmrun python3 /path/to/ishmem/ishmem4py/test/smoke_test.py
   mpiexec -n 2 ishmrun python3 /path/to/ishmem/ishmem4py/test/ring_test.py
   mpiexec -n 2 ishmrun python3 /path/to/ishmem/ishmem4py/test/collective_test.py

Current Scope
^^^^^^^^^^^^^

The exported Python API is limited to functionality that has been validated in this environment.
Host atomics and dynamic team-split helpers were intentionally removed from the public bindings
after backend-level failures in the current OpenSHMEM runtime.
