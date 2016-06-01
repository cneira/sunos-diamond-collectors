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

    def kstats(self, nfs_ver):
        return sh.get_kstat('nfs:0:rfsreqcnt_v%s' % nfs_ver, terse=True,
                no_times=True, statlist=self.config['fields'])

    def collect(self):
        for nfs_ver in self.config['nfs_vers']:
            for k, v in self.kstats(nfs_ver).items():
                self.publish('v%s.%s' % (nfs_ver, k), v)
