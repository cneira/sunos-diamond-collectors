import diamond.collector
import sunos_helpers as sh
from sys import maxint

class SmartOSZoneCollector(diamond.collector.Collector):

    def get_default_config(self):
        config = super(SmartOSZoneCollector, self).get_default_config()
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

        # My thinking right now is to send everything in the following
        # modules as if it were a gauge: i.e. no derived values. THIS
        # MAY CHANGE!

        for kstat in ('swapresv', 'lockedmem', 'nprocs', 'cpucaps',
                      'physicalmem', 'memcap'):
            for k, v in sh.get_kstat('caps:%d:%s_zone_%d' % (zid,
                kstat, zid), no_times=False, terse=True).items():
                if k == 'snaptime': continue
                if k == 'value' and v > maxint * 2: continue
                self.publish('%s.%s' % (kstat, k), v)

        # I think nearly everything in the memory_cap kstat module
        # should be considered a rate. Only `rss` and `swap` appear
        # to be genuine gauges (i.e. they go down as well as up.) It's
        # probably useful to have `nover` as a gauge too though: it
        # maybe useful to know how many times you've been "over the
        # limit".

        memcap_no_deriv = ('rss', 'swap', 'nover')

        memcap = sh.get_kstat('memory_cap', no_times=False, terse=True)
        snaptime = long(memcap['snaptime'])
        del memcap['snaptime']

        for stat in memcap_no_deriv:
            self.publish('memory_cap.%s' % stat, memcap[stat])
            del memcap[stat]

        if 'memcap_snaptime' in self.last_values:
            snaptime_delta = snaptime - self.last_values['memcap_snaptime']

            for k, v in memcap.items():
                self.publish('memory_cap.%s' % k,
                        self.derivative(k, v, time_delta=snaptime_delta))

        self.last_values['memcap_snaptime'] = snaptime
