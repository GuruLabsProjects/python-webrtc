import uuid
import datetime
from django.utils import timezone
from django.db import models
from django.test import TestCase
from django.contrib.auth.models import User, UserManager
from chat.models import ChatUserProfile, Message, Conversation

# Test cases for ChatUserProfile model
class ChatUserProfileTests(TestCase):

	# Test ChatUserProfile creation
	def testCreateUser(self):
		''' Tests the creation of a new chat user
		'''
		user = ChatUserProfile.createuser(username="aTestUsername")
		user.save()
		# Do some basic tests to make sure it's saved into the database properly
		self.assertEqual("aTestUsername", user.user.username)
		self.assertEqual("aTestUsername", ChatUserProfile.objects.get(pk=user.pk).user.username)
		self.assertEqual(user.pk, ChatUserProfile.objects.get(user=user).pk)
		self.assertEqual(user.user.pk, ChatUserProfile.objects.get(user=user).user.pk)
		self.assertEqual(len(ChatUserProfile.objects.all()), 1)


# Test cases for Message model
class MessageTests(TestCase):
	def testUniqueness(self):
		''' Tests to ensure the save() method of Message model works properly.  Set 
			message_id of two messages to the same thing, save them both, and one of them
			should be overwritten to a new pseduo random alphanumeric value.
		'''
		user = ChatUserProfile.createuser(username="Cam")
		user.save()
		convo = Conversation()
		convo.save()
		msg = Message(sender=user, text="some text msg1", message_id='abc123')
		msg1 = Message(sender=user, text="some text msg2", message_id='abc123')
		msg.save()
		msg1.save()
		self.assertNotEqual(msg.message_id, msg1.message_id)
		print msg.message_id,' vs ',msg1.message_id

# Test cases for Conversation model
class ConversationTests(TestCase):
	''' basic testing of conversation modal
	'''
	# Test Conversation creation
	def testCreateConversation(self):
		convo = Conversation()
		convo.save()
		self.assertEquals(len(Conversation.objects.all()), 1)

	# Test adding/removing of participants
	def testAddRemoveParticipants(self):
		user = ChatUserProfile.createuser(username="Cam")
		user.save()
		convo = Conversation()
		convo.save()
		convo.participants.add(user)
		users = []
		convo.save()
		for x in range(0, 29):
			users.append(ChatUserProfile.createuser(username="test" + str(x)))
			users[x].save()
		convo.participants.add(*users)
		convo.save()
		self.assertEqual(len(convo.participants.all()), len(Conversation.objects.get(
			pk=convo.pk).participants.all()))

		before = len(convo.participants.all())
		convo.participants.remove(users[0])
		convo.save()
		self.assertEqual(before-1, len(convo.participants.all()))
		convo.participants.remove(*users[1:])
		self.assertEqual(1, len(convo.participants.all()))
		self.assertEqual("Cam", convo.participants.all()[0].user.username)

	def testAddRemoveMessages(self):
		users = []
		msgs = []
		for x in range(0, 99):
			users.append(ChatUserProfile.createuser(username="test" + str(x)))
			users[x].save()
			msgs.append(Message(sender=users[x], text="some text " + str(x)))
			msgs[x].save()
		

		convo = Conversation()
		convo.save()
		convo.participants.add(*users)
		convo.messages.add(*msgs)
		convo.save()

		self.assertEqual(len(convo.messages.all()), 99)
		self.assertEqual(len(convo.participants.all()), 99)
		self.assertEqual(convo.messages.get(message_id=msgs[0].message_id).text,
			"some text 0")
		self.assertEqual(convo.messages.get(message_id=msgs[98].message_id).text,
			"some text 98")
		self.assertEqual(convo.messages.get(message_id=msgs[33].message_id).text,
			"some text 33")
		self.assertEqual(convo.participants.get(pk=users[0].pk).user.username, "test0")
		self.assertEqual(convo.messages.get(message_id=msgs[0].message_id).
			sender.user.username, "test0")

