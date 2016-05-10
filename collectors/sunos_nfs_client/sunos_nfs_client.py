import diamond.collector
import sunos_helpers as sh

class SunOSNFSClientCollector(diamond.collector.Collector):

    def get_default_config(self):
        config = super(SunOSNFSClientCollector, self).get_default_config()
        config.update({
            'fields': '__all__',
            'path':   'nfs.client',
            })
        return config

    def collect(self):
        for nfs_ver in self.config['nfs_vers']:
            for k, v in sh.kstat_name(
                    'nfs::0::rfsreqcnt_v%s' % nfs_ver).iteritems():
                if sh.wanted(k, self.config['fields']):
                  self.publish('v%s.%s' % (nfs_ver, k), v)
