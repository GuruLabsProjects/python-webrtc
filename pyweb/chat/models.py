import uuid
import datetime
from django.utils import timezone
from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import UserManager


# Create your models here.


class ChatUser(models.Model):
 	#user = models.ForeignKey(User)
 	user = models.OneToOneField(User)

 	@staticmethod
 	def createUser(username, email=None, password=None, **kwargs):
 		cuser = User.objects.create_user(username=username, email=email, password=password, **kwargs)
 		return ChatUser(user=cuser)

	def __str__(self):
		return self.user.username
 			

class Message(models.Model):
	#make message_id alphanumeric unique identifier... index on it instead of primary key?
	#collisions possible
	def messageIdGenerator():
		return uuid.uuid4().hex;

	message_id = models.CharField(primary_key=True, max_length=36, unique=True, editable=False, default=messageIdGenerator())
	text = models.CharField(editable=False, max_length=256)
	timestamp = models.DateTimeField(auto_now_add=True, verbose_name='date submitted')
	sender = models.ForeignKey(ChatUser)

	def save(self, *args, **kwargs):
		success = False
		while success==False:
			try:
				super(Message, self).save(*args, **kwargs)
				success = True
			except models.db.IntegrityError:
				success = False
		super.save(self, args, kwargs)



class Conversation(models.Model):
	participants = models.ManyToManyField(ChatUser)
	messages = models.ManyToManyField(Message)