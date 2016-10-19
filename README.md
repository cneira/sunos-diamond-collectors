# SunOS Diamond Collectors [![Code Climate](https://codeclimate.com/github/snltd/sunos-diamond-collectors/badges/gpa.svg)](https://codeclimate.com/github/snltd/sunos-diamond-collectors)

Additional SunOS- (i.e. Solaris- and Illumos-) specific collectors
for [the Diamond metrics collection
daemon](https://github.com/python-diamond/Diamond).

Diamond is great, but it has very poor support for Solaris and
SmartOS. This repo holds additional collectors suited to those
platforms. I intend to cover system (global zone) collection and a
subset of collectors for when you are a guest in, for example, the
JPC.

My target endpoint is [Wavefront](https://www.wavefront.com) using
TSDB, though that ought not to matter.

## Dependencies

Most of the metrics come from [the Solaris kstat
interface](https://docs.oracle.com/cd/E18752_01/html/816-5166/kstat-1m.html),
and are accessed by [a third party
module](https://github.com/pyhedgehog/kstat.git). That needs to be
checked out somewhere in your Python path.

## Supported Platforms

As of right now these are being developed and tested on x86 Solaris
11.3. They *will* work with SmartOS at some point, but maybe not
right now.

## Zoning

At the moment I'm concentrating on a system view: that is, the state
of the whole host as seen from the global zone. Local zones have
different views and different needs, and working out how to
elegantly address that is an interesting part of this project.

## Development

I deploy this by building a package which installs in
`/opt/diamond`, containing a minimal Python build, with Diamond and
its dependencies built in.  (This is because otherwise you need a C
compiler to `pip install diamond`, and I'm old-fashioned enough that
I don't have C compilers where I don't need to have them.) So, you
may have to tweak your `PYTHONPATH` or `sys.path` to include things
which are specific to my environment.

A test config for Diamond is supplied as `diamond-test.conf`, and
there's a little wrapper script `run.sh` which fires up a test
instance.

Diamond has an "archive mode" which is excellent for testing new
collectors. The sample config in this repo writes a line to
`/var/tmp/diamond_archive.log` whenever a metric is generated.

## Tests

I'm trying to cover everything with tests. Methods have unit tests
wherever they can, and collectors have functional tests built
following patterns in the proper Diamond repo.

To run the tests use the top-level `test.py` script. This is copied
from the Diamond repo, and hacked about until it worked. Because of
the strong dependency on the `kstat` module, the tests will only
work on a Solarish system.
