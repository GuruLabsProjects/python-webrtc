#!/usr/bin/python
import sys, os
from configobj import ConfigObj

from twisted.internet import reactor
from twisted.web.server import Site
from twisted.web.resource import Resource
from websockets import WebSocketsResource
from twisted.python import log

from messagerelay.messageserver import MessengerConnectionFactory

log.startLogging(sys.stdout)

if __name__ == '__main__':

	# Load server settings
	mdir = os.path.dirname(__file__)
	settings = ConfigObj(os.path.join(mdir, 'webrtc-python.config'))

	# Configure Twisted Web
	siteroot = Resource()
	reactor.listenTCP(int(settings.get('port')), Site(siteroot), interface=settings.get('server'))

	# Add websocket connection protocol/factory as a resource
	websocket_messages = MessengerConnectionFactory(root_site=siteroot)
	siteroot.putChild('messages', WebSocketsResource(websocket_messages))

	reactor.run()
