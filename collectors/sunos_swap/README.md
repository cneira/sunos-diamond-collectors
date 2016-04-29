# SunOS Swap

A very rudimentary collector which runs Solaris's `/usr/sbin/swap`
command and turns the output into metrics.

Output is in bytes, though `swap` natively reports in kilobytes.

This collector may be replaced by something more sophisticated.

## Metrics

```
swap.reserved
swap.available
swap.used
swap.allocated
```
