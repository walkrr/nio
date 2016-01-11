from nio.block.base import Block
from nio.util.support.test_case import NIOTestCaseNoModules
from nio.block.terminals import Input, Output, Terminal, TerminalType


@Input("i1")
@Input("i2")
@Output("o1")
@Output("o2")
class Parent(Block):
    pass


@Input("ParentSubClass_input")
@Output("ParentSubClass_output")
class ParentSubClass(Parent):
    pass


@Input("i1")
@Output("o2")
class Duplicates(Parent):
    pass


class TestInputOutput(NIOTestCaseNoModules):

    def test_terminal_inheritance(self):
        """Asserts that terminal definitions are inherited by subclasses."""
        # assert that Block has 'default' as an input attribute
        inputs = Terminal.get_terminals_on_class(Block, TerminalType.input)
        self.assertSetEqual(inputs, {"default"})

        # assert that Block has 'default' as an output attribute
        outputs = Terminal.get_terminals_on_class(Block, TerminalType.output)
        self.assertSetEqual(outputs, {"default"})

        inputs = Terminal.get_terminals_on_class(Parent, TerminalType.input)
        # TODO: Remove default after NIO-741 is complete
        self.assertSetEqual(inputs, {"i1", "i2", "default"})

        outputs = Terminal.get_terminals_on_class(Parent, TerminalType.output)
        # TODO: Remove default after NIO-741 is complete
        self.assertSetEqual(outputs, {"o1", "o2", "default"})

        inputs = Terminal.get_terminals_on_class(
            ParentSubClass, TerminalType.input)
        # TODO: Remove default after NIO-741 is complete
        self.assertSetEqual(
            inputs, {"i1", "i2", "ParentSubClass_input", "default"})

        outputs = Terminal.get_terminals_on_class(
            ParentSubClass, TerminalType.output)
        # TODO: Remove default after NIO-741 is complete
        self.assertSetEqual(
            outputs, {"o1", "o2", "ParentSubClass_output", "default"})

    def test_duplicate_terminals(self):
        """Asserts that duplicate attribute definitions are ignored."""
        inputs = Terminal.get_terminals_on_class(
            Duplicates, TerminalType.input)
        # TODO: Remove default after NIO-741 is complete
        self.assertSetEqual(inputs, {"i1", "i2", "default"})

        outputs = Terminal.get_terminals_on_class(
            Duplicates, TerminalType.output)
        # TODO: Remove default after NIO-741 is complete
        self.assertSetEqual(outputs, {"o1", "o2", "default"})

    def test_terminal_types(self):
        """Asserts that terminals can only be created with TerminalType"""
        # Try to create a bad terminal
        with self.assertRaises(TypeError):
            Terminal("not a real terminal type", "fake terminal name")

        # Try to fetch a bad terminal
        with self.assertRaises(TypeError):
            Terminal.get_terminals_on_class(Block, "not a real terminal type")
