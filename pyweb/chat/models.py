import uuid
import datetime
from django.utils import timezone
from django.db import models
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

class Profile(models.Model):
	''' User profile class for service users. Provides supplementary data, avatar
		settings, etc.
	'''
 	user = models.OneToOneField(User)

 	# @staticmethod
 	# def createUser(username, email=None, password=None, **kwargs):
 	# 	''' Convenience method to create a user and profile simultaneously
 	# 		@input username: Username, must be unique
 	# 		@input email (default=None): Email for user
 	# 		@input password (default=None): User password
 	# 		@returns user profile object
 	# 	'''
 	# 	cuser = User.objects.create_user(username=username, email=email,
 	# 		password=password, **kwargs)
 	# 	return Profile(user=cuser)

	def __str__(self):
		return self.user.username		

class Message(models.Model):
	''' This represents a single message sent during chat.  It has a unique alpha numeric
		pseudorandom message_id, the text of the actual message, the timestamp of when the
		message was sent, and a foreign key linking it to the sender
		@raise IntegrityError if the pseudorandom message_id is not unique
	'''
	message_id = models.CharField(primary_key=True, max_length=36, unique=True)
	text = models.CharField(max_length=256)
	# datetime.datetime.now doesn't work... something to do with time zone?
	# timestamp = models.DateTimeField(default=datetime.datetime.now, verbose_name='date submitted')
	timestamp = models.DateTimeField(default=datetime.datetime.now, verbose_name='date submitted')
	sender = models.ForeignKey(User)

	def __init__(self, *args, **kwargs):
		super(Message, self).__init__(*args, **kwargs)
		# print "called Message __init__"
		# self.message_id = uuid.uuid4().hex

	def generateMessageId(self):
		return uuid.uuid4().hex

	def save(self, *args, **kwargs):
		if not self.message_id:
			self.message_id = self.generateMessageId()
		success = False
		failedAttempts = 0
		while not success:
			try:
				failedAttempts+=1
				super(self.__class__, self).save(*args, **kwargs)
				success = True
			except IntegrityError:
				if(failedAttempts > 10):
					raise
				else:
					self.message_id = self.generateMessageId()

	def __str__(self):
		# return ''.join([self.sender.user.username,self.text])
		return ':'.join([str(s) for s in (self.sender.username, self.text, self.message_id) if s is not None])

class Conversation(models.Model):
	''' Conversation represents one conversation that's taking place.  It has many
		participants and many messages.
	'''
	participants = models.ManyToManyField(User, blank=True)
	messages = models.ManyToManyField(Message, blank=True)

	def __str__(self):
		return ':'.join(["Conversation", str(self.pk)])
