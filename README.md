# Services Test Manager

### Prerequisites

The following packages are needed to run stm:
- vlan
- bridge-utils
- python-pip
- python-pycurl
- python-libtorrent

The following python libraries are needed (install via pip):
- pyping
- dnspython
- pyroute2
- py-zabbix
- simplejson
- configparser

For build .deb package exec:
`
cp -r sensor sensor.deb/usr/local/lib/python2.7/dist-packages/
cp sensors sensor.deb/usr/local/sbin/
md5deep -r sensor.deb/etc > sensor.deb/DEBIAN/md5sums
md5deep -r sensor.deb/usr >> sensor.deb/DEBIAN/md5sums
fakeroot dpkg-deb --build sensor.deb
mv sensor.deb.deb sensor_<version>_all.deb
`
