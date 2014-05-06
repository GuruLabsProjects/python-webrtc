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
	MessageRestView, MessageCreateView, ConversationRestView,
	ConversationCreateView, API_RESULT, API_SUCCESS, API_FAIL, API_ERROR)

logger = logging.getLogger(__name__)

CORE_ASSETLIST_JS = ('jquery', 'underscore', 'backbone', 'modernizr', 'foundation')
CORE_ASSETLIST_CSS = ('normalize', 'foundation')

username = 'testuser'
invalidPk = 9999

def login(client, username='guru', password='work', user=None):
	''' helper method to log user in.  If you specify user you must
		also specify password.
		@input client - required Test Unit Client
		@input username - optional (you must have this or user, if you use this it will
			create the user for you)
		@input password - required
		@input user - optional (you must have this or username)
	'''
	if user is None:
		u = User.objects.create_user(username=username)
		u.set_password(password)
	else:
		u = user
	u.save()

	userDict = model_to_dict(u)
	userDict['password'] = password

	client.user = u
	client.login(username='guru', password='work')

	jsonData = json.dumps(userDict, cls=DateTimeAwareEncoder)

	response = client.post(reverse('chat:api:user-authenticate'), data=jsonData,
		content_type='application/json')
	rdata = json.loads(response.content)

	if rdata[API_RESULT] != API_SUCCESS:
		raise Exception("Error logging in %s" % (rdata[API_ERROR]))
	if response.status_code != 200:
		raise Exception("Error logging in")
	return rdata


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
		''' tests the creation and saving of conversation ids
		'''
		convo = Conversation()
		convo.save()
		self.assertFalse((convo.id == '') or (convo.id is None), "Something isn't working"
			+ " with conversation id generation")

	def testMessageIds(self):
		''' tests the creation and saving of message ids
		'''
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


