# coding=utf8

"""
SMF Service Collector

Uses the system 'svcs' command to count how many services are in
each possible state.

By default all possible service states are reported, but the user
can choose their own with the 'states' option.

#### Dependencies

 * /bin/svcs


#### Example

Only send counts of services which are uninitialized, degraded,
offline, or in maintenance state.

    states = uninitialized,degraded,offline,maintenance

"""

import diamond.collector
import subprocess
from os import path

class SmfSvcCollector(diamond.collector.Collector):

    def get_default_config(self):
        config = super(SmfSvcCollector, self).get_default_config()
        config.update({
            'path':   'smf.svcs',
            'states': ['online', 'offline', 'uninitialized',
                       'degraded', 'maintenance', 'legacy_run',
                       'disabled']
            })
        return config

    def collect(self):
        if not path.exists('/bin/svcs'):
            raise NotImplementedError("platform not supported")

        proc = subprocess.Popen(['/bin/svcs', '-aHo', 'state'],
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE)
        (out, err) = proc.communicate()
        result = out.split('\n')

        for state in self.config['states']:
            self.publish(state, result.count(state))
