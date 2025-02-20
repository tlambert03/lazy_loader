import sys
import types

import pytest

import lazy_loader as lazy


def test_lazy_import_basics():
    math = lazy.load("math")
    anything_not_real = lazy.load("anything_not_real")

    # Now test that accessing attributes does what it should
    assert math.sin(math.pi) == pytest.approx(0, 1e-6)
    # poor-mans pytest.raises for testing errors on attribute access
    try:
        anything_not_real.pi
        assert False  # Should not get here
    except ModuleNotFoundError:
        pass
    assert isinstance(anything_not_real, lazy.DelayedImportErrorModule)
    # see if it changes for second access
    try:
        anything_not_real.pi
        assert False  # Should not get here
    except ModuleNotFoundError:
        pass


def test_lazy_import_impact_on_sys_modules():
    math = lazy.load("math")
    anything_not_real = lazy.load("anything_not_real")

    assert isinstance(math, types.ModuleType)
    assert "math" in sys.modules
    assert isinstance(anything_not_real, lazy.DelayedImportErrorModule)
    assert "anything_not_real" not in sys.modules

    # only do this if numpy is installed
    pytest.importorskip("numpy")
    np = lazy.load("numpy")
    assert isinstance(np, types.ModuleType)
    assert "numpy" in sys.modules

    np.pi  # trigger load of numpy

    assert isinstance(np, types.ModuleType)
    assert "numpy" in sys.modules


def test_lazy_import_nonbuiltins():
    sp = lazy.load("scipy")
    np = lazy.load("numpy")
    if isinstance(sp, lazy.DelayedImportErrorModule):
        try:
            sp.pi
            assert False
        except ModuleNotFoundError:
            pass
    elif isinstance(np, lazy.DelayedImportErrorModule):
        try:
            np.sin(np.pi)
            assert False
        except ModuleNotFoundError:
            pass
    else:
        assert np.sin(sp.pi) == pytest.approx(0, 1e-6)


def test_lazy_attach():
    name = "mymod"
    submods = ["mysubmodule", "anothersubmodule"]
    myall = {"not_real_submod": ["some_var_or_func"]}

    locls = {
        "attach": lazy.attach,
        "name": name,
        "submods": submods,
        "myall": myall,
    }
    s = "__getattr__, __lazy_dir__, __all__ = attach(name, submods, myall)"

    exec(s, {}, locls)
    expected = {
        "attach": lazy.attach,
        "name": name,
        "submods": submods,
        "myall": myall,
        "__getattr__": None,
        "__lazy_dir__": None,
        "__all__": None,
    }
    assert locls.keys() == expected.keys()
    for k, v in expected.items():
        if v is not None:
            assert locls[k] == v


def test_attach_same_module_and_attr_name():
    import fake_pkg

    # Grab attribute twice, to ensure that importing it does not
    # override function by module
    assert isinstance(fake_pkg.some_func, types.FunctionType)
    assert isinstance(fake_pkg.some_func, types.FunctionType)

    # Ensure imports from submodule still work
    from fake_pkg.some_func import some_func

    assert isinstance(some_func, types.FunctionType)
