from django.test import TestCase
from chat.models import ChatUser, Message, Conversation
import uuid
import datetime
from django.utils import timezone
from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import UserManager

# Test cases for ChatUser model
class ChatUserTests(TestCase):

	# Test ChatUser creation
	def testCreateUser(self):
		user = ChatUser.createUser(username="aTestUsername")
		user.save()
		# Do some basic tests to make sure it's saved into the database properly
		self.assertEqual("aTestUsername", user.user.username)
		self.assertEqual("aTestUsername", ChatUser.objects.get(pk=user.pk).user.username)
		self.assertEqual(user.pk, ChatUser.objects.get(user=user).pk)
		self.assertEqual(user.user.pk, ChatUser.objects.get(user=user).user.pk)
		self.assertEqual(len(ChatUser.objects.all()), 1)


# Test cases for Message model
class MessageTests(TestCase):
	pass

# Test cases for Conversation model
class ConversationTests(TestCase):

	# Test Conversation creation
	def testCreateConversation(self):
		convo = Conversation()
		convo.save()
		self.assertEquals(len(Conversation.objects.all()), 1)

	# Test adding/removing of participants
	def testAddRemoveParticipants(self):
		user = ChatUser.createUser(username="Cam")
		user.save()
		convo = Conversation()
		convo.save()
		convo.participants.add(user)
		users = []
		convo.save()
		for x in range(0, 29):
			users.append(ChatUser.createUser(username="test" + str(x)))
			users[x].save()
		convo.participants.add(*users)
		convo.save()
		self.assertEqual(len(convo.participants.all()), len(Conversation.objects.get(pk=convo.pk).participants.all()))

		before = len(convo.participants.all())
		convo.participants.remove(users[0])
		convo.save()
		self.assertEqual(before-1, len(convo.participants.all()))
		convo.participants.remove(*users[1:])
		self.assertEqual(1, len(convo.participants.all()))
		self.assertEqual("Cam", convo.participants.all()[0].user.username)

	def testAddRemoveMessages(self):
		users = []
		for x in range(0, 33):
			users.append(ChatUser.createUser(username="test" + str(x)))
			users[x].save()
		msgs = []
		for x in range(0, 99):
			msgs.append(Message(sender=ChatUser.objects.get(username="test" + str(x/3)).pk, text="some text " + str(x)))
			msgs[x].save()
		convo = Conversation()
		convo.add(*users)
		convo.add(*msgs)


