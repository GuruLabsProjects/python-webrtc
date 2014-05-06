import uuid, datetime, posixpath, logging, json

from django.utils import timezone
from django.db import models, transaction, IntegrityError

from django.core import serializers
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import RequestFactory, Client

from django.contrib.auth.models import User, UserManager
from django.forms.models import model_to_dict

from .helpers import DateTimeAwareEncoder, DateTimeAwareDecoder

from .models import Profile, Message, Conversation
from .forms import ProfileForm, UserForm, MessageForm, ConversationForm
from .views import (UserCreateView, UserAuthenticateView, UserRestView, ProfileRestView,
	ProfileCreateView, MessageRestView, MessageCreateView, ConversationRestView,
	ConversationCreateView, API_RESULT, API_SUCCESS, API_FAIL, API_ERROR)

logger = logging.getLogger(__name__)

CORE_ASSETLIST_JS = ('jquery', 'underscore', 'backbone', 'modernizr', 'foundation')
CORE_ASSETLIST_CSS = ('normalize', 'foundation')

username = 'testuser'
invalidPk = 9999


class DatabaseTests(TestCase):

	def __init__(self, *args, **kwargs):
		super(DatabaseTests, self).__init__(*args, **kwargs)

	def testCreateUserProfile(self):
		''' Tests the creation of a chat user and user profile
		'''
		# Create test user
		user = User.objects.create(username=username)
		user.save()
		# Create user profile
		userp = Profile(user=user)
		userp.save()

		# Do some basic tests to make sure it's saved into the database properly
		self.assertEqual(username, user.username)
		self.assertEqual(user.username, Profile.objects.get(pk=user.pk).user.username)
		self.assertEqual(len(Profile.objects.all()), 1)

	def testConversationIds(self):
		convo = Conversation()
		convo.save()
		self.assertFalse((convo.id == '') or (convo.id is None), "Something isn't working"
			+ " with conversation id generation")

	def testMessageIds(self):
		user = User.objects.create(username=username)
		msg = Message(sender=user, text='heres some text')
		msg.save()
		self.assertFalse((msg.id == '') or (msg.id is None), "Something isn't working"
			+ " with message id generation")


class GenericViewTests(TestCase):

	def testIndexPage(self):
		'''	Verify that the application is able to retrieve the index page and that
			all base assets are available.
		'''
		r = self.client.get(reverse('chat:appindex'))
		self.assertEqual(200, r.status_code)
		# Check page title
		self.assertIn('Guru Labs Chat Demo Application', r.content)
		# Verify that all core assets are available for use
		for assetlist in (CORE_ASSETLIST_JS, CORE_ASSETLIST_CSS):
			for assetname in assetlist: self.assertIn(assetname, r.content)

	def testDebug(self):
		pass


