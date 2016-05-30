import diamond.collector, re
import sunos_helpers as sh

class SunOSDiskHealthCollector(diamond.collector.Collector):

    def get_default_config(self):
        config = super(SunOSDiskHealthCollector, self).get_default_config()
        config.update({
            'modules': ['cmdkerror', 'sderr'],
            'fields':  ['hard_errors', 'soft_errors' 'transport_errors',
                        'device_not_ready', 'illegal_request'],
            'path':    'disk.error',
            })
        return config

    def kstats(self, module):
        return sh.get_kstat(module, no_times=True)

    def collect(self):
        for mod in self.config['modules']:
            for k, v in self.kstats(mod).items():
                k = re.sub('.*:(\w+),error:', '\\1.', k)
                if sh.wanted(k.split('.')[1], self.config['fields']):
                    self.publish(k.replace(',error', ''), v)
