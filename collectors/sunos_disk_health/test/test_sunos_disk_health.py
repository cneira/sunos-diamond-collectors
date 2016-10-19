#!/usr/bin/python
# coding=utf-8

from test import CollectorTestCase
from test import get_collector_config
from mock import Mock
from mock import patch
from diamond.collector import Collector
from sunos_disk_health import SunOSDiskHealthCollector
import sunos_helpers.test_helpers as th


class TestSunOSDiskHealthCollector(CollectorTestCase):
    def setUp(self, config=None):
        if config is None:
            config = get_collector_config('SunOSDiskHealthCollector',
                                          {'interval': '10'})
        else:
            config = get_collector_config('SunOSDiskHealthCollector',
                                          config)

        self.collector = SunOSDiskHealthCollector(config, None)

    def test_import(self):
        self.assertTrue(SunOSDiskHealthCollector)

    @patch.object(Collector, 'publish')
    def test_should_work_with_real_data(self, publish_mock):
        mock_kstats = Mock(return_value=th.load_fixture(__file__,
                           'cmdkerror'))

        collector_mock = patch.multiple(SunOSDiskHealthCollector,
                                        kstats=mock_kstats)

        collector_mock.start()
        self.collector.collect()
        collector_mock.stop()

        metrics = {'cmdk0.hard_errors': 0,
                   'cmdk0.soft_errors': 0,
                   'cmdk0.transport_errors': 0,
                   'cmdk1.hard_errors': 15,
                   'cmdk1.soft_errors': 1023,
                   'cmdk1.transport_errors': 756,
                   'cmdk2.hard_errors': 0,
                   'cmdk2.soft_errors': 40,
                   'cmdk2.transport_errors': 0,
                   }

        self.assertPublishedMany(publish_mock, metrics)
