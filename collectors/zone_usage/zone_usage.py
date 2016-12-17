import diamond.collector
import sunos_helpers as sh
import re

"""
This collector will produce metrics for all the zones on the box. It is
kind of built on the assumption you have resource caps on all of those
zones, because if you don't, many of the kstats will be meaningless.
"""


class ZoneUsageCollector(diamond.collector.Collector):

    def get_default_config(self):
        config = super(ZoneUsageCollector, self).get_default_config()
        config.update({'path':   'zone.usage',
                       'zones':  '__all__',
                       'show_caps': False,
                       })
        return config

    def kstats(self, zid):
        return sh.get_kstat('caps:%s' % zid, no_times=True)

    def process_table(self):
        """
        Use ps(1) to get a list of processes, zones (by ID), and
        task ID
        :returns: a dict where the key is the zone ID (cast to a
            string) and the value is a dict of task_id =>
            process_name. We don't bother with args.
        """

        raw = sh.run_cmd('/bin/ps -eo taskid,zoneid,comm')
        raw.pop(0)

        ret = {}

        for l in raw:
            task, zone, cmd = l.split()

            if zone not in ret.keys():
                ret[zone] = {}

            ret[zone][task] = cmd.split('/')[-1]

        return ret

    def do_one_zone(self, zone, zid):
        """
        We're going to do a little massaging of the kstat names.
        Primarily this will be removing the zone ID.

        At the moment, we disregard projects. I don't use them.
        usage
        """

        for stat, val in self.kstats(zid).items():

            # Disregard projects. Maybe I'll implement them one day.

            if '_project_' in stat or '_task_' in stat:
                continue

            if (stat.startswith('caps:%s:cpucaps_zone' % zid) and not
                    stat.endswith('value')):
                self.log.debug(stat)
                self.publish('%s.cpucaps.%s' % (zone,
                             stat.split(':')[-1]), val)

            if (stat == 'caps:%s:swapresv_zone_%s:usage' % (zid, zid)):
                self.publish('%s.memory.swapresv.usage' % zone, val)

            if (stat == 'caps:%s:lockedmem_zone_%s:usage' % (zid, zid)):
                self.publish('%s.memory.locked.usage' % zone, val)

            if (stat == 'caps:%s:nprocs_zone_%s:usage' % (zid, zid)):
                self.publish('%s.nprocs.usage' % zone, val)

            if not self.config['show_caps']:
                continue

            if (stat == 'caps:%s:swapresv_zone_%s:value' % (zid, zid)):
                self.publish('%s.memory.swapresv.value' % zone, val)

            if (stat == 'caps:%s:lockedmem_zone_%s:value' % (zid, zid)):
                self.publish('%s.memory.locked.value' % zone, val)

            if (stat == 'caps:%s:nprocs_zone_%s:value' % (zid, zid)):
                self.publish('%s.nprocs.value' % zone, val)

            if (stat == 'caps:%s:cpucaps_zone_%s:value' % (zid, zid)):
                self.publish('%s.cpucap.value' % zone, val)

    def deal_with_tasks(self, tasks, zid):
        for task in tasks:
            self.log.debug(task)

    def collect(self):
        zm = sh.zone_map(sh.zoneadm(), self.config['zones'])

        # Our get_kstat() method doesn't handle wildcards (maybe it
        # should?) so we'll have to do a call for each zone.

        for zid, zone in zm.items():
            self.do_one_zone(zone, zid)
