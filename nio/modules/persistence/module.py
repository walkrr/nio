from nio.modules.module import Module
from nio.modules.persistence import Persistence


class PersistenceModule(Module):

    def proxy_persistence_class(self, persistence_class):
        Persistence.proxy(persistence_class)

    def finalize(self):
        Persistence.unproxy()
        super().finalize()

    def get_module_order(self):
        return 10

    def get_module_type(self):
        return "persistence"
