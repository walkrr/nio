from nio.project import Project


class ProjectSerializer(object):

    """ A project serializer is a class that is intended to be extended to
    allow for the serialization and deserialization of n.io projects.

    Subclasses should implement a serialize and deserialize method to convert
    to and from nio.project.Project instances. It is generally assumed that
    passing a project through serialize and then deserialize will return
    the same project.
    """

    def serialize(self, project, service_persistence=False):
        """ Take a project and serialize it to some state.

        This method is intended to be implemented in subclassed Serializers.
        It will be passed an instance of a nio.project.Project class and
        it should convert that instance to its serialized version. For example,
        a file based serializer would take a Project instance and create the
        proper files on the file system that represent the project.

        Args:
            project (Project): An instance of a n.io project
            service_persistence (bool): Specifies if service persistence data 
                is serialized

        Returns:
            None
        """
        raise NotImplementedError

    def deserialize(self, service_persistence=False):
        """ Create a Project instance from this serializer.

        This method should be implemented in subclassed Serializers. It should
        return an instance of a nio.project.Project class that is
        representative of the project in the serialized state. For example,
        a file based project serializer would read the file system and parse
        the data into the Project class.

        Args:
            project (Project): An instance of a n.io project
            service_persistence (bool): Specifies if service persistence data
                is de-serialized

        Returns:
            project (Project): An instance of a n.io project
        """
        raise NotImplementedError

    def validate_project(self, project):
        """ Make sure a project is a valid n.io project.

        The default implementation of this method just makes sure that the
        project is of the right type. Subclasses could perform additional
        validation if desired.

        Args:
            project: A n.io project

        Returns:
            None: This method will raise an exception if the project is
                invalid. No return should be considered a success.

        Raises:
            TypeError: If the project is not a nio.project.Project
        """
        if not isinstance(project, Project):
            raise TypeError("Project is not a valid Project instance")
