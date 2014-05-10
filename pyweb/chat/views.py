import logging, traceback
import datetime
import uuid
import json
import urlparse, requests

from django.conf import settings
from django.shortcuts import render, render_to_response

from django.core import serializers
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse

from django.http import HttpResponse, HttpResponseBadRequest, \
	HttpResponseNotFound, HttpResponseRedirect

from django.contrib.auth import logout

from django.views.generic import View
from django.template import Context, loader, RequestContext
from django.utils.decorators import method_decorator

from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

from django.forms.models import model_to_dict

from .helpers import DateTimeAwareEncoder, DateTimeAwareDecoder

from .models import Profile, Message, Conversation
from .forms import UserForm, ProfileForm, MessageForm, \
	UserCreateForm, MessageCreateForm, ConversationCreateForm

logger = logging.getLogger(__name__)

API_SUCCESS = 'success'
API_FAIL = 'fail'
API_ERROR = 'error'
API_RESULT = 'result'

API_INVALID_DATA = "invalid data: (%s) - errors:(%s)"
API_BAD_PK = "id %s does not exist (%s)"



# Helper Methods

def user_data(user):
	''' Conver user objects to a format easily consumed by Backbone.js
	'''
	return {'id' : user.get_username(), 'displayname' : user.get_full_name() }


def message_data(cmessage):
	'''	Convert conversation messages to a format that can be easily
		consumed by Backbone.js models
		1. Substitute user names for primary keys
	'''
	cmessage_data = model_to_dict(cmessage)
	if cmessage.sender:
		cmessage_data['sender'] = user_data(cmessage.sender)
	return cmessage_data


def conversation_data(conversation):
	'''	Convert conversation messages to a format that can be easily
		consumed by Backbone.js models
		1. Substitute user information for primary keys
		2. Substitute message data for message IDs
	'''
	conversation_data = model_to_dict(conversation)
	conversation_data['participants'] = map(user_data, conversation.participants.all())
	# conversation_data['messages'] = map(message_data, conversation.messages.all())
	
	return conversation_data



class BaseView(View):

	def getFormErrorResponse(self, form):
		response = {}
		response['status'] = 'fail'
		response['error'] = dict(form.errors.items())
		return HttpResponseBadRequest(json.dumps(response))

	def getSuccessResponse(self, **kwargs):
		response = {}
		response[API_RESULT] = API_SUCCESS
		for key, value in kwargs.iteritems():
			response[str(key)] = value
		return response

	def invalidRequest(self):
		return HttpResponseBadRequest()

	def pushData(self, pdata):
		'''	Push data to a remote server
		'''
		control_url = urlparse.urlunparse((
			getattr(settings, 'CONTROL_SCHEME', 'http'), 
			':'.join([str(s) for s in (getattr(settings, 'MESSAGE_SERVER', 'localhost'), 
				getattr(settings, 'MESSAGE_PORT', '1789')) if s is not None]),
			'control', '', '', ''))
		print control_url

	def get(self, request, *args, **kwargs):
		return self.invalidRequest()

	def put(self, request, *args, **kwargs):
		return self.invalidRequest()

	def delete(self, request, *args, **kwargs):
		return self.invalidRequest()

	def post(self, request, *args, **kwargs):
		return self.invalidRequest()		

class UserRestView(BaseView):
	''' RestView for User class
	'''

	@method_decorator(login_required)
	def get(self, request, *args, **kwargs):
		# do we want to limit this so only the user logged in can get the details?
		try:
			obj = User.objects.get(pk=kwargs['pk'])
			return HttpResponse(json.dumps(model_to_dict(obj), cls=DateTimeAwareEncoder),
				content_type='application/json')

		except User.DoesNotExist as err:
			return HttpResponseNotFound(json.dumps(err.message))

	@method_decorator(login_required)
	def put(self, request, *args, **kwargs):
		try:
			rdata = json.loads(request.body, cls=DateTimeAwareDecoder)
			# ensure the requesting user is logged in and requesting the right user obj
			if str(request.user.pk) == str(kwargs['pk']):

				user = User.objects.get(pk=kwargs['pk'])
				userForm = UserForm(rdata, instance=user)

				if userForm.is_valid():
					userForm.save()
					response = self.getSuccessResponse(id=userForm.data['id'])
					return HttpResponse(json.dumps(response))

				else:
					return self.getFormErrorResponse(userForm)

			return HttpResponseBadRequest()

		except User.DoesNotExist as err:
			return HttpResponseNotFound(json.dumps(err.message))
		except TypeError as err:
			return HttpResponseNotFound(json.dumps(err.message))
		except KeyError as err:
			return HttpResponseNotFound(json.dumps(err.message))

	@method_decorator(login_required)
	def delete(self, request, *args, **kwargs):
		response = {}
		try:		
			# ensure the requesting user is logged in and requesting the right user obj
			if str(request.user.pk) == str(kwargs['pk']):	
				user = User.objects.get(pk=kwargs['pk'])
				user.delete()
				response = self.getSuccessResponse(id=kwargs['pk'])
				return HttpResponse(json.dumps(response))

			# response[API_ERROR] = "%s vs %s" % (request.user.pk, kwargs['pk'], )
			return HttpResponseBadRequest()

		except User.DoesNotExist as err:
			return HttpResponseNotFound(json.dumps(err.message))


