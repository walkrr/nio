class Entity(object):

    def __init__(self, data=None):
        if data is None:
            data = dict()

        if not isinstance(data, dict):
            raise TypeError("Entity data must be a dictionary")

        self.data = data
