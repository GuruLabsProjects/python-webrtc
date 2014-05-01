import uuid
import datetime
from django.utils import timezone
from django.db import models, IntegrityError, transaction
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

class ChatUserProfile(models.Model):
	''' ChatUserProfileProfile represents a User.  It has a one to one field linking it to
		django's user model.
	'''
 	user = models.OneToOneField(User)

 	@staticmethod
 	def createuser(username, email=None, password=None, **kwargs):
 		''' Used to create a new chat user.  Will also create the underlying django user
 			as well.
 			@input username: Username, must be unique
 			@input email (default=None): Email for user
 			@input password (default=None): User password
 			@returns user profile object
 		'''
 		cuser = User.objects.create_user(username=username, email=email,
 			password=password, **kwargs)
 		return ChatUserProfile(user=cuser)

	def __str__(self):
		return self.user.username
 			

class Message(models.Model):
	''' This represents a single message sent during chat.  It has a unique alpha numeric
		pseduorandom message_id, the text of the actual message, the timestamp of when the
		message was sent, and a foreign key linking it to the sender
	'''
	message_id = models.CharField(primary_key=True, max_length=36, unique=True,
		editable=False, default=uuid.uuid4().hex)
	text = models.CharField(editable=False, max_length=256)
	timestamp = models.DateTimeField(auto_now_add=True, verbose_name='date submitted')
	sender = models.ForeignKey(ChatUserProfile)

	def save(self, *args, **kwargs):
		''' This successfully saves the message into the database.  If the message_id
			initially created isn't unique, this will create a new one until it succeeds
			in finding a unique one.
		'''
		success = False
		while success==False:
			try:
				# see https://docs.djangoproject.com/en/dev/topics/db/transactions/
				with transaction.atomic():
					super(Message, self).save(*args, **kwargs)
				success = True
			except IntegrityError as e:
				self.message_id = uuid.uuid4().hex
				success = False

	def __str__(self):
		return ''.join([self.sender.user.username,self.text])


class Conversation(models.Model):
	''' Conversation represents one conversation that's taking place.  It has many
		participants and many messages.
	'''
	participants = models.ManyToManyField(ChatUserProfile)
	messages = models.ManyToManyField(Message)

	def __str__(self):
		return ':'.join(["Conversation",self.pk])