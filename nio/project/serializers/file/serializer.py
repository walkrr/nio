from configparser import RawConfigParser
import json
import os
from nio.util.logging import get_nio_logger
from nio.project import Project, Configuration, BlockEntity, ServiceEntity
from nio.project.serializers.serializer import ProjectSerializer


class FileSerializer(ProjectSerializer):

    folders = ['blocks', 'services']
    extensions = ['.cfg', '.json']

    def __init__(self, project_path=None, conf_filename="nio.conf"):
        """ Initializes a config serializer instance

        Args:
            project_path (str): path to nio project location
            conf_filename (str): nio configuration file name
        """
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
        project.configuration = self._parse_nio_conf()

        # add blocks and services
        project.blocks = self._load_entities(
            os.path.join(etc_folder, 'blocks'), BlockEntity)
        project.services = self._load_entities(
            os.path.join(etc_folder, 'services'), ServiceEntity)

        return project

    def serialize(self, project):
        """ Take the project instance and create the necessary files """
        # TODO: Implement this method
        pass

    def _parse_nio_conf(self):
        """ Parses and converts a nio conf file to a dictionary

        Entries that are known to point to a json file are expanded and
        a converted to a dictionary.

        Returns:
            A dictionary where each section in the config file is present
            under an entry
        """
        configuration = dict()
        settings = RawConfigParser()

        # figure out path to nio conf file
        nio_conf = os.path.join(self._project_path, self._conf_filename)
        if not os.path.isfile(nio_conf):
            raise ValueError("Expected configuration file: {} is missing".
                             format(nio_conf))

        # read the contents of the conf file with the config parser
        settings.read(nio_conf)

        # Populate our configuration dictionary
        for section in settings.sections():
            data = {
                option: settings.get(section, option)
                for option in settings.options(section)
            }
            configuration[section] = Configuration(data=data)

        # special handling for entries known to be dictionaries
        self._handle_dict_entries(configuration)

        return configuration

    def _load_entities(self, from_folder, entity_type):
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
            entities[key] = entity_type(
                self._load_json(os.path.join(from_folder, f)))

        return entities

    def _handle_dict_entries(self, sections):
        """ Handles entries known to contain its values as dictionaries

        Args:
            sections (dict): Sections loaded from configuration file

        Note: if entry points to a file, this file is loaded as a json file
        """

        links = [("logging", "conf", "etc/logging.json"),
                 ("security", "users", "etc/users.json"),
                 ("security", "permissions", "etc/permissions.json"),
                 ("environment", "blocks_from", "etc/blocks.json")]

        for (section, option, default) in links:
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