class UserViewTests(TestCase):

	def __init__(self, *args, **kwargs):
		self.factory = RequestFactory()
		self.user = None
		super(UserViewTests, self).__init__(*args, **kwargs)

	def setUp(self):
		# Create test user
		self.user = User.objects.create_user(username=username, password='work')
		self.user.save()
		# self.client.login(username='guru', password='work')
		# session = self.client.session
		# session['key']='value'
		# session.save()
		self.view = UserRestView()
		self.createView = UserCreateView()
		self.authView = UserAuthenticateView()

	def testGetSuccess(self):
		dummyGet = self.factory.get(reverse('chat:api:user-rest', args=str(self.user.pk)))
		response = self.view.get(dummyGet, pk=str(self.user.pk))
		# response = self.client.get(dummyGet, pk=str(self.user.pk))

		userObj = json.loads(response.content, cls=DateTimeAwareDecoder)
		userForm = UserForm(userObj, instance=User.objects.get(
			pk=self.user.pk))

		self.assertEqual(userForm.is_valid(), True)

	def testGetError(self):
		dummyGet = self.factory.get(reverse('chat:api:user-rest', args=str(self.user.pk)))
		response = self.view.get(dummyGet, pk=invalidPk)
		
		userObj = json.loads(response.content, cls=DateTimeAwareDecoder)
		userForm = UserForm(userObj, instance=User.objects.get(
			pk=self.user.id))

		self.assertEqual(userForm.is_valid(), False)

	def testPutSuccess(self):
		userDict = model_to_dict(self.user)
		userDict['email'] = 'guru@gurulabs.com'
		jsonData = json.dumps(userDict, cls=DateTimeAwareEncoder)

		dummyPut = self.factory.put(reverse('chat:api:user-rest', args=(
			str(self.user.pk), ) ), jsonData)
		response = self.view.put(dummyPut, content_type='application/json', pk=str(self.user.pk))

		rdata = json.loads(response.content)

		self.assertEquals(rdata[API_RESULT], API_SUCCESS)
		logger.log(2, response.content)
		self.assertEquals(User.objects.get(pk=self.user.pk).email, userDict['email'])

	def testPutError(self):
		userDict = model_to_dict(self.user)
		userDict['email'] = 'guru@gurulabs.com'
		jsonData = json.dumps(userDict, cls=DateTimeAwareEncoder)

		dummyPut = self.factory.put(reverse('chat:api:user-rest', args=(
			invalidPk, ) ), jsonData)
		response = self.view.put(dummyPut, content_type='application/json', pk=str(invalidPk))
		rdata = json.loads(response.content)

		self.assertEquals(User.objects.get(pk=self.user.pk).email, '')
		self.assertEquals(rdata[API_RESULT], API_FAIL)

		self.assertTrue(rdata[API_ERROR] is not None)

	def testUserAuthenticate(self):
		#tests user authentication
		u = User.objects.create_user(username='guru')
		u.set_password('work')
		u.save()

		userDict = model_to_dict(u)
		userDict['password'] = 'work'

		jsonData = json.dumps(userDict, cls=DateTimeAwareEncoder)

		response = self.client.post(reverse('chat:api:user-authenticate'), data=jsonData, content_type='application/json')
		rdata = json.loads(response.content)

		self.assertEqual(rdata[API_RESULT], API_SUCCESS)
		self.assertEqual(response.status_code, 200)


	def testUserRegisterSuccess(self):
		userDict = {}
		userDict['username'] = 'gurulab'
		userDict['first_name'] = 'Mr'
		userDict['last_name'] = 'Guru'
		userDict['email'] = 'guru@guru.com'
		userDict['password'] = 'work'
		userDict['verify_password'] = 'work'

		count = len(User.objects.all())
		countProfiles = len(Profile.objects.all())
		jsonData = json.dumps(userDict, cls=DateTimeAwareEncoder)
		dummyPost = self.factory.post(reverse('chat:api:user-create'), data=jsonData,
			content_type='application/json')

		response = self.createView.post(dummyPost, content_type='application/json')
		rdata = json.loads(response.content)

		self.assertEquals(rdata[API_RESULT], API_SUCCESS)
		self.assertEquals(count + 1, len(User.objects.all()))
		self.assertEquals(countProfiles + 1, len(Profile.objects.all()))
		try:
			newUserObj = User.objects.get(pk=rdata['id'])
			profile = Profile.objects.get(user=newUserObj)
		except User.DoesNotExist:
			self.assertTrue(False, "User doesn't exist when it should...")
		except Profile.DoesNotExist:
			self.assertFalse(True, "Profile creation didn't occur")

	def testUserRegisterFail(self):
		userDict = {}
		userDict['username'] = 'gurulab'
		userDict['first_name'] = 'Mr'
		userDict['last_name'] = 'Guru'
		userDict['email'] = 'guru@guru.com'
		userDict['password'] = 'work'
		userDict['verify_password'] = 'not_work'

		count = len(User.objects.all())
		jsonData = json.dumps(userDict, cls=DateTimeAwareEncoder)
		dummyPost = self.factory.post(reverse('chat:api:user-create'), data=jsonData,
			content_type='application/json')

		response = self.createView.post(dummyPost, content_type='application/json')
		rdata = json.loads(response.content)


		self.assertEquals(rdata[API_RESULT], API_FAIL)
		self.assertEquals(count, len(User.objects.all()))

	def testDeleteSuccess(self):
		self.assertEquals(len(User.objects.all()), 1)
		dummyDelete = self.factory.delete(reverse('chat:api:user-rest',
			args=(self.user.pk, )))
		
		response = self.view.delete(dummyDelete, pk=self.user.pk)

		rdata = json.loads(response.content)
		self.assertEquals(len(User.objects.all()), 0)
		with self.assertRaises(User.DoesNotExist):
			User.objects.get(pk=rdata['id'])

	def testDeleteFailure(self):
		self.assertEquals(len(User.objects.all()), 1)
		dummyDelete = self.factory.delete(reverse('chat:api:user-rest',
			args=(self.user.pk + 1, )))
		
		response = self.view.delete(dummyDelete, pk=self.user.pk + 1)

		rdata = json.loads(response.content)
		self.assertEquals(rdata[API_RESULT], API_FAIL)
		self.assertEquals(len(User.objects.all()), 1)


	def testPostFailure(self):
		userDict = model_to_dict(self.user)
		# invalidPk isn't used in db yet (not enforced by anything but for the tests to
		#	work thats how it has to be)
		userDict['id'] = self.user.pk
		userDict['username'] = username
		count = len(User.objects.all())

		jsonData = json.dumps(userDict, cls=DateTimeAwareEncoder)
		dummyPost = self.factory.post(reverse('chat:api:user-create'), data=jsonData,
			content_type='application/json')

		response = self.createView.post(dummyPost, content_type='application/json')
		rdata = json.loads(response.content)

		# 
		self.assertEquals(rdata[API_RESULT], API_FAIL)
		self.assertEquals(count, len(User.objects.all()))


