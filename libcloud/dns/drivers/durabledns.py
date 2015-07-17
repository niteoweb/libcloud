import ipdb
from libcloud.dns.types import Provider, RecordType
from libcloud.dns.base import Record, Zone
from libcloud.common.durabledns import DurableConnection, DurableResponse
from libcloud.dns.base import DNSDriver


__all__ = [
        'DurableDNSResponse',
        'DurableDNSConnection',
        'DurableDNSDriver'
    ]

class DurableDNSResponse(DurableResponse):
    pass


class DurableDNSConnection(DurableConnection):
    responseCls = DurableDNSResponse


class DurableDNSDriver(DNSDriver):
    type = Provider.DURABLEDNS
    name = 'DurableDNS'
    website = 'https://durabledns.com'
    connectionCls = DurableDNSConnection

    RECORD_TYPE_MAP = {
            RecordType.NS:'NS',
            RecordType.MX:'MX',
            RecordType.A:'A',
            RecordType.AAAA:'AAAA',
            RecordType.CNAME:'CNAME',
            RecordType.TXT:'TXT',
            RecordType.SRV:'SRV'
        }

    def _to_zone(self, item):
        extra = {}
        zone = Zone(id=item['id'], type=item['type'], domain=item['id'],
                ttl=item['ttl'],driver=self, extra=extra)

        return zone

    def _to_zones(self, items):
        zones = []
        for item in items:
            zones.append(self._to_zone(item))

        return zones

    def _to_record(self, item, zone=None):
        extra = {}
        record = Record(id=item[''], type=item[''], zone=zone, name=item[''],
                data=item[''], driver=self, extra=extra)

        return record

    def _to_records(self, items, zone=None):
        records = []
        for item in items:
            records.append(self._to_record(item, zone))

        return records

    def list_zones(self):
        zones = []
        data =  """
        <soap:Body xmlns:m="https://durabledns.com/services/dns/listZones">
            <urn:listZoneswsdl:listZones>
                <urn:listZoneswsdl:apiuser>%s</urn:listZoneswsdl:apiuser>
                <urn:listZoneswsdl:apikey>%s</urn:listZoneswsdl:apikey>
            </urn:listZoneswsdl:listZones>
        </soap:Body>
            """  % (self.key, self.secret)

        action = '/services/dns/listZones.php?'
        params = {}
        headers = {"SOAPAction":"urn:listZoneswsdl#listZones"}
        objects, errors = self.connection.request(action=action, params=params,
                data=data, method="POST", headers=headers).parse_body()
        zones.append(self._to_zones(objects))

        return zones[0]

    def get_zone(self, zone_id):
        data = """
        <soap:Body xmlns:m="https://durabledns.com/services/dns/getZone">
            <urn:getZonewsdl:getZone>
                <urn:getZonewsdl:apiuser>%s</urn:getZonewsdl:apiuser>
                <urn:getZonewsdl:apikey>%s</urn:getZonewsdl:apikey>
                <urn:getZonewsdl:zonename>%s</urn:getZonewsdl:zonename>
            </urn:getZonewsdl:getZone>
        </soap:Body>
               """ % (self.key, self.secret, zone_id)
        #ipdb.set_trace()
        action = '/services/dns/getZone.php?'
        params = {}
        headers = {"SOAPAction":"urn:getZonewsdl#getZone"}
        objects, errors = self.connection.request(action=action, params=params,
                data=data, method="POST", headers=headers).parse_body()
        zones = self._to_zones(objects)

        return zones[0]

    def delete_zone(self, zone):
        pass

    def create_zone(self, domain, type=None, ttl=None, extra=None):
        pass

    def list_records(self, zone):
        pass

    def get_record(self, zone_id, record_id):
        pass

    def delete_record(self, record):
        pass

    def create_record(self, name, zone, type, data, extra=None):
        pass
