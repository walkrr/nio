import pickle
from nio.project.serializers.serializer import ProjectSerializer


class BinarySerializer(ProjectSerializer):

    """ A simple serializer that keeps a binary representation of a project
    in its memory. These bytes can be saved to disk, sent over the network, or
    really anything else you can do with bytes. The bytes are created using
    Python pickle so deserializing will require a compatible nio framework
    installed in the deserializing environment.

    To serialize a project call:
        >>> serializer = BinarySerializer()
        >>> serializer.serialize(project)
        >>> project_bytes = serializer.binary_data

    To deserialize bytes:
        >>> serializer = BinarySerializer(project_bytes)
        >>> project = BinarySerializer.deserialize()
    """

    def __init__(self, binary_data=None):
        # The bytes representing the project after serialization or before
        # deserialization
        self.binary_data = binary_data

    def serialize(self, project):
        """ Take a project and turn it into bytes """
        # Make sure the project is a valid one
        self.validate_project(project)

        self.binary_data = pickle.dumps(project)

    def deserialize(self):
        return pickle.loads(self.binary_data)
