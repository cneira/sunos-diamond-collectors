# SunOS Proc Collector

This collector largely mimics `prstat(1)`. It will present the top
`n` processes, by memory or CPU usage. Like `prstat(1)`, short-lived
processes which come and go between collections will not be
reported, so it can not give an accurate reflection of spiky
workloads. I still find it useful, particularly for watching the
memory usage of long-running processes.

Metrics are drawn from the `psinfo` and `usage` structures described
in [the `proc(4)` man page](https://illumos.org/man/4/proc). Fields
can be anything defined therein.

## Options

* **`as_nsec_delta`**: by default, the time spent in each CPU state
  is a counter. Using this list you can have any or all state
  described as "time spent over last interval". This gives you an
  accurate *rate* of CPU usage for each state, derived from
  the kstat `snaptime`. Default value is `__all__`, a magic value
  which means all `cpu_nsec_` values will be converted to rates. If
  this value is false, or undefined, the values will be sent as
  counters. If this option is truthy, the raw `cpu_nsec_` values
  will *not* be published. Describe fields as `nsec_user`,
  `nsec_idle` etc. Because this is a delta, the first run of the
  collector will produce no data.
* **`as_pc_delta`**: Lets you define a list of CPU states to sent as
  %age usitilisation over each interval. This is the way of showing
  CPU usage that most people are familiar with. If you don't want
  these, set the value to the magic value `__none__`. Because this
  is a delta, the first run of the collector will produce no data.
* **`fields`**: a list of fields you want to collect. These are the
  names of the fields in the `procfs`
  [`psinfo`](https://github.com/illumos/illumos-gate/blob/master/usr/src/uts/common/sys/procfs.h#L275-L315)
  and
  [`usage`](https://github.com/illumos/illumos-gate/blob/master/usr/src/uts/common/sys/procfs.h#L441-L472)
  structures. Most fields are passed through unaltered. These are
  the exceptions:

  * `pr_rssize` and `pr_size` are multiplied by 1024 to turn them
    into bytes.
  * `pr_pctmem` and `pr_pctcpu` are turned into "proper" percentage
    values.

### Examples

Only collect the rate of CPU usage, in percentages.

```
[[ SunOSCPUCollector ]]
enabled = True
as_nsec_delta = __none__
as_pc_delta = __all__
fields = __none__
```

Only collect the percentage of time spent in user or kernel states:

```
[[ SunOSCPUCollector ]]
enabled = True
as_nsec_delta = False
as_pc_delta = pc.kernel,pc.user
fields = __none__
```

Send through all raw kstats.

```
[[ SunOSCPUCollector ]]
enabled = True
as_nsec_delta = False
as_pc_delta = False
fields = __all__
```

## Statistics

Collecting all information, including derived metrics on a 4-core i7
system takes around 70ms.

## Metric Paths
