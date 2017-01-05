from nio.project import Project, Configuration, BlockEntity, ServiceEntity
from nio.testing import NIOTestCase
from ..serializer import BinarySerializer


class TestBinarySerializer(NIOTestCase):

    def test_serialize_and_deserialize(self):
        """ Make sure we can serialize then deserialize a project """
        project = Project()
        project.configuration = {
            "section": Configuration(data={"key": "value"})
        }
        project.services = {
            "ServiceName": ServiceEntity(data={"auto_start": True})
        }
        project.blocks = {
            "BlockName": BlockEntity(data={"log_level": "INFO"})
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
            new_project.configuration['section'].data,
            {"key": "value"})
        self.assertEqual(len(new_project.blocks), 1)
        self.assertDictEqual(
            new_project.blocks['BlockName'].data,
            {"log_level": "INFO"})
        self.assertEqual(len(new_project.services), 1)
        self.assertDictEqual(
            new_project.services['ServiceName'].data,
            {"auto_start": True})
