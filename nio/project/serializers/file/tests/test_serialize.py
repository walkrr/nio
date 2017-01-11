import os
import tempfile
import shutil
from unittest.mock import Mock

from nio.project import BlockEntity
from nio.project import ConfigurationEntity
from nio.project import Project
from nio.testing import NIOTestCase
from ..serializer import FileSerializer


class TestSerialize(NIOTestCase):
    """ Test serialize functionality
    """

    def setUp(self):
        super().setUp()
        # create a tmp directory where serialized project will reside
        self.tmp_project_dir = tempfile.mkdtemp()

    def tearDown(self):
        if os.path.isdir(self.tmp_project_dir):
            shutil.rmtree(self.tmp_project_dir)
        super().tearDown()

    def test_non_existent_project_dir(self):
        """ Asserts file is serialized when target folder doesn't exist
        """
        project1 = Project()
        project1.configuration["section"] = \
            ConfigurationEntity({"option1": "value1"})

        # remove tmp dir, effectively making serializer create it
        shutil.rmtree(self.tmp_project_dir)
        self.assertFalse(os.path.isdir(self.tmp_project_dir))

        serializer = FileSerializer(self.tmp_project_dir)
        conf_file = os.path.join(self.tmp_project_dir,
                                 serializer._conf_filename)
        self.assertFalse(os.path.isfile(conf_file))

        serializer.serialize(project1)

        # make sure conf file made it to project directory
        self.assertTrue(os.path.isfile(conf_file))

    def test_invalid_entity(self):
        """ Asserts invalid entities are ignored
        """
        project1 = Project()
        project1.blocks["block1"] = BlockEntity({"name": "block1"})
        project1.blocks["block2"] = {"name": "block2"}
        project1.blocks["block3"] = BlockEntity({"name": "block3"})

        serializer1 = FileSerializer(self.tmp_project_dir)
        # mock logger
        serializer1.logger = Mock()
        serializer1.serialize(project1)
        #  assert a warning was logged
        self.assertEqual(serializer1.logger.warning.call_count, 1)

        # deserialize back and assert that invalid entity 'block2' was ignored
        serializer2 = FileSerializer(self.tmp_project_dir)
        project2 = serializer2.deserialize()
        self.assertIn("block1", project2.blocks)
        self.assertNotIn("block2", project2.blocks)
        self.assertIn("block3", project2.blocks)

    def test_non_serializable_entity(self):
        """ Asserts invalid entities are ignored
        """
        project1 = Project()
        not_serializable_entity_attribute = self.test_non_serializable_entity
        project1.blocks["block1"] = \
            BlockEntity({"name": not_serializable_entity_attribute})

        serializer1 = FileSerializer(self.tmp_project_dir)
        # mock logger
        serializer1.logger = Mock()
        serializer1.serialize(project1)
        #  assert an exception was logged
        self.assertEqual(serializer1.logger.exception.call_count, 1)

        # deserialize back and assert that no blocks were deserialized
        serializer2 = FileSerializer(self.tmp_project_dir)
        serializer2.logger = Mock()
        project2 = serializer2.deserialize()
        #  assert an exception was logged
        self.assertEqual(serializer2.logger.exception.call_count, 1)
        # assert project2 contains no blocks
        self.assertEqual(len(project2.blocks), 0)

    def test_configuration(self):
        """ Asserts configuration serialization
        """
        project1 = Project()
        project1.configuration["logging"] = \
            ConfigurationEntity({"option1": "value1"})

        serializer1 = FileSerializer(self.tmp_project_dir)
        serializer1.serialize(project1)

        serializer2 = FileSerializer(self.tmp_project_dir)
        project2 = serializer2.deserialize()
        for section, entity in project1.configuration.items():
            self.assertDictEqual(entity.data,
                                 project2.configuration[section].data)

        # Assert that serializer is able to write to an existing conf file.
        serializer1 = FileSerializer(self.tmp_project_dir)
        project1 = Project()
        # setup project1 to now contain a new entry
        project1.configuration["logging"] = \
            ConfigurationEntity({"option2": "value2"})
        serializer1.serialize(project1)

        # assert that "option1" entry existing in file was kept intact,
        # and that option2 was added
        serializer2 = FileSerializer(self.tmp_project_dir)
        project2 = serializer2.deserialize()
        self.assertIn("option1",
                      project2.configuration["logging"].data)
        self.assertIn("option2",
                      project2.configuration["logging"].data)

    def test_config_dict_entries(self):
        """ Asserts known dict entries are serialized as files
        """
        project = Project()
        for (section, option, _) in FileSerializer.links:
            if section in project.configuration:
                project.configuration[section].data[option] = {}
            else:
                project.configuration[section] = \
                    ConfigurationEntity({option: {}})

        serializer = FileSerializer(self.tmp_project_dir)
        serializer.serialize(project)

        # assert that a file exists for each option
        for (_, _, sub_path) in FileSerializer.links:
            linked_file = os.path.join(self.tmp_project_dir, sub_path)
            self.assertTrue(os.path.isfile(linked_file))

    def test_invalid_config_dict_entry(self):
        """ Asserts known dict entries are serialized as files
        """
        project = Project()
        project.configuration['logging'] = \
            ConfigurationEntity(
                {'conf': {'invalid': self.test_invalid_config_dict_entry}})

        serializer = FileSerializer(self.tmp_project_dir)
        # mock logger
        serializer.logger = Mock()
        serializer.serialize(project)

        #  assert a warning was logged
        self.assertEqual(serializer.logger.exception.call_count, 1)

    def test_blocks(self):
        """ Asserts blocks serialization
        """

        project1 = Project()
        project1.blocks["block1"] = BlockEntity({"name": "block1"})

        serializer1 = FileSerializer(self.tmp_project_dir)
        serializer1.serialize(project1)

        serializer2 = FileSerializer(self.tmp_project_dir)
        project2 = serializer2.deserialize()
        for entity_name, entity in project1.blocks.items():
            self.assertDictEqual(entity.data,
                                 project2.blocks[entity_name].data)
