import py
from support import BaseCTypesTestChecker
from ctypes import *

class TestStructFields(BaseCTypesTestChecker):
    # Structure/Union classes must get 'finalized' sooner or
    # later, when one of these things happen:
    #
    # 1. _fields_ is set.
    # 2. An instance is created.
    # 3. The type is used as field of another Structure/Union.
    # 4. The type is subclassed
    #
    # When they are finalized, assigning _fields_ is no longer allowed.

    def test_1_A(self):
        class X(Structure):
            pass
        assert sizeof(X) == 0 # not finalized
        X._fields_ = [] # finalized
        raises(AttributeError, setattr, X, "_fields_", [])

    def test_1_B(self):
        class X(Structure):
            _fields_ = [] # finalized
        raises(AttributeError, setattr, X, "_fields_", [])

    def test_2(self):
        py.test.skip("absent _fields_ semantics not implemented")
        class X(Structure):
            pass
        X()
        raises(AttributeError, setattr, X, "_fields_", [])

    def test_3(self):
        py.test.skip("subclassing semantics not implemented")
        class X(Structure):
            pass
        class Y(Structure):
            _fields_ = [("x", X)] # finalizes X
        raises(AttributeError, setattr, X, "_fields_", [])

    def test_4(self):
        py.test.skip("subclassing semantics not implemented")
        class X(Structure):
            pass
        class Y(X):
            pass
        raises(AttributeError, setattr, X, "_fields_", [])
        Y._fields_ = []
        raises(AttributeError, setattr, X, "_fields_", [])
