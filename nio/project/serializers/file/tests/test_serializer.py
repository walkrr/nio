import os
from nio.testing import NIOTestCase
from ..serializer import FileSerializer


class TestFileSerializer(NIOTestCase):

    project_dir = os.path.join(os.path.dirname(__file__), "test_project")

    def test_serializer_defaults(self):
        """ Makes sure it uses the cwd as the default directory """
        serializer = FileSerializer()
        self.assertEqual(serializer._project_path, os.getcwd())
        self.assertEqual(serializer._conf_filename, 'nio.conf')

    def test_loads_configuration(self):
        serializer = FileSerializer(self.project_dir, "nio.conf.test")
        project = serializer.deserialize()

        config = project.configuration

        # assert that logging conf link was expanded to a dictionary
        self.assertIn("logging", config)
        self.assertIn("conf", config["logging"].configuration)
        self.assertIsInstance(config["logging"].configuration["conf"], dict)

        # assert that security users link was expanded to a dictionary
        self.assertIn("security", config)
        self.assertIn("users", config["security"].configuration)
        self.assertIsInstance(config["security"].configuration["users"], dict)

        # assert that security permissions link was expanded to a dictionary
        self.assertIn("security", config)
        self.assertIn("permissions", config["security"].configuration)
        self.assertIsInstance(
            config["security"].configuration["permissions"], dict)

        # assert that settings with environment variables are not expanded
        self.assertEqual(
            config['security'].configuration['jwt_key_b64'],
            '[[JWT_VERIFY_KEY_B64]]')

    def test_loads_blocks_and_services(self):
        serializer = FileSerializer(self.project_dir, "nio.conf.test")
        project = serializer.deserialize()

        blocks = project.blocks
        services = project.services

        # Make sure our configured blocks are there
        self.assertIn("logger", blocks)
        # And that their config came along correctly
        self.assertEqual(blocks['logger'].configuration['log_at'], 'DEBUG')

        # Make sure our configured services are there
        self.assertIn("sim_and_log", services)
        # And that their config came along correctly
        self.assertFalse(services['sim_and_log'].configuration['auto_start'])

    def test_serializer_invalid_project(self):
        serializer = FileSerializer("invalid", "nio.conf.test")

        with self.assertRaises(ValueError):
            serializer.deserialize()

        with self.assertRaises(ValueError):
            serializer._load_entities('folder_that_doesnt_exist', dict)

    def test_serializer_invalid_conf_file(self):
        serializer = FileSerializer(self.project_dir, "nio.conf")
        with self.assertRaises(ValueError):
            serializer.deserialize()
