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
                           'disk_errors'))

        collector_mock = patch.multiple(SunOSDiskHealthCollector,
                                        kstats=mock_kstats)

        collector_mock.start()
        self.collector.collect()
        collector_mock.stop()

        metrics = {'sd2.device_not_ready': 0,
                   'sd2.hard_errors': 0,
                   'sd2.illegal_request': 420,
                   'sd2.media_error': 0,
                   'sd2.no_device': 0,
                   'sd2.non-aligned_writes': 0,
                   'sd2.predictive_failure_analysis': 0,
                   'sd2.soft_errors': 0,
                   'sd2.transport_errors': 0,
                   }

        self.assertPublishedMany(publish_mock, metrics, 1)
