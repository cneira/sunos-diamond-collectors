# NFS Client Collector

Uses the `kstat` interface to get NFS client statistics. The raw `kstat`
counter values are used: the collector itself *does not* compute rates
or deltas. This should be done by your graphing software.

## Options

* **`nfs_vers`** : You can select the NFS client version(s) to collect
  through the `nfs_vers` option. It should be an array of integers, and
  currently valid values are `2` to `4` inclusive.

* **`fields`**: In addition to Diamonds `metrics_whitelist` and
  `metrics_blacklist` configuration, you can use the `fields` variable
  to supply a filter list of fields which you are interested in.  A
  metric will only be published if its name is an element of that array.

  By default all available metrics are collected for NFSv3 and NFSv4,
  hilst NFSv2 is disregarded.

To black/whitelist metrics, you must supply the version. For instance:

```
metrics_whitelist: v4.read
```

### Examples

Collect `read`, `write` and `remove` statistics for NFS v3 and v4.

```
[[ SunOSNFSClientCollector ]]
enabled = True
nfs_vers = 3,4
fields = read,write,remove
```

Collect all NFS v4 client statistics, ignoring versions 2 and 3.

```
[[ SunOSNFSClientCollector ]]
enabled = True
nfs_vers = 4
```

## Bugs and Caveats

The kstat values are reported "raw": that is `crtime` and `snaptime` are
not used to calculate differentials. Your graphing software should
calculate rates, but they will not be as accurate as if they were
calculated from the high-resolution kstat times.

## Metric Paths

The following metrics are available in Solaris 11.3. YMMV depending on
your distribution and release.

```
nfs.client.v2.create
nfs.client.v2.getattr
nfs.client.v2.link
nfs.client.v2.lookup
nfs.client.v2.mkdir
nfs.client.v2.null
nfs.client.v2.read
nfs.client.v2.readdir
nfs.client.v2.readlink
nfs.client.v2.remove
nfs.client.v2.rename
nfs.client.v2.rmdir
nfs.client.v2.root
nfs.client.v2.setattr
nfs.client.v2.statfs
nfs.client.v2.symlink
nfs.client.v2.wrcache
nfs.client.v2.write
nfs.client.v3.access
nfs.client.v3.commit
nfs.client.v3.create
nfs.client.v3.fsinfo
nfs.client.v3.fsstat
nfs.client.v3.getattr
nfs.client.v3.link
nfs.client.v3.lookup
nfs.client.v3.mkdir
nfs.client.v3.mknod
nfs.client.v3.null
nfs.client.v3.pathconf
nfs.client.v3.read
nfs.client.v3.readdir
nfs.client.v3.readdirplus
nfs.client.v3.readlink
nfs.client.v3.remove
nfs.client.v3.rename
nfs.client.v3.rmdir
nfs.client.v3.setattr
nfs.client.v3.symlink
nfs.client.v3.write
nfs.client.v4.access
nfs.client.v4.close
nfs.client.v4.commit
nfs.client.v4.compound
nfs.client.v4.create
nfs.client.v4.delegpurge
nfs.client.v4.delegreturn
nfs.client.v4.getattr
nfs.client.v4.getfh
nfs.client.v4.link
nfs.client.v4.lock
nfs.client.v4.lockt
nfs.client.v4.locku
nfs.client.v4.lookup
nfs.client.v4.lookupp
nfs.client.v4.null
nfs.client.v4.nverify
nfs.client.v4.open
nfs.client.v4.open_confirm
nfs.client.v4.open_downgrade
nfs.client.v4.openattr
nfs.client.v4.putfh
nfs.client.v4.putpubfh
nfs.client.v4.putrootfh
nfs.client.v4.read
nfs.client.v4.readdir
nfs.client.v4.readlink
nfs.client.v4.remove
nfs.client.v4.rename
nfs.client.v4.renew
nfs.client.v4.reserved
nfs.client.v4.restorefh
nfs.client.v4.savefh
nfs.client.v4.secinfo
nfs.client.v4.setattr
nfs.client.v4.setclientid
nfs.client.v4.setclientid_confirm
nfs.client.v4.verify
nfs.client.v4.write
```
