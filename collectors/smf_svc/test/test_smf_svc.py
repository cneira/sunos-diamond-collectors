#!/usr/bin/python
# coding=utf-8

from test import CollectorTestCase
from test import get_collector_config
from mock import Mock
from mock import patch
from diamond.collector import Collector
from smf_svc import SmfSvcCollector

class TestSmfSvcCollector(CollectorTestCase):
    def setUp(self, config=None):
        if config is None:
            config = get_collector_config('SmfSvcCollector', {
                'interval': '10',
            })
        else:
            config = get_collector_config('SmfSvcCollector', config)

        self.collector = SmfSvcCollector(config, None)

    def test_import(self):
        self.assertTrue(SmfSvcCollector)

    @patch.object(Collector, 'publish')
    def test_should_work_with_real_data(self, publish_mock):
        svc_data = Mock(return_value=self.getFixture('svcs').
                getvalue().strip().split('\n'))

        collector_mock = patch.multiple(SmfSvcCollector,
                 svcs=svc_data)

        collector_mock.start()
        self.collector.collect()
        collector_mock.stop()

        metrics = { 'online': 149,
                    'offline': 1,
                    'uninitialized': 0,
                    'degraded': 0,
                    'maintenance': 2,
                    'legacy_run': 3,
                    'disabled': 100,
                    }

        self.assertPublishedMany(publish_mock, metrics)
