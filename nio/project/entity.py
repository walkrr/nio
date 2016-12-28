class Entity(object):

    def __init__(self, configuration=None):
        if configuration is None:
            configuration = dict()

        if not isinstance(configuration, dict):
            raise TypeError("Entity configuration must be a dictionary")

        self.configuration = configuration
