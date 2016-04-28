import diamond.collector
import sunos_helpers

class SunOSMemoryCollector(diamond.collector.Collector):

    def get_default_config(self):
        config = super(SunOSMemoryCollector, self).get_default_config()
        config.update({
            'path':   'memory',
            })
        return config

    def collect(self):

        # page size will never change, so get it once and cache it

        if 'pagesize' in self.last_values:
            pagesize = self.last_values['pagesize']
        else:
            pagesize = sunos_helpers.run_cmd('/bin/pagesize')

        kpg = sunos_helpers.kstat_val('unix:0:system_pages:pp_kernel')
        self.publish('kernel', int(pagesize) * int(kpg))
