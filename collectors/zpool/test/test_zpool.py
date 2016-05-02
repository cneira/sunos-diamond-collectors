#!/usr/bin/python
# coding=utf-8

from test import CollectorTestCase
from test import get_collector_config
from mock import Mock
from mock import patch
from diamond.collector import Collector
from zpool import ZpoolCollector
from sunos_helpers import sunos_helpers as sh

class TestZpoolCollector(CollectorTestCase):
    def setUp(self, config=None):
        if config is None:
            config = get_collector_config('ZpoolCollector', {
                'interval': '10',
            })
        else:
            config = get_collector_config('ZpoolCollector', config)

        self.collector = ZpoolCollector(config, None)

    def test_import(self):
        self.assertTrue(ZpoolCollector)

    def test_health_as_int(self):
        z = ZpoolCollector()
        self.assertEqual(ZpoolCollector.health_as_int(z, 'ONLINE'), 0)
        self.assertEqual(ZpoolCollector.health_as_int(z, 'DEGRADED'), 1)
        self.assertEqual(ZpoolCollector.health_as_int(z, 'SUSPENDED'), 2)
        self.assertEqual(ZpoolCollector.health_as_int(z, 'UNAVAIL'), 3)
        self.assertEqual(ZpoolCollector.health_as_int(z, 'nosuch'), 4)
        self.assertEqual(ZpoolCollector.health_as_int(z, False), 4)


    @patch.object(Collector, 'publish')
    def test_should_work_with_real_data(self, publish_mock):
        zpool_data = Mock(return_value=self.getFixture('zpool').
                getvalue().strip().split('\n'))

        collector_mock = patch.multiple(ZpoolCollector,
                 zpool=zpool_data)

        collector_mock.start()
        self.collector.collect()
        collector_mock.stop()

        metrics = { 'crypto.free': 339302416384.0,
                    'crypto.cap': 46.0,
                    'crypto.health': 0,
                    'fast.alloc': 23729694310.4,
                    'fast.free': 440234147840.0,
                    'fast.cap': 5.0,
                    'fast.health': 0,
                    'rpool.alloc': 30279519436.8,
                    'rpool.free': 37903086387.2,
                    'rpool.cap': 44.0,
                    'rpool.health': 0,
                    'space.alloc': 2045091627663.36,
                    'space.free': 1231453023109.12,
                    'space.cap': 62.0,
                    'space.health': 0
                    }

        self.assertPublishedMany(publish_mock, metrics)
