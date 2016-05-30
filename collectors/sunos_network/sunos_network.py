import diamond.collector
import sunos_helpers as sh

class SunOSNetworkCollector(diamond.collector.Collector):

    def get_default_config(self):
        config = super(SunOSNetworkCollector, self).get_default_config()
        config.update({
            'nics':   ['net0'],
            'fields': ['obytes64', 'rbytes64', 'collisions',
                       'brdcstrcv', 'brdcstxmt', 'ierrors',
                       'oerrors', 'multircv', 'multixmit'
                      ],
            'path':   'network',
            'zones':  '__all__',
            })
        return config

    def zoneadm(self):
        """
        Get a list of visible zones. This needs to always be an array,
        even if there's only one.

        :returns: output of zoneadm command, one zone per line.
        """

        ret = sh.run_cmd('/usr/sbin/zoneadm list -pc')

        if isinstance(ret, basestring):
            return [ret]
        else:
            return ret

    def zone_map(self, zoneadm, passthru = '__all__'):
        """
        Return a map of zone ID to zone name. Can't be cached because
        zones could be rebooted and get a different ID mid-flight. This
        would be a problem if you were running from the global.

        :param zoneadm: the output of a `zoneadm list -pc` command.
            (string)
        :param passthru: a list of zones you want: everything else will
            be discarded. If there's no passthru, you get everything.
            Non-running zones are ignored. (string or list)
        :raises: NotImplementedError if it can't parse the zoneadm arg.
        :return: map of { zone_id: zone name}. (dict)
        """

        ret = {}

        for z in zoneadm:
            chunks = z.split(':')

            if len(chunks) != 10:
                raise NotImplementedError(
                'cannot parse zoneadm output: %d fields in %s' %
                (len(chunks), zoneadm))

            if chunks[0] == '-':
                continue

            if passthru == '__all__' or chunks[1] in passthru:
                ret[chunks[0]] = chunks[1]

        """
        Here's a cheat: if we're in an NGZ, we don't actually care about
        the zone ID. In fact, kstat `link` instances *don't* match to
        zone ID in NGZs. So, we fudge the key.
        """

        if len(zoneadm) == 1 and ret.keys()[0] != 'global':
            ret = { '0': ret.values()[0] }

        return ret

    def kstats(self, zone_id, nic):
        return sh.get_kstat('link:%s:%s' % (zone_id, nic),
                no_times=True, terse=True)

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

        nics = self.config['nics']

        if 'nic_map' in self.last_values:
            nic_map = self.last_values['nic_map']
        else:
            nic_map = self.nic_map()
            self.last_values['nic_map'] = nic_map

        zm = self.zone_map(self.zoneadm(), self.config['zones'])
        self.log.debug(zm)

        for nic_id, nic_name in nic_map:
            if (sh.wanted(nic_name, self.config['nics'], regex=True) and
                    nic_id in zm.keys()):
                for k, v in self.kstats(nic_id, nic_name).items():
                    if sh.wanted(k, self.config['fields']):
                      self.publish('%s.%s.%s' % (zm[nic_id], nic_name, k), v)
