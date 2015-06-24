import ipdb
import json
from libcloud.common.liquidweb import LiquidWebResponse, LiquidWebConnection
from libcloud.dns.base import DNSDriver, Zone
from libcloud.dns.types import Provider
from libcloud.dns.types import ZoneDoesNotExistError

__all__ = [
        'LiquidWebDNSDriver'
        ]

class LiquidWebDNSResponse(LiquidWebResponse):
    pass


class LiquidWebDNSConnection(LiquidWebConnection):
    responseCls = LiquidWebDNSResponse


class LiquidWebDNSDriver(DNSDriver):
    type = Provider.LIQUIDWEB
    name = 'Liquidweb DNS'
    website = 'https://www.liquidweb.com'
    connectionCls = LiquidWebDNSConnection

    def _to_zone(self, item):
        extra = None
        zone = Zone(domain=item['name'], id=item['id'], type=item['type'],
                ttl=None, driver=self, extra=extra)

        return zone

    def _to_zones(self, items):
        zones = []
        for item in items:
            zones.append(self._to_zone(item))

        return zones

    def list_zones(self):
        action = '/v1/Network/DNS/Zone/list'
        response, errors = self.connection.request(action=action, method='POST').parse_body()

        zones = self._to_zones(response[0])

        return zones

    def get_zone(self, zone_id):
        action = '/v1/Network/DNS/Zone/details'
        data = json.dumps({'params':{'id':zone_id}})
        response, errors = self.connection.request(action=action, method='POST',
                    data=data).parse_body()

        if (len(errors) != 0 and errors[0]['ERRORMESSAGE'] ==
                            'LW::Exception::RecordNotFound'):
            raise ZoneDoesNotExistError(zone_id=zone_id, value='', driver=self)

        zones = self._to_zones(response)

        return zones[0]

    def delete_zone(self, zone):
        action = '/v1/Network/DNS/Zone/delete'
        data = json.dumps({'params':{'id':zone.id}})
        response, errors = self.connection.request(action=action, method='POST',
                data=data).parse_body()

        return zone.domain in response