class UserAuthenticateView(BaseView):

	def post(self, request, *args, **kwargs):
		try:
			rdata = json.loads(request.body, cls=DateTimeAwareDecoder)

			response = {}
			authForm = AuthenticationForm(data=rdata)

			if authForm.is_valid():

				user = authenticate(username=authForm.cleaned_data['username'],
					password=authForm.cleaned_data['password'])

				if user:
					if user.is_active:
						login(request, user)
						response = self.getSuccessResponse()
						return HttpResponse(json.dumps(response))
					else:
						raise self.ValidationError("User account %s is disabled" % \
						username)
				else:
					raise ValidationError("Invalid username and/or password")
			else:
				return self.getFormErrorResponse(authForm)

		except User.DoesNotExist as err:
			return HttpResponseNotFound(json.dumps(err.message))

		except ValidationError as err:
			return HttpResponseNotFound(json.dumps(err.message))
		except TypeError as err:
			return HttpResponseNotFound(json.dumps(err.message))


class UserCreateView(BaseView):

	def post(self, request, *args, **kwargs):
		try:
			rdata = json.loads(request.body, cls=DateTimeAwareDecoder)
			response = {}
			userForm = UserCreateForm(rdata)

			if userForm.is_valid():
				user = userForm.save()
				profile = Profile(user=user)
				profile.save()
				response = self.getSuccessResponse(id=user.pk)
				return HttpResponse(json.dumps(response))

			else: 
				return self.getFormErrorResponse(userForm)
		except TypeError as err:
			return HttpResponseNotFound(json.dumps(err.message))		


class ProfileRestView(BaseView):

	@method_decorator(login_required)
	def get(self, request, *args, **kwargs):
		try:
			profile = Profile.objects.get(user=kwargs['pk'])
			return HttpResponse(json.dumps(model_to_dict(profile),
				cls=DateTimeAwareEncoder), content_type='application/json')

		except Profile.DoesNotExist as err:
			return HttpResponseNotFound(json.dumps(err.message))
		except KeyError as err:
			return HttpResponseNotFound(json.dumps(err.message))

	@method_decorator(login_required)
	def put(self, request, *args, **kwargs):
		try:
			rdata = json.loads(request.body, cls=DateTimeAwareDecoder)
			response = {}
			profile = Profile.objects.get(pk=rdata['id'])
			profileForm = ProfileForm(rdata, instance=profile)

			# ensure the user is updating him/herself only 
			if profile.user.pk == rdata['user']:
				if profileForm.is_valid():

					profileForm.save()
					response = self.getSuccessResponse(id=profileForm.data['id'])
					return HttpResponse(json.dumps(response))

				else: 
					return self.getFormErrorResponse(profileForm)
			return HttpResponseNotFound()
		except Profile.DoesNotExist as err:
			return HttpResponseNotFound(json.dumps(err.message))
		except KeyError as err:
			return HttpResponseNotFound(json.dumps(err.message))
		except TypeError as err:
			return HttpResponseNotFound(json.dumps(err.message))

class ConversationRestView(BaseView):

	@method_decorator(login_required)
	def get(self, request, *args, **kwargs):
		try:			
			obj = Conversation.objects.get(pk=kwargs['pk'])

			if request.user in obj.participants.all():

				msgs = list(obj.messages.all())
				response = []

				for msg in msgs:
					response.append({'id' : msg.pk, 'text' : msg.text})

				return HttpResponse(json.dumps(response, cls=DateTimeAwareEncoder),
					content_type='application/json')
			else:
				return HttpResponseNotFound("")

		except Conversation.DoesNotExist as err:
			return HttpResponseNotFound(json.dumps(err.message))
		except KeyError as err:
			return HttpResponseNotFound(json.dumps(err.message))

	@method_decorator(login_required)
	def delete(self, request, *args, **kwargs):
		response = {}
		try:
			convoObj = Conversation.objects.get(pk=kwargs['pk'])
			if request.user in convoObj.participants.all():
				convoObj.delete()
				response = self.getSuccessResponse(id=kwargs['pk'])
				return HttpResponse(json.dumps(response))
			else:
				return HttpResponseNotFound()

		except Conversation.DoesNotExist as err:
			return HttpResponseNotFound(json.dumps(err.message))
		except KeyError as err:
			return HttpResponseNotFound(json.dumps(err.message))


