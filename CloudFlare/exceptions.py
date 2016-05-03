
class CloudFlareError(Exception):
	def __init__(self, code, message):
 		self.code = code
 		self.message =  message

	def __int__(self):
		return self.code

	def __str__(self):
		return self.message

class CloudFlareAPIError(CloudFlareError):
	pass

class CloudFlareInternalError(CloudFlareError):
	pass

