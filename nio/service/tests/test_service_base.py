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
            {"id": "ServiceId", "log_level": "WARNING"},
            block_router_type=BlockRouter
        ))
        # Make sure the id property got set properly
        self.assertEqual(service.id(), "ServiceId")
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
            {"id": "ServiceId", "log_level": "WARNING"},
            blocks=blocks,
            block_router_type=BlockRouter,
            blocks_async_start=False,
            blocks_async_stop=False
        ))
        # verify that statuses were updated
        status = service.full_status()
        # 4 statuses, 2 blocks, 1 service, 1 service_and_blocks
        self.assertEqual(len(status), 4)
        # assert all statuses
        self.assertIn("service", status)
        self.assertIn("service_and_blocks", status)
        self.assertIn("block1", status)
        self.assertIn("block2", status)
        for _, item_status in status.items():
            self.assertEqual(item_status, "configured")

        service.do_start()
        # verify that statuses were updated
        status = service.full_status()
        self.assertEqual(len(status), 4)
        for _, item_status in status.items():
            self.assertEqual(item_status, "started")

        self.assertEqual(len(service.blocks), 2)

        service.do_stop()

        # verify that statuses were updated
        status = service.full_status()
        self.assertEqual(len(status), 4)
        for _, item_status in status.items():
            self.assertEqual(item_status, "stopped")

    def test_blocks_async(self):
        """ Makes sure blocks are started/stopped according to 'async' setting
        """
        service = Service()
        blocks = [{"type": Block,
                   "properties": {'id': 'block1'}},
                  {"type": Block,
                   "properties": {'id': 'block2'}}]

        with patch("nio.service.base.spawn") as spawn_patched:
            service.do_configure(ServiceContext(
                {"id": "ServiceId", "log_level": "WARNING"},
                blocks=blocks,
                block_router_type=BlockRouter,
                blocks_async_configure=True,
                blocks_async_start=True,
                blocks_async_stop=True
            ))
            # assert one spawn call per block configured
            self.assertEqual(spawn_patched.call_count, 2)

            service.do_start()
            # assert one spawn call per block started
            self.assertEqual(spawn_patched.call_count, 4)

            service.do_stop()
            # assert one spawn call per block stopped
            self.assertEqual(spawn_patched.call_count, 6)

        service = Service()
        blocks = [{"type": Block,
                   "properties": {'id': 'block1'}},
                  {"type": Block,
                   "properties": {'id': 'block2'}}]

        with patch("nio.service.base.spawn") as spawn_patched:
            service.do_configure(ServiceContext(
                {"id": "ServiceId", "log_level": "WARNING"},
                blocks=blocks,
                block_router_type=BlockRouter,
                blocks_async_configure=False,
                blocks_async_start=True,
                blocks_async_stop=False
            ))
            # assert no spawn calls per block configured
            self.assertEqual(spawn_patched.call_count, 0)

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

        with patch("nio.service.base.spawn") as spawn_patched:
            service.do_configure(ServiceContext(
                {"id": "ServiceId", "log_level": "WARNING"},
                blocks=blocks,
                block_router_type=BlockRouter,
                blocks_async_configure=True,
                blocks_async_start=False,
                blocks_async_stop=True
            ))
            # assert one spawn call per block configured
            self.assertEqual(spawn_patched.call_count, 2)

            service.do_start()
            # start is not async, no spawn calls expected
            self.assertEqual(spawn_patched.call_count, 2)

            service.do_stop()
            # assert one spawn call per block stopped
            self.assertEqual(spawn_patched.call_count, 4)

    def test_commands(self):
        """ Asserts commands functionality """
        service = Service()

        service.do_configure(ServiceContext(
            {"id": "ServiceId", "log_level": "WARNING"},
            block_router_type=BlockRouter
        ))

        service.do_start()

        # check get_description and assert that info matches expectations
        description = service.get_description()
        self.assertIn("properties", description)
        self.assertIn("id", description["properties"])
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
        self.assertIn("id", run_properties)
        self.assertEqual(run_properties["id"], "ServiceId")

        service.do_stop()

    def test_config_with_no_name(self):
        """Make sure a service config has required 'id' property."""
        service = Service()
        with self.assertRaises(AllowNoneViolation):
            service.configure(ServiceContext({}))

    def test_invalid_config(self):
        """Make sure a service cononfig fails with invalid property config."""
        invalid_configs = [
            {"id": "ServiceId", "log_level": 42},
            {"id": "ServiceId", "execution": "not a list"},
            {"id": "ServiceId", "mappings": "not a list"},
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
            {"id": "ServiceId", "log_level": "WARNING"},
            block_router_type=BlockRouter,
            mgmt_signal_handler=service_mgmt_signal_handler))
        my_sig = Signal({"key": "val"})
        service.mgmt_signal_handler(my_sig)
        service_mgmt_signal_handler.assert_called_once_with(my_sig)

    def test_failed_start(self):
        """Test service start failure"""
        context = ServiceContext({"id": "TestFailedStart"},
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
