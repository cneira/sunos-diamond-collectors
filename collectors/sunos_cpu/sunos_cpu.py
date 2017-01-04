import diamond.collector
import sunos_helpers as sh
from re import sub

"""
Collect CPU metrics and send them on. Most are sent through
unprocessed, but 'nsec' times can be sent as rates, and %ages can be
derived from these.

Other things may change to rates. This is work in progress.

This collector only works on "global" CPU usage. If you want
per-zone statistics, look at the 'zone_usage' collector.
"""


class SunOSCPUCollector(diamond.collector.Collector):

    def get_default_config(self):
        config = super(SunOSCPUCollector, self).get_default_config()
        config.update({
            'as_nsec_delta': '__all__',
            'as_pc_delta':   '__all__',
            'path':          'cpu',
            'fields':        '__all__',
            })
        return config

    def split_stats(self, kstats):
        """
        Break a single list of kstats into one list per instance.

        :param kstats: a standard dict of kstats are returned by
          sunos_helpers::get_kstat() (dict)
        :returns: a dict where the key is the instance number and
          the value is a key-value dict of the same form as the
          kstats arg
        """

        ret = {}

        for k, v in kstats.items():
            t = k.split(':')
            cpu_id = int(t[1])

            if cpu_id not in ret.keys():
                ret[cpu_id] = {}

            ret[cpu_id][t[3]] = v

        if 'cpu' not in self.last_values:
            self.last_values['cpu'] = {}

        return ret

    def ns_and_pc(self, cpu_id, data):
        """
        In addition to sending raw metrics through, we can calculate
        rates and percentages of the time spent in each possible CPU
        state.

        :param cpu_id: the number of the CPU kstat instance (int)
        :param data: kstat data for this CPU (dict)
        :returns: void
        """

        st = data['snaptime']

        if cpu_id not in self.last_values['cpu'].keys():
            self.last_values['cpu'][cpu_id] = {}

        try:
            st_delta = st - self.last_values['cpu'][cpu_id]['st']
        except:
            self.log.debug('cannot calculate snaptime delta')

        self.last_values['cpu'][cpu_id]['st'] = st

        for m in data:
            if not m.startswith('cpu_nsec'):
                continue

            metric_name = sub('_', '.', m[4:])

            try:
                delta = data[m] - self.last_values['cpu'][cpu_id][m]

                # The delta is the time in this state since the last
                # snapshot

                if sh.wanted(metric_name, self.config['as_nsec_delta']):
                    self.publish('%d.%s' % (cpu_id, metric_name), delta)

                # We now have the number of nanoseconds spent in
                # this state since the last snapshot. So, we can
                # create a %age, if the user wants it.

                pc_metric_name = sub('nsec', 'pc', metric_name)

                if sh.wanted(pc_metric_name, self.config['as_pc_delta']):
                    pc_in_state = delta / float(st_delta) * 100
                    self.publish('%d.%s' % (cpu_id, pc_metric_name),
                                 pc_in_state, precision=3)
            except:
                self.log.debug('cannot calculate %s delta' % m)

            self.last_values['cpu'][cpu_id][m] = data[m]

    def vcpus(self):
        if 'vcpus' not in self.last_values:
            self.last_values['vcpus'] = len(
                    sh.run_cmd('/usr/sbin/psrinfo', as_arr=True))

        return self.last_values['vcpus']

    def clock_speed(self):
        """
        This works for all the Intel processors I can access. I
        imagine it won't work for AMD, and possibly for other Intel
        models. This seems better than parsing prstat(1).
        """
        speeds = sh.get_kstat(
                'cpu_info:0:cpu_info0:supported_frequencies_Hz',
                terse=True, only_num=False)

        return float(speeds['supported_frequencies_hz'].
                rstrip('\x00').split(':')[-1])

    def cpu_stat(self, name, cpu):
        """
        Returns only the value for a given cpu_info kstat
        """

        speed = sh.get_kstat(
                'cpu_info:%d:cpu_info%d:%s' % (cpu, cpu, name),
                terse=True)

        return float(speed[name.lower()])

    def collect(self):
        cpu_t = sh.get_kstat('cpu::sys')
        per_cpu = self.split_stats(cpu_t)

        num_cpus = self.vcpus()

        if sh.wanted('vcpus', self.config['fields']):
            self.publish('global.vcpus', num_cpus)

        if sh.wanted('speed', self.config['fields']):
            self.publish('global.clock_speed', self.clock_speed())

            for n in range(0, num_cpus):
                self.publish('%d.cpuinfo.current_speed' % n,
                        self.cpu_stat('current_clock_Hz', n))

        if sh.wanted('state', self.config['fields']):
            for n in range(0, num_cpus):
                states = sh.get_kstat(
                    'cpu_info:%d:cpu_info%d' % (n, n), terse=True)

                for s in ('cstate', 'pstate'):
                    self.publish('%d.cpuinfo.current_%s' % (n, s),
                        float(states['current_%s' % s]))

        # If we want rate metrics, call the method which does that,
        # and remove the things it uses from the kstat list. This
        # needs to be done for each CPU.

        if self.config['as_pc_delta'] or self.config['as_nsec_delta']:

            for cpu, k in per_cpu.items():
                self.ns_and_pc(cpu, k)

                per_cpu[cpu] = {k: per_cpu[cpu][k] for k in
                                per_cpu[cpu] if not
                                k.startswith('cpu_nsec')}

        for cpu, kstats in per_cpu.items():
            kstats.pop('snaptime', None)
            kstats.pop('crtime', None)

            for k, v in kstats.items():
                if sh.wanted(k, self.config['fields']):
                    self.publish('%d.sys.%s' % (cpu, k), v)
