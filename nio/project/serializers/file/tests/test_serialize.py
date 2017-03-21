import os
import shutil
import tempfile
from configparser import RawConfigParser
from unittest.mock import Mock

from nio.project import BlockEntity, ConfigurationEntity, Project, ServiceEntity
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
        # at the end of each test, make sure tmp folder/subfolders are removed
        if os.path.isdir(self.tmp_project_dir):
            shutil.rmtree(self.tmp_project_dir)
        super().tearDown()

    def test_non_existent_project_dir(self):
        """ Asserts file is serialized even if target folder doesn't exist
        """
        project = Project()
        project.configuration["section"] = \
            ConfigurationEntity({"option1": "value1"})

        # remove tmp dir, effectively making serializer create it
        shutil.rmtree(self.tmp_project_dir)
        self.assertFalse(os.path.isdir(self.tmp_project_dir))

        serializer = FileSerializer(self.tmp_project_dir)
        conf_file = os.path.join(self.tmp_project_dir,
                                 serializer._conf_filename)
        self.assertFalse(os.path.isfile(conf_file))

        serializer.serialize(project)

        # make sure conf file made it to project directory
        self.assertTrue(os.path.isfile(conf_file))

    def test_invalid_entity(self):
        """ Asserts invalid entities are ignored

        Note: A log statement is issued
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
        """ Asserts invalid entity data causes entity to be ignored

        Note: A log statement is issued
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

        If a conf file already exists it gets overwritten wiping out
        former contents
        """
        project1 = Project()
        # option to be wiped out
        project1.configuration["logging"] = \
            ConfigurationEntity({"option1": "value1"})
        # option to be saved with a new value
        project1.configuration["security"] = \
            ConfigurationEntity({"option3": "value3"})

        # seralize configuration creating a conf file on disk
        serializer1 = FileSerializer(self.tmp_project_dir)
        serializer1.serialize(project1)

        # assert that it is deserialized containing expected data
        serializer2 = FileSerializer(self.tmp_project_dir)
        project2 = serializer2.deserialize()
        for section, entity in project1.configuration.items():
            self.assertDictEqual(entity.data,
                                 project2.configuration[section].data)

        # Setup a new configuration asserting that existing configuration
        # is wiped out and only the new configuration is serialized
        serializer1 = FileSerializer(self.tmp_project_dir)
        project1 = Project()
        # setup project1 to now contain a new entry
        project1.configuration["logging"] = \
            ConfigurationEntity({"option2": "value2"})
        # add an option that already exists in file
        project1.configuration["security"] = \
            ConfigurationEntity({"option3": "new value3"})
        # serialize new project
        serializer1.serialize(project1)

        # deserialize new configuration
        serializer2 = FileSerializer(self.tmp_project_dir)
        project2 = serializer2.deserialize()

        # assert that option 1 was wiped out
        self.assertNotIn("option1",
                         project2.configuration["logging"].data)
        # assert that option 2 was added
        self.assertIn("option2",
                      project2.configuration["logging"].data)
        self.assertEqual('value2',
                         project2.configuration["logging"].data["option2"])
        # assert that option3 contains the new value
        self.assertIn("option3",
                      project2.configuration["security"].data)
        self.assertEqual('new value3',
                         project2.configuration["security"].data["option3"])

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

        # read created config file
        conf_file = os.path.join(self.tmp_project_dir,
                                 serializer._conf_filename)
        self.assertTrue(os.path.isfile(conf_file))
        settings = RawConfigParser()
        settings.read(conf_file)

        # for each potential link
        for (section, option, sub_path) in FileSerializer.links:
            # assert that a file exists for each option
            linked_file = os.path.join(self.tmp_project_dir, sub_path)
            self.assertTrue(os.path.isfile(linked_file))

            # assert that incoming configuration value was not saved in the
            # resulting config file, thus the link to it is what resulted
            # being saved
            self.assertTrue(settings.get(section, option).endswith(sub_path))

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

        # create a new instance to deserialize and compare
        serializer2 = FileSerializer(self.tmp_project_dir)
        project2 = serializer2.deserialize()

        # iterate through project1 and make sure project2 data matches it
        for entity_name, entity in project1.blocks.items():
            self.assertDictEqual(entity.data,
                                 project2.blocks[entity_name].data)

    def test_services(self):
        """ Asserts services serialization
        """

        project1 = Project()
        project1.services["service1"] = ServiceEntity({"name": "service1"})

        serializer1 = FileSerializer(self.tmp_project_dir)
        serializer1.serialize(project1)

        # create a new instance to deserialize and compare
        serializer2 = FileSerializer(self.tmp_project_dir)
        project2 = serializer2.deserialize()

        # iterate through project1 and make sure project2 data matches it
        for entity_name, entity in project1.services.items():
            self.assertDictEqual(entity.data,
                                 project2.services[entity_name].data)

    def test_services_exclusion(self):
        """ Asserts services exclusion during serialization
        """

        project1 = Project()
        project1.services["service1"] = ServiceEntity({"name": "service1"})

        serializer1 = FileSerializer(self.tmp_project_dir)
        serializer1.serialize(project1, include_services=False)

        # create a new instance to deserialize and compare
        serializer2 = FileSerializer(self.tmp_project_dir)
        project2 = serializer2.deserialize()

        # assert no services were deserialized since they were not serialized
        # in the first place
        self.assertEqual(len(project2.services), 0)
