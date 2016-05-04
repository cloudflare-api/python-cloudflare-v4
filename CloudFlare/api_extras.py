
import re

def api_extras(self, extras=None):
	for extra in extras:
		if extra == '':
			continue
		extra = re.sub(r"^.*/client/v4/", '/', extra)
		extra = re.sub(r"^.*/v4/", '/', extra)
		extra = re.sub(r"^/", '', extra)
		current = self

		# build parts of the extra command
		parts = []
		nn = 0
		for element in extra.split('/'):
			if element[0] == ':':
				nn += 1
				continue
			try:
				parts[nn]
			except:
				parts.append([])
			parts[nn].append(element)

		# insert extra command into class
		element_path = []
		for element in parts[0]:
			element_path.append(element)
			try:
				current = getattr(current, element)
				# exists
				continue
			except:
				pass
			# does not exist
			if element == parts[0][-1] and len(parts) > 1:
				# last element
				setattr(current, element, self._client_with_auth(self.base, '/'.join(element_path), '/'.join(parts[1])))
			else:
				setattr(current, element, self._client_with_auth(self.base, '/'.join(element_path)))
			current = getattr(current, element)

