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
		print request.__dict__
		rdata = request.content.getvalue()
		mdata = json.loads(rdata)
		return json.dumps({'success' : 'yay'})