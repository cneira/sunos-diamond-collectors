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
import subprocess
import re
from os import path

class SunOSSwapCollector(diamond.collector.Collector):

    def get_default_config(self):
        config = super(SunOSSwapCollector, self).get_default_config()
        config.update({
            'path':   'swap'
            })
        return config

    def collect(self):
        if not path.exists('/usr/sbin/swap'):
            raise NotImplementedError("platform not supported")

        proc = subprocess.Popen(['/usr/sbin/swap', '-s'],
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE)
        (out, err) = proc.communicate()

        info = re.match(
                'total: (\d+)k [\w ]* \+ (\d+)k.*= (\d+)k used, (\d+)k.*$',
                out)

        for i, metric in enumerate(['allocated', 'reserved', 'used',
            'available']):
            self.publish(metric, int(info.group(i + 1)) * 1024)
