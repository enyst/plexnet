import py
from pypy.rpython.lltypesystem.lloperation import LL_OPERATIONS, llop, void
from pypy.rpython.lltypesystem import lltype, opimpl
from pypy.rpython.ootypesystem import ootype, ooopimpl
from pypy.rpython.llinterp import LLFrame
from pypy.rpython.test.test_llinterp import interpret
from pypy.rpython import rclass

LL_INTERP_OPERATIONS = [name[3:] for name in LLFrame.__dict__.keys()
                                 if name.startswith('op_')]

# ____________________________________________________________

def test_canfold_opimpl_complete():
    for opname, llop in LL_OPERATIONS.items():
        assert opname == llop.opname
        if llop.canfold:
            if llop.oo:
                func = ooopimpl.get_op_impl(opname)
            else:
                func = opimpl.get_op_impl(opname)
            assert callable(func)

def test_llop_fold():
    assert llop.int_add(lltype.Signed, 10, 2) == 12
    assert llop.int_add(lltype.Signed, -6, -7) == -13
    S1 = lltype.GcStruct('S1', ('x', lltype.Signed), hints={'immutable': True})
    s1 = lltype.malloc(S1)
    s1.x = 123
    assert llop.getfield(lltype.Signed, s1, 'x') == 123
    S2 = lltype.GcStruct('S2', ('x', lltype.Signed))
    s2 = lltype.malloc(S2)
    s2.x = 123
    py.test.raises(TypeError, "llop.getfield(lltype.Signed, s2, 'x')")

def test_llop_interp():
    from pypy.rpython.annlowlevel import LowLevelAnnotatorPolicy
    def llf(x, y):
        return llop.int_add(lltype.Signed, x, y)
    res = interpret(llf, [5, 7], policy=LowLevelAnnotatorPolicy())
    assert res == 12

def test_llop_with_voids_interp():
    from pypy.rpython.annlowlevel import LowLevelAnnotatorPolicy
    S = lltype.GcStruct('S', ('x', lltype.Signed), ('y', lltype.Signed))
    name_y = void('y')
    def llf():
        s = lltype.malloc(S)
        llop.bare_setfield(lltype.Void, s, void('x'), 3)
        llop.bare_setfield(lltype.Void, s, name_y, 2)        
        return s.x + s.y
    res = interpret(llf, [], policy=LowLevelAnnotatorPolicy())
    assert res == 5

def test_is_pure():
    from pypy.objspace.flow.model import Variable, Constant
    assert llop.bool_not.is_pure([Variable()])
    assert llop.debug_assert.is_pure([Variable()])
    assert not llop.int_add_ovf.is_pure([Variable(), Variable()])
    #
    S1 = lltype.GcStruct('S', ('x', lltype.Signed), ('y', lltype.Signed))
    v_s1 = Variable()
    v_s1.concretetype = lltype.Ptr(S1)
    assert not llop.setfield.is_pure([v_s1, Constant('x'), Variable()])
    assert not llop.getfield.is_pure([v_s1, Constant('y')])
    #
    A1 = lltype.GcArray(lltype.Signed)
    v_a1 = Variable()
    v_a1.concretetype = lltype.Ptr(A1)
    assert not llop.setarrayitem.is_pure([v_a1, Variable(), Variable()])
    assert not llop.getarrayitem.is_pure([v_a1, Variable()])
    assert llop.getarraysize.is_pure([v_a1])
    #
    S2 = lltype.GcStruct('S', ('x', lltype.Signed), ('y', lltype.Signed),
                         hints={'immutable': True})
    v_s2 = Variable()
    v_s2.concretetype = lltype.Ptr(S2)
    assert not llop.setfield.is_pure([v_s2, Constant('x'), Variable()])
    assert llop.getfield.is_pure([v_s2, Constant('y')])
    #
    A2 = lltype.GcArray(lltype.Signed, hints={'immutable': True})
    v_a2 = Variable()
    v_a2.concretetype = lltype.Ptr(A2)
    assert not llop.setarrayitem.is_pure([v_a2, Variable(), Variable()])
    assert llop.getarrayitem.is_pure([v_a2, Variable()])
    assert llop.getarraysize.is_pure([v_a2])
    #
    accessor = rclass.FieldListAccessor()
    S3 = lltype.GcStruct('S', ('x', lltype.Signed), ('y', lltype.Signed),
                         hints={'immutable_fields': accessor})
    accessor.initialize(S3, ['x'])
    v_s3 = Variable()
    v_s3.concretetype = lltype.Ptr(S3)
    assert not llop.setfield.is_pure([v_s3, Constant('x'), Variable()])
    assert not llop.setfield.is_pure([v_s3, Constant('y'), Variable()])
    assert llop.getfield.is_pure([v_s3, Constant('x')])
    assert not llop.getfield.is_pure([v_s3, Constant('y')])

def test_getfield_pure():
    S1 = lltype.GcStruct('S', ('x', lltype.Signed), ('y', lltype.Signed))
    S2 = lltype.GcStruct('S', ('x', lltype.Signed), ('y', lltype.Signed),
                         hints={'immutable': True})
    accessor = rclass.FieldListAccessor()
    S3 = lltype.GcStruct('S', ('x', lltype.Signed), ('y', lltype.Signed),
                         hints={'immutable_fields': accessor})
    accessor.initialize(S3, ['x'])
    #
    s1 = lltype.malloc(S1); s1.x = 45
    py.test.raises(TypeError, llop.getfield, lltype.Signed, s1, 'x')
    s2 = lltype.malloc(S2); s2.x = 45
    assert llop.getfield(lltype.Signed, s2, 'x') == 45
    s3 = lltype.malloc(S3); s3.x = 46; s3.y = 47
    assert llop.getfield(lltype.Signed, s3, 'x') == 46
    py.test.raises(TypeError, llop.getfield, lltype.Signed, s3, 'y')
    #
    py.test.raises(TypeError, llop.getinteriorfield, lltype.Signed, s1, 'x')
    assert llop.getinteriorfield(lltype.Signed, s2, 'x') == 45
    assert llop.getinteriorfield(lltype.Signed, s3, 'x') == 46
    py.test.raises(TypeError, llop.getinteriorfield, lltype.Signed, s3, 'y')

# ___________________________________________________________________________
# This tests that the LLInterpreter and the LL_OPERATIONS tables are in sync.

def test_table_complete():
    for opname in LL_INTERP_OPERATIONS:
        assert opname in LL_OPERATIONS

def test_llinterp_complete():
    for opname, llop in LL_OPERATIONS.items():
        if llop.canfold:
            continue
        if opname.startswith('gc_x_'):
            continue   # ignore experimental stuff
        assert opname in LL_INTERP_OPERATIONS
