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

    def test_list_zones_empty(self):
        LiquidWebMockHttp.type = 'EMPTY_ZONES_LIST'
        zones = self.driver.list_zones()

        self.assertEqual(zones, [])


class LiquidWebMockHttp(MockHttp):
    fixtures = DNSFileFixtures('liquidweb')

    def _v1_Network_DNS_Zone_list(self, method, url, body, headers):
        body = self.fixtures.load('zones_list.json')
        return (httplib.OK, body, {}, httplib.responses[httplib.OK])

    def _v1_Network_DNS_Zone_list_EMPTY_ZONES_LIST(self, method, url, body,
            headers):
        body = self.fixtures.load('empty_zones_list.json')
        return (httplib.OK, body, {}, httplib.responses[httplib.OK])


if __name__ == '__main__':
    sys.exit(unittest.main())
