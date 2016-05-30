import diamond.collector
import sunos_helpers as sh

class SunOSNFSClientCollector(diamond.collector.Collector):

    def get_default_config(self):
        config = super(SunOSNFSClientCollector, self).get_default_config()
        config.update({
            'fields':   '__all__',
            'path':     'nfs.client',
            'nfs_vers': [3, 4],
            })

        return config

    def collect(self):
        for nfs_ver in self.config['nfs_vers']:
            for k, v in sh.get_kstat('nfs:0:rfsreqcnt_v%s' % nfs_ver,
                    terse=True, no_times=True).iteritems():
                if sh.wanted(k, self.config['fields']):
                    self.publish('v%s.%s' % (nfs_ver, k), v)
