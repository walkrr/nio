class Project(object):

    """ A class that contains all information needed for a n.io project.

    This class allows for us to create an in-memory represenation of a project.
    That instance can be validated and/or serialized into different formats
    that will ultimately be read by a n.io binary.

    For the most part, a n.io project consists of a collection of configured
    blocks, services, and other configuration options. A special configuration
    option is the block types that are available to the project. Currently,
    this representation only allows for block types that are configured in the
    environment section of a configuration file.
    """

    def __init__(self):
        super().__init__()
        # A project has configured blocks. It is stored as a dictionary
        # where the key is the block name and the value is a Block instance
        self.blocks = dict()

        # A project has configured services. It is stored as a dictionary
        # where the key is the service name and the value is a Service instance
        self.services = dict()

        # A project has some configuration. The top-level dictionary keys are
        # the configuration sections, the values are configuration objects
        self.configuration = dict()

        # A project might contain persistence data besides blocks and services
        # at the core level, for example, a given core component might save
        # data using Persistence and would like such data to be part of
        # the project
        self.core_persistence = dict()

        # Data saved for a service using Persistence
        self.service_persistence = dict()