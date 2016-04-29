import diamond.collector
import sunos_helpers

class SunOSNFSClientCollector(diamond.collector.Collector):

    def get_default_config(self):
        config = super(SunOSNFSClientCollector, self).get_default_config()
        config.update({
            'path':     'nfs.client',
            })
        return config

    def collect(self):
        for nfs_ver in self.config['nfs_vers']:
            for k, v in sunos_helpers.kstat_name(
                    'nfs::0::rfsreqcnt_v%s' % nfs_ver).iteritems():
                if (not 'fields' in self.config) or (k in
                self.config['fields']):
                  self.publish('v%s.%s' % (nfs_ver, k), v)
