from json import loads, dumps
import sys, itertools, traceback

from twisted.internet import threads
from twisted.python import log
from twisted.protocols.basic import LineReceiver
from twisted.internet.protocol import ServerFactory


class MessengerConnection(LineReceiver):
	'''	Connection which can be used to forward messages from the Django application to
		a connected client
	'''

	def __init__(self, factory):
		self.factory = factory
		self.ctype = None
		self.ipaddr = None
		self.cport = None

	def connectionMade(self):
		'''	Event fired when a client connection is made to the server.
			Can be used to provide an authentication challenge, or to provide
			data that might be used by the client when first creating a connection.
		'''
		cpeer = self.transport.getPeer()
		self.ipaddr = cpeer.host
		self.port = cpeer.port
		log.msg('Client connection created: %s:%s' % (str(self.ipaddr), str(self.port)))

	def dataReceived(self, data):
		''' Event fired when the server receives data sent by the client
		'''
		log.msg('Data received: ' + data)
		self.sendLine(data)

	def connectionLost(self, reason): 
		'''	Event fired when a client connection is closed.
			Useful for performing cleanup and removing persistent objects from the factory.
		'''
		pass


class MessengerConnectionFactory(ServerFactory):
	'''	Manage the creation and retiring of connected clients
	'''

	protocol = MessengerConnection

	def __init__(self, root_site=None):
		''' @input root_site (default=None): Reference which can be used to access the
				root resource of the site
		'''

		self.root_site = root_site
		self.connections = {}
		log.msg('Creating root messenger factory')

	def buildProtocol(self, addr):
		'''	Return a new instance of a protocol connection
		'''
		return self.protocol(self)