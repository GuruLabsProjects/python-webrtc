import uuid
import datetime
from django.utils import timezone
from django.db import models, IntegrityError, transaction
from django.contrib.auth.models import User

class ChatUser(models.Model):
 	user = models.OneToOneField(User)

 	@staticmethod
 	def createUser(username, email=None, password=None, **kwargs):
 		cuser = User.objects.create_user(username=username, email=email, password=password, **kwargs)
 		return ChatUser(user=cuser)

	def __str__(self):
		return self.user.username
 			

class Message(models.Model):
	message_id = models.CharField(primary_key=True, max_length=36, unique=True, editable=False, default=uuid.uuid4().hex)
	text = models.CharField(editable=False, max_length=256)
	timestamp = models.DateTimeField(auto_now_add=True, verbose_name='date submitted')
	sender = models.ForeignKey(ChatUser)

	def save(self, *args, **kwargs):
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
		return "(" + self.sender.user.username + " : " + self.text + ")"



class Conversation(models.Model):
	participants = models.ManyToManyField(ChatUser)
	messages = models.ManyToManyField(Message)