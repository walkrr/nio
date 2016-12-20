from enum import Enum

from nio.properties import FloatProperty, SelectProperty, \
    BoolProperty
from nio.properties import IntProperty
from nio.properties import ListProperty
from nio.properties import ObjectProperty
from nio.properties import PropertyHolder
from nio.properties import StringProperty
from nio.properties import TimeDeltaProperty
from nio.properties.util.object_type import ObjectType
from nio.types import BoolType
from nio.types import FloatType
from nio.types import IntType
from nio.types import ListType
from nio.types import SelectType
from nio.types import StringType
from nio.types import TimeDeltaType
from nio.testing.test_case import NIOTestCaseNoModules


class ContainedClass(PropertyHolder):
    string_property = StringProperty(title="string_property", default="str")
    int_property = IntProperty(title="int_property", default=5)


class SampleEnum(Enum):
    option1 = 0
    option2 = 1
    option3 = 2


class ContainerClass(PropertyHolder):
    string_property = StringProperty(
        title="string_property", default="string1")
    string_property_default_env_variable = \
        StringProperty(title="string_property_default_env_variable",
                       default='[[ENV_VARIABLE]]')

    expression_property = StringProperty(title="expression_property",
                                         default='Default to {{$v1}}')
    expression_property_default_env_variable = \
        StringProperty(title="expression_property_default_env_variable",
                       default='[[ENV_VARIABLE]]')

    bool_property = BoolProperty(title="bool_property",
                                 default=False)
    bool_property_default_env_variable = \
        BoolProperty(title="bool_property_default_env_variable",
                     default='[[ENV_VARIABLE]]')

    int_property = IntProperty(title="int_property", default=8)
    int_property_default_env_variable = \
        IntProperty(title="int_property_default_env_variable",
                    default='[[ENV_VARIABLE]]')

    float_property = FloatProperty(title="float_property", default=8)
    float_property_default_env_variable = \
        FloatProperty(title="float_property_default_env_variable",
                      default='[[ENV_VARIABLE]]')

    object_property = ObjectProperty(ContainedClass, title="object_property")
    object_property_default_env_variable = \
        ObjectProperty(ContainedClass,
                       title="object_property_default_env_variable",
                       default='[[ENV_VARIABLE]]')

    list_property1 = ListProperty(ContainedClass, title="list_property1",
                                  default=[ContainedClass()])
    list_property2 = ListProperty(ContainedClass, title="list_property2")
    list_property3 = ListProperty(IntType, title="list_property3", default=[1])
    list_property_default_env_variable = \
        ListProperty(ContainedClass,
                     title="list_property_default_env_variable",
                     default='[[ENV_VARIABLE]]')

    timedelta_property = TimeDeltaProperty(title="timedelta_property",
                                           default={"seconds": 9})
    timedelta_property_no_default = \
        TimeDeltaProperty(title="timedelta_property_no_default")

    select_property = SelectProperty(
        SampleEnum, title="select_property", default=SampleEnum.option2)
    select_property_default_env_variable = \
        SelectProperty(
            SampleEnum, title="select_property_default_env_variable",
            default='[[ENV_VARIABLE]]')


class TestTypes(NIOTestCaseNoModules):

    def test_types(self):
        """Testing that defaults are retrieved and are serializable."""
        description = ContainerClass.get_description()

        self.assertEqual(description['string_property']['type'],
                         StringType.__name__)
        self.assertEqual(description['string_property_default_env_variable']
                         ['type'], StringType.__name__)

        self.assertEqual(description['expression_property']['type'],
                         StringType.__name__)
        self.assertEqual(
            description['expression_property_default_env_variable']
            ['type'], StringType.__name__)

        self.assertEqual(description['bool_property']['type'],
                         BoolType.__name__)
        self.assertEqual(description['bool_property_default_env_variable']
                         ['type'], BoolType.__name__)

        self.assertEqual(description['int_property']['type'],
                         IntType.__name__)
        self.assertEqual(description['int_property_default_env_variable']
                         ['type'], IntType.__name__)

        self.assertEqual(description['float_property']['type'],
                         FloatType.__name__)
        self.assertEqual(description['float_property_default_env_variable']
                         ['type'], FloatType.__name__)

        self.assertEqual(description['object_property']['type'],
                         ObjectType.__name__)
        self.assertEqual(description['object_property_default_env_variable']
                         ['type'], ObjectType.__name__)

        self.assertEqual(description['list_property1']['type'],
                         ListType.__name__)
        self.assertEqual(description['list_property2']['type'],
                         ListType.__name__)
        self.assertEqual(description['list_property3']['type'],
                         ListType.__name__)
        self.assertEqual(description['list_property_default_env_variable']
                         ['type'], ListType.__name__)

        self.assertEqual(description['timedelta_property']['type'],
                         TimeDeltaType.__name__)
        self.assertEqual(description['timedelta_property_no_default']['type'],
                         TimeDeltaType.__name__)

        self.assertEqual(description['select_property']['type'],
                         SelectType.__name__)
        self.assertEqual(description['select_property_default_env_variable']
                         ['type'], SelectType.__name__)
