# Copyright (C) 2026 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause

import struct
import sys

import ishmem4py as ishmem


def _expect_equal(label: str, actual: int, expected: int) -> None:
    if actual != expected:
        raise AssertionError(f"{label}: expected {expected}, got {actual}")


def main() -> int:
    ishmem.init()
    try:
        my_pe = ishmem.my_pe()
        npes = ishmem.n_pes()
        if npes < 2:
            raise RuntimeError("ring_test.py requires at least 2 PEs")

        next_pe = (my_pe + 1) % npes
        prev_pe = (my_pe + npes - 1) % npes

        src = ishmem.malloc(4)
        dst = ishmem.calloc(1, 4)
        try:
            src.write(struct.pack("=i", my_pe))

            ishmem.barrier_all()

            ishmem.putmem(dst, src.read(4), pe=next_pe)
            ishmem.barrier_all()

            received = struct.unpack("=i", dst.read(4))[0]
            _expect_equal("putmem ring result", received, prev_pe)

            host_value = bytearray(4)
            ishmem.getmem(host_value, src, pe=next_pe)
            fetched = struct.unpack("=i", host_value)[0]
            _expect_equal("getmem ring result", fetched, next_pe)

            ishmem.barrier_all()
        finally:
            ishmem.free(dst)
            ishmem.free(src)
    finally:
        ishmem.finalize()

    return 0


if __name__ == "__main__":
    sys.exit(main())
