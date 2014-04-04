#import uuid
import datetime
from django.utils import timezone
from django.db import models
from django.contrib.auth.models import User

# Create your models here.


# class ChatUser(User):
# 	pass

class Message(models.Model):
	#make message_id alphanumeric unique identifier... index on it instead of primary key?
	#collisions possible
	message_id = models.CharField(max_length=36, primary_key=True, editable=False, unique=True, default=Message.messageIdGenerator())
	text = models.CharField(editable=False, max_length=256)
	timestamp = models.DateTimeField(auto_now_add=True, verbose_name='date submitted')
	sender = models.ForeignKey(User)

	@staticmethod
	def messageIdGenerator():
		return uuid.uuid4();


class Conversation(models.Model):
	participants = models.ManyToManyField(User)
	messages = models.ManyToManyField(Message)