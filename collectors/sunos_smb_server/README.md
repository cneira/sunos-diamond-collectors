# SMB Server collector

Uses the `kstat` interface to get SMBv2 server statistics. The raw
`kstat` counter values are used: the collector itself *does not*
compute rates or deltas. This should be done by your graphing
software.

## Options

* **`fields`**: In addition to Diamonds `metrics_whitelist` and
  `metrics_blacklist` configuration, you can use the `fields` variable
  to supply a filter list of fields which you are interested in.  A
  metric will only be published if its name is an element of that array.

By default all available `smbsrv` metrics are collected.

### Examples

## Statistics

## Bugs and Caveats

The kstat values are reported "raw": that is `crtime` and `snaptime` are
not used to calculate differentials. Your graphing software should
calculate rates, but they will not be as accurate as if they were
calculated from the high-resolution kstat times.

## Metric Paths

The following metrics are available in Solaris 11.3. YMMV depending on
your distribution and release.

```
smbsrv:Smb2Cancel
smbsrv:Smb2ChangeNotify
smbsrv:Smb2Close
smbsrv:Smb2Create
smbsrv:Smb2Echo
smbsrv:Smb2Flush
smbsrv:Smb2Ioctl
smbsrv:Smb2Lock
smbsrv:Smb2Logoff
smbsrv:Smb2Negotiate
smbsrv:Smb2OplockBreak
smbsrv:Smb2QueryDirectory
smbsrv:Smb2QueryInfo
smbsrv:Smb2Read
smbsrv:Smb2SessionSetup
smbsrv:Smb2SetInfo
smbsrv:Smb2TreeConnect
smbsrv:Smb2TreeDisconnect
smbsrv:Smb2Write
```
