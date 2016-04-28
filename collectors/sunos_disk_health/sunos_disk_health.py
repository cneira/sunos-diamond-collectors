import diamond.collector
import sunos_helpers

class SunOSDiskHealthCollector(diamond.collector.Collector):

    def get_default_config(self):
        config = super(SunOSDiskHealthCollector, self).get_default_config()
        config.update({
            'path':   'disk.error',
            })
        return config

    def collect(self):
        kstats = sunos_helpers.kstat_module('cmdkerror', '.* Errors')

        for name, val in kstats.items():
            self.publish(name.replace(',error', ''), val)

