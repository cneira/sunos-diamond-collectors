import diamond.collector
import sunos_helpers as sh

class SunOSNetworkCollector(diamond.collector.Collector):

    def get_default_config(self):
        config = super(SunOSNetworkCollector, self).get_default_config()
        config.update({
            'nic':    ['net0'],
            'fields': ['obytes64', 'rbytes64', 'collisions',
                       'brdcstrcv', 'brdcstxmt', 'ierrors',
                       'oerrors', 'multircv', 'multixmit'
                      ],
            'path':     'network',
            })
        return config

    def zoneadm(self):
        return sh.run_cmd('/usr/sbin/zoneadm list -pc')

    def zone_map(self, zoneadm, passthru = '__all__'):
        #
        # Return a map of zone ID to zone name. Can't be cached
        # because zones could be rebooted and get a different ID
        # mid-flight. The passthru arg is a list of zones you want:
        # everything else will be discarded. If there's no passthru,
        # you get everything. Non-running zones are ignored.
        #
        ret = {}

        for z in zoneadm:
            chunks = z.split(':')

            if len(chunks) != 10:
                raise NotImplementedError(
                'cannot parse zoneadm output: %d fields' % len(chunks))

            if chunks[0] == '-':
                continue

            if passthru == '__all__' or chunks[1] in passthru:
                ret[chunks[0]] = chunks[1]

        return ret

    def collect(self):
        if 'zones' in self.config:
            passthru = self.config['zones']
            zm = self.zone_map(self.zoneadm(), passthru)
        else:
            zm = { '0': 'global' }

        for nic in self.config['nic']:
            for zid, zname in zm.items():
                for k, v in sh.kstat_name(
                        'link:%s:%s' % (zid, nic)).iteritems():
                    if sh.wanted(k, self.config['fields']):
                      self.publish('%s.%s.%s' % (zname, nic, k), v)
