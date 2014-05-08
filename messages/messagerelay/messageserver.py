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

	def connectionMade(self):
		log.msg('Client connection created')

	def dataReceived(self, data): self.sendLine(data)

	def connectionLost(self, reason): pass


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