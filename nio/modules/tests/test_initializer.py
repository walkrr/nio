from datetime import datetime

from unittest.mock import patch, MagicMock
from nio.modules.initializer import ModuleInitializer
from nio.modules.proxy import ProxyNotProxied, ProxyAlreadyProxied
from nio.modules.module import Module
from nio.testing.test_case import NIOTestCaseNoModules


class MyModuleInitializer(ModuleInitializer):

    def get_context(self, module):
        pass


class TestModuleInterface(Module):

    def __init__(self):
        super().__init__()
        self._initialized_time = None
        self._finalized_time = None

    def initialize(self, context):
        super().initialize(context)
        self._initialized_time = datetime.now()

    def finalize(self):
        self._finalized_time = datetime.now()
        super().finalize()


class FirstModuleImplementation(TestModuleInterface):

    def get_module_order(self):
        return 1


class SecondModuleImplementation(TestModuleInterface):

    def get_module_order(self):
        return 2


class TestModuleInitializer(NIOTestCaseNoModules):

    def test_register_module(self):
        """ Test that we can register then initialize a module """
        initializer = MyModuleInitializer()
        impl = FirstModuleImplementation()
        with patch.object(impl, 'initialize') as init_call:
            initializer.register_module(impl)
            # Don't want an init call after registering
            self.assertEqual(init_call.call_count, 0)
            initializer.initialize()
            init_call.assert_called_once()
        with patch.object(impl, 'finalize') as finalize_call:
            initializer.finalize()
            finalize_call.assert_called_once_with()

    def test_register_types(self):
        """ Asserts that registration must be called with the right type """
        initializer = ModuleInitializer()
        # Can't register a class, must be instance
        with self.assertRaises(TypeError):
            initializer.register_module(TestModuleInterface)

        # Have to register with a module context
        with self.assertRaises(TypeError):
            initializer.register_module(TestModuleInterface(), {})

    def test_module_order(self):
        """ Asserts modules get initialized in the correct order """
        initializer = MyModuleInitializer()
        impl1 = FirstModuleImplementation()
        impl2 = SecondModuleImplementation()
        # Even if we register them in reverse order
        initializer.register_module(impl2)
        initializer.register_module(impl1)
        initializer.initialize()
        # Make sure, despite the order of registration, the modules were
        # initialized in the correct order (low order to high order)
        self.assertLess(impl1._initialized_time, impl2._initialized_time)

        # Make sure finalization happens in the reverse order
        initializer.finalize()
        self.assertGreater(impl1._finalized_time, impl2._finalized_time)

    def test_unsafe_initialize(self):
        """ Test that an unsafe module initialize raises an exception """
        initializer = MyModuleInitializer()
        # Our implementation is a module that raises ProxyAlreadyProxied
        # when it is initialized
        impl = MagicMock(spec=TestModuleInterface)
        impl.initialize.side_effect = ProxyAlreadyProxied
        initializer.register_module(impl)
        with self.assertRaises(ProxyAlreadyProxied):
            initializer.initialize(safe=False)
        # We should not have finalized either
        self.assertEqual(impl.finalize.call_count, 0)

    def test_unsafe_finalize(self):
        """ Test that an unsafe module finalize raises an exception """
        initializer = MyModuleInitializer()
        impl = TestModuleInterface()
        initializer.register_module(impl)
        initializer.initialize()
        with patch.object(impl, 'finalize', side_effect=ProxyNotProxied):
            with self.assertRaises(ProxyNotProxied):
                initializer.finalize(safe=False)

    def test_safe_finalize(self):
        """ Test that a safe module finalize ignores the exception """
        initializer = MyModuleInitializer()
        impl = TestModuleInterface()
        initializer.register_module(impl)
        initializer.initialize()
        with patch.object(impl, 'finalize', side_effect=ProxyNotProxied):
            # This should just work and do nothing
            initializer.finalize(safe=True)