class ConversationCreateView(BaseView):
	'''	View used to create conversations and to retrieve all active conversations for a user
	'''

	@method_decorator(login_required)
	def get(self, request, *args, **kwargs):
		''' Retrieve all active conversations for a user
		'''
		active_conversations = Conversation.objects.filter(participants=request.user)
		return HttpResponse(json.dumps([conversation_data(conv) for conv in active_conversations],
			cls=DateTimeAwareEncoder))

	@method_decorator(login_required)
	def post(self, request, *args, **kwargs):
		try:
			rdata = json.loads(request.body, cls=DateTimeAwareDecoder)
			response = {}
			
			# Create conversation
			conversation = Conversation()
			conversation.save()
			
			# Add users
			for ruid in rdata.get('participants', []):
				try:
					cuser = User.objects.get(username=ruid)
					conversation.participants.add(cuser)
				except User.DoesNotExist:
					conversation.delete()
					response['error'] = 'Conversations user does not exst'
					return HttpResponseBadRequest(json.dumps(response))
			
			response = self.getSuccessResponse(id=conversation.id)

			# Push data to client
			try: self.pushData({ 'opcode' : 'tst-op' })
			except: print traceback.print_exc()

			return HttpResponse(json.dumps(response))

		except Conversation.DoesNotExist as err:
			return HttpResponseNotFound(json.dumps(err.message))
		except TypeError as err:
			return HttpResponseNotFound(json.dumps(err.message))


class MessageRestView(BaseView):

	@method_decorator(login_required)
	def get(self, request, *args, **kwargs):
		try:
			convo = Conversation.objects.get(pk=kwargs['cpk'])

			# ensure requesting user is participant in conversation
			if request.user in convo.participants.all():
				msg = convo.messages.get(pk=kwargs['pk'])

				return HttpResponse(json.dumps(model_to_dict(msg),
					cls=DateTimeAwareEncoder), content_type='application/json')
			return HttpResponseNotFound()	

		except Message.DoesNotExist as err:
			# the message is not in a conversation that they're requesting it for
			return HttpResponseNotFound() 
		except KeyError as err:
			return HttpResponseNotFound(json.dumps(err.message))

	@method_decorator(login_required)
	def delete(self, request, *args, **kwargs):
		response = {}
		try:
			convo = Conversation.objects.get(pk=kwargs['cpk'])
			# ensure requesting user is participant in conversation
			if request.user in convo.participants.all():
				msg = convo.messages.get(pk=kwargs['pk'])

				if(msg.sender == request.user):
					msg.delete()
					response = self.getSuccessResponse(id=kwargs['pk'])
					return HttpResponse(json.dumps(response))

			return HttpResponseNotFound()
		except Message.DoesNotExist as err:
			return HttpResponseNotFound(json.dumps(err.message))
		except KeyError as err:
			return HttpResponseNotFound(json.dumps(err.message))


class MessageCreateView(BaseView):


	@method_decorator(login_required)
	def get(self, request, *args, **kwargs):
		''' Retrieve all active conversations for a user
		'''
		try: conversation = Conversation.objects.get(pk=kwargs.get('cpk'))
		except Conversation.DoesNotExist: return HttpResponseNotFound()
		return HttpResponse(json.dumps([message_data(message) 
			for message in conversation.messages.all()], cls=DateTimeAwareEncoder))

	@method_decorator(login_required)
	def post(self, request, *args, **kwargs):
		try:
			rdata = json.loads(request.body, cls=DateTimeAwareDecoder)
			response = {}
			msgForm = MessageForm(rdata)
			conversation = Conversation.objects.get(pk=kwargs['cpk'])
			if not msgForm.is_valid():
				return self.getFormErrorResponse(msgForm)

			# Validate that the request user has permission to add messages to the conversation
			elif request.user in conversation.participants.all():
				obj = msgForm.save()
				# Add the request user as the sender
				obj.sender = request.user
				obj.save()
				conversation.messages.add(obj)
				conversation.save()
				response = self.getSuccessResponse(id=obj.pk)
				return HttpResponse(json.dumps(response))

			else:
				return HttpResponseNotFound()
		except Message.DoesNotExist as err:
			return HttpResponseNotFound(json.dumps(err.message))
		except TypeError as err:
			return HttpResponseNotFound(json.dumps(err.message))
		except KeyError as err:
			return HttpResponseNotFound(json.dumps(err.message))


def application_index(request):
	'''	Index view for the chat application. Checks to see if a user is authenticated.
		If a user is authenticated, the view returns the active user index page.
		Otherwise the "create user" page is provided.
	'''
	return render_to_response(
		'chat.active-user.html' if request.user.is_authenticated() else 'chat.create-account.html', {
			'title' : 'Guru Labs Chat Demo Application',
			'message_server' : getattr(settings, 'MESSAGE_SERVER', '127.0.0.1'),
			'message_port' : getattr(settings, 'MESSAGE_PORT', '1789'),
			'username' : request.user.get_username(),
			'displayname' : request.user.get_full_name(),
		} if request.user.is_authenticated() else {
			'title' : 'Welcome to Connections!',
		}, context_instance=RequestContext(request))


def chat_logout(request):
	'''	Log the user out of the application, return to the home page
	'''
	logout(request)
	return HttpResponseRedirect(reverse('chat:appindex'))


def form_user_create(request):
	return render_to_response('forms/user-create.html', {
			'form' : UserCreateForm(),
			'createurl' : reverse('chat:api:user-create')
		}, context_instance=RequestContext(request))


def form_user_auth(request):
	return render_to_response('forms/user-auth.html', {
			'form' : AuthenticationForm(),
			'createurl' : reverse('chat:api:user-authenticate')
		}, context_instance=RequestContext(request))