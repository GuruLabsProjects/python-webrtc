import uuid, datetime, posixpath, logging, json

from django.utils import timezone
from django.db import models, IntegrityError

from django.test import TestCase
from django.test.client import RequestFactory
from django.core.urlresolvers import reverse

from django.contrib.auth.models import User, UserManager
from django.forms.models import model_to_dict

from .models import ChatUserProfile, Message, Conversation
from .views import (UserRestView, UserCreateView, MessageRestView, MessageCreateView,
	ConversationCreateView, ConversationRestView)

logger = logging.getLogger(__name__)

CORE_ASSETLIST_JS = ('jquery', 'underscore', 'backbone', 'modernizr', 'foundation')
CORE_ASSETLIST_CSS = ('normalize', 'foundation')


API_SUCCESS = 'success'
API_FAIL = 'fail'
API_ERROR = 'error'
API_OBJECT_CREATE = 'object-create'
API_OBJECT_UPDATE = 'object-update'
API_OBJECT_DELETE = 'object-delete'

username = 'testuser'


class DatabaseTests(TestCase):

	def __init__(self, *args, **kwargs):
		self.user = None
		super(DatabaseTests, self).__init__(*args, **kwargs)

	def testCreateUserProfile(self):
		''' Tests the creation of a chat user and user profile
		'''
		# Create test user
		user = User.objects.create(username=username)
		user.save()
		# Create user profile
		userp = ChatUserProfile(user=user)
		userp.save()

		# Do some basic tests to make sure it's saved into the database properly
		self.assertEqual(username, user.username)
		self.assertEqual(user.username, ChatUserProfile.objects.get(pk=user.pk).user.username)
		self.assertEqual(len(ChatUserProfile.objects.all()), 1)


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

	def tearDown(self):
		self.user.delete()
		self.user.save()

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