class ProfileViewTests(TestCase):
	def __init__(self, *args, **kwargs):
		self.factory = RequestFactory()
		self.user = None
		self.profile = None
		super(ProfileViewTests, self).__init__(*args, **kwargs)

	def setUp(self):
		# Create test user
		self.user = User.objects.create_user(username=username)
		self.profile = Profile(user=self.user)
		self.user.save()
		self.profile.save()
		self.view = ProfileRestView()
		self.createView = ProfileCreateView()

	def testGet(self):
		dummyGet = self.factory.get(reverse('chat:api:profile-rest',
			args=(self.user.username, )))
		response = self.view.get(dummyGet, pk=str(self.profile.pk),
			username=self.user.username)
		
		response_user = json.loads(response.content, cls=DateTimeAwareDecoder)
		userForm = ProfileForm(response_user,
			instance=Profile.objects.get(pk=response_user['id']))
		#ensure the data we got is valid
		self.assertEqual(userForm.is_valid(), True)

	def testGetError(self):
		dummyGet = self.factory.get(reverse('chat:api:profile-rest',
			args=(self.user.username, )))
		response = self.view.get(dummyGet, pk=str(self.profile.pk + 1))
		
		profileObj = json.loads(response.content, cls=DateTimeAwareDecoder)
		profileForm = ProfileForm(profileObj, instance=Profile.objects.get(
			pk=self.profile.pk))

		self.assertEqual(profileObj[API_RESULT], API_FAIL)

		self.assertEqual(profileForm.is_valid(), False)

	def testPutSuccess(self):
		#Not really sure what to test here since Profile (so far) only has a one to one
		#	method.  Maybe try changing the id?
		user = User.objects.create_user(username='another_user')
		user.save()
		self.profile.user = user
		profileDict = model_to_dict(self.profile)
		jsonData = json.dumps(profileDict, cls=DateTimeAwareEncoder)

		dummyPut = self.factory.put(reverse('chat:api:profile-rest', 
			args=(self.user.username, ) ), jsonData)

		response = self.view.put(dummyPut, content_type='application/json',
			pk=str(self.profile.pk))

		rdata = json.loads(response.content)

		self.assertEquals(rdata[API_RESULT], API_SUCCESS)
		self.assertNotEquals(Profile.objects.get(pk=self.profile.pk).user.pk, self.user.pk)
		self.assertEquals(Profile.objects.get(pk=self.profile.pk).user.pk, user.pk)

	def testPutFailure(self):
		#Not really sure what to test here since Profile (so far) only has a one to one
		#	method.  Maybe try changing the id?
		user = User.objects.create_user(username='another_user')
		user.save()
		self.profile.user = user
		profileDict = model_to_dict(self.profile)
		jsonData = json.dumps(profileDict, cls=DateTimeAwareEncoder)

		dummyPut = self.factory.put(reverse('chat:api:profile-rest', 
			args=(self.user.username, ) ), jsonData)

		response = self.view.put(dummyPut, content_type='application/json',
			pk=str(self.profile.pk + 1))

		rdata = json.loads(response.content)

		self.assertEquals(rdata[API_RESULT], API_FAIL)
		self.assertEquals(Profile.objects.get(pk=self.profile.pk).user.pk, self.user.pk)
		self.assertNotEquals(Profile.objects.get(pk=self.profile.pk).user.pk, user.pk)

	def testDeleteSuccess(self):
		self.assertEquals(len(Profile.objects.all()), 1)
		dummyDelete = self.factory.delete(reverse('chat:api:profile-rest',
			args=(self.user.username, )))
		
		response = self.view.delete(dummyDelete, pk=self.profile.pk)

		rdata = json.loads(response.content)
		self.assertEquals(len(Profile.objects.all()), 0)
		with self.assertRaises(Profile.DoesNotExist):
			Profile.objects.get(pk=rdata['id'])

	def testDeleteFailure(self):
		self.assertEquals(len(Profile.objects.all()), 1)
		dummyDelete = self.factory.delete(reverse('chat:api:profile-rest',
			args=(self.user.username, )))
		
		response = self.view.delete(dummyDelete, pk=self.profile.pk + 1)

		rdata = json.loads(response.content)
		self.assertEquals(rdata[API_RESULT], API_FAIL)
		self.assertEquals(len(Profile.objects.all()), 1)

	def testPostSuccess(self):
		user = User.objects.create_user(username='another_user')
		user.save()
		self.profile.user = user
		profileDict = model_to_dict(self.profile)

		count = len(Profile.objects.all())
		jsonData = json.dumps(profileDict, cls=DateTimeAwareEncoder)
		dummyPost = self.factory.post(reverse('chat:api:profile-create', 
			args=(self.user.username, )), data=jsonData,
			content_type='application/json')

		response = self.createView.post(dummyPost, content_type='application/json')
		rdata = json.loads(response.content)
		self.assertEquals(count + 1, len(Profile.objects.all()))
		try:
			newProfileObj = Profile.objects.get(pk=rdata['id'])
		except Profile.DoesNotExist:
			self.assertTrue(false, "error with profile post")

	def testPostFailure(self):
		user = User.objects.create_user(username='another_user')
		user.save()
		user.pk = invalidPk
		self.profile.user = user
		profileDict = model_to_dict(self.profile)

		count = len(Profile.objects.all())
		jsonData = json.dumps(profileDict, cls=DateTimeAwareEncoder)
		dummyPost = self.factory.post(reverse('chat:api:profile-create', 
			args=(self.user.username, )), data=jsonData,
			content_type='application/json')

		response = self.createView.post(dummyPost, content_type='application/json')
		rdata = json.loads(response.content)
		self.assertEquals(count, len(Profile.objects.all()))
		self.assertEquals(rdata[API_RESULT], API_FAIL)


