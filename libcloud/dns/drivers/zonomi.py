#Zonomi DNSDriver
import ipdb
from libcloud.common.zonomi import ZonomiConnection, ZonomiResponse
from libcloud.dns.base import DNSDriver
from libcloud.dns.types import Provider
from libcloud.utils.py3 import urllib2

__all__  = [
        'ZonomiDNSDriver',
    ]

class ZonomiDNSResponse(ZonomiResponse):
    pass


class ZonomiDNSConnection(ZonomiConnection):
    responseCls = ZonomiDNSResponse


class ZonomiDNSDriver(DNSDriver):
    type = Provider.ZONOMI
    name = 'Zonomi DNS'
    website = 'https://zonomi.com'
    connectionCls = ZonomiDNSConnection


    def list_zones(self):
        url = '%s/dns/dyndns.jsp?action=QUERYZONES&api_key=%s' % (self.connection.host, self.key)
        req = urllib2.Request(url)
        response = urllib2.urlopen(req).read()
        ipdb.set_trace()
        return response
