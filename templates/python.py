#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest2 as unittest

class CLASSNAME:
    def __init__(self):
        pass

class CLASSNAMETest(unittest.TestCase):
    def test_init(self):
        self.assertNotEqual(CLASSNAME(), None)

if __name__ == '__main__':
    unittest.main()
