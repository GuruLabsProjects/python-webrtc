import uuid, datetime, posixpath, logging, json

from django.utils import timezone
from django.db import models, IntegrityError

from django.core import serializers
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import RequestFactory

from django.contrib.auth.models import User, UserManager
from django.forms.models import model_to_dict

from .util import DateTimeAwareEncoder, DateTimeAwareDecoder

from .models import Profile, Message, Conversation
from .forms import ProfileForm, UserForm, MessageForm, ConversationForm
from .views import (UserRestView, UserCreateView, MessageRestView, MessageCreateView,
	ConversationCreateView, ConversationRestView, ProfileRestView, ProfileCreateView,
	API_FAIL, API_ERROR, API_RESULT, API_SUCCESS)

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

class GenericViewTests(TestCase):
	def testIndexPage(self):
		'''	Verify that the application is able to retrieve the index page.
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
		self.user = User.objects.create_user(username=username)
		self.user.save()
		self.view = UserRestView()
		self.createView = UserCreateView()

	def testGetSuccess(self):
		dummyGet = self.factory.get(reverse('chat:api:user-rest', args=str(self.user.pk)))
		response = self.view.get(dummyGet, pk=str(self.user.pk))

		userObj = json.loads(response.content, cls=DateTimeAwareDecoder)
		userForm = UserForm(userObj, instance=User.objects.get(
			pk=self.user.id))

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

	def testPostSuccess(self):
		userDict = model_to_dict(self.user)
		# invalidPk isn't used in db yet (not enforced by anything but for the tests to
		#	work thats how it has to be)
		userDict['id'] = None
		userDict['username'] = 'guru_labs'
		count = len(User.objects.all())
		jsonData = json.dumps(userDict, cls=DateTimeAwareEncoder)
		dummyPost = self.factory.post(reverse('chat:api:user-create'), data=jsonData,
			content_type='application/json')

		response = self.createView.post(dummyPost, content_type='application/json')
		rdata = json.loads(response.content)
		self.assertEquals(count + 1, len(User.objects.all()))
		try:
			newUserObj = User.objects.get(pk=rdata['id'])
		except User.DoesNotExist:
			self.assertTrue(false)


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

	def testGet(self):
		dummyGet = self.factory.get(reverse('chat:api:profile-rest',
			args=(self.user.username, str(self.profile.pk))))
		response = self.view.get(dummyGet, pk=str(self.profile.pk),
			username=self.user.username)
		logger.log(2, response.content)
		response_user = json.loads(response.content, cls=DateTimeAwareDecoder)
		userForm = ProfileForm(response_user,
			instance=Profile.objects.get(pk=response_user['id']))
		#ensure the data we got is valid
		self.assertEqual(userForm.is_valid(), True)


class RestViewTest(TestCase):
	def testGet(self):
		pass

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

	def testGet(self):

		dummyGet = self.factory.get(reverse('chat:api:message-rest',
			args=(self.msg1.message_id, )))
		response = self.view.get(dummyGet, message_id=self.msg1.message_id)

		logger.log(2, response.content)

		response_message = json.loads(response.content, cls=DateTimeAwareDecoder)

		messageForm = MessageForm(response_message,
			instance=Message.objects.get(message_id=response_message['message_id']))

		#ensure the data we got is valid
		self.assertEqual(messageForm.is_valid(), True)

	def testDeleteSuccess(self):
		self.assertEquals(len(Message.objects.all()), 2)
		dummyDelete = self.factory.delete(reverse('chat:api:message-rest',
			args=(self.msg1.message_id, )))
		
		response = self.view.delete(dummyDelete, message_id=self.msg1.message_id)

		rdata = json.loads(response.content)
		self.assertEquals(len(Message.objects.all()), 1)
		with self.assertRaises(Message.DoesNotExist):
			Message.objects.get(message_id=rdata['id'])
