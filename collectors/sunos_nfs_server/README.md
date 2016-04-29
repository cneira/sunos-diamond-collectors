# NFS Server Collector

Uses the `kstat` interface to get NFS server statistics. The raw
`kstat` counter values are used: the collector itself *does not*
compute rates or deltas. This should be done by your graphing
software.

## Options

You can select the NFS server version(s) to collect through the
`vers` option. It should be an array of integers from `2` to `4`

You can use the `fields` variable to supply a filter list of fields
which you are interested in.  A metric will only be published if its
name is an element of that array.

By default all available metrics are collected for NFSv3 and NFSv4,
whilst NFSv2 is disregarded.

### Examples

Collect `read`, `write` and `remove` statistics for NFS v3 and v4.


```
[[ SunOSNFSServerCollector ]]
enabled = True
nfs_vers = 3,4
fields = read,write,remove
```

Collect all NFS v4 server statistics, ignoring versions 2 and 3.

```
[[ SunOSNFSServerCollector ]]
enabled = True
nfs_vers = 4
```


## Metric Paths

```
nfs.server.v2.create
nfs.server.v2.getattr
nfs.server.v2.link
nfs.server.v2.lookup
nfs.server.v2.mkdir
nfs.server.v2.null
nfs.server.v2.read
nfs.server.v2.readdir
nfs.server.v2.readlink
nfs.server.v2.remove
nfs.server.v2.rename
nfs.server.v2.rmdir
nfs.server.v2.root
nfs.server.v2.setattr
nfs.server.v2.statfs
nfs.server.v2.symlink
nfs.server.v2.wrcache
nfs.server.v2.write
nfs.server.v3.access
nfs.server.v3.commit
nfs.server.v3.create
nfs.server.v3.fsinfo
nfs.server.v3.fsstat
nfs.server.v3.getattr
nfs.server.v3.link
nfs.server.v3.lookup
nfs.server.v3.mkdir
nfs.server.v3.mknod
nfs.server.v3.null
nfs.server.v3.pathconf
nfs.server.v3.read
nfs.server.v3.readdir
nfs.server.v3.readdirplus
nfs.server.v3.readlink
nfs.server.v3.remove
nfs.server.v3.rename
nfs.server.v3.rmdir
nfs.server.v3.setattr
nfs.server.v3.symlink
nfs.server.v3.write
nfs.server.v4.access
nfs.server.v4.close
nfs.server.v4.commit
nfs.server.v4.compound
nfs.server.v4.create
nfs.server.v4.delegpurge
nfs.server.v4.delegreturn
nfs.server.v4.getattr
nfs.server.v4.getfh
nfs.server.v4.illegal
nfs.server.v4.link
nfs.server.v4.lock
nfs.server.v4.lockt
nfs.server.v4.locku
nfs.server.v4.lookup
nfs.server.v4.lookupp
nfs.server.v4.null
nfs.server.v4.nverify
nfs.server.v4.open
nfs.server.v4.open_confirm
nfs.server.v4.open_downgrade
nfs.server.v4.openattr
nfs.server.v4.putfh
nfs.server.v4.putpubfh
nfs.server.v4.putrootfh
nfs.server.v4.read
nfs.server.v4.readdir
nfs.server.v4.readlink
nfs.server.v4.release_lockowner
nfs.server.v4.remove
nfs.server.v4.rename
nfs.server.v4.renew
nfs.server.v4.reserved
nfs.server.v4.restorefh
nfs.server.v4.savefh
nfs.server.v4.secinfo
nfs.server.v4.setattr
nfs.server.v4.setclientid
nfs.server.v4.setclientid_confirm
nfs.server.v4.verify
nfs.server.v4.write
```
