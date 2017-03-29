import os
from configparser import RawConfigParser

from nio.project import Project, ConfigurationEntity, BlockEntity, ServiceEntity
from nio.project.entity import Entity
from nio.project.serializers.serializer import ProjectSerializer
from nio.util.codec import save_json, load_json, save_pickle, load_pickle
from nio.util.logging import get_nio_logger


class SerializationFormat(object):
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

        # store in these format serializers specifics for each format
        self._json_format = SerializationFormat([".cfg", ".json"], ".cfg",
                                                load_json, save_json)
        self._pickle_format = SerializationFormat([".dat"], ".dat",
                                                  load_pickle, save_pickle)

    def deserialize(self, service_persistence=False):
        """ Deserializes a file n.io project to a Project instance.

        This method will read the files that this serializer class has been
        configured with and return a Project instance based on the structure
        and configuration of the files.

        Args:
            service_persistence (bool): Specifies if service persistence data 
                is de-serialized

        Returns:
            project (Project): A representation of this project as an instance
                of nio.project.Project
        """
        project = Project()

        if not os.path.isdir(self._project_path):
            raise ValueError("Folder {} does not exist".format(
                self._project_path))

        # change to project dir to account for relative paths
        os.chdir(self._project_path)

        # load nio conf first in case upcoming de-serializations depend
        # on anything we read from nio conf
        project.configuration = self._deserialize_nio_conf()

        core_p_folder = self._get_core_persistence_folder(project)

        # add blocks
        blocks_folder = os.path.join(core_p_folder, 'blocks')
        project.blocks = \
            self._deserialize_entities(blocks_folder,
                                       BlockEntity,
                                       self._json_format)

        services_folder = os.path.join(core_p_folder, 'services')
        # add services
        project.services = \
            self._deserialize_entities(services_folder,
                                       ServiceEntity,
                                       self._json_format)

        # deserialize core persistence
        project.core_persistence = \
            self._deserialize_persistence(core_p_folder,
                                          [blocks_folder, services_folder],
                                          self._json_format)

        if service_persistence:
            # deserialize service persistence
            service_p_folder = self._get_service_persistence_folder(project)
            project.service_persistence = \
                self._deserialize_persistence(service_p_folder, [],
                                              self._pickle_format)

        return project

    def serialize(self, project, service_persistence=False):
        """ Take the project instance and create the necessary files 

        Args:
            project (Project): configuration to serialize
            service_persistence (bool): Specifies if service persistence data 
                is serialized
        """

        # make sure target path exists
        if not os.path.isdir(self._project_path):
            os.makedirs(self._project_path)

        # change to project dir to account for relative paths
        os.chdir(self._project_path)

        # serialize configuration
        self._serialize_nio_conf(project.configuration)

        core_p_folder = self._get_core_persistence_folder(project)

        # serialize core persistence
        self._serialize_entities(project.blocks,
                                 os.path.join(core_p_folder, 'blocks'),
                                 self._json_format)

        # serialize services
        self._serialize_entities(project.services,
                                 os.path.join(core_p_folder, 'services'),
                                 self._json_format)

        self._serialize_entities(project.core_persistence, core_p_folder,
                                 self._json_format)

        if service_persistence:
            # serialize service persistence
            service_p_folder = self._get_service_persistence_folder(project)
            self._serialize_entities(project.service_persistence,
                                     service_p_folder,
                                     self._pickle_format)

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

    def _serialize_entities(self, entities, to_folder, ser_format):
        """ Serializes a list of entities to a folder.

        For example, this function can save in the 'services' folder
        a list of Service objects.

        Args:
            entities (dict): Entities to serialize with format: {name: entity}
            to_folder (str): The folder where the entities are saved
            ser_format (SerializationFormat): Serialization format
        """

        if not os.path.isdir(to_folder):
            os.makedirs(to_folder)

        for entity_name, entity in entities.items():
            if isinstance(entity, dict):
                # if entity is a dict, create a folder for it and
                # save each entry as an entity
                sub_folder = os.path.join(to_folder, entity_name)
                self._serialize_entities(entity, sub_folder, ser_format)
            elif not isinstance(entity, Entity):
                self.logger.warning('{} is not an entity, ignoring it'.
                                    format(entity_name))
                continue
            else:
                # create filename to serialize to
                filename = \
                    os.path.join(to_folder, "{}{}".format(entity_name,
                                                          ser_format.extension))
                try:
                    ser_format.save(filename, entity.data)
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

    def _deserialize_entities(self, from_folder, entity_type, ser_format):
        """ Returns a list of entities loaded from a folder.

        For example, this function can look through the services/ folder
        to load a list of Service objects.

        Args:
            from_folder: The folder where the entity configurations are
            entity_type: A class to deserialize the configs in to
            ser_format (SerializationFormat): Serialization format

        Returns:
            entities (dict): A dict of entity type instances, keyed off of
                their filename basenames
        """

        entities = dict()
        if os.path.isdir(from_folder):
            for f in os.listdir(from_folder):
                key, entity = self._deserialize_entity(from_folder, f,
                                                       entity_type, ser_format)
                if key and entity:
                    entities[key] = entity

        return entities

    def _deserialize_persistence(self, folder, excluded, ser_format):
        """ Deserializes persistence data

        Args:
            folder (str): folder where persistence data resides
            excluded (list): list of sub-folders to exclude
            ser_format (SerializationFormat): Serialization format

        Returns:
            dictionary containing persistence data
        """
        data = {}
        if not os.path.isdir(folder):
            return data

        for f in os.listdir(folder):
            subdir = os.path.join(folder, f)
            if os.path.isdir(subdir):
                if subdir in excluded:
                    continue
                result = self._deserialize_persistence(subdir,
                                                       excluded,
                                                       ser_format)
                if result:
                    data[f] = result
            else:
                key, entity = self._deserialize_entity(folder, f,
                                                       Entity, ser_format)
                if key and entity:
                    data[key] = entity

        return data

    def _deserialize_entity(self, folder, file, entity_type, ser_format):
        """ Deserializes an entity

        Args:
            folder: folder where entity exists
            file: entity's file name
            entity_type: Entity type
            ser_format (SerializationFormat): Serialization format

        Returns:
            tuple containing (Key, Entity)
        """
        # grab extension and make sure it is one to process
        filename, extension = os.path.splitext(file)
        if extension in ser_format.allowed_extensions:
            try:
                # return tuple containing:
                # (filename without extension, actual entity instance)
                return filename, entity_type(
                    ser_format.load(os.path.join(folder, file)))
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

    def _get_core_persistence_folder(self, project):
        try:
            core_p_folder = \
                project.configuration["persistence"].data["configuration_data"]
        except KeyError:
            # if entry is not defined, have 'etc' as fallback
            core_p_folder = os.path.join(self._project_path, "etc")

        return core_p_folder

    def _get_service_persistence_folder(self, project):
        try:
            service_p_folder = \
                project.configuration["persistence"].data["data"]
        except KeyError:
            # if entry is not defined, have 'etc/persist' as fallback
            service_p_folder = os.path.join(self._project_path,
                                            "etc", "persist")

        return service_p_folder
