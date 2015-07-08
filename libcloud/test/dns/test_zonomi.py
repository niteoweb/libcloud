import sys
import unittest


from libcloud.test import MockHttp #used in conn_classes
from libcloud.utils.py3 import httplib
from libcloud.common.zonomi import ZonomiException
from libcloud.dns.drivers.zonomi import ZonomiDNSDriver
from libcloud.test.secrets import DNS_PARAMS_ZONOMI
from libcloud.test.file_fixtures import DNSFileFixtures
from libcloud.dns.types import ZoneDoesNotExistError, ZoneAlreadyExistsError
from libcloud.dns.types import RecordDoesNotExistError, RecordAlreadyExistsError
from libcloud.dns.base import Zone, Record



class ZonomiTests(unittest.TestCase):
    def setUp(self):
        ZonomiDNSDriver.connectionCls.conn_classes = (None, ZonomiMockHttp)
        ZonomiMockHttp.type = None
        self.driver = ZonomiDNSDriver(*DNS_PARAMS_ZONOMI)
        self.test_zone = Zone(id='zone.com', domain='zone.com', driver=
                self.driver, type='NATIVE', ttl=None, extra={})
        self.test_record = Record(id='record.zone.com', name='record.zone.com',
                data='127.0.0.1', type='A', zone=self.test_zone, driver=self,
                                            extra={})

    def test_list_zones_empty(self):
        ZonomiMockHttp.type = 'EMPTY_ZONES_LIST'
        zones = self.driver.list_zones()

        self.assertEqual(zones, [])

    def test_list_zones_success(self):
        #ZonomiMockHttp.type = 'LIST_ZONES_SUCCESS'
        zones = self.driver.list_zones()

        self.assertEqual(len(zones), 3)

        zone = zones[0]
        self.assertEqual(zone.id, 'thegamertest.com')
        self.assertEqual(zone.domain, 'thegamertest.com')
        self.assertEqual(zone.type, 'NATIVE')
        self.assertEqual(zone.ttl, None)
        self.assertEqual(zone.driver, self.driver)

        second_zone = zones[1]
        self.assertEqual(second_zone.id, 'lonelygamer.com')
        self.assertEqual(second_zone.domain, 'lonelygamer.com')
        self.assertEqual(second_zone.type, 'NATIVE')
        self.assertEqual(second_zone.ttl, None)
        self.assertEqual(second_zone.driver, self.driver)

        third_zone = zones[2]
        self.assertEqual(third_zone.id, 'gamertest.com')
        self.assertEqual(third_zone.domain, 'gamertest.com')
        self.assertEqual(third_zone.type, 'NATIVE')
        self.assertEqual(third_zone.ttl, None)
        self.assertEqual(third_zone.driver, self.driver)

    def test_get_zone_GET_ZONE_DOES_NOT_EXIST(self):
        ZonomiMockHttp.type = 'GET_ZONE_DOES_NOT_EXIST'
        try:
            self.driver.get_zone('testzone.com')
        except ZoneDoesNotExistError:
            e = sys.exc_info()[1]
            self.assertEqual(e.zone_id, 'testzone.com')
        else:
            self.fail('Exception was not thrown.')

    def test_get_zone_GET_ZONE_SUCCESS(self):
        ZonomiMockHttp.type = 'GET_ZONE_SUCCESS'
        zone = self.driver.get_zone(zone_id='gamertest.com')

        self.assertEqual(zone.id, 'gamertest.com')
        self.assertEqual(zone.domain, 'gamertest.com')
        self.assertEqual(zone.type, 'NATIVE')
        self.assertEqual(zone.ttl, None)
        self.assertEqual(zone.driver, self.driver)

    def test_delete_zone_DELETE_ZONE_DOES_NOT_EXIST(self):
        ZonomiMockHttp.type = 'DELETE_ZONE_DOES_NOT_EXIST'
        try:
            self.driver.delete_zone(zone=self.test_zone)
        except ZoneDoesNotExistError:
            e = sys.exc_info()[1]
            self.assertEqual(e.zone_id, self.test_zone.id)
        else:
            self.fail('Exception was not thrown.')

    def test_delete_zone_delete_zone_success(self):
        ZonomiMockHttp.type = 'DELETE_ZONE_SUCCESS'
        status = self.driver.delete_zone(zone=self.test_zone)

        self.assertEqual(status, True)

    def test_create_zone_already_exists(self):
        ZonomiMockHttp.type = 'CREATE_ZONE_ALREADY_EXISTS'
        try:
            self.driver.create_zone(zone_id='gamertest.com')
        except ZoneAlreadyExistsError:
            e = sys.exc_info()[1]
            self.assertEqual(e.zone_id, 'gamertest.com')
        else:
            self.fail('Exception was not thrown.')

    def test_create_zone_create_zone_success(self):
        ZonomiMockHttp.type = 'CREATE_ZONE_SUCCESS'

        zone = self.driver.create_zone(zone_id='myzone.com')

        self.assertEqual(zone.id, 'myzone.com')
        self.assertEqual(zone.domain, 'myzone.com')
        self.assertEqual(zone.type, 'NATIVE')
        self.assertEqual(zone.ttl, None)

    def test_list_records_empty_list(self):
        ZonomiMockHttp.type = 'LIST_RECORDS_EMPTY_LIST'
        pass

    def test_list_records_success(self):
        ZonomiMockHttp.type = 'LIST_RECORDS_SUCCESS'
        records = self.driver.list_records(zone=self.test_zone)

        self.assertEqual(len(records), 4)

        record = records[0]
        self.assertEqual(record.id, 'zone.com')
        self.assertEqual(record.type,  'SOA')
        self.assertEqual(record.data,'ns1.zonomi.com. soacontact.zonomi.com. 13')
        self.assertEqual(record.name, 'zone.com')
        self.assertEqual(record.zone, self.test_zone)

        second_record = records[1]
        self.assertEqual(second_record.id, 'zone.com')
        self.assertEqual(second_record.name, 'zone.com')
        self.assertEqual(second_record.type, 'NS')
        self.assertEqual(second_record.data, 'ns1.zonomi.com')
        self.assertEqual(second_record.zone, self.test_zone)

        third_record = records[2]
        self.assertEqual(third_record.id, 'oltjano.thegamertest.com')
        self.assertEqual(third_record.name, 'oltjano.thegamertest.com')
        self.assertEqual(third_record.type, 'A')
        self.assertEqual(third_record.data, '127.0.0.1')
        self.assertEqual(third_record.zone, self.test_zone)

        fourth_record = records[3]
        self.assertEqual(fourth_record.id, 'zone.com')
        self.assertEqual(fourth_record.name, 'zone.com')
        self.assertEqual(fourth_record.type, 'NS')
        self.assertEqual(fourth_record.data, 'ns5.zonomi.com')
        self.assertEqual(fourth_record.zone, self.test_zone)

    """
    def test_get_record_does_not_exist(self):
        ZonomiMockHttp.type = 'GET_RECORD_DOES_NOT_EXIST'
        pass

    def test_get_record_success(self):
        ZonomiMockHttp.type = 'GET_RECORD_SUCCESS'

        record = self.driver.get_record(record_id='oltjano.thegamertest.com',
                zone_id='thegamertest.com')

        self.assertEqual(record.id, 'oltjano.thegamertest.com')
        self.assertEqual(record.name, 'oltjano.thegamertest.com')
        self.assertEqual(record.type, 'A')
        self.assertEqual(record.data, '127.0.0.1')
        #elf.assertEqual
    """

    def test_delete_record_does_not_exist(self):
        ZonomiMockHttp.type = 'DELETE_RECORD_DOES_NOT_EXIST'
        record = self.test_record
        try:
            self.driver.delete_record(record=record)
        except RecordDoesNotExistError:
            e = sys.exc_info()[1]
            self.assertEqual(e.record_id, record.id)
        else:
            self.fail('Exception was not thrown.')

    def test_delete_record_success(self):
        ZonomiMockHttp.type = 'DELETE_RECORD_SUCCESS'
        record = self.test_record
        status = self.driver.delete_record(record=record)

        self.assertEqual(status, True)

    def test_create_record_already_exists(self):
        zone = self.test_zone
        ZonomiMockHttp.type = 'CREATE_RECORD_ALREADY_EXISTS'
        try:
            self.driver.create_record(name='createrecord.zone.com', type='A',
                    data='127.0.0.1', zone=zone, extra={})
        except RecordAlreadyExistsError:
            e = sys.exc_info()[1]
            self.assertEqual(e.record_id, 'createrecord.zone.com')
        else:
            self.fail('Exception was not thrown.')

    def test_create_record_success(self):
        ZonomiMockHttp.type = 'CREATE_RECORD_SUCCESS'
        zone = self.test_zone
        record = self.driver.create_record(name='createrecord.zone.com',
            zone=zone, type='A', data='127.0.0.1', extra={})

        self.assertEqual(record.id, 'createrecord.zone.com')
        self.assertEqual(record.name, 'createrecord.zone.com')
        self.assertEqual(record.type, 'A')
        self.assertEqual(record.data, '127.0.0.1')
        self.assertEqual(record.zone, zone)


