# Copyright (C) 2026 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause

from __future__ import annotations

import sys

import torch

import ishmem4py as ishmem

from utils import expect_equal, expect_true


def main() -> int:
    ishmem.init()
    try:
        tensor = ishmem.tensor((4,), dtype=torch.float32, device="xpu")
        mirror = ishmem.tensor((4,), dtype=torch.float32, device="xpu")
        try:
            tensor.fill_(3.0)
            torch.xpu.synchronize()

            expect_true("tensor allocation is symmetric", ishmem.is_symmetric_tensor(tensor))
            expect_true("tensor base returns self for base allocation", ishmem.tensor_base(tensor) is tensor)
            expect_equal("tensor contents", tensor.cpu().tolist(), [3.0, 3.0, 3.0, 3.0])

            stream = torch.xpu.Stream()
            ishmem.put(mirror, tensor, pe=ishmem.my_pe(), queue=stream)
            ishmem.quiet(queue=stream)
            expect_equal("queued self put", mirror.cpu().tolist(), [3.0, 3.0, 3.0, 3.0])

            recv = ishmem.tensor((4,), dtype=torch.float32, device="xpu")
            try:
                recv.zero_()
                stream = torch.xpu.Stream()
                ishmem.get(recv, tensor, pe=ishmem.my_pe(), queue=stream)
                ishmem.quiet(queue=stream)
                expect_equal("queued self get", recv.cpu().tolist(), [3.0, 3.0, 3.0, 3.0])
            finally:
                ishmem.free_tensor(recv)
        finally:
            ishmem.free_tensor(mirror)
            ishmem.free_tensor(tensor)
    finally:
        ishmem.finalize()

    return 0


if __name__ == "__main__":
    sys.exit(main())
