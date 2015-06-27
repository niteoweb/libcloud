#Zonomi DNSDriver
import ipdb
from libcloud.common.zonomi import ZonomiConnection, ZonomiResponse
from libcloud.dns.base import DNSDriver, Zone
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

    def _to_zone(self, item):
        zone = Zone(id=item['name'], domain=item['name'], type=item['type'],
                driver=self, extra={}, ttl=None)

        return zone

    def _to_zones(self, items):
        zones = []
        for item in items:
            zones.append(self._to_zone(item))

        return zones

    def list_zones(self):
        action = '/app/dns/dyndns.jsp?'
        params = {'action':'QUERYZONES', 'api_key':self.key}
        response, errors = self.connection.request(action=action,
                params=params).parse_body()

        zones = self._to_zones(response)
        zone = zones[0]

        return zone
