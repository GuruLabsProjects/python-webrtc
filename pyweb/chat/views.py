import uuid, json, logging, datetime, traceback

from django.shortcuts import render, render_to_response

from django.core import serializers
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse

from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseNotFound

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
from .forms import UserForm, ProfileForm, MessageForm, ConversationForm, \
	UserCreateForm, MessageCreateForm, ConversationCreateForm

logger = logging.getLogger(__name__)

API_SUCCESS = 'success'
API_FAIL = 'fail'
API_ERROR = 'error'
API_RESULT = 'result'

API_INVALID_DATA = "invalid data: (%s) - errors:(%s)"
API_BAD_PK = "id %s does not exist (%s)"

class BaseView(View):
	def getFailResponse(self, error=None):
		response = {}
		response[API_RESULT] = API_FAIL
		if error:
			response[API_ERROR] = error
		return response

	def getSuccessResponse(self, **kwargs):
		response = {}
		response[API_RESULT] = API_SUCCESS
		for key, value in kwargs.iteritems():
			response[str(key)] = value
		return response

	def invalidRequest(self, error=''):
		error = self.__class__.__name__
		response = self.getFailResponse(str(' : '.join([str(traceback.format_exc()),
			error])))
		return HttpResponseBadRequest(json.dumps(response))

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

		except User.DoesNotExist:
			return HttpResponseNotFound(json.dumps(self.getFailResponse()))

	@method_decorator(login_required)
	def put(self, request, *args, **kwargs):
		rdata = json.loads(request.body, cls=DateTimeAwareDecoder)
		try:
			# ensure the requesting user is logged in and requesting the right user obj
			if str(request.user.pk) == str(kwargs['pk']):

				user = User.objects.get(pk=kwargs['pk'])
				userForm = UserForm(rdata, instance=user)

				if userForm.is_valid():
					userForm.save()
					response = self.getSuccessResponse(id=userForm.data['id'])
					return HttpResponse(json.dumps(response))

				else:
					response[API_ERROR] = dict(userForm.errors.items())

			response = self.getFailResponse()
			return HttpResponseNotFound(json.dumps(response))

		except User.DoesNotExist:
			response = self.getFailResponse(API_BAD_PK % (kwargs['pk'], User.__name__))
		return HttpResponseBadRequest(json.dumps(response))

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

			response = self.getFailResponse()
			# response[API_ERROR] = "%s vs %s" % (request.user.pk, kwargs['pk'], )
			return HttpResponseNotFound(json.dumps(response))

		except User.DoesNotExist:
			response = self.getFailResponse(API_BAD_PK % (kwargs['pk'], User.__name__))
			return HttpResponseBadRequest(json.dumps(response))


class UserAuthenticateView(BaseView):

	def post(self, request, *args, **kwargs):

		rdata = json.loads(request.body, cls=DateTimeAwareDecoder)

		response = {}
		try:
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
				response = self.getFailResponse(API_INVALID_DATA % (str(rdata),
					authForm.errors))

		except User.DoesNotExist:
			response = self.getFailResponse()
			return HttpResponseNotFound(json.dumps(response))
			# response[API_ERROR] = API_BAD_PK % (kwargs['pk'], self.model.__name__)

		except ValidationError as err:
			response = self.getFailResponse(err)
		return HttpResponseBadRequest(json.dumps(response))


class UserCreateView(BaseView):

	def post(self, request, *args, **kwargs):
		rdata = json.loads(request.body, cls=DateTimeAwareDecoder)
		response = {}
		try:
			userForm = UserCreationForm(rdata)

			if userForm.is_valid():
				user = userForm.save()
				profile = Profile(user=user)
				profile.save()
				response = self.getSuccessResponse(id=user.pk)
				return HttpResponse(json.dumps(response))

			else: response[API_ERROR] = dict(userForm.errors.items())

		except self.model.DoesNotExist:
			response[API_RESULT] = API_FAIL
			response[API_ERROR] = API_BAD_PK % (kwargs['pk'], self.model.__name__)
		
		return HttpResponseBadRequest(json.dumps(response))


