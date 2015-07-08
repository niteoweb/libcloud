import sys
import unittest


from libcloud.test import MockHttp #used in conn_classes
from libcloud.utils.py3 import httplib
from libcloud.common.zonomi import ZonomiException
from libcloud.dns.drivers.zonomi import ZonomiDNSDriver
from libcloud.test.secrets import DNS_PARAMS_ZONOMI
from libcloud.test.file_fixtures import DNSFileFixtures
from libcloud.dns.types import ZoneDoesNotExistError
from libcloud.dns.base import Zone



class ZonomiTests(unittest.TestCase):
    def setUp(self):
        ZonomiDNSDriver.connectionCls.conn_classes = (None, ZonomiMockHttp)
        ZonomiMockHttp.type = None
        self.driver = ZonomiDNSDriver(*DNS_PARAMS_ZONOMI)
        self.test_zone = Zone(id='zone.com', domain='zone.com', driver=
                self.driver, type='NATIVE', ttl=None, extra={})

    def test_list_zones_empty(self):
        ZonomiMockHttp.type = 'EMPTY_ZONES_LIST'
        zones = self.driver.list_zones()

        self.assertEqual(zones, [])

    def test_list_zones_success(self):
        ZonomiMockHttp.type = 'LIST_ZONES_SUCCESS'
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

    def test_delete_zone_DELETE_ZONE_SUCCESS(self):
        ZonomiMockHttp.type = 'DELETE_ZONE_SUCCESS'
        status = self.driver.delete_zone(zone=self.test_zone)

        self.assertEqual(status, True)


class ZonomiMockHttp(MockHttp):
    fixtures = DNSFileFixtures('zonomi')

    def _app_dns_dyndns_jsp_EMPTY_ZONES_LIST(self, method, url, body, headers):
        body = self.fixtures.load('empty_zones_list.xml')
        return (httplib.OK, body, {}, httplib.responses[httplib.OK])

    def _app_dns_dyndns_jsp_LIST_ZONES_SUCCESS(self, method, url, body, headers):
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

if __name__ == '__main__':
    sys.exit(unittest.main())
