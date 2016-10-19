import sys
import os
import unittest

class_dir = '/'.join(os.path.realpath(__file__).split('/')[0:-2])
help_dir = '/'.join(os.path.realpath(__file__).split('/')[0:-4])

sys.path.append('/opt/diamond/lib/python2.7/site-packages')
sys.path.append(class_dir)
sys.path.append(help_dir)

from sunos_network import SunOSNetworkCollector as klass


class TestNetworkCollector(unittest.TestCase):

    def test_zonemap(self):
        k = klass()

        # Get an exception with bad data
        #
        with open('fixtures/faulty_zoneadm_output', 'r') as f:
            zadm = f.read().strip().split('\n')

        with self.assertRaises(NotImplementedError):
            klass.zone_map(k, zadm, False)

        # Now use good data
        #
        with open('fixtures/zoneadm_output', 'r') as f:
            zadm = f.read().strip().split('\n')

        # Ask for the global, just get the global
        #
        self.assertIsInstance(klass.zone_map(k, zadm, 'global'), dict)
        self.assertDictEqual(klass.zone_map(k, zadm, 'global'),
                             {'0': 'global'})

        # Ask for something not there: get nothing
        #
        self.assertIsInstance(klass.zone_map(k, zadm, 'not_exist'), dict)
        self.assertDictEqual(klass.zone_map(k, zadm, 'not_exist'), {})

        # Ask for three out of nine, get three out of nine
        #
        z_arr = ['global', 'shark-media', 'shark-ws']

        self.assertIsInstance(klass.zone_map(k, zadm, z_arr), dict)
        self.assertDictEqual(klass.zone_map(k, zadm, z_arr),
                             {'0': 'global', '8': 'shark-ws',
                              '12': 'shark-media'})

        # Ask for all of nine, get all of nine, in any order
        #
        self.assertIsInstance(klass.zone_map(k, zadm, '__all__'), dict)
        self.assertDictContainsSubset(klass.zone_map(k, zadm, '__all__'),
                                      {'0': 'global',
                                       '5': 'shark-wavefront',
                                       '6': 'shark-graylog',
                                       '7': 'shark-dns',
                                       '8': 'shark-ws',
                                       '12': 'shark-media',
                                       '13': 'shark-mysql',
                                       '14': 'shark-www',
                                       '15': 'shark-login'})

        self.assertIs(len(klass.zone_map(k, zadm, '__all__')), 9)

if __name__ == '__main__':
    unittest.main()
