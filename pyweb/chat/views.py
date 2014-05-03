import uuid, json, logging, datetime
from abc import ABCMeta

from django.shortcuts import render, render_to_response

from django.core import serializers

from django.http import HttpResponse, HttpResponseBadRequest
from django.contrib.auth.decorators import login_required

from django.views.generic import View
from django.template import Context, loader, RequestContext

from django.contrib.auth.models import User
from django.forms.models import model_to_dict

from .util import DateTimeAwareEncoder, DateTimeAwareDecoder

from .models import Profile, Message, Conversation
from .forms import UserForm, ProfileForm, MessageForm, ConversationForm

logger = logging.getLogger(__name__)

API_SUCCESS = 'success'
API_FAIL = 'fail'
API_ERROR = 'error'
API_RESULT = 'result'

API_INVALID_DATA = "invalid data:\n %s"
API_BAD_PK = "id %s does not exist (%s)"

class CreateView(View):
	def get(self, request, *args, **kwargs):
		response = {}
		try:
			raise Exception
		except Exception as e:
			response[API_RESULT] = API_FAIL
			response[API_ERROR] = str(e)
			return HttpResponseBadRequest(response)

	def put(self, request, *args, **kwargs):
		response = {}
		try:
			raise Exception
		except Exception as e:
			response[API_RESULT] = API_FAIL
			response[API_ERROR] = str(e)
			return HttpResponseBadRequest(response)

	def delete(self, request, *args, **kwargs):
		response = {}
		try:
			raise Exception
		except Exception as e:
			response[API_RESULT] = API_FAIL
			response[API_ERROR] = str(e)
			return HttpResponseBadRequest(response)

	def post(self, request, *args, **kwargs):
		rdata = json.loads(request.body, cls=DateTimeAwareDecoder)
		response = {}
		try:
			objForm = self.form(rdata)
			if not objForm.is_valid():
				response[API_RESULT] = API_FAIL
				response[API_ERROR] = API_INVALID_DATA % str(rdata)
			else:
				obj = objForm.save()
				foundPrimaryKey = False
				# for field in self.model._meta.fields:
				# 	if field.primary_key:
				# 		response[self.pk] = field.data
				# 		foundPrimaryKey = True
				# if not foundPrimaryKey:
				# 	response['id'] = None
				response[self.pkString] = obj.pk
				response[API_RESULT] = API_SUCCESS
				return HttpResponse(json.dumps(response))

		except self.model.DoesNotExist:
			response[API_RESULT] = API_FAIL
			response[API_ERROR] = API_BAD_PK % (kwargs[self.pkString], self.model.__name__)
		return HttpResponseBadRequest(json.dumps(response))


class RestView(View):
	''' Abstract class for RestView's.  Make sure each of the following are declared
		within child class.  RestView will take care of get, put*, delete*.
		self.model - Points to the Django model class
		self.form - points to the Django FormModel for the self.model class
		self.pkString - The primary key 'key' that will be passed through kwargs

		*not implemented yet
	'''
	def get(self, request, *args, **kwargs):
		try:
			obj = self.model.objects.get(pk=kwargs[self.pkString])
			return HttpResponse(json.dumps(model_to_dict(obj), cls=DateTimeAwareEncoder),
				content_type='application/json')
		except self.model.DoesNotExist:
			response = {}
			response[API_RESULT] = API_FAIL
			response[API_ERROR] = API_BAD_PK % (kwargs[self.pkString], self.model.__name__)
			return HttpResponseBadRequest(json.dumps(response))

	def put(self, request, *args, **kwargs):
		rdata = json.loads(request.body, cls=DateTimeAwareDecoder)
		response = {}
		try:
			dbObj = self.model.objects.get(pk=kwargs[self.pkString])

			objForm = self.form(rdata, instance=dbObj)

			if not objForm.is_valid():
				response[API_RESULT] = API_FAIL
				response[API_ERROR] = API_INVALID_DATA % str(rdata)
			else:
				objForm.save()
				response['id'] = objForm.data['id']
				response[API_RESULT] = API_SUCCESS
				return HttpResponse(json.dumps(response))

		except self.model.DoesNotExist:
			response[API_RESULT] = API_FAIL
			response[API_ERROR] = API_BAD_PK % (kwargs[self.pkString], self.model.__name__)
		return HttpResponseBadRequest(json.dumps(response))

	def delete(self, request, *args, **kwargs):
		response = {}
		try:
			dbObj = self.model.objects.get(pk=kwargs[self.pkString])
			dbObj.delete()
			response['id'] = kwargs[self.pkString]
			response[API_RESULT] = API_SUCCESS
		except self.model.DoesNotExist:
			response = {}
			response[API_RESULT] = API_FAIL
			response[API_ERROR] = API_BAD_PK % (kwargs[self.pkString], self.model.__name__)
			return HttpResponseBadRequest(json.dumps(response))
		return HttpResponse(json.dumps(response))

	def post(self, request, *args, **kwargs):
		response = {}
		try:
			raise Exception
		except Exception as e:
			response[API_RESULT] = API_FAIL
			response[API_ERROR] = str(e)
			return HttpResponseBadRequest(response)

class UserRestView(RestView):
	def __init__(self, *args, **kwargs):
		self.model = User
		self.form = UserForm
		self.pkString = 'pk'
		super(self.__class__, self).__init__(*args, **kwargs)

class UserCreateView(CreateView):
	def __init__(self, *args, **kwargs):
		self.model = User
		self.form = UserForm
		self.pkString = 'id'
		super(self.__class__, self).__init__(*args, **kwargs)


class ProfileRestView(RestView):

	def __init__(self, *args, **kwargs):
		self.model = Profile
		self.form = ProfileForm
		self.pkString = 'pk'
		super(self.__class__, self).__init__(*args, **kwargs)

class ProfileCreateView(View):
	def get(self, request, *args, **kwargs):
		return HttpResponseBadRequest()

	def put(self, request, *args, **kwargs):
		return HttpResponseBadRequest()

	def delete(self, request, *args, **kwargs):
		return HttpResponseBadRequest()

	def post(self, request, *args, **kwargs):
		pass

class ConversationRestView(RestView):
	def __init__(self, *args, **kwargs):
		self.model = Conversation
		self.form = ConversationForm
		self.pkString = 'pk'
		super(self.__class__, self).__init__(*args, **kwargs)

class ConversationCreateView(View):
	def get(self, request, *args, **kwargs):
		return HttpResponseBadRequest()

	def put(self, request, *args, **kwargs):
		return HttpResponseBadRequest()

	def delete(self, request, *args, **kwargs):
		return HttpResponseBadRequest()

	def post(self, request, *args, **kwargs):
		return HttpResponseBadRequest()

class MessageRestView(RestView):
	def __init__(self, *args, **kwargs):
		self.model = Message
		self.form = MessageForm
		self.pkString = 'message_id'
		super(self.__class__, self).__init__(*args, **kwargs)

	def put(self, request, *args, **kwargs):
		return HttpResponseBadRequest()

class MessageCreateView(View):
	def get(self, request, *args, **kwargs):
		return HttpResponseBadRequest()

	def put(self, request, *args, **kwargs):
		return HttpResponseBadRequest()

	def delete(self, request, *args, **kwargs):
		return HttpResponseBadRequest()

	def post(self, request, *args, **kwargs):
		return HttpResponseBadRequest()		


def application_index(request):
	return render_to_response('index.html', {
			'title' : 'Guru Labs Chat Demo Application',
		}, context_instance=RequestContext(request))