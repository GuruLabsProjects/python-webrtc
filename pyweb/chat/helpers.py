import traceback, json, re
from datetime import datetime
from contextlib import contextmanager
from .errors import OperationError

def retry_action(action, number_retries=3, exception_actions={}):
	'''	Helper method to retry an action a set number of times
		@input action: Action which should be retried
		@input number_retries (int, default=3): Number of times the action
			should be retried
		@input exception_actions (dictionary, default={}): A dictionary
			of actions which should 
	'''
	opdetails = []
	if not callable(action):
		raise OperationError('The action you provided cannot be called')
	for i in xrange(number_retries):
		try:
			action()
			return
		except Exception as err:
			if type(err) in exception_actions:
				exception_actions.get(type(err))()
				# Collect details of error for later troubleshooting
				opdetails.append('\n'.join((err.message, traceback.format_exc())))
			else: raise(err)
	raise OperationError('Unable to complete the requested action, '
		+ 'max number of retries exceeded', details=opdetails)

class DateTimeAwareEncoder(json.JSONEncoder):
	''' Allows for encoding objects with datetime support
		@example: json.dumps(obj, cls=DateTimeAwareEncoder)
	'''
	def default(self, obj):
		if isinstance(obj, datetime): return obj.strftime('%Y-%m-%dT%H:%M:%S')	
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