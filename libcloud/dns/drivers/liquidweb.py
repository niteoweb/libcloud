import ipdb
import json
from libcloud.common.liquidweb import LiquidWebResponse, LiquidWebConnection
from libcloud.dns.base import DNSDriver, Zone, Record
from libcloud.dns.types import Provider
from libcloud.dns.types import ZoneDoesNotExistError, ZoneAlreadyExistsError
from libcloud.dns.types import RecordDoesNotExistError, RecordAlreadyExistsError


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

    def _to_record(self, item, zone):
        extra = None
        record = Record(id=item['id'], name=item['name'], type=item['type'],
                data=item['rdata'], zone=zone, driver=self, extra=extra)

        return record

    def _to_records(self, items, zone):
        records = []
        for item in items:
            records.append(self._to_record(item, zone))

        return records

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

        if (len(errors) !=0 and errors[0]['ERRORMESSAGE'] ==
                'LW::Exception::RecordNotFound'):
            raise ZoneDoesNotExistError(zone_id=zone.id, value='', driver=self)

        return zone.domain in response

    def create_zone(self, zone_id):
        action = '/v1/Network/DNS/Zone/create'
        data = json.dumps({'params':{'name':zone_id}})
        response, errors = self.connection.request(action=action, method='POST',
                data=data).parse_body()

        if (len(errors) != 0 and errors[0]['ERRORMESSAGE'] ==
                'LW::Exception::DuplicateRecord'):
            raise ZoneAlreadyExistsError(zone_id=zone_id, value='', driver=self)

        zones = self._to_zones(response)

        return zones[0]

    def list_records(self, zone):
        action = '/v1/Network/DNS/Record/list'
        data = json.dumps({'params':{'zone_id':zone.id}})
        response, errors = self.connection.request(action=action, method='POST',
                data=data).parse_body()

        records =self._to_records(response[0], zone=zone)

        return records

    def get_record(self, zone_id, record_id):
        zone = self.get_zone(zone_id=zone_id)
        action = '/v1/Network/DNS/Record/details'
        data = json.dumps({'params':{'id':record_id}})
        response, errors = self.connection.request(action=action, method='POST',
                data=data).parse_body()
        #ipdb.set_trace()
        if len(errors) != 0 and errors[0]['ERRORMESSAGE'] == 'LW::Exception::RecordNotFound':
            raise RecordDoesNotExistError(record_id=record_id, driver=self,
                            value='')
        #ipdb.set_trace()
        records = self._to_records(response, zone=zone)

        return records[0]

    def delete_record(self, record):
        action = '/v1/Network/DNS/Record/delete'
        data = json.dumps({'params':{'id':record.id}})
        response, errors = self.connection.request(action=action, method='POST',
                data=data).parse_body()

        if len(errors) != 0 and errors[0]['ERRORMESSAGE'] == 'LW::Exception::RecordNotFound':
            raise RecordDoesNotExistError(record_id=record.id, driver=self,
                    value='')

        return record.id in response

    def create_record(self, name, zone, rtype, data, extra):
        action = '/v1/Network/DNS/Record/create'
        #rdata = extra.get('rdata')
        #region_id = extra.get('region_id')
        ttl = extra.get('ttl')
        data = json.dumps({'params':
                             {'name':name,
                              'rdata':data ,
                              #'region_overrides':[{'rdata':rdata, 'region_id':region_id}],
                              'zone':zone.domain,
                              'ttl':ttl,
                              'type':rtype,
                              'zone_id':zone.id
                                }
                            }
                                )
        response, errors = self.connection.request(action=action, method='POST',
                data=data).parse_body()
        #ipdb.set_trace()
        if len(errors) != 0 and errors[0]['ERRORMESSAGE'] == 'LW::Exception::DuplicateRecord':
            raise RecordAlreadyExistsError(record_id=name, value='', driver=self)
        records = self._to_records(response, zone=zone)

        return records[0]
