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

Only tested on Solaris and SmartOS. May work with bedroom hobbyist
operating systems.

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
        states = ['ONLINE', 'DEGRADED', 'SUSPENDED', 'UNAVAIL']

        try:
            return states.index(health)
        except ValueError:
            return 4

    def zpool(self):
        sh.run_cmd('/usr/sbin/zpool list')

    def zpool_dict(self):
        """
        SmartOS and Solaris do not return the same fields for zpool
        information. Rather than hardcode each and hope neither
        changes, let's look at the header and use that to build up a
        dict for each pool. Put those in a dict with the zone name
        as the key.
        """
        raw = self.zpool()
        ret = {}

        headers = raw.pop(0).lower().split()
        pools = [pool.split() for pool in raw]

        for pool in pools:
            ret[pool[0]] = dict(zip(headers, pool))

        return ret

    def collect(self):
        for pool, data in self.zpool_dict().items():
            for k, v in data.items():

                if not sh.wanted(k, self.config['fields']):
                    continue

                if k in ('size', 'alloc', 'free', 'expandsz'):
                    self.publish('%s.%s' % (pool, k), sh.bytify(v))
                elif v.endswith('%') or v.endswith('x'):
                    self.publish('%s.%s' % (pool, k), float(v[:-1]))
                elif k == 'health':
                    self.publish('%s.health' % pool, self.health_as_int(v))
