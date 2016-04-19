# SunOS Diamond Collectors

Additional SunOS- (i.e. Solaris- and Illumos-) specific collectors
for [the Diamond metrics collection
daemon](https://github.com/python-diamond/Diamond).

## Dependencies

Most of the metrics come from [the Solaris kstat
interface](https://docs.oracle.com/cd/E18752_01/html/816-5166/kstat-1m.html),
and are accessed by [a third party
module](https://github.com/pyhedgehog/kstat.git). That needs to be
checked out somewhere in your Python path.

## Development

A test config for Diamond is supplied. Run

```bash
$ diamond -f --skip-pidfile -c ./diamond-test.conf
```

Diamond has an "archive mode" which is excellent for testing new
collectors. The sample config in this repo writes a line to
`/var/tmp/diamond_archive.log` whenever a metric is generated.
