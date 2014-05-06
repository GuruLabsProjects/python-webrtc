import uuid, json, logging, datetime, traceback

from django.shortcuts import render, render_to_response

from django.core import serializers
from django.core.exceptions import ValidationError

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
from .forms import (UserForm, ProfileForm, MessageForm, ConversationForm,
	MessageCreateForm, ConversationCreateForm)

logger = logging.getLogger(__name__)

API_SUCCESS = 'success'
API_FAIL = 'fail'
API_ERROR = 'error'
API_RESULT = 'result'

API_INVALID_DATA = "invalid data: (%s) - errors:(%s)"
API_BAD_PK = "id %s does not exist (%s)"

class BaseView(View):
	def invalidRequest(self, error=''):
		error = self.__class__.__name__
		response = {}
		response[API_RESULT] = API_FAIL
		response[API_ERROR] = ' : '.join([str(traceback.format_exc()), error])
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
			response = {}
			response[API_RESULT] = API_FAIL
			return HttpResponseNotFound(json.dumps(response))

	@method_decorator(login_required)
	def put(self, request, *args, **kwargs):
		rdata = json.loads(request.body, cls=DateTimeAwareDecoder)
		response = {}
		try:
			# ensure the requesting user is logged in and requesting the right user obj
			if str(request.user.pk) == str(kwargs['pk']):

				user = User.objects.get(pk=kwargs['pk'])
				userForm = UserForm(rdata, instance=user)
				if userForm.is_valid():
					userForm.save()
					response['id'] = userForm.data['id']
					response[API_RESULT] = API_SUCCESS
					return HttpResponse(json.dumps(response))
				else:
					response[API_ERROR] = API_INVALID_DATA % (str(rdata), userForm.errors)
			response[API_RESULT] = API_FAIL
			return HttpResponseNotFound(json.dumps(response))

		except User.DoesNotExist:
			response[API_RESULT] = API_FAIL
			response[API_ERROR] = API_BAD_PK % (kwargs['pk'], User.__name__)
		return HttpResponseBadRequest(json.dumps(response))

	@method_decorator(login_required)
	def delete(self, request, *args, **kwargs):
		response = {}
		try:		
			# ensure the requesting user is logged in and requesting the right user obj
			if str(request.user.pk) == str(kwargs['pk']):	
				user = User.objects.get(pk=kwargs['pk'])
				user.delete()
				response['id'] = kwargs['pk']
				response[API_RESULT] = API_SUCCESS
				return HttpResponse(json.dumps(response))
			response[API_RESULT] = API_FAIL
			# response[API_ERROR] = "%s vs %s" % (request.user.pk, kwargs['pk'], )
			return HttpResponseNotFound(json.dumps(response))
		except User.DoesNotExist:
			response = {}
			response[API_RESULT] = API_FAIL
			response[API_ERROR] = API_BAD_PK % (kwargs['pk'], User.__name__)
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
						response[API_RESULT] = API_SUCCESS
						return HttpResponse(json.dumps(response))
					else:
						raise self.ValidationError("User account %s is disabled" % \
						username)
				else:
					raise ValidationError("Invalid username and/or password")
			else:
				response[API_RESULT] = API_FAIL
				response[API_ERROR] = API_INVALID_DATA % (str(rdata), authForm.errors)
		except User.DoesNotExist:
			response[API_RESULT] = API_FAIL
			return HttpResponseNotFound(json.dumps(response))
			# response[API_ERROR] = API_BAD_PK % (kwargs['pk'], self.model.__name__)
		except ValidationError as err:
			response[API_RESULT] = API_FAIL
			response[API_ERROR] = err
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
				response['id'] = user.pk
				response[API_RESULT] = API_SUCCESS
				return HttpResponse(json.dumps(response))

			else:
				response[API_RESULT] = API_FAIL
				response[API_ERROR] = API_INVALID_DATA % (str(rdata), userForm.errors)

		except User.DoesNotExist:
			response[API_RESULT] = API_FAIL
			response[API_ERROR] = API_BAD_PK % (kwargs['pk'], User.__name__)
		return HttpResponseBadRequest(json.dumps(response))

