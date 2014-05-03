# Custom application errors
class OperationError(Exception):

	def __init__(self, message, details=None, *args, **kwargs):
		self.details = details
		super(self.__class__, self).__init__(message, *args, **kwargs)