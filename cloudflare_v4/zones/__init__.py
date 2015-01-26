from .. import util

ENDPOINT = 'zones'

def get(auth, params=None):
    return util.call(auth, 'GET', ENDPOINT, params)
