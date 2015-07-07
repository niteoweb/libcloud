import sys
import unittest


from libcloud.test import MockHttp #used in conn_classes
from libcloud.utils.py3 import httplib
from libcloud.common.zonomi import ZonomiException
from libcloud.dns.drivers.zonomi import ZonomiDNSDriver
from libcloud.test.secrets import DNS_PARAMS_ZONOMI
from libcloud.test.file_fixtures import DNSFileFixtures


class ZonomiTests(unittest.TestCase):
    def setUp(self):
        ZonomiDNSDriver.connectionCls.conn_classes = (None, ZonomiMockHttp)
        ZonomiMockHttp.type = None
        self.driver = ZonomiDNSDriver(*DNS_PARAMS_ZONOMI)

    def test_list_zones_empty(self):
        ZonomiMockHttp.type = 'EMPTY_ZONES_LIST'
        zones = self.driver.list_zones()

        self.assertEqual(zones, [])

    def test_list_zones_success(self):
        ZonomiMockHttp.type = 'LIST_ZONES_SUCCESS'
        zones = self.driver.list_zones()

        self.assertEqual(len(zones), 4)


class ZonomiMockHttp(MockHttp):
    fixtures = DNSFileFixtures('zonomi')

    def _app_dns_dyndns_jsp_EMPTY_ZONES_LIST(self, method, url, body, headers):
        body = self.fixtures.load('empty_zones_list.xml')
        return (httplib.OK, body, {}, httplib.responses[httplib.OK])

    def _app_dns_dyndns_jsp_LIST_ZONES_SUCCESS(self, method, url, body, headers):
        body = self.fixtures.load('list_zones.xml')
        return (httplib.OK, body, {}, httplib.responses[httplib.OK])

if __name__ == '__main__':
    sys.exit(unittest.main())
