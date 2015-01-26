from .. import util

ENDPOINT = 'user'

def get(auth, params=None):
    return util.call(auth, 'GET', ENDPOINT, params)
