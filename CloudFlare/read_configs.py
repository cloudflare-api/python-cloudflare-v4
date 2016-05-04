
import os
import re
import ConfigParser

def read_configs():

	# envioronment variables override config files
	email = os.getenv('CF_API_EMAIL')
	token = os.getenv('CF_API_KEY')
	certtoken = os.getenv('CF_API_CERTKEY')

	# grab values from config files
	config = ConfigParser.RawConfigParser()
	config.read(['.cloudflare.cfg', os.path.expanduser('~/.cloudflare.cfg'), os.path.expanduser('~/.cloudflare/cloudflare.cfg')])

	if email is None:
		try:
			email = re.sub(r"\s+", '', config.get('CloudFlare', 'email'))
		except:
			email = None

	if token is None:
		try:
			token = re.sub(r"\s+", '', config.get('CloudFlare', 'token'))
		except:
			token = None

	if certtoken is None:
		try:
			certtoken = re.sub(r"\s+", '', config.get('CloudFlare', 'certtoken'))
		except:
			certtoken = None

	try:
		extras = re.sub(r"\s+", ' ', config.get('CloudFlare', 'extras'))
	except:
		extras = None

	extras = extras.split(' ')

	return [ email, token, certtoken, extras ]

