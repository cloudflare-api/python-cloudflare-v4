#!/usr/bin/env python

import os
import sys
sys.path.insert(0, os.path.abspath('..'))
import CloudFlare

def main():
	cf = CloudFlare.CloudFlare()
	zones = cf.zones.get(params={'per_page':50})
	for zone in zones:
		zone_name = zone['name']
		zone_id = zone['id']
		settings_ipv6 = cf.zones.settings.ipv6.get(zone_id)
		ipv6_on = settings_ipv6['value']
		print zone_id, ipv6_on, zone_name
	exit(0)

if __name__ == '__main__':
	main()

