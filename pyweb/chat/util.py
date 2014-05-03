import json, re
from datetime import datetime

class DateTimeAwareEncoder(json.JSONEncoder):
	''' Allows for encoding objects with datetime support
		@example: json.dumps(obj, cls=DateTimeAwareEncoder)
	'''
	def default(self, obj):
		if isinstance(obj, datetime):
			return {
				'__type__' : 'datetime',
				'year' : obj.year,
				'month' : obj.month,
				'day' : obj.day,
				'hour' : obj.hour,
				'minute' : obj.minute,
				'second' : obj.second,
				'microsecond' : obj.microsecond
			}
		else:
			return json.JSONEncoder.default(self, obj)

class DateTimeAwareDecoder(json.JSONDecoder):
	''' Allows for decoding objects with datetime support.
		@example:  json.loads(data, cls=DateTimeAwareDecoder)
	'''
	def __init__(self, *args, **kwargs):
		json.JSONDecoder.__init__(self, object_hook=self.dict_to_object)

	def dict_to_object(self, d):
		if '__type__' not in d:
			return d

		type = d.pop('__type__')
		if type == 'datetime':
			return datetime(**d)
		else:
			d['__type__'] = type
			return d