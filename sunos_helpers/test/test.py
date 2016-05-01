import platform, sys, os, unittest

if platform.system() != 'SunOS':
    print 'Tests require a SunOS system.'
    sys.exit(1)

class_dir = '/'.join(os.path.realpath(__file__).split('/')[0:-2])
sys.path.append(class_dir)

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
        self.assertNotRegexpMatches(sh.run_cmd('/usr/bin/id'), 'root')
        self.assertRegexpMatches(sh.run_cmd('/usr/bin/id', True), 'root')

    def test_to_bytes(self):
        self.assertEqual(sh.to_bytes('2K'), 2048)
        self.assertEqual(sh.to_bytes('2K', True), 2000)
        self.assertEqual(sh.to_bytes('2.5K'), 2560)
        self.assertEqual(sh.to_bytes('800M'), 838860800)
        self.assertEqual(sh.to_bytes('800M', True), 800000000)
        self.assertEqual(sh.to_bytes('6.12G'), 6571299962.88)
        self.assertEqual(sh.to_bytes('6.12G', True), 6120000000)
        self.assertEqual(sh.to_bytes('0.5T'), 549755813888)
        self.assertEqual(sh.to_bytes('0.5T', True), 500000000000)

    def test_kstat_name(self):
        with self.assertRaises(ValueError):
            sh.kstat_name('nfs:NOT_ALLOWED:nfs4')

        with self.assertRaises(ValueError):
            sh.kstat_name('nfs:0')

        self.assertIsInstance(sh.kstat_name('nfs:4:nfs4'), dict)
        self.assertGreater(len(sh.kstat_name('nfs:4:nfs4')), 10)
        self.assertIn('rtime', sh.kstat_name('nfs:4:nfs4').keys())
        self.assertIsInstance(sh.kstat_name('nfs:99:nfs4'), dict)
        self.assertEqual(len(sh.kstat_name('nfs:99:nfs4')), 0)

    def test_kstat_module(self):
        self.assertIsInstance(sh.kstat_module('NOMATCH', 'NOMATCH'), dict)
        self.assertEqual(len(sh.kstat_module('NOMATCH', 'NOMATCH')), 0)
        self.assertIsInstance(sh.kstat_module('nfs', 'NOMATCH'), dict)
        self.assertEqual(len(sh.kstat_module('nfs', 'NOMATCH')), 0)
        self.assertIsInstance(sh.kstat_module('cmdkerror', 'Size'), dict)
        self.assertGreater(len(sh.kstat_module('cmdkerror', 'Size')), 0)
        self.assertIn('cmdk0,error.size',
                sh.kstat_module('cmdkerror', 'Size').keys())

    def test_kstat_val(self):
        with self.assertRaises(ValueError):
            sh.kstat_name('nfs:NOT_ALLOWED:nfs4')

        with self.assertRaises(ValueError):
            sh.kstat_name('nfs:0')

        self.assertIsInstance(sh.kstat_val(
            'unix:0:system_pages:pp_kernel'), long)
        self.assertGreater(sh.kstat_val('unix:0:system_pages:pp_kernel'), 0)

        self.assertIs(sh.kstat_val('unix:0:system_pages:NOMATCH'), False)
        self.assertIs(sh.kstat_val('unix:0:NOMATCH:pp_kernel'), False)
        self.assertIs(sh.kstat_val('NOMATCH:0:system_pages:pp_kernel'),
                False)

if __name__ == '__main__':
    unittest.main()