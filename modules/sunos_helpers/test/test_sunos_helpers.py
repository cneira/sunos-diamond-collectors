#!/bin/env python

import platform, sys, os, unittest

if platform.system() != 'SunOS':
    print 'Tests require a SunOS system.'
    sys.exit(1)

class_dir = '/'.join(os.path.realpath(__file__).split('/')[0:-2])
sys.path.append(class_dir)
kstat_dir = '/'.join(os.path.realpath(__file__).split('/')[0:-3])
sys.path.append(os.path.join(kstat_dir, 'kstat'))

import sunos_helpers as sh

class TestSunOSHelpers(unittest.TestCase):

    def test_run_cmd(self):
        with self.assertRaises(NotImplementedError):
            sh.run_cmd('/no/such/command')

        with self.assertRaises(NotImplementedError):
            sh.run_cmd('/no/such/command', True)

        with self.assertRaises(Exception):
            sh.run_cmd('/bin/cat /etc/shadow')

        self.assertIsInstance(sh.run_cmd('/bin/uname -s'), basestring)
        self.assertEqual(sh.run_cmd('/bin/uname -s'), 'SunOS')
        self.assertIsInstance(sh.run_cmd('/bin/sed 5q /etc/passwd'),
                list)
        self.assertEqual(len(sh.run_cmd('/bin/sed 5q /etc/passwd')), 5)

        # This test requires a suitable profile. I gave myself this
        # privilege:
        #   System Telemetry:solaris:cmd:RO::/usr/bin/id:uid=0;euid=0
        #
        if 'System Telemetry' in sh.run_cmd('/bin/profiles'):
            self.assertNotRegexpMatches(sh.run_cmd('/usr/bin/id'), 'root')
            self.assertRegexpMatches(sh.run_cmd('/usr/bin/id', True), 'root')

    def test_bytify(self):
        self.assertEqual(sh.bytify('2K'), 2048)
        self.assertEqual(sh.bytify('2K', True), 2000)
        self.assertEqual(sh.bytify('2.5K'), 2560)
        self.assertEqual(sh.bytify('800M'), 838860800)
        self.assertEqual(sh.bytify('800M', True), 800000000)
        self.assertEqual(sh.bytify('6.12G'), 6571299962.88)
        self.assertEqual(sh.bytify('6.12G', True), 6120000000)
        self.assertEqual(sh.bytify('0.5T'), 549755813888)
        self.assertEqual(sh.bytify('0.5T', True), 500000000000)
        self.assertEqual(sh.bytify(400, True), 400)
        self.assertEqual(sh.bytify('400', True), 400)
        self.assertEqual(sh.bytify(-400, True), -400)
        self.assertEqual(sh.bytify('-6.12G', True), -6120000000)

        with self.assertRaises(ValueError):
            sh.bytify('10L')

        with self.assertRaises(ValueError):
            sh.bytify([1, 2, 3])

    def test_wanted(self):
        want = ['cmdk0', 'cmdk2']
        self.assertFalse(sh.wanted('__all__', want))
        self.assertTrue(sh.wanted('anything', '__all__'))
        self.assertFalse(sh.wanted('anything', '__none__'))
        self.assertTrue(sh.wanted('word', 'word'))
        self.assertTrue(sh.wanted('cmdk0', want))
        self.assertFalse(sh.wanted('cmdk1', want))
        self.assertFalse(sh.wanted('pen', 'pencil'))

        self.assertTrue(sh.wanted('cmdk0', 'cmdk\d+', regex=True))
        self.assertTrue(sh.wanted('cmdk2', '^.*2$', regex=True))

        want = ['cmdk[0-3]', 'did.*']
        self.assertTrue(sh.wanted('cmdk1', want, regex=True))
        self.assertFalse(sh.wanted('cmdk5', want, regex=True))
        self.assertFalse(sh.wanted('sda', want, regex=True))
        self.assertTrue(sh.wanted('did99', want, regex=True))

    def test_kstat_req_parse(self):
        self.assertEqual(sh.kstat_req_parse('nfs:3:nfs_server:calls'),
                { 'module': 'nfs', 'instance': 3, 'name': 'nfs_server',
                    'statistic': 'calls' })
        self.assertEqual(sh.kstat_req_parse('nfs:3:nfs_server'),
                { 'module': 'nfs', 'instance': 3, 'name': 'nfs_server',
                    'statistic': None })
        self.assertEqual(sh.kstat_req_parse('nfs:3'),
                { 'module': 'nfs', 'instance': 3, 'name': None,
                    'statistic': None })
        self.assertEqual(sh.kstat_req_parse(':::'),
                { 'module': None, 'instance': None, 'name': None,
                    'statistic': None })
        self.assertEqual(sh.kstat_req_parse('nfs'),
                { 'module': 'nfs', 'instance': None, 'name': None,
                    'statistic': None })
        self.assertEqual(sh.kstat_req_parse('nfs::nfs_server'),
                { 'module': 'nfs', 'instance': None, 'name':
                'nfs_server', 'statistic': None })
        self.assertEqual(sh.kstat_req_parse('nfs:::calls'),
                { 'module': 'nfs', 'instance': None, 'name': None,
                'statistic': 'calls' })
        self.assertEqual(sh.kstat_req_parse('::disk:'),
                { 'module': None, 'instance': None, 'name': 'disk',
                'statistic': None })

    def test_get_kstat(self):
        self.assertEqual(sh.get_kstat('nosuch:0:kstat:name'), {})
        self.assertEqual(sh.get_kstat('nosuch:0::name'), {})
        self.assertEqual(sh.get_kstat('nosuch:::name'), {})
        self.assertEqual(sh.get_kstat('nosuch:0:kstat'), {})
        self.assertEqual(sh.get_kstat('nosuch:0'), {})
        self.assertEqual(sh.get_kstat('nosuch'), {})

        self.assertIsInstance(sh.get_kstat('cpu:0:sys:canch',
            single_val=True), long)

        self.assertEqual(len(sh.get_kstat('cpu::vm:pgin')),
            len(sh.run_cmd('/usr/sbin/psrinfo')))
        self.assertEqual(len(sh.get_kstat('cpu:0:vm:pgin')), 1)
        self.assertEqual(sh.get_kstat('cpu:0:vm:pgin', ks_class='disk'),
                {})

        res = sh.get_kstat('cpu:0:vm')
        self.assertIsInstance(res, dict)

        self.assertIn('cpu:0:vm:execpgin', res.keys())
        self.assertIn('cpu:0:vm:crtime', res.keys())

        self.assertNotIn('cpu:0:vm:crtime', sh.get_kstat('cpu:0:vm',
            no_times=True))

        self.assertNotIn('cpu:0:vm:crtime', sh.get_kstat('cpu:0:vm',
            no_times=True))

        self.assertNotIn('cpu_info:0:cpu_info0:brand',
                sh.get_kstat('cpu_info:0:cpu_info0').keys())

        self.assertIn('cpu_info:0:cpu_info0:brand',
                sh.get_kstat('cpu_info:0:cpu_info0', only_num=False).keys())

        self.assertIn('brand',
                sh.get_kstat('cpu_info:0:cpu_info0', only_num=False,
                    terse=True).keys())

        self.assertNotIn('cpu_info:0:cpu_info0:brand',
                sh.get_kstat('cpu_info:0:cpu_info0', only_num=False,
                    terse=True).keys())

        self.assertNotRegexpMatches(''.join(sh.get_kstat('ip:0:icmp').keys()),
                '[A-Z]')

        self.assertEqual(sh.get_kstat(':::', ks_class='nosuch'), {})
        self.assertEqual(sh.get_kstat('cpu:0:vm', ks_class='disk'), {})

        self.assertIn('ilb:0:global:snaptime', sh.get_kstat(':::',
            ks_class='kstat'))

        self.assertNotIn('ilb:0:global:snaptime', sh.get_kstat(':::',
            ks_class='kstat', no_times=True))

        self.assertEqual(sh.get_kstat('cpu_info:0:cpu_info0', only_num=False,
                statlist=['nosuch']), {})

        res = sh.get_kstat('cpu_info:0:cpu_info0', only_num=False,
                terse=True, statlist=('state', 'core_id'))

        self.assertEqual(len(res), 2)
        self.assertItemsEqual(res.keys(), ['state', 'core_id'])

        self.assertIn('core_id', sh.get_kstat('cpu_info:0:cpu_info0',
            statlist='__all__', terse=True))

if __name__ == '__main__':
    unittest.main()