class UserViewTests(TestCase):

	def __init__(self, *args, **kwargs):
		self.factory = RequestFactory()
		self.user = None
		super(UserViewTests, self).__init__(*args, **kwargs)

	def setUp(self):
		# Create test user
		self.user = User.objects.create_user(username=username, password='work')
		self.user.save()
		self.view = UserRestView()
		self.createView = UserCreateView()
		self.authView = UserAuthenticateView()

	def testGetSuccess(self):
		''' tests a successfull User Get request
		'''
		login(self.client)
	
		response = self.client.get(reverse('chat:api:user-rest',
			args=(str(self.user.pk),)), pk=str(self.user.pk))

		userObj = json.loads(response.content, cls=DateTimeAwareDecoder)
		userForm = UserForm(userObj, instance=User.objects.get(
			pk=self.user.pk))

		self.assertEqual(userForm.is_valid(), True)

	def testGetError(self):
		''' tests an attempt to get an invalid user
		'''
		login(self.client)

		response = self.client.get(reverse('chat:api:user-rest', args=(str(invalidPk), )),
			pk=str(invalidPk))

		rdata = json.loads(response.content, cls=DateTimeAwareDecoder)

		self.assertEquals(rdata[API_RESULT], API_FAIL)
		self.assertEquals(response.status_code, 404)

	def testPutSuccess(self):
		''' Successfully updates a user through a Put request
		'''
		login(self.client)

		userDict = model_to_dict(self.user)
		userDict['email'] = 'guru@guru.com'

		jsonData = json.dumps(userDict, cls=DateTimeAwareEncoder)

		response = self.client.put(
			reverse('chat:api:user-rest',
			args=(self.user.pk, ) ),
			data=jsonData,
			content_type='application/json')

		rdata = json.loads(response.content)

		self.assertEquals(rdata[API_RESULT], API_SUCCESS)
		logger.log(2, response.content)
		self.assertEquals(User.objects.get(pk=self.user.pk).email, userDict['email'])

	def testPutError(self):
		''' unsuccessfully updates the user - invalid user id
		'''
		login(self.client)

		# userDict = model_to_dict(self.user)
		userDict = {}
		userDict['username'] = username
		userDict['first_name'] = 'Mr'
		userDict['last_name'] = 'Guru'
		userDict['email'] = 'guru@guru.com'
		userDict['password'] = 'work'
		userDict['verify_password'] = 'work'
		userDict['email'] = 'guru@gurulabs.com'
		jsonData = json.dumps(userDict, cls=DateTimeAwareEncoder)

		response = self.client.put(reverse('chat:api:user-rest', args=(invalidPk,)),
		 data=jsonData, content_type='application/json')

		rdata = json.loads(response.content)

		self.assertEquals(User.objects.get(pk=self.user.pk).email, '')
		self.assertEquals(rdata[API_RESULT], API_FAIL)

		self.assertTrue(rdata[API_ERROR] is not None)

	def testUserAuthenticate(self):
		''' tests the login method to ensure it's working
		'''
		rdata = login(self.client)
		self.assertEquals(rdata[API_RESULT], API_SUCCESS)


	def testUserRegisterSuccess(self):
		''' tests user register successfully
		'''
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

		response = self.client.post(reverse('chat:api:user-create'), data=jsonData,
			content_type='application/json')

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
		''' tests user register failure due to differing password/verify_password values
		'''
		userDict = {}
		userDict['username'] = 'gurulab'
		userDict['first_name'] = 'Mr'
		userDict['last_name'] = 'Guru'
		userDict['email'] = 'guru@guru.com'
		userDict['password'] = 'work'
		userDict['verify_password'] = 'not_work'

		count = len(User.objects.all())
		jsonData = json.dumps(userDict, cls=DateTimeAwareEncoder)

		response = self.client.post(reverse('chat:api:user-create'), data=jsonData,
			content_type='application/json')
		rdata = json.loads(response.content)


		self.assertEquals(rdata[API_RESULT], API_FAIL)
		self.assertEquals(count, len(User.objects.all()))

	def testUserRegisterFailUnuniqueUsername(self):
		''' tests user register failure due to username already in use
		'''
		user = User.objects.create_user(username='gurulab')
		user.save()
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

		response = self.client.post(reverse('chat:api:user-create'), data=jsonData,
			content_type='application/json')

		rdata = json.loads(response.content)

		self.assertEquals(rdata[API_RESULT], API_FAIL)
		self.assertEquals(count, len(User.objects.all()))
		self.assertEquals(countProfiles, len(Profile.objects.all()))


	def testDeleteSuccess(self):
		''' tests deletion of user through delete request
		'''
		login(self.client)

		count = len(User.objects.all())

		response = self.client.delete(reverse('chat:api:user-rest',
			args=(self.user.pk, )), content_type='application/json')

		rdata = json.loads(response.content)
		self.assertEquals(len(User.objects.all()), count - 1)

		with self.assertRaises(User.DoesNotExist):
			User.objects.get(pk=rdata['id'])

	def testDeleteFailure(self):
		''' failed delete due to invalid user id
		'''
		login(self.client)

		count = len(User.objects.all())
		response = self.client.delete(reverse('chat:api:user-rest',
			args=(invalidPk, )), content_type='application/json')

		rdata = json.loads(response.content)
		self.assertEquals(rdata[API_RESULT], API_FAIL)
		self.assertEquals(len(User.objects.all()), count)


	def testPostFailure(self):
		''' failed user create due to user id being the same as another id
		'''
		login(self.client)

		userDict = model_to_dict(self.user)
		# invalidPk isn't used in db yet (not enforced by anything but for the tests to
		#	work thats how it has to be)
		userDict['id'] = self.user.pk
		userDict['username'] = username
		count = len(User.objects.all())

		jsonData = json.dumps(userDict, cls=DateTimeAwareEncoder)

		response = self.client.post(reverse('chat:api:user-create'), data=jsonData,
			content_type='application/json')

		rdata = json.loads(response.content)

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

	def testGetSuccess(self):
		login(self.client)

		response = self.client.get(reverse('chat:api:profile-rest',
			args=(self.user.pk, )), content_type='application/json')
	
		response_user = json.loads(response.content, cls=DateTimeAwareDecoder)

		userForm = ProfileForm(response_user,
			instance=Profile.objects.get(pk=response_user['id']))
		#ensure the data we got is valid
		self.assertEqual(userForm.is_valid(), True)

	def testGetInvalidInput(self):
		login(self.client)

		response = self.client.get(reverse('chat:api:profile-rest',
			args=(invalidPk, )), content_type='application/json')
	
		rdata = json.loads(response.content, cls=DateTimeAwareDecoder)

		self.assertEquals(rdata[API_RESULT], API_FAIL)
		errMsg = "Invalid response - got '%s' when I should have got '%s' " % \
			(rdata[API_ERROR],"id 9999 does not exist (Profile)", )
		self.assertTrue(rdata[API_ERROR] ==  
			"id 9999 does not exist (Profile)", errMsg)

	def testGetNotLoggedIn(self):
		# login(self.client)
		response = self.client.get(reverse('chat:api:profile-rest',
			args=(invalidPk, )), content_type='application/json')
		self.assertTrue(response.status_code, 302)

	def testLoggedInGetProfile(self):
		login(self.client)

		response = self.client.get(reverse('chat:api:login-test', args=(self.user.pk, )),
			content_type='application/json')
		
		response_user = json.loads(response.content, cls=DateTimeAwareDecoder)
		userForm = ProfileForm(response_user,
			instance=Profile.objects.get(pk=response_user['id']))

		self.assertEqual(userForm.is_valid(), True)

	def testPutSuccess(self):
		login(self.client)

		user = User.objects.create_user(username='another_user')
		user.save()
		self.profile.user = user
		profileDict = model_to_dict(self.profile)
		jsonData = json.dumps(profileDict, cls=DateTimeAwareEncoder)

		response = self.client.put(reverse('chat:api:profile-rest',
			args=(self.user.pk, )), data=jsonData, content_type='application/json')

		rdata = json.loads(response.content)

		self.assertEquals(rdata[API_RESULT], API_SUCCESS)
		self.assertNotEquals(Profile.objects.get(pk=self.profile.pk).user.pk,
			self.user.pk)
		self.assertEquals(Profile.objects.get(pk=self.profile.pk).user.pk, user.pk)

	def testPutFailInvalid(self):
		''' Tests if the id of the profile sent matches the id of the actual user tied to
				that profile in the database.  In this case it is not, so it should fail.
		'''
		login(self.client)

		user = User.objects.create_user(username='another_user')
		user.save()
		self.profile.user = user
		profileDict = model_to_dict(self.profile)
		profileDict['user'] = invalidPk
		jsonData = json.dumps(profileDict, cls=DateTimeAwareEncoder)

		response = self.client.put(reverse('chat:api:profile-rest',
			args=(self.user.pk, )), data=jsonData, content_type='application/json')

		rdata = json.loads(response.content)

		self.assertEquals(rdata[API_RESULT], API_FAIL)

	def testPutFailure(self):
		''' Invalid profile id sent, should fail and not touch the profiles.
		'''
		login(self.client)
		user = User.objects.create_user(username='another_user')
		user.save()
		self.profile.user = user
		profileDict = model_to_dict(self.profile)
		profileDict['id'] = profileDict['id'] + 1
		jsonData = json.dumps(profileDict, cls=DateTimeAwareEncoder)

		response = self.client.put(reverse('chat:api:profile-rest', 
		 	args=(self.user.username, ) ), data=jsonData, content_type='application/json')

		rdata = json.loads(response.content)

		self.assertEquals(rdata[API_RESULT], API_FAIL)
		self.assertEquals(Profile.objects.get(pk=self.profile.pk).user.pk, self.user.pk)
		self.assertNotEquals(Profile.objects.get(pk=self.profile.pk).user.pk, user.pk)


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
		self.user = User.objects.create_user(username=username, password='work')
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
		login(self.client, user=self.user)
		# dummyGet = self.factory.get(reverse('chat:api:message-rest',
		# 	args=(self.conversation.pk, self.msg1.id, )))


		# response = self.view.get(dummyGet, pk=self.msg1.id)
		response = self.client.get(reverse('chat:api:message-rest',
			args=(self.conversation.pk, self.msg1.id, )), content_type='application/json')

		response_message = json.loads(response.content, cls=DateTimeAwareDecoder)

		messageForm = MessageForm(response_message,
			instance=Message.objects.get(pk=response_message['id']))

		#ensure the data we got is valid
		self.assertEqual(messageForm.is_valid(), True)

	def testGetFailMsg(self):
		''' Message doesn't belong in convo and User doesnt
		'''
		# message isn't in conversation (but user is)
		login(self.client, user=self.user)
		m = Message(sender=self.user, text='bogusmessage')
		m.save()

		response = self.client.get(reverse('chat:api:message-rest',
			args=(self.conversation.pk, m.pk, )), content_type='application/json')

		self.assertEquals(response.status_code, 400)

		# user isn't in conversation, but message is
		login(self.client, username='newUser', password='work')
		response = self.client.get(reverse('chat:api:message-rest',
			args=(self.conversation.pk, self.msg1.pk, )), content_type='application/json')

		self.assertEquals(response.status_code, 404)		


	def testGetFail(self):
		login(self.client)
		response = self.client.get(reverse('chat:api:message-rest',
			args=(self.conversation.pk, 'bogusmessageid', )),
			content_type='application/json')

		response_message = json.loads(response.content, cls=DateTimeAwareDecoder)

		self.assertEquals(response_message[API_RESULT], API_FAIL)

		with self.assertRaises(Message.DoesNotExist):
			msg = Message.objects.get(pk='bogusmessageid')

	def testDeleteSuccess(self):
		login(self.client, user=self.user, password='work')

		self.assertEquals(len(Message.objects.all()), 2)

		response = self.client.delete(reverse('chat:api:message-rest',
			args=(self.conversation.pk, self.msg1.pk, )), content_type='application/json')

		rdata = json.loads(response.content)

		self.assertEquals(len(Message.objects.all()), 1)
		with self.assertRaises(Message.DoesNotExist):
			Message.objects.get(pk=rdata['id'])

	def testDeleteFailure(self):
		login(self.client, user=self.user, password='work')
		self.assertEquals(len(Message.objects.all()), 2)


		response = self.client.delete(reverse('chat:api:message-rest',
			args=(self.conversation.pk, 'bogusmessageid',)),
			content_type='application/json', cpk=self.conversation.pk, pk='bogusmessageid'
			)

		rdata = json.loads(response.content)
		self.assertEquals(response.status_code, 400)
		self.assertEquals(len(Message.objects.all()), 2)
		self.assertEquals(rdata[API_RESULT], API_FAIL)

	def testPut(self):
		#this should always fail
		user = User.objects.create_user(username='bogusGuru', password='work')
		user.save()
		self.msg1.sender = user

		login(self.client, user=user, password='work')

		messageDict = model_to_dict(self.msg1)
		jsonData = json.dumps(messageDict, cls=DateTimeAwareEncoder)

		response = self.client.put(reverse('chat:api:message-rest', args=(
		 	self.conversation.pk, self.msg1.pk, ) ), data=jsonData,
			content_type='application/json')

		self.assertEquals(response.status_code, 400)

	def testPostSuccess(self):
		login(self.client, user=self.user, password='work')

		msg = Message(sender=self.user, text='new message')
		msg.id = 'uniqueuniqueunique'
		messageDict = model_to_dict(msg)
		
		count = len(Message.objects.all())
		jsonData = json.dumps(messageDict, cls=DateTimeAwareEncoder)

		response = self.client.post(reverse('chat:api:message-create',
			args=(self.conversation.pk, )), data=jsonData,
		 	content_type='application/json')

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
		login(self.client, user=self.user, password='work')

		msg = Message(sender=self.user, text='new message')
		msg.id = self.msg1.id
		messageDict = model_to_dict(msg)
		
		count = len(Message.objects.all())
		jsonData = json.dumps(messageDict, cls=DateTimeAwareEncoder)

		response = self.client.post(reverse('chat:api:message-create',
			args=(self.conversation.pk, )), data=jsonData,
		 	content_type='application/json')

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
		self.user = User.objects.create_user(username=username, password='work')
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
		login(self.client, user=self.user, password='work')

		self.conversation.participants.add(self.user)
		self.conversation.save()

		response = self.client.get(reverse('chat:api:conversation-rest',
			args=(self.conversation.id, )), content_type='application/json')

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
		login(self.client)

		convo = Conversation()
		conversationDict = model_to_dict(convo)
		count = len(Conversation.objects.all())
		jsonData = json.dumps(conversationDict, cls=DateTimeAwareEncoder)

		# dummyPost = self.factory.post(reverse('chat:api:conversation-create'), data=jsonData,
		# 	content_type='application/json')

		# response = self.createView.post(dummyPost, content_type='application/json')

		response = self.client.post(reverse('chat:api:conversation-create'), data=jsonData,
			content_type='application/json')

		rdata = json.loads(response.content)

		self.assertEquals(count + 1, len(Conversation.objects.all()))
		try:
			newConvoObj = Conversation.objects.get(pk=rdata['id'])
		except Conversation.DoesNotExist:
			self.assertTrue(false, "error with message post")

	def testPut(self):
		login(self.client)
		#this should always fail
		convo = Conversation()
		convo.save()
		convo.participants.add(self.user)
		
		convoDict = model_to_dict(convo)
		jsonData = json.dumps(convoDict, cls=DateTimeAwareEncoder)

		response = self.client.put(reverse('chat:api:conversation-rest', args=(
			str(convo.pk), ) ), data=jsonData, content_type='application/json')

		rdata = json.loads(response.content)

		self.assertTrue(rdata[API_RESULT], API_FAIL)
		self.assertTrue(response.status_code == 400)

	def testDeleteFail(self):
		''' This tests a user trying to delete a conversation they don't belong to.
				Should 404
		'''
		login(self.client)
		response = self.client.delete(reverse('chat:api:conversation-rest',
			args=(self.conversation.id, ) ), content_type='application/json')

		self.assertEquals(response.status_code, 404)

	def testDeleteSuccess(self):
		''' This tests a user trying to delete a conversation they belong to.
				Should 200
		'''
		user = User.objects.create_user(username='user1', password='work')
		user.save()

		self.conversation.participants.add(user)
		self.conversation.save()

		count = len(Conversation.objects.all())

		login(self.client, user=user)
		response = self.client.delete(reverse('chat:api:conversation-rest',
			args=(self.conversation.id, ) ), content_type='application/json')
		rdata = json.loads(response.content)


		self.assertEquals(count - 1, len(Conversation.objects.all()))
		self.assertEquals(response.status_code, 200)
		self.assertEquals(rdata[API_RESULT], API_SUCCESS)