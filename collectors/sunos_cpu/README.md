# SunOS CPU Collector

Uses the `kstat` interface to get CPU usage IO statistics.

Solaris/Illumos CPU statistics are very detailed, going far beyond
the "percent sys/percent user" type thing that many people are
content with. The CPU sys kstats also provide information about
interrupts, mutexes, system calls, and all manner of other things

This collector is a little opinionated in how it presents some of
that information, and it gives you the option to easily filter out
the stuff you don't want. On boxes with many cores, huge amounts of
unnecessary metrics could be created.

Most metrics, in common with most other collectors in this package,
are passed straight through, as counters. If you wish to convert
them to rates at the other end, your graphing software should do it.

However, this collector is also able to express CPU usage as
nanoseconds spent in each state (some subset of `idle`, `user`,
`kernel`, `intr`, `dtrace` and `stolen`, depending on your kernel)
as a delta. This delta can also be used to calculate the more
familiar percentage breakdown, which it derives from the nanosecond
values. See the "options" section below on how to activate these
derived metrics.

Every core gets its own set of metrics.

The collector can also supply various `cpuinfo` metrics. These are
bundled together, and bundles can be turned on or off with the
`fields` parameter. (See below.) They provide mostly power usage
information: clock speed, C- and P-states.

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
* **`as_pc_delta`**: Lets you define a list of CPU states to send as
  %age usitilisation over each interval. This is the way of showing
  CPU usage that most people are familiar with. If you don't want
  these, set to the magic value `__none__`. Because this is a
  delta, the first run of the collector will produce no data.
* **`fields`**: a list of fields you want to collect. These are the
  names of the raw kstats, so refer to the [metric paths
  section](#metric-paths) below for a list of viable fields, or look
  at the output of `kstat cpu.<cpu_id>:sys`.

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

The following lists are from a Solaris 11.3 system. Illumos metrics
are slightly different.

This batch of metrics are derived.

```
cpu.<cpu_id>.nsec.idle
cpu.<cpu_id>.nsec.intr
cpu.<cpu_id>.nsec.kernel
cpu.<cpu_id>.nsec.stolen
cpu.<cpu_id>.nsec.user
cpu.<cpu_id>.pc.idle
cpu.<cpu_id>.pc.intr
cpu.<cpu_id>.pc.kernel
cpu.<cpu_id>.pc.stolen
cpu.<cpu_id>.pc.user
```

These are sent raw:

```
cpu.<cpu_id>.sys.bawrite
cpu.<cpu_id>.sys.bread
cpu.<cpu_id>.sys.bwrite
cpu.<cpu_id>.sys.canch
cpu.<cpu_id>.sys.cpu_load_intr
cpu.<cpu_id>.sys.cpu_ticks_idle
cpu.<cpu_id>.sys.cpu_ticks_kernel
cpu.<cpu_id>.sys.cpu_ticks_stolen
cpu.<cpu_id>.sys.cpu_ticks_user
cpu.<cpu_id>.sys.cpu_ticks_wait
cpu.<cpu_id>.sys.cpumigrate
cpu.<cpu_id>.sys.idlethread
cpu.<cpu_id>.sys.intr
cpu.<cpu_id>.sys.intrblk
cpu.<cpu_id>.sys.intrthread
cpu.<cpu_id>.sys.intrunpin
cpu.<cpu_id>.sys.inv_swtch
cpu.<cpu_id>.sys.iowait
cpu.<cpu_id>.sys.lread
cpu.<cpu_id>.sys.lwrite
cpu.<cpu_id>.sys.mdmint
cpu.<cpu_id>.sys.modload
cpu.<cpu_id>.sys.modunload
cpu.<cpu_id>.sys.msg
cpu.<cpu_id>.sys.mutex_adenters
cpu.<cpu_id>.sys.namei
cpu.<cpu_id>.sys.nthreads
cpu.<cpu_id>.sys.outch
cpu.<cpu_id>.sys.phread
cpu.<cpu_id>.sys.phwrite
cpu.<cpu_id>.sys.procovf
cpu.<cpu_id>.sys.pswitch
cpu.<cpu_id>.sys.rawch
cpu.<cpu_id>.sys.rcvint
cpu.<cpu_id>.sys.readch
cpu.<cpu_id>.sys.rw_rdfails
cpu.<cpu_id>.sys.rw_wrfails
cpu.<cpu_id>.sys.sema
cpu.<cpu_id>.sys.syscall
cpu.<cpu_id>.sys.sysexec
cpu.<cpu_id>.sys.sysfork
cpu.<cpu_id>.sys.sysread
cpu.<cpu_id>.sys.sysvfork
cpu.<cpu_id>.sys.syswrite
cpu.<cpu_id>.sys.trap
cpu.<cpu_id>.sys.ufsdirblk
cpu.<cpu_id>.sys.ufsiget
cpu.<cpu_id>.sys.ufsinopage
cpu.<cpu_id>.sys.ufsipage
cpu.<cpu_id>.sys.wait_ticks_io
cpu.<cpu_id>.sys.writech
cpu.<cpu_id>.sys.xcalls
cpu.<cpu_id>.sys.xmtint
```

Here are the `cpuinfo` bundles. The first is enabled or disabled
with the `speed` field.

```
cpu.<cpu_id>.cpuinfo.current_speed
cpu.global.clock_speed
```

The `state` bundle reports on CPU P- and C- states.

```
cpu.<cpu_id>.cpuinfo.current_cstate
cpu.<cpu_id>.cpuinfo.current_pstate
```

The number of vCPUs can also be sent. This can be useful in
calculating meaningful load across different sized hosts.

```
cpu.global.vcpus
```
