import diamond.collector
import sunos_helpers as sh
import os
import time
from re import sub

class SunOSProcCollector(diamond.collector.Collector):

    def get_default_config(self):
        config = super(SunOSProcCollector, self).get_default_config()
        config.update({
                'path': 'process',
                'top_x': 10,
                'fields': '__all__',
                'as_pc_delta': True,
            })
        return config

    def leaderboard(self, procs, metric, limit=10):
        """
        returns a a list of dicts describing the top 'limit'
        processes, measured by 'metric'.
        :param procs: all processes, defined by the proc_info()
            method in the sunos_helpers module. (list)
        :param metric: a key in the process dict from proc_info(),
            as defined in the `psinfo` or `usage` structs in
            proc(4). (string)
        :param limit: how many results to return. (int)
        :returns: list of hashes (see below) sorted on the `val`
            field.
        """

        unsorted = [{
            'zone': self.zone_lookup(str(procs[o]['pr_zoneid'])),
            'name': procs[o]['pr_fname'].rstrip('\x00').replace('.', '_'),
            'pid':  o,
            'val':  procs[o][metric],
            'ctid': procs[o]['pr_contract'],
            'ts':   procs[o]['pr_tstamp']} for o in procs]

        return sorted(unsorted, key=lambda d: d['val'],
                reverse=True)[:limit]

    def cpu_time(self, procs, metric):
        """
        """
        if 'proc' not in self.last_values.keys():
            self.last_values['proc'] = {}

        for p in self.leaderboard(procs, metric, self.config['top_x']):
            p_id = '%s-%s-%s' % (p['name'], p['pid'], metric)

            if p_id not in self.last_values['proc'].keys():
                self.last_values['proc'][p_id] = {}

            last = self.last_values['proc'][p_id]
            self.last_values['proc'][p_id] = p

            try:
                ts_delta = p['ts'] - last['ts']
            except:
                self.log.debug('cannot calculate timestamp delta for %s'
                        % p['name'])
                return False

            try:
                delta = p['val'] - last['val']

                # Don't send null metrics. Think of the point rate!

                if delta == 0:
                    return False

                pc = delta / float(ts_delta) * 100

                self.publish('cpu_pc.%s.%s' % (p['name'], metric),
                             pc, precision=3,
                             point_tags={'pid':  p['pid'],
                                         'zone': p['zone']})
            except:
                self.log.debug('cannot calculate %s %s delta' %
                (p['name'], metric))

    def all_procs(self):
        """
        return a hash of all process information on the box
        """
        procs = {}

        for pid in os.listdir('/proc'):
            psinfo = sh.proc_info('psinfo', pid)
            usage = sh.proc_info('usage', pid)
            procs[pid] = psinfo.copy()
            procs[pid].update(usage)

        return procs

    def zone_lookup(self, zid):
        """
        In an NGZ, the zone map will always return 0 for the local
        zone, to work with kstats.
        """
        try:
            z = self.zm[zid]
        except:
            if 'zone_name' in self.last_values:
                z = self.last_values['zone_name']
            else:
                z = sh.run_cmd('/bin/zonename')
                self.last_values['zone_name'] = z

        return z

    def svc_tag(self, ctid):
        try:
            svc = self.ct_map[str(ctid)]
        except:
            svc = 'unknown'

        return svc

    def collect(self):
        procs = self.all_procs()
        self.zm = sh.zone_map(sh.zoneadm())
        self.ct_map = sh.contract_map()

        for m in ('pr_stime', 'pr_utime', 'pr_ttime', 'pr_rtime',
                  'pr_tftime', 'pr_dftime', 'pr_kftime', 'pr_ltime',
                  'pr_slptime', 'pr_wtime', 'pr_stoptime'):
            if sh.wanted(m, self.config['fields']) and \
            self.config['as_pc_delta'] == True:
                self.cpu_time(procs, m)

        for m in ('pr_rssize', 'pr_size'):
            if sh.wanted(m, self.config['fields']):
                for p in self.leaderboard(procs, m,
                        self.config['top_x']):
                    if p['val'] > 0:
                        self.publish('memory.%s.%s' % (m,
                            p['name']), (p['val'] * 1024),
                            point_tags={'pid': p['pid'],
                                'zone': p['zone'],
                                'svc': self.svc_tag(p['ctid'])})

        for m in ('pr_pctmem', 'pr_pctcpu'):
            if sh.wanted(m, self.config['fields']):
                for p in self.leaderboard(procs, m,
                        self.config['top_x']):
                    if p['val'] > 0:
                        self.publish('memory.%s.%s' % (m,
                            p['name']), sh.bpc_to_pc(p['val']),
                            point_tags={'pid': p['pid'], 'zone':
                                p['zone'],
                                'svc': self.svc_tag(p['ctid'])})
