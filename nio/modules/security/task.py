class SecureTask(object):

    def __init__(self, resource, permission, **kwargs):
        super().__init__(**kwargs)
        self.resource = resource
        self.permission = permission
