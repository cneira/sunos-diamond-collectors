# coding=utf8

"""
SunOS Swap

The default diamond stuff doesn't seem to give you any useful virtual
memory or swap info on Solaris.

Output is in bytes.

#### Dependencies

 * /usr/sbin/swap

"""

import diamond.collector
import re
import sunos_helpers

class SunOSSwapCollector(diamond.collector.Collector):

    def get_default_config(self):
        config = super(SunOSSwapCollector, self).get_default_config()
        config.update({
            'path':   'swap'
            })
        return config

    def collect(self):
        swap = sunos_helpers.run_cmd('/usr/sbin/swap -s')

        info = re.match(
                'total: (\d+)k [\w ]* \+ (\d+)k.*= (\d+)k used, (\d+)k.*$',
                swap)

        for i, metric in enumerate(['allocated', 'reserved', 'used',
            'available']):
            self.publish(metric, int(info.group(i + 1)) * 1024)
