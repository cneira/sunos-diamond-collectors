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

        # I think nearly everything in the memory_cap kstat module
        # should be considered a rate. Only `rss` and `swap` appear
        # to be gauges.

        no_deriv = ('rss', 'swap')

        memcap = sh.kstat_raw_module('memory_cap')
        snaptime = long(memcap['snaptime'])
        del memcap['snaptime']

        for stat in no_deriv:
            self.publish('memory_cap.%s' % stat, memcap[stat])
            del memcap[stat]

        if 'memcap_snaptime' in self.last_values:
            snaptime_delta = snaptime - self.last_values['memcap_snaptime']
            self.log.debug('snaptime delta is %d' % snaptime_delta)

            for k, v in memcap.items():
                self.log.debug('memory_cap.%s = %d' % (k, v))
                self.publish('memory_cap.%s' % k,
                        self.derivative(k, v, time_delta=snaptime_delta))

        self.last_values['memcap_snaptime'] = snaptime
