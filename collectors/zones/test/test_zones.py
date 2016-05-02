#!/usr/bin/python
# coding=utf-8

from test import CollectorTestCase
from test import get_collector_config
from mock import Mock
from mock import patch
from diamond.collector import Collector
from zones import ZonesCollector

class TestZonesCollector(CollectorTestCase):
    def setUp(self, config=None):
        if config is None:
            config = get_collector_config('ZonesCollector', {
                'interval': '10',
            })
        else:
            config = get_collector_config('ZonesCollector', config)

        self.collector = ZonesCollector(config, None)

    def test_import(self):
        self.assertTrue(ZonesCollector)

    @patch.object(Collector, 'publish')
    def test_should_work_with_real_data(self, publish_mock):
        zoneadm_data = Mock(return_value=self.getFixture('zoneadm').
                getvalue().strip().split('\n'))

        collector_mock = patch.multiple(ZonesCollector,
                 zoneadm=zoneadm_data)

        collector_mock.start()
        self.collector.collect()
        collector_mock.stop()

        metrics = { 'count.configured': 0,
                    'count.down':   0,
                    'count.incomplete': 0,
                    'count.installed': 1,
                    'count.ready': 0,
                    'count.running': 9,
                    'count.shutting_down': 0,
                    }

        self.assertPublishedMany(publish_mock, metrics)
