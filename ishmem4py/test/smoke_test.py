# Copyright (C) 2026 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause

import struct
import unittest

import ishmem4py as ishmem


class SmokeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        ishmem.init()

    @classmethod
    def tearDownClass(cls):
        if ishmem.is_initialized():
            ishmem.finalize()

    def test_version_and_world_info(self):
        major, minor = ishmem.info_get_version()
        self.assertGreaterEqual(major, 1)
        self.assertGreaterEqual(minor, 0)
        self.assertEqual(ishmem.n_pes(), 1)
        self.assertEqual(ishmem.my_pe(), 0)

    def test_malloc_read_write_free(self):
        buf = ishmem.malloc(16)
        buf.write(struct.pack("=4i", 1, 2, 3, 4))
        self.assertEqual(struct.unpack("=4i", buf.read(16)), (1, 2, 3, 4))
        ishmem.free(buf)

    def test_calloc_zero_initialized(self):
        buf = ishmem.calloc(4, 4)
        self.assertEqual(buf.read(16), b"\x00" * 16)
        ishmem.free(buf)


if __name__ == "__main__":
    unittest.main()
