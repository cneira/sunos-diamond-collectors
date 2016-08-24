import diamond.collector
import sunos_helpers as sh

class SunOSMemoryCollector(diamond.collector.Collector):

    def get_default_config(self):
        config = super(SunOSMemoryCollector, self).get_default_config()
        config.update({
            'path':   'memory',
            })
        return config

    def pagesize(self):
        """
        page size will never change, so get it once and cache it
        """

        if 'pagesize' in self.last_values:
            pagesize = self.last_values['pagesize']
        else:
            pagesize = sh.run_cmd('/bin/pagesize')

        return pagesize

    def collect(self):
        kstat = 'unix:0:system_pages:pp_kernel'
        kpg = sh.get_kstat(kstat)[kstat]
        self.publish('kernel', int(self.pagesize()) * int(kpg))
