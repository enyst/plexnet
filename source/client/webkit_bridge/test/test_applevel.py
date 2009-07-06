
from pypy.conftest import gettestobjspace
from webkit_bridge.jsobj import JSObject, JavaScriptContext
from webkit_bridge.webkit_rffi import (JSGlobalContextCreate,
                                       JSGlobalContextRelease,
                                       empty_object)

class AppTestBindings(object):
    def setup_method(cls, meth):
        ctx = JavaScriptContext(cls.space, JSGlobalContextCreate())
        cls.w_js_obj = cls.space.wrap(JSObject(ctx, ctx.eval('[]')))
        this = ctx.eval('[]')
        ctx.eval('this.x = function(a, b) { return(a + b); }', this)
        cls.w_func = cls.space.wrap(JSObject(ctx, ctx.get(this, 'x')))
        cls.w_js_obj_2 = cls.space.wrap(JSObject(ctx, ctx.eval('[]')))
    
    def test_getattr_none(self):
        assert self.js_obj.x == None

    def test_getsetattr_obj(self):
        self.js_obj['x'] = 3
        assert isinstance(self.js_obj.x, float)
        assert self.js_obj.x == 3
        self.js_obj.y = 3
        assert isinstance(self.js_obj['y'], float)
        assert self.js_obj['y'] == 3

    def test_str(self):
        assert str(self.js_obj) == 'JSObject()'

    def test_call(self):
        assert self.func(3, 4) == 7
        assert self.func('a', 'bc') == 'abc'

    def test_obj_wrap_unwrap(self):
        self.js_obj['x'] = self.js_obj_2
        assert str(self.js_obj.x) == 'JSObject()'

    def test_floats(self):
        self.js_obj.y = 3.5
        assert self.js_obj.y == 3.5

    def test_bools(self):
        self.js_obj.x = True
        assert self.js_obj.x

    def test_none(self):
        self.js_obj.x = None
