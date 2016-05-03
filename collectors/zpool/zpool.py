# coding=utf8

"""
Zpool Collector

Uses the system 'zpool' command to get a list, and therefore the
status, of the pools on the system, which it converts into metrics.

Allocations and sizes are converted from human-readable form to
bytes, assuming 1024 b in a kb, 1024 kb in a Mb etc.

The health of the pool is sent as an integer. See below for values,
but basically, if it's non-zero, ALERT!

By default sends the allocated data in the pool (b), free space (b)
capacity (%) and the pool's health. Override with the 'fields'
setting in your config.

Only tested on Solaris. May work with bedroom hobbyist operating
systems.

#### Dependencies

 * /usr/sbin/zpool

#### Examples

    only send capacity and health information

    fields = cap,health
"""

import diamond.collector
import sunos_helpers as sh

class ZpoolCollector(diamond.collector.Collector):

    def get_default_config(self):
        config = super(ZpoolCollector, self).get_default_config()
        config.update({
            'path':  'zpool',
            'fields': ['alloc', 'free', 'cap', 'health']
            })
        return config

    def health_as_int(self, health):
        #
        # convert the health of a zpool to an integer, so you can
        # alert off it.
        #
        # 0 : ONLINE
        # 1 : DEGRADED
        # 2 : SUSPENDED
        # 3 : UNAVAIL
        # 4 : <cannot parse>
        #
        healths = ['ONLINE', 'DEGRADED', 'SUSPENDED', 'UNAVAIL']

        try:
            return healths.index(health)
        except ValueError:
            return 4

    def zpool(self):
        return sh.run_cmd('/usr/sbin/zpool list -H')

    def collect(self):
        for p in self.zpool():
            (name, size, alloc, free, cap, dedup, health,
                    altroot) = p.split();

            if 'size' in self.config['fields']:
                self.publish('%s.size' % name, sh.bytify(alloc))

            if 'alloc' in self.config['fields']:
                self.publish('%s.alloc' % name, sh.bytify(alloc))

            if 'free' in self.config['fields']:
                self.publish('%s.free' % name, sh.bytify(free))

            if 'cap' in self.config['fields']:
                self.publish('%s.cap' % name, float(cap[:-1]))

            if 'dedup' in self.config['fields']:
                self.publish('%s.dedup' % name, float(dedup[:-1]))

            if 'health' in self.config['fields']:
                self.publish('%s.health' % name, self.health_as_int(health))
