import uuid, datetime, posixpath, logging, json
from django.utils import timezone
from django.db import models, IntegrityError
from django.test import TestCase
from django.test.client import RequestFactory
from django.forms.models import model_to_dict
from django.contrib.auth.models import User, UserManager
from .models import ChatUserProfile, Message, Conversation
from .views import (UserRestView, UserCreateView, MessageRestView, MessageCreateView,
	ConversationCreateView, ConversationRestView)


logger = logging.getLogger(__name__)

API_SUCCESS = 'success'
API_FAIL = 'fail'
API_ERROR = 'error'
API_OBJECT_CREATE = 'object-create'
API_OBJECT_UPDATE = 'object-update'
API_OBJECT_DELETE = 'object-delete'

class UserViewTests(TestCase):
	factory = RequestFactory()
	username = 'guru'
	user = None

	def setUp(self):
		# Create test user
		self.user = User.objects.create_user(username=self.username)
		self.user.save()
		self.view = UserRestView()
	
	def testGet(self):
		url_components = ['/chat/usr', str(self.user.pk)]
		dummyGet = self.factory.get(''.join(['/chat/usr/', str(self.user.pk)]))
		response = self.view.get(dummyGet,[], pk=str(self.user.pk))
		logger.log(2, response.content)
		response_user = json.loads(response.content)

	def testPut(self):
		dthandler = lambda obj: obj.isoformat() if isinstance(obj, datetime.datetime) or \
			isinstance(obj, datetime.date) else	json.JSONEncoder().default(obj)

		userDict = model_to_dict(self.user)
		userDict['email'] = 'guru@gurulabs.com'
		jsonData = json.dumps(userDict, default=dthandler)

		dummyPut = self.factory.put(''.join(['/chat/usr/',str(self.user.pk)]), jsonData)
		response = self.view.put(dummyPut, content_type='application/json', data=jsonData,
			pk=str(self.user.pk))

		logger.log(2, response.content)

		self.assertEquals(User.objects.get(pk=self.user.pk).email, userDict['email'])

	# Test ChatUserProfile creation
	# def testCreateUser(self):
	# 	''' Tests the creation of a chat user and user profile
	# 	'''
	# 	# Create user profile
	# 	userp = ChatUserProfile(user=self.user)
	# 	userp.save()

	# 	# Do some basic tests to make sure it's saved into the database properly
	# 	self.assertEqual(self.username, self.user.username)
	# 	self.assertEqual(self.user.username, ChatUserProfile.objects.get(pk=self.user.pk).user.username)
	# 	# self.assertEqual(user.pk, ChatUserProfile.objects.get(user=user).pk)
	# 	# self.assertEqual(user.user.pk, ChatUserProfile.objects.get(user=user).user.pk)
	# 	self.assertEqual(len(ChatUserProfile.objects.all()), 1)


# # Test cases for Message model
# class MessageTests(TestCase):
# 	def testUniqueness(self):
# 		''' Test to ensure an IntegrityError is raised when message_id is NOT unique
# 		'''
# 		user = User.objects.create_user(username="Cam")
# 		user.save()
# 		convo = Conversation()
# 		convo.save()
# 		msg = Message(sender=user, text="some text msg1", message_id='abc123')
# 		msg1 = Message(sender=user, text="some text msg2", message_id='abc123')
# 		msg.save()
# 		print ' '.join([str(msg.message_id), str(msg1.message_id)])
# 		with self.assertRaises(IntegrityError):
# 			msg1.save()
# 		# msg1.save()

# ##########all tests below here are just for Cam's learning for now.  They don't test any
# #	real functionality of anything other than django itself.

# # Test cases for Conversation model
# class ConversationTests(TestCase):
# 	''' basic testing of conversation modal
# 	'''
# 	# Test Conversation creation
# 	def testCreateConversation(self):
# 		convo = Conversation()
# 		convo.save()
# 		self.assertEquals(len(Conversation.objects.all()), 1)

# 	# Test adding/removing of participants
# 	def testAddRemoveParticipants(self):
# 		user = User.objects.create_user(username="Cam")
# 		user.save()
# 		convo = Conversation()
# 		convo.save()
# 		convo.participants.add(user)
# 		users = []
# 		convo.save()
# 		for x in range(0, 29):
# 			users.append(User.objects.create_user(username="test" + str(x)))
# 			users[x].save()
# 		convo.participants.add(*users)
# 		convo.save()
# 		self.assertEqual(len(convo.participants.all()), len(Conversation.objects.get(
# 			pk=convo.pk).participants.all()))

# 		before = len(convo.participants.all())
# 		convo.participants.remove(users[0])
# 		convo.save()
# 		self.assertEqual(before-1, len(convo.participants.all()))
# 		convo.participants.remove(*users[1:])
# 		self.assertEqual(1, len(convo.participants.all()))
# 		self.assertEqual("Cam", convo.participants.all()[0].username)

# 	def testAddRemoveMessages(self):
# 		users = []
# 		msgs = []
# 		for x in range(0, 99):
# 			users.append(User.objects.create_user(username="test" + str(x)))
# 			users[x].save()
# 			msgs.append(Message(sender=users[x], text="some text " + str(x)))
# 			msgs[x].save()
		
# 		self.assertEqual(len(msgs), 99)

# 		convo = Conversation()
# 		convo.save()
# 		convo.participants.add(*users)
# 		convo.messages.add(*msgs)
# 		convo.save()

# 		print 'HERE: '
# 		print convo.messages.all()

# 		self.assertEqual(len(convo.messages.all()), 99)
# 		self.assertEqual(len(convo.participants.all()), 99)
# 		self.assertEqual(convo.messages.get(message_id=msgs[0].message_id).text,
# 			"some text 0")
# 		self.assertEqual(convo.messages.get(message_id=msgs[98].message_id).text,
# 			"some text 98")
# 		self.assertEqual(convo.messages.get(message_id=msgs[33].message_id).text,
# 			"some text 33")
# 		self.assertEqual(convo.participants.get(pk=users[0].pk).username, "test0")
# 		self.assertEqual(convo.messages.get(message_id=msgs[0].message_id).
# 			sender.username, "test0")

