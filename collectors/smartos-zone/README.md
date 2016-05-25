# SmartOS Zone Collector

This collector tries to be a one-stop-shot for all the useful measurables inside
a SmartOS zone.

The view from an NGZ is very different from the global, with many metrics
reflective of the physical host, or unavailable.

Joyent have made sufficient changes to the `kstat` view from an NGZ that you
probably won't get an awful lot of mileage using this in, say, a Solaris 11
zone.

Uses the `kstat` interface.

## Options

## Statistics

### Examples

```
[[ SmartOSZoneCollector ]]
enabled = True
```

## Metric Paths
```
tenant.cpucaps.above_base_sec
tenant.cpucaps.above_sec
tenant.cpucaps.baseline
tenant.cpucaps.below_sec
tenant.cpucaps.burst_limit_sec
tenant.cpucaps.bursting_sec
tenant.cpucaps.effective
tenant.cpucaps.maxusage
tenant.cpucaps.nwait
tenant.cpucaps.usage
tenant.cpucaps.value
tenant.lockedmem.usage
tenant.lockedmem.value
tenant.memory_cap.rss
tenant.memory_cap.swap
tenant.nprocs.usage
tenant.nprocs.value
tenant.physicalmem.usage
tenant.physicalmem.value
tenant.swapresv.usage
tenant.swapresv.value
```
