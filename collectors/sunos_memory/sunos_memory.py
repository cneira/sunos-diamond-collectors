import diamond.collector
import sunos_helpers as sh
import re


class SunOSMemoryCollector(diamond.collector.Collector):

    def get_default_config(self):
        config = super(SunOSMemoryCollector, self).get_default_config()
        config.update({
            'path':            'memory',
            'vminfo_fields':   '__all__',
            'swap_fields':     '__all__',
            'swapping_fields': '__all__',
            'paging_fields':   '__all__',
            'per_cpu_swapping': False,
            'per_cpu_paging':   False,
            })

        return config

    def pagesize(self):
        """
        Returns the memory page size on this system. Page size will
        never change, so get it once and cache it.
        """

        if 'pagesize' not in self.last_values:
            pgs = sh.run_cmd('/bin/pagesize')
            self.last_values['pagesize'] = int(pgs)

        return self.last_values['pagesize']

    def collect_swap_cmd(self):
        """
        Shells out to /usr/sbin/swap and sends the results as
        metrics. Converts to bytes from kB. Not smart, so if the
        output of the command changes, this will break.
        """

        info = re.match(
            'total: (\d+)k [\w ]* \+ (\d+)k.*= (\d+)k used, (\d+)k.*$',
            sh.run_cmd('/usr/sbin/swap -s'))

        for i, metric in enumerate(['allocated', 'reserved', 'used',
                                   'available']):
            if sh.wanted(metric, self.config['swap_fields']):
                self.publish('swap.%s' % metric, int(info.group(i + 1)) *
                             1024)

    def collect_vminfo(self, pgs):
        """
        Collect and present metrics from the 'vminfo' kstat. These
        are in pages, and they need to be converted into rates.

        :param pgs: the system page size. (int)
        """

        for k, v in sh.get_kstat('unix:0:vminfo', terse=True,
                                 no_times=True).items():
            if sh.wanted(k, self.config['vminfo_fields']):
                self.publish('vminfo.%s' % k, self.derivative(k, v) * pgs)

    def collect_in_and_out(self, ks, ptn, prefix):
        """
        A bit of a shot-in-the-dark, which I *think* will provide
        useful information. Pulls all paging or swapping
        ins-and-outs out of the cpu::vm kstats and presents them.
        Has the ability to aggregate or present on a per-CPU basis.

        :param ks: the raw cpu::vm kstats as collected by
            sunos_helpers::get_kstats() (dict)
        :param ptn: the pattern to match in the kstats ('pg' or
            'swap') (string)
        :param prefix: the string with which to prefix each metric.
            Also used in the class config variable names. ('paging'
            or 'swapping'. (string)
        :returns: void
        """

        sums = {}
        fields = self.config['%s_fields' % prefix]

        for k, v in {k: v for (k, v) in ks.items()
                     if k.endswith('%sin' % ptn) or
                     k.endswith('%sout' % ptn)}.items():
            c = k.split(':')

            if self.config['per_cpu_%s' % prefix] is True and
            sh.wanted(k, fields):
                self.publish('%s.cpu.%s.%s' % (prefix, c[1], c[3]), v)
            else:
                if c[3] not in sums:
                    sums[c[3]] = 0

                sums[c[3]] += v

        for k, v in sums.items():
            if sh.wanted(k, fields):
                self.publish('%s.%s' % (prefix, k), v)

    def collect(self):
        pgs = self.pagesize()
        #
        # Start off with a few simple, system-wide things
        #
        kpg = sh.get_kstat('unix:0:system_pages:pp_kernel', single_val=True)

        self.publish('kernel', int(kpg) * pgs)

        self.publish('arc_size', sh.get_kstat('zfs:0:arcstats:size',
                     single_val=True))

        self.publish('pages.free',
                     sh.get_kstat('unix:0:system_pages:pagesfree',
                                  single_val=True))

        if (self.config['swap_fields'] and self.config['swap_fields'] !=
                '__none__'):
            self.collect_swap_cmd()

        if (self.config['vminfo_fields'] and
                self.config['vminfo_fields'] != '__none__'):
            self.collect_vminfo(pgs)

        ks = sh.get_kstat('cpu::vm')
        self.collect_in_and_out(ks, 'pg', 'paging')
        self.collect_in_and_out(ks, 'swap', 'swapping')