class MessageViewTest(TestCase):
	def __init__(self, *args, **kwargs):
		self.factory = RequestFactory()
		self.user = None
		self.conversation = None
		self.msg1 = None
		self.msg2 = None
		super(MessageViewTest, self).__init__(*args, **kwargs)

	def setUp(self):
		# Create test user
		self.user = User.objects.create_user(username=username)
		self.user.save()
		self.msg1 = Message(sender=self.user, text="heres the first message")
		self.msg1.save()

		self.msg2 = Message(sender=self.user, text="heres the second message")
		self.msg2.save()
		
		self.conversation = Conversation()
		self.conversation.save()
		self.conversation.participants.add(self.user)
		self.conversation.messages.add(self.msg1)
		self.conversation.messages.add(self.msg2)
		self.conversation.save()
		self.view = MessageRestView()
		self.createView = MessageCreateView()

	def testGetSuccess(self):
		dummyGet = self.factory.get(reverse('chat:api:message-rest',
			args=(self.conversation.pk, self.msg1.id, )))
		response = self.view.get(dummyGet, pk=self.msg1.id)

		response_message = json.loads(response.content, cls=DateTimeAwareDecoder)

		messageForm = MessageForm(response_message,
			instance=Message.objects.get(pk=response_message['id']))

		#ensure the data we got is valid
		self.assertEqual(messageForm.is_valid(), True)

	def testGetFail(self):
		dummyGet = self.factory.get(reverse('chat:api:message-rest',
			args=(self.conversation.pk, 'bogusmessageid', )))
		response = self.view.get(dummyGet, pk='bogusmessageid')

		response_message = json.loads(response.content, cls=DateTimeAwareDecoder)

		self.assertEquals(response_message[API_RESULT], API_FAIL)

		with self.assertRaises(Message.DoesNotExist):
			msg = Message.objects.get(pk='bogusmessageid')

	def testDeleteSuccess(self):
		self.assertEquals(len(Message.objects.all()), 2)
		dummyDelete = self.factory.delete(reverse('chat:api:message-rest',
			args=(self.conversation.pk, self.msg1.id, )))
		
		response = self.view.delete(dummyDelete, pk=self.msg1.id)

		rdata = json.loads(response.content)
		self.assertEquals(len(Message.objects.all()), 1)
		with self.assertRaises(Message.DoesNotExist):
			Message.objects.get(pk=rdata['id'])

	def testDeleteFailure(self):
		self.assertEquals(len(Message.objects.all()), 2)
		dummyDelete = self.factory.delete(reverse('chat:api:message-rest',
			args=(self.conversation.pk, 'bogusmessageid', )))
		
		response = self.view.delete(dummyDelete, pk='bogusmessageid')

		rdata = json.loads(response.content)
		self.assertEquals(len(Message.objects.all()), 2)
		self.assertEquals(rdata[API_RESULT], API_FAIL)

	def testPut(self):
		#this should always fail
		user = User.objects.create_user(username='bogusGuru')
		user.save()
		self.msg1.sender = user
		messageDict = model_to_dict(self.msg1)
		jsonData = json.dumps(messageDict, cls=DateTimeAwareEncoder)

		dummyPut = self.factory.put(reverse('chat:api:message-rest', args=(
			self.conversation.pk, self.msg1.pk, ) ), jsonData)
		response = self.view.put(dummyPut, content_type='application/json', pk=str(self.msg1.pk))

		self.assertTrue(response.status_code == 400)

	def testPostSuccess(self):
		msg = Message(sender=self.user, text='new message')
		msg.id = 'uniqueuniqueunique'
		messageDict = model_to_dict(msg)
		
		count = len(Message.objects.all())
		jsonData = json.dumps(messageDict, cls=DateTimeAwareEncoder)

		dummyPost = self.factory.post(reverse('chat:api:message-create', args=(self.conversation.pk, )), data=jsonData,
			content_type='application/json')

		response = self.createView.post(dummyPost, content_type='application/json', cpk=self.conversation.pk)

		rdata = json.loads(response.content)

		self.assertEquals(count + 1, len(Message.objects.all()))
		try:
			newMessageObj = Message.objects.get(pk=rdata['id'])
			self.assertTrue(newMessageObj in Conversation.objects.get(
				pk=self.conversation.pk).messages.all())
		except Message.DoesNotExist:
			self.assertTrue(false, "error with message post")
		self.assertTrue(Message.objects.get(pk=rdata['id']).text == msg.text)

	def testPostFailure(self):
		msg = Message(sender=self.user, text='new message')
		msg.id = self.msg1.id
		messageDict = model_to_dict(msg)
		
		count = len(Message.objects.all())
		jsonData = json.dumps(messageDict, cls=DateTimeAwareEncoder)
		dummyPost = self.factory.post(reverse('chat:api:message-create', args=(self.conversation.pk, )), data=jsonData,
			content_type='application/json')

		response = self.createView.post(dummyPost, content_type='application/json', cpk=self.conversation.pk)

		rdata = json.loads(response.content)

		self.assertEquals(rdata[API_RESULT], API_FAIL)
		self.assertEquals(count, len(Message.objects.all()))

