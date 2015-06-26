import ipdb
import sys
import unittest

from libcloud.utils.py3 import httplib
from libcloud.dns.drivers.liquidweb import LiquidWebDNSDriver
from libcloud.test import MockHttp
from libcloud.test.file_fixtures import DNSFileFixtures
from libcloud.test.secrets import LIQUIDWEB_PARAMS
from libcloud.dns.types import ZoneDoesNotExistError, ZoneAlreadyExistsError
from libcloud.dns.types import RecordDoesNotExistError
from libcloud.dns.types import RecordType
from libcloud.dns.base import Zone, Record


class LiquidWebTests(unittest.TestCase):
    def setUp(self):
        LiquidWebMockHttp.type = None
        LiquidWebDNSDriver.connectionCls.conn_classes = (None,
                LiquidWebMockHttp)
        self.driver = LiquidWebDNSDriver(LIQUIDWEB_PARAMS)
        self.test_zone = Zone(id='11', type='master', ttl=None,
                domain='example.com', extra={}, driver=self.driver)

    def test_list_zones_empty(self):
        LiquidWebMockHttp.type = 'EMPTY_ZONES_LIST'
        zones = self.driver.list_zones()

        self.assertEqual(zones, [])

    def test_list_zones_success(self):
        zones = self.driver.list_zones()

        self.assertEqual(len(zones), 3)

        zone = zones[0]
        self.assertEqual(zone.id, '378451')
        self.assertEqual(zone.domain, 'blogtest.com')
        self.assertEqual(zone.type, 'NATIVE')
        self.assertEqual(zone.driver, self.driver)
        self.assertEqual(zone.ttl, None)

        second_zone = zones[1]
        self.assertEqual(second_zone.id, '378449')
        self.assertEqual(second_zone.domain, 'oltjanotest.com')
        self.assertEqual(second_zone.type, 'NATIVE')
        self.assertEqual(second_zone.driver, self.driver)
        self.assertEqual(second_zone.ttl, None)

        third_zone = zones[2]
        self.assertEqual(third_zone.id, '378450')
        self.assertEqual(third_zone.domain, 'pythontest.com')
        self.assertEqual(third_zone.type, 'NATIVE')
        self.assertEqual(third_zone.driver, self.driver)
        self.assertEqual(third_zone.ttl, None)

    def test_get_zone_zone_does_not_exist(self):
        LiquidWebMockHttp.type = 'ZONE_DOES_NOT_EXIST'
        try:
            self.driver.get_zone(zone_id='13')
        except ZoneDoesNotExistError:
            e = sys.exc_info()[1]
            self.assertEqual(e.zone_id, '13')
        else:
            self.fail('Exception was not thrown')

    def test_get_zone_success(self):
        LiquidWebMockHttp.type = 'GET_ZONE_SUCCESS'
        zone = self.driver.get_zone(zone_id='13')

        self.assertEqual(zone.id, '13')
        self.assertEqual(zone.domain, 'blogtest.com')
        self.assertEqual(zone.type, 'NATIVE')
        self.assertEqual(zone.ttl, None)
        self.assertEqual(zone.driver, self.driver)

    def test_delete_zone_success(self):
        LiquidWebMockHttp.type = 'DELETE_ZONE_SUCCESS'
        zone = self.test_zone
        status = self.driver.delete_zone(zone=zone)

        self.assertEqual(status, True)

    def test_delete_zone_zone_does_not_exist(self):
        LiquidWebMockHttp.type = 'DELETE_ZONE_ZONE_DOES_NOT_EXIST'
        zone = self.test_zone
        try:
            self.driver.delete_zone(zone=zone)
        except ZoneDoesNotExistError:
            e = sys.exc_info()[1]
            self.assertEqual(e.zone_id, '11')
        else:
            self.fail('Exception was not thrown')

    def test_create_zone_success(self):
        LiquidWebMockHttp.type = 'CREATE_ZONE_SUCCESS'
        zone = self.driver.create_zone(zone_id='test.com')

        self.assertEqual(zone.id, '13')
        self.assertEqual(zone.domain, 'test.com')
        self.assertEqual(zone.type, 'NATIVE')
        self.assertEqual(zone.ttl, None)
        self.assertEqual(zone.driver, self.driver)


class LiquidWebMockHttp(MockHttp):
    fixtures = DNSFileFixtures('liquidweb')

    def _v1_Network_DNS_Zone_list(self, method, url, body, headers):
        body = self.fixtures.load('zones_list.json')
        return (httplib.OK, body, {}, httplib.responses[httplib.OK])

    def _v1_Network_DNS_Zone_list_EMPTY_ZONES_LIST(self, method, url, body,
            headers):
        body = self.fixtures.load('empty_zones_list.json')
        return (httplib.OK, body, {}, httplib.responses[httplib.OK])

    def _v1_Network_DNS_Zone_details_ZONE_DOES_NOT_EXIST(self, method, url,
            body, headers):
        body = self.fixtures.load('zone_does_not_exist.json')
        return (httplib.OK, body, {}, httplib.responses[httplib.OK])

    def _v1_Network_DNS_Zone_details_GET_ZONE_SUCCESS(self, method, url,
            body, headers):
        body = self.fixtures.load('get_zone.json')
        return (httplib.OK, body, {}, httplib.responses[httplib.OK])

    def _v1_Network_DNS_Zone_delete_DELETE_ZONE_SUCCESS(self, method, url,
            body, headers):
        body = self.fixtures.load('delete_zone_success.json')
        return (httplib.OK, body, {}, httplib.responses[httplib.OK])

    def _v1_Network_DNS_Zone_delete_DELETE_ZONE_ZONE_DOES_NOT_EXIST(self,
            method, url, body, headers):
        body = self.fixtures.load('zone_does_not_exist.json')
        return (httplib.OK, body, {}, httplib.responses[httplib.OK])

    def _v1_Network_DNS_Zone_create_CREATE_ZONE_SUCCESS(self, method, url, body,
            headers):
        body = self.fixtures.load('create_zone_success.json')
        return (httplib.OK, body, {}, httplib.responses[httplib.OK])

if __name__ == '__main__':
    sys.exit(unittest.main())
