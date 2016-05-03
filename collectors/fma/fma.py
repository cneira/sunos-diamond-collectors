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
import sunos_helpers
import re
from collections import Counter

class FMACollector(diamond.collector.Collector):

    def get_default_config(self):
        config = super(FMACollector, self).get_default_config()
        config.update({
            'path':     'fma',
            'fmstat':   True,
            'fmadm':    True
            })
        return config

    def collect(self):
        # This is an attempt to create a metric for alerting. It
        # looks for any unresolved faults, and classifies them based
        # on the first part of the failing FMRI

        if self.config['fmadm']:
            try:
                fmadm = sunos_helpers.run_cmd(
                        '/usr/sbin/fmadm list-defect', True)
            except Exception as e:
                self.log.debug(e)
                raise NotImplementedError('unable to run fmadm')

            impacts = filter(lambda l: re.search('Impact', l), fmadm)
            impacts = [i.split(':')[1].strip() for i in impacts]

            for scheme, count in Counter(impacts).items():
                self.publish('fmadm.alert.%s' % scheme, int(count))

        if self.config['fmstat']:
            try:
                fmstat = sunos_helpers.run_cmd('/usr/sbin/fmstat', True)
            except:
                raise NotImplementedError('unable to run fmstat')

            keys = ('ev_recv', 'ev_acpt', 'wait', 'svc_t', 'pc_w', 'pc_b',
                    'open', 'solve', 'memsz', 'bufsz')

            # first line is a header (there's no -H. Or -p. For shame.)
            fmstat = fmstat[1:]

            for mod in fmstat:

                # the first value, the module name will be part of the
                # metric path

                chunks = mod.split()
                module = chunks.pop(0)

                raw = zip(keys, chunks)

                for k, v in raw:
                    if k == 'memsz' or k == 'bufsz':
                        v = sunos_helpers.bytify(v)

                    self.publish('fmstat.%s.%s' % (module, k), v)
