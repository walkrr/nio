import os

from nio.testing import NIOTestCase

from ..serializer import FileSerializer


class TestFileSerializer(NIOTestCase):

    project_dir = os.path.join(os.path.dirname(__file__), "test_project")

    def test_serializer_defaults(self):
        """ Makes sure it uses the cwd as the default directory """
        serializer = FileSerializer(self.project_dir)
        self.assertEqual(serializer._project_path, os.getcwd())
        self.assertEqual(serializer._conf_filename, 'nio.conf')

    def test_loads_configuration(self):
        serializer = FileSerializer(self.project_dir, "nio.conf.test",
                                    "nio.env.test")
        project = serializer.deserialize()

        config = project.configuration

        # assert that logging conf link was expanded to a dictionary
        self.assertIn("logging", config)
        self.assertIn("conf", config["logging"].data)
        self.assertIsInstance(config["logging"].data["conf"], dict)

        # assert that security users link was expanded to a dictionary
        self.assertIn("security", config)
        self.assertIn("users", config["security"].data)
        self.assertIsInstance(config["security"].data["users"], dict)

        # assert that security permissions link was expanded to a dictionary
        self.assertIn("security", config)
        self.assertIn("permissions", config["security"].data)
        self.assertIsInstance(
            config["security"].data["permissions"], dict)

        # assert that settings with environment variables are not expanded
        self.assertEqual(
            config['security'].data['jwt_key_b64'],
            '[[JWT_VERIFY_KEY_B64]]')

    def test_loads_blocks_and_services(self):
        serializer = FileSerializer(self.project_dir, "nio.conf.test",
                                    "nio.env.test")
        project = serializer.deserialize()

        blocks = project.blocks
        services = project.services

        # Make sure our configured blocks are there
        self.assertIn("logger", blocks)
        # And that their config came along correctly
        self.assertEqual(blocks['logger'].data['log_at'], 'DEBUG')

        # Make sure our configured services are there
        self.assertIn("sim_and_log", services)
        # And that their config came along correctly
        self.assertFalse(services['sim_and_log'].data['auto_start'])

    def test_serializer_invalid_project(self):
        serializer = FileSerializer("invalid", "nio.conf.test",
                                    "nio.env.test")

        with self.assertRaises(ValueError):
            serializer.deserialize()

        with self.assertRaises(ValueError):
            serializer._deserialize_entities('folder_that_doesnt_exist', dict,
                                             None)
