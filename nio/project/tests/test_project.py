from nio.testing import NIOTestCase
from nio.project import Block, Configuration, Project, Service
from nio.project.serializers.serializer import ProjectSerializer


class TestProject(NIOTestCase):

    def test_project(self):
        """ Test that we can create a project with blocks/services """
        project = Project()
        project.configuration = {
            "section": Configuration(configuration={"key": "value"})
        }
        project.services = {
            "ServiceName": Service(configuration={"key": "value"})
        }
        project.blocks = {
            "BlockName": Block(configuration={"key": "value"})
        }

    def test_entity_defaults(self):
        """ Make sure we get reasonable defaults on new entities """
        # Not providing configuration should give us an empty dict
        b = Block()
        self.assertDictEqual(b.configuration, {})
        s = Service()
        self.assertDictEqual(s.configuration, {})

    def test_invalid_entities(self):
        """ Ensure exceptions raised when creating invalid entities """
        with self.assertRaises(TypeError):
            Block(configuration="not a dictionary")
        with self.assertRaises(TypeError):
            Service(configuration="not a dictionary")

    def test_serializer(self):
        """ Some sanity checks for the default serializer class """
        s = ProjectSerializer()
        proj = Project()
        # Even an empty project should be valid, the validate method should
        # pass without any exceptions
        s.validate_project(proj)
        # Validating a non project won't pass though
        with self.assertRaises(TypeError):
            s.validate_project({})
        # Can't serialize or deserialize from the base serializer
        with self.assertRaises(NotImplementedError):
            s.deserialize()
        with self.assertRaises(NotImplementedError):
            s.serialize(proj)
