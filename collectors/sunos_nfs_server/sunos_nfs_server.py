import diamond.collector
import sunos_helpers

class SunOSNFSServerCollector(diamond.collector.Collector):

    def get_default_config(self):
        config = super(SunOSNFSServerCollector, self).get_default_config()
        config.update({
            'vers':  [2, 3, 4],
            'path':   'nfs.server',
            })
        return config

    def collect(self):

        for v in self.config['vers']:
            self.log.debug('getting server stats for version %d', v)
        #kstats = sunos_helpers.kstat_module('cmdkerror', '.* Errors')

        #for name, val in kstats.items():
            #self.publish(name.replace(',error', ''), val)

