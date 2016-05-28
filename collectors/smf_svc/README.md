# SMF Service Collector

Uses the system `svcs` command to count how many services are in each
possible state.

## Options

* **`states`**: by default the collector reports services in all
  possible states: `online`, `offline`, `uninitialized`, `degraded`,
  `maintenance`, `legacy_run`, and `disabled`. This parameter lets you
  choose the states you want counted.

### Examples

Count services in maintenance state, perhaps for an alert.

```
[[ SmfSvcCollector ]]
enabled = True
states = maintenance
```

## Metric Paths
```
smf.svcs.degraded
smf.svcs.disabled
smf.svcs.legacy_run
smf.svcs.maintenance
smf.svcs.offline
smf.svcs.online
smf.svcs.uninitialized
```

## Statistics

On an eight-core i7 box, collection of all service states takes ~50ms.
