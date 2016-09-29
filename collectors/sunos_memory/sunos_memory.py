import diamond.collector
import sunos_helpers as sh
import re

class SunOSMemoryCollector(diamond.collector.Collector):

    def get_default_config(self):
        config = super(SunOSMemoryCollector, self).get_default_config()
        config.update({
            'vminfo_fields':   '__all__',
            'swap_fields':     '__all__',
            'swapping_fields': '__all__',
            'paging_fields':   '__all__',
            'path':            'memory',
            'per_cpu_swapping': False,
            'per_cpu_paging':   False,
            })
        return config

    def pagesize(self):
        """
        page size will never change, so get it once and cache it
        """
        if 'pagesize' in self.last_values:
            pagesize = self.last_values['pagesize']
        else:
            pagesize = sh.run_cmd('/bin/pagesize')

        return pagesize

    def collect_swap_cmd(self, pgs):
        info = re.match(
                'total: (\d+)k [\w ]* \+ (\d+)k.*= (\d+)k used, (\d+)k.*$',
                sh.run_cmd('/usr/sbin/swap -s'))

        for i, metric in enumerate(['allocated', 'reserved', 'used',
            'available']):
            if sh.wanted(metric, self.config['swap_fields']):
                self.publish('swap.%s' % metric, int(info.group(i + 1))
                        * 1024)


    def collect_stuff(self, ks, ptn, prefix):
        sums = {}


        for k, v in { k:v for (k,v) in ks.items() if k.endswith('%sin' %
            ptn) or k.endswith('%sout' % ptn) }.items():
            c = k.split(':')

            if self.config['per_cpu_%s' % prefix]:
                self.publish('%s.cpu.%s.%s' % (prefix, c[1], c[3]), v)
            else:
                if c[3] not in sums: sums[c[3]] = 0
                sums[c[3]] += v

        for k, v in sums.items():
            self.publish('%s.%s' % (prefix, k), v)

    def collect(self):
        pgs = int(self.pagesize())
        #
        # Start off with a few simple, system-wide things
        #
        kpg = sh.get_kstat('unix:0:system_pages:pp_kernel', single_val=True)
        self.publish('kernel', int(kpg) * pgs)

        self.publish('arc_size', sh.get_kstat('zfs:0:arcstats:size',
            single_val=True))

        self.publish('pages.free',
            sh.get_kstat('unix:0:system_pages:pagesfree', single_val=True))

        # A breakdown of the output of the swap command. It reports in
        # kb. Don't shell out if we don't need the results.

        if (self.config['swap_fields'] and self.config['swap_fields'] !=
                '__none__'):
            self.collect_swap_cmd(pgs)

        # metrics from the 'vminfo' kstat. These are in pages.

        for k, v in sh.get_kstat('unix:0:vminfo', terse=True,
                no_times=True).items():
            if sh.wanted(k, self.config['vminfo_fields']):
                self.publish('vminfo.%s' % k, v * pgs)

        ks = sh.get_kstat('cpu::vm')
        self.collect_stuff(ks, 'pg', 'paging')
        self.collect_stuff(ks, 'swap', 'swapping')
