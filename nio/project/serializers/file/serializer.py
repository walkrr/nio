import json
import os
from configparser import RawConfigParser

from nio.project import Project, ConfigurationEntity, BlockEntity, ServiceEntity
from nio.project.entity import Entity
from nio.project.serializers.serializer import ProjectSerializer
from nio.util.logging import get_nio_logger


class FileSerializer(ProjectSerializer):

    extensions = ['.cfg', '.json']
    links = [("logging", "conf", "etc/logging.json"),
             ("security", "users", "etc/users.json"),
             ("security", "permissions", "etc/permissions.json"),
             ("environment", "blocks_from", "etc/blocks.json")]

    def __init__(self, project_path=None, conf_filename="nio.conf"):
        """ Initializes a config serializer instance

        Args:
            project_path (str): path to nio project location
            conf_filename (str): nio configuration file name
        """
        self.logger = get_nio_logger("FileSerializer")

        if project_path is None:
            project_path = os.getcwd()
        self._project_path = project_path
        self._conf_filename = conf_filename
        self.logger = get_nio_logger("File Project Serializer")

    def deserialize(self):
        """ Deserializes a file n.io project to a Project instance.

        This method will read the files that this serializer class has been
        configured with and return a Project instance based on the structure
        and configuration of the files.

        Returns:
            project (Project): A representation of this project as an instance
                of nio.project.Project
        """
        project = Project()
        # figure out path to etc folder
        etc_folder = os.path.join(self._project_path, "etc")
        if not os.path.isdir(etc_folder):
            raise ValueError("Expected 'etc' folder at: {} is missing".
                             format(etc_folder))

        # load nio conf first in case in the future '_load' itself depends
        # on anything we read from nio conf
        project.configuration = self._deserialize_nio_conf()

        # add blocks and services
        project.blocks = self._deserialize_entities(
            os.path.join(etc_folder, 'blocks'), BlockEntity)
        project.services = self._deserialize_entities(
            os.path.join(etc_folder, 'services'), ServiceEntity)

        return project

    def serialize(self, project):
        """ Take the project instance and create the necessary files """

        # serialize configuration
        self._serialize_nio_conf(project.configuration)

        # serialize blocks
        self._serialize_entities(
            project.blocks,
            os.path.join(self._project_path, 'etc', 'blocks'))

        # serialize services
        self._serialize_entities(
            project.services,
            os.path.join(self._project_path, 'etc', 'services'))

    def _serialize_nio_conf(self, configuration):
        """ Serializes nio configuration settings to a file

        Note: Any existing configuration will be wiped out

        Args:
            configuration (dict): Configuration to serialize with format:
                {name: entity}
        """
        if not configuration:
            self.logger.info("No configuration items need to be serialized, "
                             "{} will not be affected".
                             format(self._conf_filename))
            return

        # make sure path where conf file will be written exists
        if not os.path.isdir(self._project_path):
            os.makedirs(self._project_path)

        # create instance where settings will be stored and written from
        settings = RawConfigParser()

        # save special dict entries known to be saved as linked files
        serialized_entries = self._serialize_dict_entries(configuration)

        # write settings to parser
        for section, entity in configuration.items():
            # check for section existence
            if not settings.has_section(section):
                settings.add_section(section)
            # save every section option
            for option, value in entity.data.items():
                # handle potential links since need to save the link
                # instead of the value, (the link-value was not written into
                # the configuration to preserve incoming configuration
                # integrity)
                if (section,option) in serialized_entries:
                    # override value with 'link' value
                    value = serialized_entries[(section,option)]
                # save to settings resulting option value
                settings.set(section, option, value)

        # figure out path to nio conf file
        nio_conf = os.path.join(self._project_path, self._conf_filename)
        # save actual config file
        with open(nio_conf, 'w') as fp:
            settings.write(fp)

    def _serialize_entities(self, entities, to_folder):
        """ Serializes a list of entities as json files to a folder.

        For example, this function can save in the 'services' folder
        a list of Service objects.

        Args:
            entities (dict): Entities to serialize with format: {name: entity}
            to_folder (str): The folder where the entities are saved
        """

        if not os.path.isdir(to_folder):
            os.makedirs(to_folder)

        for entity_name, entity in entities.items():
            if not isinstance(entity, Entity):
                self.logger.warning('{} is not an entity, ignoring it'.
                                    format(entity_name))
                continue

            # create filename to serialize to
            filename = os.path.join(to_folder, "{}.cfg".format(entity_name))

            try:
                self.save_json(filename, entity.data,
                               indent=4, separators=(',', ': '), sort_keys=True)
            except Exception:
                # log exception and continue handling entities
                self.logger.exception("Could not save entity data for: {}".
                                      format(entity_name))

    def _serialize_dict_entries(self, configuration):
        """ Handles entries known to contain its values as dictionaries

        Saves dictionary entries as stand-alone files and overrides actual
        entries to point to saved files.

        Args:
            configuration (dict): Configuration data with format:
                {name: entity}
        """

        serialized_entries = {}
        for (section, option, sub_path) in FileSerializer.links:
            if section not in configuration:
                # move to next if section is not in the incoming configuration
                continue
            data = configuration[section].data.get(option, None)
            if data is None:
                # move to next when option is not in incoming configuration
                continue

            # is data a potential link
            if isinstance(data, dict):
                # determine target filename
                filename = os.path.join(self._project_path, sub_path)
                # guarantee path to file
                path_to_file = os.path.dirname(filename)
                if not os.path.isdir(path_to_file):
                    os.makedirs(path_to_file)

                # save link file
                try:
                    self.save_json(filename, data, indent=4,
                                   separators=(',', ': '), sort_keys=True)

                    # save entry so that it can be referenced
                    serialized_entries[(section,option)] = sub_path
                except Exception:
                    # log exception and continue handling entries
                    self.logger.exception(
                        "Could not save linked file for: {}.{}".
                        format(section, option))

        return serialized_entries

    def _deserialize_nio_conf(self):
        """ Parses and converts a nio conf file to a dictionary

        Entries that are known to point to a json file are expanded and
        a converted to a dictionary.

        Returns:
            A dictionary where each section in the config file is present
            under an entry
        """
        configuration = dict()

        # figure out path to nio conf file
        nio_conf = os.path.join(self._project_path, self._conf_filename)
        if not os.path.isfile(nio_conf):
            self.logger.info('There is no configuration data to deserialize')
            # return an empty configuration
            return configuration

        # read the contents of the conf file with the config parser
        settings = RawConfigParser()
        settings.read(nio_conf)

        # Populate our configuration dictionary
        for section in settings.sections():
            data = {
                option: settings.get(section, option)
                for option in settings.options(section)
            }
            configuration[section] = ConfigurationEntity(data=data)

        # special handling for entries known to be dictionaries
        self._deserialize_dict_entries(configuration)

        return configuration

    def _deserialize_entities(self, from_folder, entity_type):
        """ Returns a list of entities loaded from a folder.

        For example, this function can look through the services/ folder
        to load a list of Service objects.

        Args:
            from_folder: The folder where the entity configurations are
            entity_type: A class to deserialize the configs in to

        Returns:
            entities (dict): A dict of entity type instances, keyed off of
                their filename basenames
        """

        entities = dict()
        if not os.path.isdir(from_folder):
            raise ValueError("Folder {} does not exist".format(from_folder))

        for f in os.listdir(from_folder):
            # grab extension and make sure it is one to process
            filename, extension = os.path.splitext(f)
            if extension not in FileSerializer.extensions:
                # Not a valid extension
                continue
            # grab only name portion (remove extension and prefix folders)
            key = os.path.basename(filename)
            try:
                entities[key] = entity_type(
                    self._load_json(os.path.join(from_folder, f)))
            except ValueError:
                # handle json file errors
                self.logger.exception("Could not load entity data for: {}".
                                      format(key))

        return entities

    def _deserialize_dict_entries(self, sections):
        """ Handles entries known to contain its values as dictionaries

        Args:
            sections (dict): Sections loaded from configuration file

        Note: if entry points to a file, this file is loaded as a json file
        """

        for (section, option, default) in FileSerializer.links:
            if section not in sections:
                continue
            data = sections[section].data
            setting = data.get(option, default)
            # is it a link
            potential_link = os.path.join(self._project_path, setting)
            if os.path.isfile(potential_link):
                try:
                    # assume a json file
                    data[option] = self._load_json(potential_link)
                except:  # pragma: no cover
                    self.logger.exception(
                        "Could not load {} as json".
                        format(potential_link))  # pragma: no cover

    # HELPER METHODS
    @staticmethod
    def _load_json(path):
        data = {}
        if os.path.isfile(path):
            with open(path, 'r') as f:
                data = json.load(f)
        return data

    @staticmethod
    def save_json(path, data, **kwargs):
        with open(path, 'w+') as f:
            json.dump(data, f, **kwargs)
