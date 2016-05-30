# coding=utf8

"""

Takes ZFS arc kstats (and related) and turns them into metrics. Does not
do the renaming that the collectd equivalent does, which I think makes
it more future-proof.

By default all stats are dumped from the `arcstats`, `vdev_cache_stats`
and `zfetchstats` modules. If you wish to be more selective, you can
supply a comma-separated list of the kstat names you want via the
`arc_stats`, `vdev_stats`, and `zfetch_stats` stats.

#### Dependencies

  * kstat module from https://github.com/imp/kstat
  * SunOS

"""

import diamond.collector
import sunos_helpers as sh

class ZFSArcCollector(diamond.collector.Collector):

    def get_default_config(self):
        config = super(ZFSArcCollector, self).get_default_config()
        config.update({
            'path':             'zfs',
            'arcstats':         '__all__',
            'vdev_cache_stats': '__all__',
            'zfetchstats':      '__all__',
            })
        return config

    def kstats(self, group):
        return sh.get_kstat('zfs:0:%s' % group, terse=True, no_times=True)

    def collect(self):
        for group in ('arcstats', 'vdev_cache_stats', 'zfetchstats'):
            if self.config[group]:
                for k, v in self.kstats(group).items():
                    if sh.wanted(k, self.config[group]):
                        self.publish('.'.join([group, k]), v)
