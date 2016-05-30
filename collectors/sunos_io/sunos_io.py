import diamond.collector
import sunos_helpers as sh

class SunOSIOCollector(diamond.collector.Collector):

    def get_default_config(self):
        config = super(SunOSIOCollector, self).get_default_config()
        config.update({
            'devices': 'cmdk0',
            'fields': '__all__',
            'path':     'io',
            })
        return config

    def kstats(self):
        return sh.get_kstat(':::', ks_class='disk', no_times=True)

    def collect(self):
        for k, v in self.kstats().items():
            mod, inst, dev, name = k.split(':')
            if (sh.wanted(dev, self.config['devices'], regex=True) and
                    sh.wanted(name, self.config['fields'])):
                self.publish('%s.%s' % (dev, name), v)
