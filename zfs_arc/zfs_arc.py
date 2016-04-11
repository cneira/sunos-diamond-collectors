# coding=utf8

"""

Takes ZFS arc kstats and turns them into metrics. Does not do the
renaming that the collectd equivalent does, which I think makes it
more future-proof.

By default all ARC stats are dumped. If you wish to be more
selective, you can supply a comma-separated list of kstat names of
the kstats you want.

#### Dependencies

  * kstat module from https://github.com/imp/kstat
  * SunOS


"""

import diamond.collector
import kstat

class ZFSArcCollector(diamond.collector.Collector):

    def get_default_config(self):
        config = super(ZFSArcCollector, self).get_default_config()
        config.update({
            'path':  'zfs.arc',
            'stats': False,
            })
        return config

    def collect(self):
        ko = kstat.Kstat('zfs')
        for stat, val in ko.__getitem__(['zfs', 0, 'arcstats']).items():
            if not self.config['stats'] or (self.config['stats'] and
                    stat in self.config['stats']):
                If isinstance(val, long):
                    self.publish(stat, val)
