# coding=utf8

"""
FMA Collector

This is a very vague, experimental collector for the Solaris fault
management architecture. I'm not sure yet what it is worth
recording, and how, so this is almost certainly subject to change.

#### Dependencies

To run the `fmstat` command, your Diamond user needs the `System
Observability` profile. Add it with `usermod -P "System
Observability" diamond`. I don't know how useful the `fmstat` output is
likely to be.

 * /usr/sbin/fmadm
 * /bin/pfexec
 * /usr/sbin/fmstat

"""

import diamond.collector
import sunos_helpers as sh
import re
from collections import Counter


class FMACollector(diamond.collector.Collector):

    def get_default_config(self):
        config = super(FMACollector, self).get_default_config()
        config.update({
            'path':   'fma',
            'fmstat': False,
            'fmadm':  True
        })
        return config

    def fmadm(self):
        try:
            return sh.run_cmd('/usr/sbin/fmadm faulty', True)
        except:
            raise NotImplementedError('unable to run fmadm')

    def fmstat(self):
        try:
            return sh.run_cmd('/usr/sbin/fmstat', True)
        except:
            raise NotImplementedError('unable to run fmstat')

    def fmadm_impacts(self, fmadm_info):
        impacts = filter(lambda l: re.search('Problem class', l),
                         fmadm_info)
        return [i.split(':')[1].strip() for i in impacts]

    def collate_fmstats(self, fmstat_info):
        """
        return a dict of the form:

        fmstat.module.key => value
        """

        keys = ('ev_recv', 'ev_acpt', 'wait', 'svc_t', 'pc_w',
                'pc_b', 'open', 'solve', 'memsz', 'bufsz')

        # first line is a header (there's no -H. Or -p. For shame.)
        fmstat = self.fmstat()[1:]
        ret = {}

        for mod in fmstat:
            # the first value, the module name will be part of the
            # metric path
            chunks = mod.split()
            module = chunks.pop(0)
            raw = zip(keys, chunks)

            for k, v in raw:
                if k == 'memsz' or k == 'bufsz':
                    v = sh.bytify(v)

                ret['fmstat.%s.%s' % (module, k)] = v

        return ret

    def collect(self):
        if self.config['fmadm']:
            impacts = self.fmadm_impacts(self.fmadm())

            for scheme, count in Counter(impacts).items():
                self.publish('fmadm.alert.%s' % scheme, int(count))

        if self.config['fmstat']:
            for k, v in self.collate_fmstats(self.fmstat()).items():
                self.publish(k, v)
