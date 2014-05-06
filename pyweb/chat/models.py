import uuid
import datetime

from django.utils import timezone
from django.db import models, IntegrityError

from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

from .helpers import retry_action


class Profile(models.Model):
	''' User profile class for service users. Provides supplementary data, avatar
		settings, etc.
	'''
 	user = models.OneToOneField(User)

	def __str__(self):
		return self.user.username		

class Message(models.Model):
	''' This represents a single message sent during chat.  It has a unique alpha numeric
		pseudorandom message_id, the text of the actual message, the timestamp of when the
		message was sent, and a foreign key linking it to the sender
		@raise IntegrityError if the pseudorandom message_id is not unique
	'''
	id = models.CharField(primary_key=True, max_length=36, unique=True)
	text = models.CharField(max_length=256)
	timestamp = models.DateTimeField(default=datetime.datetime.now, verbose_name='date submitted')
	sender = models.ForeignKey(User)

	def generateMessageId(self): return uuid.uuid4().hex

	def save(self, *args, **kwargs):
		# Generate message id if the model does not already have one
		if not self.id: self.id = self.generateMessageId()
		# Save model instance, in cases with duplicate IDs, generate new ID and resave
		def messagesave(): super(self.__class__, self).save(*args, **kwargs)
		def duplicateid(): self.id = self.generateMessageId()
		retry_action(messagesave, exception_actions={ IntegrityError : duplicateid })

	def __str__(self):
		# return ''.join([self.sender.user.username,self.text])
		return ' : '.join([str(s) for s in (self.sender.username, self.text, self.id) if s is not None])

class Conversation(models.Model):
	''' Conversation represents one conversation that's taking place.  It has many
		participants and many messages.
	'''
	id = models.CharField(primary_key=True, max_length=36, unique=True)
	participants = models.ManyToManyField(User, blank=True)
	messages = models.ManyToManyField(Message, blank=True)

	def __str__(self):
		return ' : '.join(["Conversation", str(self.pk)])

	def generateConversationId(self): return uuid.uuid4().hex

	def save(self, *args, **kwargs):
		# Generate conversation id if the model does not already have one
		if not self.id: self.id = self.generateConversationId()
		# Save model instance, in cases with duplicate IDs, generate a new ID and resave
		def conversationsave():	super(self.__class__, self).save(*args, **kwargs)
		def duplicateid(): self.id = self.generateConversationId()
		retry_action(conversationsave, exception_actions={ IntegrityError : duplicateid })

