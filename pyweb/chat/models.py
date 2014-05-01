import uuid
import datetime
from django.utils import timezone
from django.db import models
from django.forms import ModelForm
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

class ChatUserProfileForm(ModelForm):
	class Meta:
		model = ChatUserProfile
		fields = ['user']

class ChatUserProfile(models.Model):
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
 	# 	return ChatUserProfile(user=cuser)

	def __str__(self):
		return self.user.username

class MessageForm(ModelForm):
	class Meta:
		model = Message
		fields = ['message_id', 'text', 'timestamp', 'sender']			

class Message(models.Model):
	''' This represents a single message sent during chat.  It has a unique alpha numeric
		pseudorandom message_id, the text of the actual message, the timestamp of when the
		message was sent, and a foreign key linking it to the sender
		@raise IntegrityError if the pseudorandom message_id is not unique
	'''
	message_id = models.CharField(primary_key=True, max_length=36, 
		unique=True, editable=False, default=uuid.uuid4().hex)
	text = models.CharField(editable=False, max_length=256)
	# datetime.datetime.now doesn't work... something to do with time zone?
	timestamp = models.DateTimeField(default=timezone.now, verbose_name='date submitted')
	sender = models.ForeignKey(User)

	def __str__(self):
		# return ''.join([self.sender.user.username,self.text])
		return ':'.join([str(s) for s in (self.sender.username, self.text) if s is not None])

class ConversationForm(ModelForm):
	class Meta:
		model = Conversation
		fields = ['participants', 'messages']	

class Conversation(models.Model):
	''' Conversation represents one conversation that's taking place.  It has many
		participants and many messages.
	'''
	participants = models.ManyToManyField(User)
	messages = models.ManyToManyField(Message)

	def __str__(self):
		return ':'.join(["Conversation",self.pk])
