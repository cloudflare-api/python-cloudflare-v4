#from ..util import Util as util

ENDPOINT = 'dns_records'

def get(self, zone_id, params=None):
    return self.call('GET', 'zones/' + zone_id + '/' + ENDPOINT, params)

def post(self, zone_id, params=None):
    return self.call('POST', 'zones/' + zone_id + '/' + ENDPOINT, params)

def put(self, zone_id, params=None):
    return self.call('PUT', 'zones/' + zone_id + '/' + ENDPOINT, params)
