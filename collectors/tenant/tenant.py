import diamond.collector
import sunos_helpers as sh
from sys import maxint

class TenantCollector(diamond.collector.Collector):

    def get_default_config(self):
        config = super(TenantCollector, self).get_default_config()
        config.update({
            'path':   'tenant',
            })
        return config

    def zid(self):
        """
        Return the zone id. I don't *think* this can change, so
        we'll cache it.
        """

        if 'zid' in self.last_values:
            zid = self.last_values['zid']
        else:
            zid = int(sh.run_cmd(
                        '/usr/sbin/zoneadm list -p').split(':')[0])
            self.last_values['zid'] = zid

        return zid

    def collect(self):
        zid = self.zid()

        for kstat in ('swapresv', 'lockedmem', 'nprocs', 'cpucaps',
                      'physicalmem'):
            for k, v in sh.kstat_name('caps:%d:%s_zone_%d' % (zid,
                kstat, zid)).items():
                if k == 'snaptime': continue
                if k == 'value' and v > maxint * 2: continue
                self.publish('%s.%s' % (kstat, k), v)
