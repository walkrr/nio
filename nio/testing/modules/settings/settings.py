from collections import defaultdict


class Settings(object):

    """ Helper class to store settings """

    _settings = defaultdict(dict)

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
            settings (AttributeDict): The requested settings or
                None if no possible value was found
        """
        if section is None:
            return cls._settings
        elif option is None:
            return cls._settings.get(section, kwargs.get("fallback", None))
        else:
            try:
                return cls._settings.get(section)[option]
            except:
                pass
        return kwargs.get("fallback", None)

    @classmethod
    def getint(cls, section, option, *args, **kwargs):
        # a convenience method converting section value to an integer
        value = cls.get(section, option, *args, **kwargs)
        if value is not None:
            value = int(value)
        return value

    @classmethod
    def getfloat(cls, section, option, *args, **kwargs):
        # a convenience method converting section value to a float
        value = cls.get(section, option, *args, **kwargs)
        if value is not None:
            value = float(value)
        return value

    @classmethod
    def getboolean(cls, section, option, *args, **kwargs):
        # a convenience method converting section value to a boolean
        value = cls.get(section, option, *args, **kwargs)
        if value is not None:
            value = bool(value)
        return value

    @classmethod
    def getdict(cls, section, option, *args, **kwargs):
        return cls.get(section, option, *args, **kwargs)

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
        if option is None:
            cls._settings[section] = value
        else:
            cls._settings[section][option] = value

    @classmethod
    def clear(cls):
        """ Reset settings """
        cls._settings.clear()