class ZonomiMockHttp(MockHttp):
    fixtures = DNSFileFixtures('zonomi')

    def _app_dns_dyndns_jsp_EMPTY_ZONES_LIST(self, method, url, body, headers):
        body = self.fixtures.load('empty_zones_list.xml')
        return (httplib.OK, body, {}, httplib.responses[httplib.OK])

    def _app_dns_dyndns_jsp(self, method, url, body, headers):
        body = self.fixtures.load('list_zones.xml')
        return (httplib.OK, body, {}, httplib.responses[httplib.OK])

    def _app_dns_dyndns_jsp_GET_ZONE_DOES_NOT_EXIST(self, method, url, body,
            headers):
        body = self.fixtures.load('list_zones.xml')
        return (httplib.OK, body, {}, httplib.responses[httplib.OK])

    def _app_dns_dyndns_jsp_GET_ZONE_SUCCESS(self, method, url, body, headers):
        body = self.fixtures.load('list_zones.xml')
        return (httplib.OK, body, {}, httplib.responses[httplib.OK])

    def _app_dns_dyndns_jsp_DELETE_ZONE_DOES_NOT_EXIST(self, method, url, body,
            headers):
        body = self.fixtures.load('delete_zone_does_not_exist.xml')
        return (httplib.OK, body, {}, httplib.responses[httplib.OK])

    def _app_dns_dyndns_jsp_DELETE_ZONE_SUCCESS(self, method, url, body, headers):
        body = self.fixtures.load('delete_zone.xml')
        return (httplib.OK, body, {}, httplib.responses[httplib.OK])

    def _app_dns_addzone_jsp_CREATE_ZONE_SUCCESS(self, method, url, body,
            headers):
        body = self.fixtures.load('create_zone.xml')
        return (httplib.OK, body, {}, httplib.responses[httplib.OK])

    def _app_dns_addzone_jsp_CREATE_ZONE_ALREADY_EXISTS(self, method, url,
            body, headers):
        body = self.fixtures.load('create_zone_already_exists.xml')
        return (httplib.OK, body, {}, httplib.responses[httplib.OK])

    def _app_dns_dyndns_jsp_LIST_RECORDS_EMPTY_LIST(self, method, url, body,
            headers):
        body = self.fixtures.load('list_records_empty_list.xml')
        return (httplib.OK, body, {}, httplib.responses[httplib.OK])

    def _app_dns_dyndns_jsp_LIST_RECORDS_SUCCESS(self, method, url, body,
            headers):
        body = self.fixtures.load('list_records.xml')
        return (httplib.OK, body, {}, httplib.responses[httplib.OK])

    def _app_dns_dyndns_jsp_DELETE_RECORD_SUCCESS(self, method, url, body,
            headers):
        body = self.fixtures.load('delete_record.xml')
        return (httplib.OK, body, {}, httplib.responses[httplib.OK])

    def _app_dns_dyndns_jsp_DELETE_RECORD_DOES_NOT_EXIST(self, method, url,
            body, headers):
        body = self.fixtures.load('delete_record_does_not_exist.xml')
        return (httplib.OK, body, {}, httplib.responses[httplib.OK])

    def _app_dns_dyndns_jsp_CREATE_RECORD_SUCCESS(self, method, url, body,
            headers):
        body = self.fixtures.load('create_record.xml')
        return (httplib.OK, body, {}, httplib.responses[httplib.OK])

    def _app_dns_dyndns_jsp_CREATE_RECORD_ALREADY_EXISTS(self, method, url,
            body, headers):
        body = self.fixtures.load('create_record_already_exists.xml')
        return (httplib.OK, body, {}, httplib.responses[httplib.OK])

    def _app_dns_dyndns_jsp_GET_RECORD_SUCCESS(self, method, url, body,
            headers):
        body = self.fixtures.load('list_zones.xml')
        return (httplib.OK, body, {}, httplib.responses[httplib.OK])

    #def _app_dns_dyndns_jsp_GET_RECORD_SUCCESS(self, method, url, body,
    #        headers):
    #    body = self.fixtures.load('list_records.xml')

    #    return(httplib.OK, body, {}, httplib.responses[httplib.OK])

if __name__ == '__main__':
    sys.exit(unittest.main())
