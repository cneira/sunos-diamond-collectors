import diamond.collector
import sunos_helpers

class SunOSDiskHealthCollector(diamond.collector.Collector):

    def get_default_config(self):
        config = super(SunOSDiskHealthCollector, self).get_default_config()
        config.update({
            'path':   'disk.error',
            })
        return config

    def kstats(self):
        return sunos_helpers.kstat_module('cmdkerror', '.* Errors')

    def collect(self):
        for name, val in self.kstats().items():
            self.publish(name.replace(',error', ''), val)

