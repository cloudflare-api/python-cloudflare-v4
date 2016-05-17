:

cli4 -v --post \
	targets='[ { "target": "url", "constraint": { "operator": "matches", "value": "*.example.com/url1*" } } ]' \
	actions='[ { "id": "forwarding_url", "value": { "status_code": 302, "url": "http://example.com/url2" } } ]' \
	status=active \
	priority=1 \
		/zones/:exmaple.com/pagerules | jq '{"status":.status,"priority":.priority,"id":.id}'

exit 0

