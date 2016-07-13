import diamond.collector
import sunos_helpers as sh

class ZoneUsageCollector(diamond.collector.Collector):

    def get_default_config(self):
        config = super(ZoneUsageCollector, self).get_default_config()
        config.update({
            'path':   'zone.usage',
            'zones':  '__all__',
            })
        return config

    def nprocs(self, zid):
        # return the number of processes in the zone
        return sh.get_kstat('caps:%s:nprocs_zone_%s:usage' %
                (zid, zid)).values()[-1]

    def collect(self):
        zm = sh.zone_map(sh.zoneadm(), self.config['zones'])

        # Our get_kstat() method doesn't handle wildcards (maybe it
        # should?) so we'll have to do a call for each zone.

        for zid, zone in zm.items():
            self.publish('%s.nprocs' % zone, self.nprocs(zid))
