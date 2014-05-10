import os, sys, json, itertools, traceback

from twisted.internet import reactor
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
		self.username = None
		self.displayname = None
		self.cdata = ''

	def identifyUser(self, userid):
		''' Add user information to the connection
		'''
		self.username = userid.get('id')
		self.displayname = userid.get('displayname')
		log.msg('Connection User Identified: %s' % ' : '.join([str(p) for p in 
			(self.username, self.displayname) if p is not None]))
		if self.username:
			self.factory.addClientConnection(self.username, self)

	def activeUserList(self):
		''' Send client a list of active users
		'''
		self.sendLine(json.dumps({ 'opcode' : 'user-activelist', 'users' : self.factory.activeUsers() }))
		

	def connectionMade(self):
		'''	Event fired when a client connection is made to the server.
			Can be used to provide an authentication challenge, or to provide
			data that might be used by the client when first creating a connection.
		'''
		# Add connection information
		cpeer = self.transport.getPeer()
		self.ipaddr = cpeer.host
		self.port = cpeer.port
		self.cdata = ':'.join((str(self.ipaddr), str(self.port)))
		log.msg('Client connection created: %s' % self.cdata)
		# Terminate connection if no user id provided
		def loginrequired():
			log.msg('Checking connection credentials: %s' % self.cdata)
			if not self.username: self.transport.loseConnection()
		reactor.callLater(2, loginrequired)

	def dataReceived(self, data):
		''' Event fired when the server receives data sent by the client
		'''
		try: mdata = json.loads(data)
		except: self.sendLine(json.dumps({'error' : 'parse-error', 'message' : 'Unable to parse request'}))
		
		# Retrieve operation code
		opcode = mdata.get('opcode')
		# Client operations
		if opcode == 'user-identity': self.identifyUser(mdata.get('user-identify', {}))
		elif opcode == 'user-active': self.activeUserList()

	def connectionLost(self, reason): 
		'''	Event fired when a client connection is closed.
			Useful for performing cleanup and removing persistent objects from the factory.
		'''
		log.msg('Connection Terminated: %s' % self.cdata)
		self.factory.removeClientConnection(self.username, self)
		


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
		self.userdata = {}
		log.msg('Creating root messenger factory')

	def addClientConnection(self, username, connection):
		'''	Add client connection to the pool of clients, indexed by username
		'''
		if username in self.connections.keys(): self.connections[username].append(connection)
		else: self.connections[username] = [connection, ]

		if username not in self.userdata.keys():
			self.userdata[username] = { 
				'id' : username, 
				'displayname' : connection.displayname,
			}

	def removeClientConnection(self, username, connection):
		''' Remove client connection from the pool of clients
		'''
		# Remove connection from pool
		if username in self.connections.keys():
			try: self.connections[username].remove(connection)
			except ValueError:
				log.msg('Connection not in pool for %s' % username)

		# Remove user name from pool list if no connections available
		if len(self.connections.get(username, [])) == 0:
			log.msg('User (%s) no longer connected' % username)
			try: self.connections.pop(username)
			except KeyError:
				log.msg('Unable to find any connections for user (%s)' % str(username))
			# Remove user connection data from userdata
			if username in self.userdata.keys(): self.userdata.pop(username)

	def activeUsers(self):
		return self.userdata.values()

	def buildProtocol(self, addr):
		'''	Return a new instance of a protocol connection
		'''
		return self.protocol(self)