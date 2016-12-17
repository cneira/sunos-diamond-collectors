#!/usr/bin/python
# coding=utf-8

from test import CollectorTestCase
from test import get_collector_config
from mock import Mock
from mock import patch
from diamond.collector import Collector
from fma import FMACollector
import sunos_helpers.test_helpers as th


class TestFMACollector(CollectorTestCase):
    def setUp(self, config=None):
        if config is None:
            config = get_collector_config('FMACollector', {
                'interval': '10',
                'fmstat': True,
            })
        else:
            config = get_collector_config('FMACollector', config)

        self.collector = FMACollector(config, None)

    def test_import(self):
        self.assertTrue(FMACollector)

    def test_fmadm_impacts(self):
        klass = FMACollector()
        raw = th.read_fixture(__file__, 'fmadm')

        self.maxDiff = None
        self.assertEqual(FMACollector.fmadm_impacts(klass, raw),
                         ['fault.fs.zfs.vdev.io',
                          'fault.fs.zfs.vdev.probe_failure',
                          'fault.fs.zfs.vdev.probe_failure',
                          'fault.fs.zfs.vdev.io',
                          'fault.fs.zfs.vdev.probe_failure',
                          'fault.io.pciex.device-interr-corr',
                          'fault.fs.zfs.vdev.checksum',
                          'fault.fs.zfs.vdev.io'
                          ])

        self.assertEqual(FMACollector.fmadm_impacts(klass, []), [])

    def test_collate_fmstats(self):
        #
        # The stats you see are different in global and local zones,
        # and likely different on Illumos and Solaris. If we get at
        # least 20 stats, including a few key ones, we'll assume it
        # worked.
        #
        klass = FMACollector()
        raw = th.read_fixture(__file__, 'fmstat')
        res = FMACollector.collate_fmstats(klass, raw)

        self.assertIsInstance(res, dict)
        self.assertGreater(len(res), 20)

        res_keys = sorted(set([k.split('.')[1] for k in res.keys()]))

        for key in ('ext-event-transport', 'fmd-self-diagnosis',
                    'software-diagnosis', 'software-response',
                    'syslog-msgs'):
            self.assertIn(key, res_keys)

    @patch.object(Collector, 'publish')
    def test_should_work_with_real_data(self, publish_mock):
        fmstat_data = Mock(return_value=self.getFixture('fmstat').
                           getvalue().strip().split('\n'))

        collector_mock = patch.multiple(FMACollector,
                                        fmstat=fmstat_data)

        collector_mock.start()
        self.collector.collect()
        collector_mock.stop()

        metrics = {'fmstat.cpumem-retire.memsz': 0,
                   'fmstat.fmd-self-diagnosis.ev_recv':  367,
                   'fmstat.software-response.memsz':  2355.2,
                   'fmstat.zfs-retire.memsz': 4,
                   }

        self.assertPublishedMany(publish_mock, metrics)
