# coding=utf8

"""
ZFS Collector

Uses the system 'zfs' command to gather various metrics for any or
all ZFS datasets on the host.

Only tested on Solaris and SmartOS. May work with bedroom hobbyist
operating systems.

#### Dependencies

 * /usr/sbin/zfs

"""

import diamond.collector
import sunos_helpers as sh


class ZfsCollector(diamond.collector.Collector):

    def get_default_config(self):
        config = super(ZfsCollector, self).get_default_config()
        config.update({
            'path': 'zfs',
            'fields': '__none__',
            'datasets': ['^crypto$', 'fast', 'space/ufs/jumpstart'],
            'regex': True,
            'counts': ['filsystem', 'snapshot', 'volume'],
        })
        return config

    def fs_list(self):
        """
        Use the 'datasets' and 'recurse' values in the user config
        to create a list of ZFS datasets which we wish to monitor.
        Even though it can be an expensive action, the list is
        regenerated on each collector run, so new datasets can be
        found.
        """
        if not self.config['recurse']:
            return self.config['datasets']

    def zfs_list(self):
        """
        :returns: a list of ZFS filesystems
        """
        return sh.run_cmd('/usr/sbin/zfs list -Ho name')

    def get_all(self, dataset):
        raw = sh.run_cmd('/usr/sbin/zfs get -Ho property,value all %s'
                         % dataset)

        ret = {}

        for metric in raw:
            k, v = metric.split(None, 1)
            try:
                ret[k] = sh.handle_value(v)
            except:
                next

        return ret

    def num_children(self, dataset):
        """
        returns the number of datasets under the given dataset
        """
        return len(sh.grep('^%s\/' % dataset, self._fs_list))

    def num_obj(self, dataset, obj):
        """
        return the number of volumes or snapshots held by the given
        dataset
        """

        raw = sh.run_cmd(
            '/usr/sbin/zfs list -r -d1 -Ho name -t %s %s' %
            (obj, dataset))

        if isinstance(raw, basestring):
            return 1
        else:
            return len(raw)

    def collect(self):
        self._fs_list = self.zfs_list()

        for fs in self._fs_list:

            if sh.wanted(fs, self.config['datasets'],
                         regex=self.config['regex']):

                if sh.wanted('filesystem', self.config['counts']):
                    self.publish('count.%s.filesystem' %
                                 sh.to_metric(fs), self.num_children(fs))

                for t in ('volume', 'snapshot'):
                    if sh.wanted(t, self.config['counts']):
                        self.publish('count.%s.%s' % (sh.to_metric(fs), t),
                                     self.num_obj(fs, t))

                for k, v in self.get_all(fs).items():
                    if sh.wanted(k, self.config['fields']):
                        self.publish('dataset.%s.%s' % (sh.to_metric(fs),
                                                        k), v)
