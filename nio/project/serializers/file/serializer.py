import os
from configparser import RawConfigParser

from nio.project import Project, ConfigurationEntity, BlockEntity, ServiceEntity
from nio.project.entity import Entity
from nio.project.serializers.file.environment import NIOEnvironment
from nio.project.serializers.serializer import ProjectSerializer
from nio.util.codec import save_json, load_json, save_pickle, load_pickle
from nio.util.logging import get_nio_logger


class FormatSerializer(object):
    """ Holds serialization settings for a given format
    """
    def __init__(self, allowed_extensions, extension, load, save):
        self.allowed_extensions = allowed_extensions
        self.extension = extension
        self.load = load
        self.save = save


class FileSerializer(ProjectSerializer):

    links = [("logging", "conf", "etc/logging.json"),
             ("security", "users", "etc/users.json"),
             ("security", "permissions", "etc/permissions.json")]

    def __init__(self, project_path=None, conf_filename="nio.conf",
                 environment="nio.env"):
        """ Initializes a config serializer instance

        Args:
            project_path (str): path to nio project location
            conf_filename (str): nio configuration file name
        """

        # set environment so that when reading a configured value it becomes
        # possible to replace it if it references an environment variable
        NIOEnvironment.set_environment(project_path,
                                       environment)

        self.logger = get_nio_logger("FileSerializer")

        if project_path is None:
            project_path = os.getcwd()
        self._project_path = project_path
        self._conf_filename = conf_filename
        self.logger = get_nio_logger("File Project Serializer")

        # store in these format serializers specifics for each format
        self._json_serializer = FormatSerializer([".cfg", ".json"], ".cfg",
                                                 load_json, save_json)
        self._pickle_serializer = FormatSerializer([".dat"], ".dat",
                                                   load_pickle, save_pickle)

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

        # figure out where core persistence is located at
        try:
            core_p_folder = \
                project.configuration["persistence"].data["configuration_data"]
        except KeyError:
            print("De-serializing, could not access persistence - "
                  "configuration_data entry, using 'etc' for backwards "
                  "compatibility")
            core_p_folder = etc_folder

        # is core persisted data referencing an environment variable?
        core_p_folder = NIOEnvironment.replace_setting(core_p_folder)

        # add blocks
        blocks_folder = os.path.join(core_p_folder, 'blocks')
        project.blocks = \
            self._deserialize_entities(blocks_folder,
                                       BlockEntity,
                                       self._json_serializer)

        # add services
        services_folder = os.path.join(core_p_folder, 'services')
        project.services = \
            self._deserialize_entities(services_folder,
                                       ServiceEntity,
                                       self._json_serializer)

        # deserialize core persistence
        project.core_persistence = \
            self._deserialize_persistence(core_p_folder,
                                          [blocks_folder, services_folder],
                                          self._json_serializer)

        # deserialize service persistence
        try:
            service_p_folder = \
                project.configuration["persistence"].data["data"]
        except KeyError:
            print("Deserializing, could not access persistence-data entry, "
                  "using 'etc' for backwards compatibility")
            service_p_folder = etc_folder

        # is service persisted data referencing an environment variable?
        service_p_folder = NIOEnvironment.replace_setting(service_p_folder)

        project.service_persistence = \
            self._deserialize_persistence(service_p_folder, [],
                                          self._pickle_serializer)

        return project

    def serialize(self, project):
        """ Take the project instance and create the necessary files """

        # serialize configuration
        self._serialize_nio_conf(project.configuration)

        try:
            core_p_folder = \
                project.configuration["persistence"].data["configuration_data"]
        except KeyError:
            print("Serializing, could not access persistence - "
                  "configuration_data entry, using 'etc' for backwards "
                  "compatibility")
            core_p_folder = os.path.join(self._project_path, "etc")

        # is core persisted data referencing an environment variable?
        core_p_folder = NIOEnvironment.replace_setting(core_p_folder)

        # serialize blocks
        self._serialize_entities(project.blocks,
                                 os.path.join(core_p_folder, 'blocks'),
                                 self._json_serializer)

        # serialize services
        self._serialize_entities(project.services,
                                 os.path.join(core_p_folder, 'services'),
                                 self._json_serializer)

        # serialize core persistence
        self._serialize_entities(project.core_persistence, core_p_folder,
                                 self._json_serializer)

        # serialize service persistence
        try:
            service_p_folder = \
                project.configuration["persistence"].data["data"]
        except KeyError:
            print("Serializing, could not access persistence-data entry, "
                  "using 'etc' for backwards compatibility")
            service_p_folder = os.path.join(self._project_path, "etc")

        # is service persisted data referencing an environment variable?
        service_p_folder = NIOEnvironment.replace_setting(service_p_folder)

        self._serialize_entities(project.service_persistence,
                                 service_p_folder,
                                 self._pickle_serializer)

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
            # write section only if it has entries
            if entity.data:
                # check for section existence
                if not settings.has_section(section):
                    settings.add_section(section)
                # save every section option
                for option, value in entity.data.items():
                    # handle potential links since need to save the link
                    # instead of the value, (the link-value was not written into
                    # the configuration to preserve incoming configuration
                    # integrity)
                    if (section, option) in serialized_entries:
                        # override value with 'link' value
                        value = serialized_entries[(section, option)]
                    # save to settings resulting option value
                    settings.set(section, option, value)

        # figure out path to nio conf file
        nio_conf = os.path.join(self._project_path, self._conf_filename)
        # save actual config file
        with open(nio_conf, 'w') as fp:
            settings.write(fp)

    def _serialize_entities(self, entities, to_folder, serializer):
        """ Serializes a list of entities to a folder.

        For example, this function can save in the 'services' folder
        a list of Service objects.

        Args:
            entities (dict): Entities to serialize with format: {name: entity}
            to_folder (str): The folder where the entities are saved
            serializer (FormatSerializer): Format serializer
        """

        if not os.path.isdir(to_folder):
            os.makedirs(to_folder)

        for entity_name, entity in entities.items():
            if isinstance(entity, dict):
                # if entity is a dict, create a folder for it and
                # save each entry as an entity
                sub_folder = os.path.join(to_folder, entity_name)
                self._serialize_entities(entity, sub_folder, serializer)
            elif not isinstance(entity, Entity):
                self.logger.warning('{} is not an entity, ignoring it'.
                                    format(entity_name))
                continue
            else:
                # create filename to serialize to
                filename = \
                    os.path.join(to_folder, "{}{}".format(entity_name,
                                                          serializer.extension))

                try:
                    serializer.save(filename, entity.data)
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
                    save_json(filename, data)

                    # save entry so that it can be referenced
                    serialized_entries[(section, option)] = sub_path
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

    def _deserialize_entities(self, from_folder, entity_type, serializer):
        """ Returns a list of entities loaded from a folder.

        For example, this function can look through the services/ folder
        to load a list of Service objects.

        Args:
            from_folder: The folder where the entity configurations are
            entity_type: A class to deserialize the configs in to
            serializer (FormatSerializer): Format serializer

        Returns:
            entities (dict): A dict of entity type instances, keyed off of
                their filename basenames
        """

        entities = dict()
        if not os.path.isdir(from_folder):
            raise ValueError("Folder {} does not exist".format(from_folder))

        for f in os.listdir(from_folder):
            key, entity = self._deserialize_entity(from_folder, f, entity_type,
                                                   serializer)
            if key and entity:
                entities[key] = entity

        return entities

    def _deserialize_persistence(self, folder, excluded, serializer):
        """ Deserializes persistence data

        Args:
            folder (str): folder where persistence data resides
            excluded (list): list of sub-folders to exclude
            serializer (FormatSerializer): Format serializer

        Returns:
            dictionary containing persistence data
        """
        data = {}
        for f in os.listdir(folder):
            subdir = os.path.join(folder, f)
            if os.path.isdir(subdir):
                if subdir in excluded:
                    continue
                data[f] = self._deserialize_persistence(subdir,
                                                        excluded,
                                                        serializer)
            else:
                key, entity = self._deserialize_entity(folder, f,
                                                       Entity, serializer)
                if key and entity:
                    data[key] = entity

        return data

    def _deserialize_entity(self, folder, file, entity_type, serializer):
        """ Deserializes an entity

        Args:
            folder: folder where entity exists
            file: entity's file name
            entity_type: Entity type
            serializer: Format serializer

        Returns:
            tuple containing (Key, Entity)
        """
        # grab extension and make sure it is one to process
        filename, extension = os.path.splitext(file)
        if extension in serializer.allowed_extensions:
            try:
                # return tuple containing:
                # (filename without extension, actual entity instance)
                return filename, entity_type(
                    serializer.load(os.path.join(folder, file)))
            except Exception:
                # handle json file errors
                self.logger.exception("Could not load entity data for: {}".
                                      format(filename))

        return None, None

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
                    data[option] = load_json(potential_link)
                except:  # pragma: no cover
                    self.logger.exception(
                        "Could not load {} as json".
                        format(potential_link))  # pragma: no cover
