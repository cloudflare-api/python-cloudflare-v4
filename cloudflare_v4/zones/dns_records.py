from .. import util

ENDPOINT = 'dns_records'

def get(auth, zone_id, params=None):
    return util.call(auth, 'GET', 'zones/' + zone_id + '/' + ENDPOINT, params)

def post(auth, zone_id, params=None):
    return util.call(auth, 'POST', 'zones/' + zone_id + '/' + ENDPOINT, params)

def put(auth, zone_id, params=None):
    return util.call(auth, 'PUT', 'zones/' + zone_id + '/' + ENDPOINT, params)
