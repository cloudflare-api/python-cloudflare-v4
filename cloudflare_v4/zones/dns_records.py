from .. import util

ENDPOINT = 'dns_records'

def get(auth, params=None):
    util.call(auth, 'GET', 'zones/' + params + '/' + ENDPOINT)
