from nio.types.base import Type


class BoolType(Type):

    @staticmethod
    def serialize(value, **kwargs):
        """ Convert a value to a JSON serializable value """
        return value

    @staticmethod
    def deserialize(value, **kwargs):
        """ Convert value to bool"""
        try:
            if isinstance(value, str) and \
                    value.lower() in ['true', 'yes', 'on']:
                return True
            elif isinstance(value, str) and \
                    value.lower() in ['false', 'no', 'off']:
                return False
            return bool(value)
        except:
            raise TypeError("Unable to cast value to bool: {}".format(value))
