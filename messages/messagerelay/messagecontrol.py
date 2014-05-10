import traceback
import json

from twisted.web.resource import Resource

from twisted.python import log


class WebSocketControl(Resource):
	'''	Twisted web socket control resource: Provides a REST interface for Django
		to forward messages to connected clients
	'''

	def __init__(self, siteroot, websockets, *args, **kwargs):
		super(type(self), self).__init__(*args, **kwargs)
		self.siteroot = siteroot
		self.websockets = websockets
		log.msg('Initializing control interface')

	def render_POST(self, request):
		# Parse request
		response = {}
		rdata = request.content.getvalue()
		try:
			mdata = json.loads(rdata)
			recipients = mdata.pop('recipients', [])
			for recipient in recipients:
				if recipient in self.websockets.connections.keys():
					socket_connections = self.websockets.connections.get(recipient, [])
					for connection in socket_connections:
						try: connection.sendLine(json.dumps(mdata))
						except: print traceback.print_exc()
						log.msg('Forwarding message data to user (%s)' % recipient)
			response['status'] = 'success'
		except Exception as err:
			response['status'] = 'fail'
			response['error'] = unicode(err)
			response['details'] = traceback.format_exc()
		

		return json.dumps(response)