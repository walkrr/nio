class RouterContext(object):

    """ Maintains information needed to configure a block router """

    def __init__(self, execution, blocks, settings=None,
                 mgmt_signal_handler=None,
                 instance_id=None,
                 service_id=None,
                 service_name=""):
        """Initializes a router context.

        Args:
            execution (list):  execution list as defined by BaseService
                execution property
            blocks (dict):  dictionary of blocks that looks like this:
                [block_id]: [block instance]
            settings (dict): router settings, these can include
                "clone_signals" and/or any other settings depending on router
                being used
            mgmt_signal_handler (method): method to use to notify
                management signals, receives signal as only parameter
            instance_id: Instance the service belongs to
            service_id (str): service this router belongs to
            service_name (str): The name of the service this router belongs to
        """
        self.execution = execution
        self.blocks = blocks
        self.settings = settings or {}
        self.mgmt_signal_handler = mgmt_signal_handler
        self.instance_id = instance_id
        self.service_id = service_id
        self.service_name = service_name
