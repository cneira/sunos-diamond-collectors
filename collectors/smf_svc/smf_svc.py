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
import sunos_helpers

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

    def svcs(self):
        return sunos_helpers.run_cmd('/bin/svcs -aHo state')

    def collect(self):
        svcs = self.svcs()

        for state in self.config['states']:
            self.publish(state, svcs.count(state))
