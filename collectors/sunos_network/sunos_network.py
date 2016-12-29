import diamond.collector
import sunos_helpers as sh


class SunOSNetworkCollector(diamond.collector.Collector):

    def get_default_config(self):
        config = super(SunOSNetworkCollector, self).get_default_config()
        config.update({'nics':   ['net0'],
                       'fields': ['obytes64', 'rbytes64', 'collisions',
                                  'brdcstrcv', 'brdcstxmt', 'ierrors',
                                  'oerrors', 'multircv', 'multixmit'],
                       'path':   'network',
                       'zones':  '__all__'}
                      )
        return config

    def kstats(self, zone_id, nic):
        return sh.get_kstat('link:%s:%s' % (zone_id, nic),
                            no_times=True, terse=True,
                            statlist=self.config['fields'])

    def nic_map(self):
        """
        If the user has used the magic value '__all__' for nics
        parameter, we will kindly fetch them a list of all the nics
        known. I think it's safe to cache this.

        :returns: a list of lists: inner lists are [kstat_instance,
            kstat_name]
        """

        return [y.split(':')[1:-1] for y in sh.get_kstat('link:::rbytes',
                ks_class='net', no_times=True).keys()]

    def collect(self):
        """
        If we are in the global zone then all the NGZ vnics use the zone
        ID as their instance number. The user may wish us to get all,
        some, or none of these. Unless it's the latter, we need a map of
        zone name (which will end up in the metric path) to zone ID
        (which we need to get the correct kstats).

        In an NGZ, the instance numer mapping is different. Everything
        *seems* to be instance 0.
        """

        if 'nic_map' in self.last_values:
            nic_map = self.last_values['nic_map']
        else:
            nic_map = self.nic_map()
            self.last_values['nic_map'] = nic_map

        zm = sh.zone_map(sh.zoneadm(), self.config['zones'])

        for nic_id, nic_name in nic_map:
            if (sh.wanted(nic_name, self.config['nics'], regex=True) and
                    nic_id in zm.keys()):
                for k, v in self.kstats(nic_id, nic_name).items():
                    self.publish('%s.%s.%s' % (zm[nic_id], nic_name, k), v)