class ProfileRestView(BaseView):

	@method_decorator(login_required)
	def get(self, request, *args, **kwargs):
		try:
			profile = Profile.objects.get(user=kwargs['pk'])
			return HttpResponse(json.dumps(model_to_dict(profile), cls=DateTimeAwareEncoder),
				content_type='application/json')

		except Profile.DoesNotExist:
			response = {}
			response[API_RESULT] = API_FAIL
			response[API_ERROR] = API_BAD_PK % (kwargs['pk'], Profile.__name__)
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
				response['id'] = profileForm.data['id']
				response[API_RESULT] = API_SUCCESS
				return HttpResponse(json.dumps(response))
			else:
				response[API_RESULT] = API_FAIL
				response[API_ERROR] = API_INVALID_DATA % (str(rdata), profileForm.errors)

		except Profile.DoesNotExist:
			response[API_RESULT] = API_FAIL
			response[API_ERROR] = API_BAD_PK % (kwargs['pk'], Profile.__name__)
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
				response = {}
				response[API_RESULT] = API_FAIL
				# response[API_RESULT] = 'user doesnt belong in that convo'
				return HttpResponseNotFound(json.dumps(response))

		except Conversation.DoesNotExist:
			response = {}
			response[API_RESULT] = API_FAIL
			response[API_ERROR] = API_BAD_PK % (kwargs['pk'], Conversation.__name__)
			return HttpResponseBadRequest(json.dumps(response))

	@method_decorator(login_required)
	def delete(self, request, *args, **kwargs):
		response = {}
		try:
			dbObj = Conversation.objects.get(pk=kwargs['pk'])
			if request.user in dbObj.participants.all():
				dbObj.delete()
				response['id'] = kwargs['pk']
				response[API_RESULT] = API_SUCCESS
			else:
				response[API_RESULT] = API_FAIL
				# response[API_RESULT] = 'user doesnt belong in that convo'
				return HttpResponseNotFound(json.dumps(response))
		except Conversation.DoesNotExist:
			response = {}
			response[API_RESULT] = API_FAIL
			response[API_ERROR] = API_BAD_PK % (kwargs['pk'], Conversation.__name__)
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
				response['id'] = convo.pk
				response[API_RESULT] = API_SUCCESS
				return HttpResponse(json.dumps(response))
			else:
				response[API_RESULT] = API_FAIL
				response[API_ERROR] = API_INVALID_DATA % (str(rdata), convoForm.errors)

		except Conversation.DoesNotExist:
			response[API_RESULT] = API_FAIL
			response[API_ERROR] = API_BAD_PK % (kwargs['pk'], Conversation.__name__)
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
			response = {}
			response[API_RESULT] = API_FAIL
			response[API_ERROR] = 'message/user doesnt belong'
			return HttpResponseNotFound(json.dumps(response))				
		except Message.DoesNotExist:
			response = {}
			response[API_RESULT] = API_FAIL
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
					response['id'] = kwargs['pk']
					response[API_RESULT] = API_SUCCESS
					return HttpResponse(json.dumps(response))
			response = {}
			response[API_RESULT] = API_FAIL
			return HttpResponseNotFound(json.dumps(response))
		except Message.DoesNotExist:
			response = {}
			response[API_RESULT] = API_FAIL
			response[API_ERROR] = API_BAD_PK % (kwargs['pk'], Message.__name__)
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
				response[API_RESULT] = API_FAIL
				response[API_ERROR] = API_INVALID_DATA % (str(rdata), msgForm.errors)
			elif request.user in conversation.participants.all():
				obj = msgForm.save()
				conversation.messages.add(obj)
				conversation.save()
				response['id'] = obj.pk
				response[API_RESULT] = API_SUCCESS
				return HttpResponse(json.dumps(response))
			else:
				response[API_RESULT] = API_FAIL
				return HttpResponseNotFound(json.dumps(response))
		except Message.DoesNotExist:
			response[API_RESULT] = API_FAIL
			response[API_ERROR] = ' - '.join([API_BAD_PK % (kwargs['pk'],
				Message.__name__), (API_BAD_PK % (kwargs['cpk']))])
		return HttpResponseBadRequest(json.dumps(response))


def application_index(request):
	return render_to_response('index.html', {
			'title' : 'Guru Labs Chat Demo Application',
		}, context_instance=RequestContext(request))