class ConversationViewTests(TestCase):
	def __init__(self, *args, **kwargs):
		self.factory = RequestFactory()
		self.user = None
		self.conversation = None
		self.msg1 = None
		self.msg2 = None
		super(self.__class__, self).__init__(*args, **kwargs)

	def setUp(self):
		# Create test user
		self.user = User.objects.create_user(username=username)
		self.user.save()
		self.msg1 = Message(sender=self.user, text="heres the first message")
		self.msg1.save()

		self.msg2 = Message(sender=self.user, text="heres the second message")
		self.msg2.save()
		
		self.conversation = Conversation()
		self.conversation.save()
		self.conversation.participants.add(self.user)
		self.conversation.messages.add(self.msg1)
		self.conversation.messages.add(self.msg2)
		self.conversation.save()
		self.view = ConversationRestView()
		self.createView = ConversationCreateView()

	def testGetSuccess(self):
		dummyGet = self.factory.get(reverse('chat:api:conversation-rest', args=(self.conversation.id, )))
		response = self.view.get(dummyGet, pk=str(self.conversation.id))

		msgs = json.loads(response.content, cls=DateTimeAwareDecoder)

		dbmsgs = Conversation.objects.get(pk=self.conversation.id).messages.all()

		self.assertEquals(len(msgs), len(dbmsgs))

		for msg in msgs:
			foundIt = False
			for dbmsg in dbmsgs:
				if msg['id'] == dbmsg.id:
					if msg['text'] is dbmsg.text:
						foundIt = True
						break
			self.assertFalse(foundIt, "%s not found in %s" % (msg, str(dbmsgs)))

	def testPostSuccess(self):
		convo = Conversation()
		conversationDict = model_to_dict(convo)
		count = len(Conversation.objects.all())
		jsonData = json.dumps(conversationDict, cls=DateTimeAwareEncoder)
		dummyPost = self.factory.post(reverse('chat:api:conversation-create'), data=jsonData,
			content_type='application/json')

		response = self.createView.post(dummyPost, content_type='application/json')

		rdata = json.loads(response.content)

		self.assertEquals(count + 1, len(Conversation.objects.all()))
		try:
			newConvoObj = Conversation.objects.get(pk=rdata['id'])
		except Conversation.DoesNotExist:
			self.assertTrue(false, "error with message post")

	def testPut(self):
		#this should always fail
		convo = Conversation()
		convo.save()
		convo.participants.add(self.user)
		
		convoDict = model_to_dict(convo)
		jsonData = json.dumps(convoDict, cls=DateTimeAwareEncoder)

		dummyPut = self.factory.put(reverse('chat:api:conversation-rest', args=(
			str(convo.pk), ) ), jsonData)
		response = self.view.put(dummyPut, content_type='application/json',
			pk=str(convo.pk))

		rdata = json.loads(response.content)

		self.assertTrue(rdata[API_RESULT], API_FAIL)
		self.assertTrue(response.status_code == 400)

	def testDelete(self):
		#this should always fail
		dummyPut = self.factory.delete(reverse('chat:api:conversation-rest',
			args=(self.conversation.id, ) ))
		response = self.view.delete(dummyPut, 
			content_type='application/json', pk=str(self.conversation.id))

		self.assertTrue(response.status_code == 400)

	# def testPostFailure(self):
	# 	badDict = model_to_dict(self.user)
		
	# 	count = len(Conversation.objects.all())
	# 	jsonData = json.dumps(badDict, cls=DateTimeAwareEncoder)
	# 	dummyPost = self.factory.post(reverse('chat:api:conversation-create'), data=jsonData,
	# 		content_type='application/json')

	# 	response = self.createView.post(dummyPost, content_type='application/json')

	# 	rdata = json.loads(response.content)
		

	# 	self.assertEquals(count, len(Conversation.objects.all()))
	# 	self.assertEquals(rdata[API_RESULT], API_FAIL)