class ProfileRestView(RestView):

	@method_decorator(login_required)
	def get(self, request, *args, **kwargs):
		try:
			profile = Profile.objects.get(user=kwargs['pk'])
			return HttpResponse(json.dumps(model_to_dict(profile),
				cls=DateTimeAwareEncoder), content_type='application/json')

		except Profile.DoesNotExist:
			response = self.getFailResponse(API_BAD_PK % (kwargs['pk'], Profile.__name__))
			return HttpResponseBadRequest(json.dumps(response))

	@method_decorator(login_required)
	def put(self, request, *args, **kwargs):
		rdata = json.loads(request.body, cls=DateTimeAwareDecoder)
		response = {}
		try:
			profile = Profile.objects.get(pk=rdata['id'])
			profileForm = ProfileForm(rdata, instance=profile)

			# ensure the user is updating him/herself only 
			if profileForm.is_valid() and profile.user.pk == rdata['user']:

				profileForm.save()
				response = self.getSuccessResponse(id=profileForm.data['id'])
				return HttpResponse(json.dumps(response))

			else:
				response = self.getFailResponse(API_INVALID_DATA % (str(rdata),
					profileForm.errors))

		except Profile.DoesNotExist:
			response = self.getFailResponse(API_BAD_PK % (kwargs['pk'], Profile.__name__))
		return HttpResponseBadRequest(json.dumps(response))

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
				response = self.getFailResponse()
				# response[API_RESULT] = 'user doesnt belong in that convo'
				return HttpResponseNotFound(json.dumps(response))

		except Conversation.DoesNotExist:
			response = self.getFailResponse(API_BAD_PK % (kwargs['pk'],
				Conversation.__name__))
			return HttpResponseBadRequest(json.dumps(response))

	@method_decorator(login_required)
	def delete(self, request, *args, **kwargs):
		response = {}
		try:
			convoObj = Conversation.objects.get(pk=kwargs['pk'])

			if request.user in convoObj.participants.all():
				convoObj.delete()
				response = self.getSuccessResponse(id=kwargs['pk'])
			else:
				response = self.getFailResponse()
				# response[API_RESULT] = 'user doesnt belong in that convo'
				return HttpResponseNotFound(json.dumps(response))

		except Conversation.DoesNotExist:
			response = self.getFailResponse(API_BAD_PK % (kwargs['pk'],
				Conversation.__name__))
			return HttpResponseBadRequest(json.dumps(response))
		return HttpResponse(json.dumps(response))

class ConversationCreateView(BaseView):

	@method_decorator(login_required)
	def post(self, request, *args, **kwargs):
		rdata = json.loads(request.body, cls=DateTimeAwareDecoder)
		response = {}
		try:
			convoForm = ConversationCreateForm(rdata)

			if convoForm.is_valid():
				convo = convoForm.save()
				response = self.getSuccessResponse(id=convo.pk)
				return HttpResponse(json.dumps(response))

			else:
				response = self.getFailResponse(API_INVALID_DATA % (str(rdata),
					convoForm.errors))

		except Conversation.DoesNotExist:
			response = self.getFailResponse(API_BAD_PK % (kwargs['pk'],
				Conversation.__name__))
		return HttpResponseBadRequest(json.dumps(response))

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

			response = self.getFailResponse()
			return HttpResponseNotFound(json.dumps(response))	

		except Message.DoesNotExist:
			response = self.getFailResponse()
			return HttpResponseBadRequest(json.dumps(response))

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

			response = self.getFailResponse()
			return HttpResponseNotFound(json.dumps(response))
		except Message.DoesNotExist:
			response = self.getFailResponse(API_BAD_PK % (kwargs['pk'], Message.__name__))
			return HttpResponseBadRequest(json.dumps(response))

class MessageCreateView(BaseView):

	@method_decorator(login_required)
	def post(self, request, *args, **kwargs):
		rdata = json.loads(request.body, cls=DateTimeAwareDecoder)
		response = {}
		try:
			msgForm = MessageForm(rdata)
			conversation = Conversation.objects.get(pk=kwargs['cpk'])
			if not msgForm.is_valid():
				response = self.getFailResponse(API_INVALID_DATA % (str(rdata),
					msgForm.errors))

			elif request.user in conversation.participants.all():
				obj = msgForm.save()
				conversation.messages.add(obj)
				conversation.save()
				response = self.getSuccessResponse(id=obj.pk)
				return HttpResponse(json.dumps(response))

			else:
				response = self.getFailResponse()
				return HttpResponseNotFound(json.dumps(response))
		except Message.DoesNotExist:
			response = self.getFailResponse(' - '.join([API_BAD_PK % (kwargs['pk'],
				Message.__name__), (API_BAD_PK % (kwargs['cpk']))]))
		return HttpResponseBadRequest(json.dumps(response))


def application_index(request):
	'''	Index view for the chat application. Checks to see if a user is authenticated.
		If a user is authenticated, the view returns the active user index page.
		Otherwise the "create user" page is provided.
	'''
	vname = 'chat.create-account.html'
	if request.user.is_authenticated(): vname = 'index.html'
	return render_to_response(vname, {
			'title' : 'Guru Labs Chat Demo Application',
		}, context_instance=RequestContext(request))


def form_user_create(request):
	return render_to_response('forms/user-create.html', {
			'form' : UserCreateForm(),
			'createurl' : reverse('chat:api:user-create')
		}, context_instance=RequestContext(request))