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
        return sh.get_kstat(':::', ks_class='disk', no_times=True,
                            statlist=self.config['fields'])

    def collect(self):
        for k, v in self.kstats().items():
            mod, inst, dev, name = k.split(':')
            if (sh.wanted(dev, self.config['devices'], regex=True)):
                self.publish('%s.%s' % (dev, name), v)
