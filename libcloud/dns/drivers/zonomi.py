#Zonomi DNSDriver
import ipdb
from libcloud.common.zonomi import ZonomiConnection, ZonomiResponse
from libcloud.dns.base import DNSDriver, Zone, Record
from libcloud.dns.types import ZoneDoesNotExistError, ZoneAlreadyExistsError
from libcloud.dns.types import RecordAlreadyExistsError
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

    def _to_record(self, item, zone):
        """
        :param item: `dict`
        :param item: contains information about a record
        such as id, name, data, type and extra info.
        """
        extra = {'ttl':item.get('ttl')}
        record = Record(id=item['name'], name=item['name'], data=item['content'],
             type=item['type'], zone=zone, driver=self, extra=extra)

        return record

    def _to_records(self, items, zone):
        records = []
        for item in items:
            records.append(self._to_record(item, zone))

        return records

    def list_zones(self):
        action = '/app/dns/dyndns.jsp?'
        params = {'action':'QUERYZONES', 'api_key':self.key}
        response, errors = self.connection.request(action=action,
                params=params).parse_body()

        zones = self._to_zones(response)

        return zones

    def get_zone(self, zone_id):
        zone = None
        zones = self.list_zones()
        for z in zones:
            if z.id == zone_id:
                zone = z

        if zone is None:
            raise ZoneDoesNotExistError(zone_id=zone_id, driver=self, value='')

        return zone

    def create_zone(self, zone_id):
        action = '/app/dns/addzone.jsp?'
        params = {'name':zone_id}
        response, errors = self.connection.request(action=action,
                params=params).parse_body()


        if len(errors) != 0 and 'ERROR: This zone is already in your zone list.' in errors:
            raise ZoneAlreadyExistsError(zone_id=zone_id, driver=self,
                    value='')

        zone = Zone(id=zone_id, domain=zone_id, type='NATIVE', ttl=None,
                driver=self, extra={})

        return zone

    def delete_zone(self, zone):

        action = '/app/dns/dyndns.jsp?'
        params = {'action':'DELETEZONE', 'name':zone.id}
        response, errors = self.connection.request(action=action,
                params=params).parse_body()
        #ipdb.set_trace()
        if len(errors) != 0 and 'ERROR: No zone found for %s' % (zone.id)in errors:
                    raise ZoneDoesNotExistError(zone_id=zone.id, driver=self,
                            value='')

        return 'DELETED' in response

    def list_records(self, zone):
        action = '/app/dns/dyndns.jsp?'
        params = {'action':'QUERY', 'name':'**.'+ zone.id}
        response, errors = self.connection.request(action=action, params=
                params).parse_body()

        if len(errors) != 0 and 'ERROR: No zone found for %s' % zone.id in errors:
            raise ZoneDoesNotExistError(zone_id=zone.id, driver=self,
                    value='')

        records = self._to_records(response, zone)

        return records

    def get_record(self, record_id, zone_id):
        pass

    def delete_record(self, record):
        """
        Use this method to delete a record.
        """
        action = '/app/dns/dyndns.jsp?'
        params = {'action':'DELETE', 'name':record.name, 'type':record.type}
        response, errors = self.connection.request(action=action, params=
                params).parse_body()

        #ipdb.set_trace()
        return 'DELETED' in response

    def create_record(self, name, zone, type, data, extra):
        """
        Use this to create MX and A records.
        """

        action = '/app/dns/dyndns.jsp?'
        params = {'action':'SET', 'name':name, 'value':data,
                'type':type}

        if type == 'MX' and extra is not None:
            params['prio'] = extra.get('prio')
        #ipdb.set_trace()
        response, errors = self.connection.request(action=action,
                params=params).parse_body()
        #ipdb.set_trace()
        if len(errors) != 0 and 'ERROR: No zone found for %s' % name in errors:
                raise ZoneDoesNotExistError(zone_id=zone.id, driver=self,
                                value='')
        #we determine if an A or MX record already exists
        #by looking at the response
        #check the key 'skipped' in the response
        #if this key is present, it means record
        #already exists
        #check if record already exists, if this is True
        #then raise RecordAlreadyExistsError
        if len(response) != 0 and response[0].get('skipped') == 'unchanged':
            raise RecordAlreadyExistsError(record_id=name, driver=self, value='')

        if 'DELETED' in response:
            for el in response[:2]:
                if el.get('content') == data:
                    response = [el]
        #ipdb.set_trace()
        records = self._to_records(response, zone=zone)
        #ipdb.set_trace()
        return records[0]

