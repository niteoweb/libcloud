import ipdb
from libcloud.utils.py3 import httplib
from libcloud.dns.types import Provider, RecordType
from libcloud.dns.base import Record, Zone
from libcloud.common.durabledns import DurableConnection, DurableResponse
from libcloud.dns.base import DNSDriver
from libcloud.dns.types import ZoneDoesNotExistError, ZoneAlreadyExistsError
from libcloud.dns.base import Zone


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
        #ipdb.set_trace()
        #check errors list
        #if errors list not empty and 'Zone does not exist' in it
        #raise ZoneDoesNotExistError
        if len(errors) != 0 and 'Zone does not exist' in errors[0]['ERRORMESSAGE']:
            raise ZoneDoesNotExistError(zone_id=zone_id, driver=self, value='')

        zones = self._to_zones(objects)

        return zones[0]

    def delete_zone(self, zone):
        data = """
            <soap:Body xmlns:m="https://durabledns.com/dns/services/deleteZone">
                <urn:deleteZonewsdl:deleteZone>
                    <urn:deleteZonewsdl:apiuser>%s</urn:deleteZonewsdl:apiuser>
                    <urn:deleteZonewsdl:apikey>%s</urn:deleteZonewsdl:apikey>
                    <urn:deleteZonewsdl:zonename>%s</urn:deleteZonewsdl:zonename>
                </urn:deleteZonewsdl:deleteZone>
            </soap:Body>
        """   % (self.key, self.secret, zone.id)
        action = '/services/dns/deleteZone.php?'
        params = {}
        headers = {"SOAPAction":"urn:deleteZonewsdl#deleteZone"}
        response = self.connection.request(action=action, params=params, data=
                data, method="POST", headers=headers)
        ipdb.set_trace()
        objects, errors = response.parse_body()
        if len(errors) != 0 and 'Zone does not exist' in errors[0]['ERRORMESSAGE']:
            raise ZoneDoesNotExistError(zone_id=zone.id, driver=self, value='')

        return response.status in [httplib.OK]

    def create_zone(self, domain, type=None, ttl=None, extra=None):
        zone = None
        data = """
            <soap:Body xmlns:m="https://durabledns.com/dns/services/createZone">
                <urn:createZonewsdl:createZone>
                    <urn:createZonewsdl:apiuser>%s</urn:createZonewsdl:apiuser>
                    <urn:createZonewsdl:apikey>%s</urn:createZonewsdl:apikey>
                    <urn:createZonewsdl:zonename>%s</urn:createZonewsdl:zonename>
                    <urn:createZonewsdl:ns>%s</urn:createZonewsdl:ns>
                    <urn:createZonewsdl:mbox>%s</urn:createZonewsdl:mbox>
                    <urn:createZonewsdl:refresh>%d</urn:createZonewsdl:refresh>
                    <urn:createZonewsdl:retry>%d</urn:createZonewsdl:retry>
                    <urn:createZonewsdl:expire>%d</urn:createZonewsdl:expire>
                    <urn:createZonewsdl:minimum>%d</urn:createZonewsdl:minimum>
                    <urn:createZonewsdl:ttl>%d</urn:createZonewsdl:ttl>
                    <urn:createZonewsdl:xfer>%s</urn:createZonewsdl:xfer>
                    <urn:createZonewsdl:update_acl>%s</urn:createZonewsdl:update_acl>
                </urn:createZonewsdl:createZone>
            </soap:Body>""" % (self.key, self.secret, domain, extra['ns'], extra['mbox'],
                    extra['refresh'], extra['retry'], extra['expire'],extra['minimum'],
                     ttl, extra['xfer'], extra['update_acl']
                    )
        action = '/services/dns/createZone.php?'
        params = {}
        headers = {"SOAPAction":"urn:createZonewsdl#createZone"}
        #make request to server
        response = self.connection.request(action=action, params=params, data=data,
                    method="POST", headers=headers)
        objects, errors = response.parse_body()
        ipdb.set_trace()
        #check for error Zone already exists in errors
        #if present, raise ZoneAlreadyExistsError
        if len(errors) != 0 and 'Zone Already Exist'in errors[0]['ERRORMESSAGE']:
            raise ZoneAlreadyExistsError(zone_id=domain, driver=self, value='')
        if response.status == 200:
            zone = Zone(id=domain, type=type, ttl=ttl, driver=self, domain=domain,
                    extra=extra)

        return zone

    def list_records(self, zone):
        pass

    def get_record(self, zone_id, record_id):
        pass

    def delete_record(self, record):
        pass

    def create_record(self, name, zone, type, data, extra=None):
        pass
