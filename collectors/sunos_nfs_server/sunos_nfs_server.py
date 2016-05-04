import diamond.collector
import sunos_helpers

class SunOSNFSServerCollector(diamond.collector.Collector):

    def get_default_config(self):
        config = super(SunOSNFSServerCollector, self).get_default_config()
        config.update({
            'nfs_vers': [3,4],
            'path':     'nfs.server',
            })
        return config

    def collect(self):
        for nfs_ver in self.config['nfs_vers']:
            for k, v in sunos_helpers.kstat_name(
                    'nfs:0:rfsproccnt_v%s' % nfs_ver).iteritems():
                if (not 'fields' in self.config) or (k in
                self.config['fields']):
                  self.publish('v%s.%s' % (nfs_ver, k), v)
