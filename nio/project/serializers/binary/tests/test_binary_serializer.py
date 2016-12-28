from nio.project import Project, Configuration, Block, Service
from nio.testing import NIOTestCase
from ..serializer import BinarySerializer


class TestBinarySerializer(NIOTestCase):

    def test_serialize_and_deserialize(self):
        """ Make sure we can serialize then deserialize a project """
        project = Project()
        project.configuration = {
            "section": Configuration(configuration={"key": "value"})
        }
        project.services = {
            "ServiceName": Service(configuration={"auto_start": True})
        }
        project.blocks = {
            "BlockName": Block(configuration={"log_level": "INFO"})
        }

        serializer = BinarySerializer()
        serializer.serialize(project)
        project_bytes = serializer.binary_data

        self.assertIsInstance(project_bytes, bytes)

        deserializer = BinarySerializer(project_bytes)
        new_project = deserializer.deserialize()
        # Make sure our new project has all of the same project settings
        # as the original project
        self.assertEqual(len(new_project.configuration), 1)
        self.assertDictEqual(
            new_project.configuration['section'].configuration,
            {"key": "value"})
        self.assertEqual(len(new_project.blocks), 1)
        self.assertDictEqual(
            new_project.blocks['BlockName'].configuration,
            {"log_level": "INFO"})
        self.assertEqual(len(new_project.services), 1)
        self.assertDictEqual(
            new_project.services['ServiceName'].configuration,
            {"auto_start": True})
