# SunOS Memory

The SunOS kernels provide us with an almost overwhelming view of the
machine's virtual memory usage. This collector
presents information from various sources, which you can enable or
disable as you see fit.

## Options

* **`vminfo_fields`**: tells the collector to use the
  `unix:0:vminfo` kstat to produce a number of metrics. Setting this
  value to `__all__` presents whatever is found (so will reflect
  future changes), and `__none__` turns them all off. These are
  rates calculated using Diamond's internal
  [derivative()](https://github.com/python-diamond/Diamond/blob/master/src/diamond/collector.py#L425-L462)
  function, so it lacks the extreme accuracy which could be obtained
  by using the kstat `snaptime` in the calculation. I think it's
  good enough. Many of these values overlap with those collected in
  `swap_fields`, but with a [one-second
  lag](https://github.com/illumos/illumos-gate/blob/5a4ef21a18dfdc65328821a265582d03e85a97c9/usr/src/uts/common/sys/sysinfo.h#L179-L186).
* **`swap_fields`**: setting this to anything other than `__none__`
  makes the collector parse the output of the `/usr/sbin/swap`
  command. All fields are converted from kB to bytes. You can select
  the fields you want by name, or use the magic `__all__` value to
  get the lot. This largely duplicates the kstat information
  controllable through `vminfo_fields`.
* **`swapping_fields`**:
  the collector can examine the `cpu::vm` kstats and pull out anything
  ending `swapin` or `swapout`. As the kstat name suggests, there is
  one of these counters per-cpu, but I see few cases where a user
  might want that level of detail. (Perhaps if you pin applications
  to processors?) By default the metrics are aggregated across all
  CPUs. If you want them per-CPU, set `per_cpu_swapping` to `True`.
  Metrics can be selected by giving their names in a list, or by
  using the usual `__all__` or `__none__` magic values.
* **`per_cpu_swapping`**: see above
* **`paging_fields`**: as for `swapping fields`, but on anything
  matching `pgin` or `pgout`.
* **`per_cpu_paging`**: as for `per_cpu_swapping`, but applies to
  `paging_fields` metrics.

## Metrics

On a Solaris 11.3 system, with `per_cpu_paging` and
`per_cpu_swapping` disabled.

```
memory.arc_size
memory.kernel
memory.pages.free
memory.paging.anonpgin
memory.paging.anonpgout
memory.paging.execpgin
memory.paging.execpgout
memory.paging.fspgin
memory.paging.fspgout
memory.paging.pgin
memory.paging.pgout
memory.paging.pgpgin
memory.paging.pgpgout
memory.swap.allocated
memory.swap.available
memory.swap.reserved
memory.swap.used
memory.swapping.pgswapin
memory.swapping.pgswapout
memory.swapping.swapin
memory.swapping.swapout
memory.vminfo.freemem
memory.vminfo.swap_alloc
memory.vminfo.swap_avail
memory.vminfo.swap_free
memory.vminfo.swap_resv
```

The same system, with per-CPU statistics turned on. The host has
four processors.

```
memory.arc_size
memory.kernel
memory.pages.free
memory.paging.cpu.0.anonpgin
memory.paging.cpu.0.anonpgout
memory.paging.cpu.0.execpgin
memory.paging.cpu.0.execpgout
memory.paging.cpu.0.fspgin
memory.paging.cpu.0.fspgout
memory.paging.cpu.0.pgin
memory.paging.cpu.0.pgout
memory.paging.cpu.0.pgpgin
memory.paging.cpu.0.pgpgout
memory.paging.cpu.1.anonpgin
memory.paging.cpu.1.anonpgout
memory.paging.cpu.1.execpgin
memory.paging.cpu.1.execpgout
memory.paging.cpu.1.fspgin
memory.paging.cpu.1.fspgout
memory.paging.cpu.1.pgin
memory.paging.cpu.1.pgout
memory.paging.cpu.1.pgpgin
memory.paging.cpu.1.pgpgout
memory.paging.cpu.2.anonpgin
memory.paging.cpu.2.anonpgout
memory.paging.cpu.2.execpgin
memory.paging.cpu.2.execpgout
memory.paging.cpu.2.fspgin
memory.paging.cpu.2.fspgout
memory.paging.cpu.2.pgin
memory.paging.cpu.2.pgout
memory.paging.cpu.2.pgpgin
memory.paging.cpu.2.pgpgout
memory.paging.cpu.3.anonpgin
memory.paging.cpu.3.anonpgout
memory.paging.cpu.3.execpgin
memory.paging.cpu.3.execpgout
memory.paging.cpu.3.fspgin
memory.paging.cpu.3.fspgout
memory.paging.cpu.3.pgin
memory.paging.cpu.3.pgout
memory.paging.cpu.3.pgpgin
memory.paging.cpu.3.pgpgout
memory.swap.allocated
memory.swap.available
memory.swap.reserved
memory.swap.used
memory.swapping.cpu.0.pgswapin
memory.swapping.cpu.0.pgswapout
memory.swapping.cpu.0.swapin
memory.swapping.cpu.0.swapout
memory.swapping.cpu.1.pgswapin
memory.swapping.cpu.1.pgswapout
memory.swapping.cpu.1.swapin
memory.swapping.cpu.1.swapout
memory.swapping.cpu.2.pgswapin
memory.swapping.cpu.2.pgswapout
memory.swapping.cpu.2.swapin
memory.swapping.cpu.2.swapout
memory.swapping.cpu.3.pgswapin
memory.swapping.cpu.3.pgswapout
memory.swapping.cpu.3.swapin
memory.swapping.cpu.3.swapout
memory.vminfo.freemem
memory.vminfo.swap_alloc
memory.vminfo.swap_avail
memory.vminfo.swap_free
memory.vminfo.swap_resv
```
