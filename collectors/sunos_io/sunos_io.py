import diamond.collector
import sunos_helpers as sh

class SunOSIOCollector(diamond.collector.Collector):

    def get_default_config(self):
        config = super(SunOSIOCollector, self).get_default_config()
        config.update({
            'devices': '__all__',
            'fields': '__all__',
            'path':     'io',
            })
        return config

    def kstats(self):
        return sh.kstat_class('disk')

    def collect(self):
        for disk, kstats in self.kstats().iteritems():
            if sh.wanted(disk, self.config['devices']):
                for k, v in kstats.items():
                    if sh.wanted(k, self.config['fields']):
                        self.publish('%s.%s' % (disk, k), v)
