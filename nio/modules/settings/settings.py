from nio.modules.proxy import ModuleProxy


class Settings(ModuleProxy):

    """ Interface class to store settings """

    @classmethod
    def get(cls, section=None, option=None, *args, **kwargs):
        """Accessor for settings.

        Args:
            section (str): section to get information from
            option (str): option to get information from

        if no section is specified, all sections are returned
        if no option is specified, all options within given section are returned

        Keyword Args:
            fallback: default to use when no information can be found

        Returns:
            settings: The requested settings or
                None if no possible value was found
        """
        raise NotImplementedError()

    @classmethod
    def getint(cls, section, option, **kwargs):
        # a convenience method converting section option value to an integer
        raise NotImplementedError()

    @classmethod
    def getfloat(cls, section, option, **kwargs):
        # a convenience method converting section option value to a float
        raise NotImplementedError()

    @classmethod
    def getboolean(cls, section, option, **kwargs):
        # a convenience method converting section option value to a boolean
        raise NotImplementedError()

    @classmethod
    def getdict(cls, section, option, **kwargs):
        # a convenience method reading the section option value interpreting
        # it as a python dictionary
        raise NotImplementedError()

    @classmethod
    def set(cls, section, option=None, value=None):
        """ Sets the value for a given section and option

        if the section does not exists, it creates it
        if option is not specified, value is assigned to the section and it
            must be a dictionary type

        Args:
            section (str): section to set information to
            option (str): option to set information to
            value: value to assign

        Raises:
            TypeError if value is invalid
        """
        raise NotImplementedError()

    @classmethod
    def clear(cls):
        """ Clears all settings """
        raise NotImplementedError()
