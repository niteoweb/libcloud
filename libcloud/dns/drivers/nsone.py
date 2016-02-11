import httplib

from libcloud.dns.base import DNSDriver, Zone
from libcloud.common.nsone import NsOneConnection, NsOneResponse
from libcloud.dns.types import Provider, ZoneDoesNotExistError


__all__ = [
    'NsOneDNSDriver'
]


class NsOneDNSResponse(NsOneResponse):
    pass


class NsOneDNSConnection(NsOneConnection):
    responseCls = NsOneDNSResponse


class NsOneDNSDriver(DNSDriver):
    name = 'NS1 DNS'
    website = 'https://ns1.com'
    type = Provider.NSONE
    connectionCls = NsOneDNSConnection

    def list_zones(self):
        action = '/v1/zones'
        response = self.connection.request(action=action, method='GET')
        zones = self._to_zones(items=response.parse_body())

        return zones

    def get_zone(self, zone_id):
        action = '/v1/zones/%s' % zone.domain
        pass

    def create_zone(self, domain, type='master', ttl=None, extra=None):
        pass

    def delete_zone(self, zone):
        action = '/v1/zones/%s' % zone.domain
        zones_list = self.list_zones()
        if not self.ex_zone_exists(zone_id=zone.id, zones_list=zones_list):
            raise ZoneDoesNotExistError(value='', driver=self, zone_id=zone.id)

        response = self.connection.request(action=action, method='DELETE')

        return response.status == httplib.OK

    def update_zone(self, zone, domain, type='master', ttl=None, extra=None):
        pass

    def list_records(self, zone):
        pass

    def get_record(self, zone_id, record_id):
        pass

    def delete_record(self, record):
        pass

    def create_record(self, name, zone, type, data, extra=None):
        pass

    def update_record(self, record, name, type, data, extra=None):
        pass

    def ex_zone_exists(self, zone_id, zones_list):
        """
        Function to check if a `Zone` object exists.
        :param zone_id: ID of the `Zone` object.
        :type zone_id: ``str``

        :param zones_list: A list containing `Zone` objects.
        :type zones_list: ``list``.

        :rtype: Returns `True` or `False`.
        """
        zone_ids = []
        for zone in zones_list:
            zone_ids.append(zone.id)

        return zone_id in zone_ids

    def _to_zone(self, item):
        common_attr = ['zone', 'id', 'type']
        extra = {}
        for key in item:
            if key not in common_attr:
                extra[key] = item.get(key)

        zone = Zone(domain=item['zone'], id=item['id'], type=item.get('type'), extra=extra, ttl=None,
                    driver=self)

        return zone

    def _to_zones(self, items):
        zones = []
        for item in items:
            zones.append(self._to_zone(item))

        return zones
