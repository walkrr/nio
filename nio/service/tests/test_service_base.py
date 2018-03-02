from unittest.mock import Mock, patch

from nio import Block
from nio.properties.exceptions import AllowNoneViolation
from nio.router.base import BlockRouter
from nio.service.base import Service
from nio.service.context import ServiceContext
from nio.signal.base import Signal
from nio.testing.test_case import NIOTestCase


class TestBaseService(NIOTestCase):

    def test_configure(self):
        """Make sure a service can be configured"""
        service = Service()
        service.configure(ServiceContext(
            {"name": "ServiceName", "log_level": "WARNING"},
            block_router_type=BlockRouter
        ))
        # Make sure the name property got set properly
        self.assertEqual(service.name(), "ServiceName")
        self.assertIsNotNone(service.logger)

    def test_start_stop(self):
        """Makes sure service and blocks update statuses accordingly """
        service = Service()

        class Block1(Block):
            pass

        class Block2(Block):
            pass

        blocks = [{"type": Block1,
                   "properties": {'id': 'block1'}},
                  {"type": Block2,
                   "properties": {'id': 'block2'}}]

        service.do_configure(ServiceContext(
            {"name": "ServiceName", "log_level": "WARNING"},
            blocks=blocks,
            block_router_type=BlockRouter,
            blocks_async_start=False,
            blocks_async_stop=False
        ))
        # verify that statuses were updated
        status = service.full_status()
        status_values = list(status.values())
        self.assertEqual(len(status_values), 3)
        self.assertEqual(status_values[0], "configured")
        self.assertEqual(status_values[1], "configured")
        self.assertEqual(status_values[2], "configured")

        service.do_start()

        # verify that statuses were updated
        status = service.full_status()
        status_values = list(status.values())
        self.assertEqual(len(status_values), 3)
        self.assertEqual(status_values[0], "started")
        self.assertEqual(status_values[1], "started")
        self.assertEqual(status_values[2], "started")

        self.assertEqual(len(service.blocks), 2)

        service.do_stop()

        # verify that statuses were updated
        status = service.full_status()
        status_values = list(status.values())
        self.assertEqual(len(status_values), 3)
        self.assertEqual(status_values[0], "stopped")
        self.assertEqual(status_values[1], "stopped")
        self.assertEqual(status_values[2], "stopped")

    def test_start_stop_blocks_async(self):
        """ Makes sure blocks are started/stopped according to 'async' setting
        """
        service = Service()
        blocks = [{"type": Block,
                   "properties": {'id': 'block1'}},
                  {"type": Block,
                   "properties": {'id': 'block2'}}]
        service.do_configure(ServiceContext(
            {"name": "ServiceName", "log_level": "WARNING"},
            blocks=blocks,
            block_router_type=BlockRouter,
            blocks_async_start=True,
            blocks_async_stop=True
        ))

        with patch("nio.service.base.spawn") as spawn_patched:
            service.do_start()
            # assert one spawn call per block started
            self.assertEqual(spawn_patched.call_count, 2)

            service.do_stop()
            # assert one spawn call per block stopped
            self.assertEqual(spawn_patched.call_count, 4)

        service = Service()
        blocks = [{"type": Block,
                   "properties": {'id': 'block1'}},
                  {"type": Block,
                   "properties": {'id': 'block2'}}]
        service.do_configure(ServiceContext(
            {"name": "ServiceName", "log_level": "WARNING"},
            blocks=blocks,
            block_router_type=BlockRouter,
            blocks_async_start=True,
            blocks_async_stop=False
        ))

        with patch("nio.service.base.spawn") as spawn_patched:
            service.do_start()
            # assert one spawn call per block started
            self.assertEqual(spawn_patched.call_count, 2)

            # stop is not async, no more spawn calls expected
            service.do_stop()
            self.assertEqual(spawn_patched.call_count, 2)

        service = Service()
        blocks = [{"type": Block,
                   "properties": {'id': 'block1'}},
                  {"type": Block,
                   "properties": {'id': 'block2'}}]
        service.do_configure(ServiceContext(
            {"name": "ServiceName", "log_level": "WARNING"},
            blocks=blocks,
            block_router_type=BlockRouter,
            blocks_async_start=False,
            blocks_async_stop=True
        ))

        with patch("nio.service.base.spawn") as spawn_patched:
            service.do_start()
            # start is not async, no spawn calls expected
            self.assertEqual(spawn_patched.call_count, 0)

            service.do_stop()
            # assert one spawn call per block stopped
            self.assertEqual(spawn_patched.call_count, 2)

    def test_commands(self):
        """ Asserts commands functionality """
        service = Service()

        service.do_configure(ServiceContext(
            {"name": "ServiceName", "log_level": "WARNING"},
            block_router_type=BlockRouter
        ))

        service.do_start()

        # check get_description and assert that info matches expectations
        description = service.get_description()
        self.assertIn("properties", description)
        self.assertIn("name", description["properties"])
        self.assertIn("auto_start", description["properties"])

        self.assertIn("commands", description)
        self.assertIn("start", description["commands"])
        self.assertIn("stop", description["commands"])
        self.assertIn("status", description["commands"])
        self.assertIn("heartbeat", description["commands"])
        self.assertIn("runproperties", description["commands"])

        # verify heartbeat command
        self.assertEqual(service.heartbeat().name, "started")

        # verify runproperties command
        run_properties = service.runproperties()
        self.assertIn("name", run_properties)
        self.assertEqual(run_properties["name"], "ServiceName")

        service.do_stop()

    def test_config_with_no_name(self):
        """Make sure a service config has required 'name' property."""
        service = Service()
        with self.assertRaises(AllowNoneViolation):
            service.configure(ServiceContext({}))

    def test_invalid_config(self):
        """Make sure a service cononfig fails with invalid property config."""
        invalid_configs = [
            {"name": "ServiceName", "log_level": 42},
            {"name": "ServiceName", "execution": "not a list"},
            {"name": "ServiceName", "mappings": "not a list"},
        ]
        for config in invalid_configs:
            service = Service()
            with self.assertRaises(TypeError):
                service.configure(ServiceContext(config))

    def test_notify_management_signal(self):
        """Test the service can notify management signals properly"""
        service = Service()
        service_mgmt_signal_handler = Mock()
        service.configure(ServiceContext(
            {"name": "ServiceName", "log_level": "WARNING"},
            block_router_type=BlockRouter,
            mgmt_signal_handler=service_mgmt_signal_handler))
        my_sig = Signal({"key": "val"})
        service.mgmt_signal_handler(my_sig)
        service_mgmt_signal_handler.assert_called_once_with(my_sig)

    def test_failed_start(self):
        """Test service start failure"""
        context = ServiceContext({"name": "TestFailedStart"},
                                 [],
                                 BlockRouter)

        service = Service()
        service.configure(context)

        service.start = Mock(side_effect=Exception())
        with self.assertRaises(Exception):
            service.do_start()

        service.start.assert_called_once_with()
        self.assertIn('error', str(service.status).split(', '))
        service.stop()
