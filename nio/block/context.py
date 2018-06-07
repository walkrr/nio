""" The data that a block will be configured with """


class BlockContext(object):

    def __init__(self, block_router, properties,
                 service_id=None, service_name='', command_url='',
                 mgmt_signal_handler=None):
        """ Initializes information needed for a Block

        This BlockContext will be passed to the `configure` method on each
        block instance before getting started.

        Args:
            block_router (BlockRouter): The router in which the
                block will be running. The only requirements are that it
                can handle signals notified by its blocks.

            properties (dict): The block properties (metadata) that
                will be deserialized and loaded as block properties.
            service_id (str): The service this block belongs to
            service_name (str): The name of the service this block belongs to
            command_url (str): The URL at which this block can be commanded.
                This URL will not have host or port information, as that may
                be different based on public/private IP. It will look like
                "/services/ServiceName/BlockAlias/"
            mgmt_signal_handler (callable): function to use to notify
                management signals, receives signal as only parameter

        """

        self.block_router = block_router
        self.properties = properties
        self.service_id = service_id
        self.service_name = service_name
        self.command_url = command_url
        self.mgmt_signal_handler = mgmt_signal_handler
