#from .. import util
from . import dns_records
from .. import CloudFlare

ENDPOINT = 'zones'

#class CloudFlare:
def get(self, params=None):
    if type(params) is dict:
        return self.call('GET', ENDPOINT, params)
    elif type(params) is str:
        return self.call('GET', ENDPOINT + '/' + params)

def purge(auth, params):
    return self.call('DELETE', ENDPOINT + '/' + params + '/purge_cache', { 'purge_everything': True })
